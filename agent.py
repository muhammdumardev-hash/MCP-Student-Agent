import asyncio
import json
import os
import sys

from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def get_tool_text(result):
    """Extract readable text from an MCP tool result."""
    parts = []

    for item in result.content:
        if hasattr(item, "text"):
            parts.append(item.text)

    if parts:
        return "\n".join(parts)

    return str(result.structured_content or result)


async def run_agent(user_request: str):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Add it as an environment variable before running the agent."
        )

    client = Groq(api_key=api_key)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_result = await session.list_tools()

            tools = []
            for tool in tool_result.tools:
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema,
                        },
                    }
                )

            print("\nAvailable MCP tools:")
            for tool in tool_result.tools:
                print(f"- {tool.name}")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful student assistant. "
                        "Use MCP tools whenever they are useful. "
                        "You may call more than one tool when a request needs multiple steps. "
                        "After receiving tool results, give a clear final answer."
                    ),
                },
                {"role": "user", "content": user_request},
            ]

            while True:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )

                message = response.choices[0].message

                assistant_message = {
                    "role": "assistant",
                    "content": message.content or "",
                }

                if message.tool_calls:
                    assistant_message["tool_calls"] = []

                    for call in message.tool_calls:
                        assistant_message["tool_calls"].append(
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {
                                    "name": call.function.name,
                                    "arguments": call.function.arguments,
                                },
                            }
                        )

                    messages.append(assistant_message)

                    for call in message.tool_calls:
                        tool_name = call.function.name

                        try:
                            arguments = json.loads(call.function.arguments or "{}")
                        except json.JSONDecodeError:
                            arguments = {}

                        print(f"\nMCP tool call: {tool_name}")
                        print(f"Arguments: {arguments}")

                        try:
                            result = await session.call_tool(
                                tool_name,
                                arguments=arguments,
                            )
                            result_text = get_tool_text(result)
                        except Exception as exc:
                            result_text = f"Tool error: {exc}"

                        print(f"Tool result: {result_text}")

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result_text,
                            }
                        )

                    continue

                print("\nFinal answer:")
                print(message.content)
                return


def main():
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = input("Ask the Student Assistant: ")

    asyncio.run(run_agent(request))


if __name__ == "__main__":
    main()
