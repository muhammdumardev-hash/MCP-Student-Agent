import asyncio
import json
import os
import sys

import streamlit as st
from groq import Groq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


st.set_page_config(
    page_title="MCP Student Assistant",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 MCP Student Assistant")
st.write("An AI student assistant powered by Groq and Model Context Protocol (MCP).")


def get_tool_text(result):
    parts = []

    for item in result.content:
        if hasattr(item, "text"):
            parts.append(item.text)

    if parts:
        return "\n".join(parts)

    return str(result.structured_content or result)


async def run_agent(user_request):
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets."
        )

    model = st.secrets.get(
        "GROQ_MODEL",
        os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    )

    client = Groq(api_key=api_key)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    tool_calls_log = []

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_result = await session.list_tools()

            tools = []
            available_tools = []

            for tool in tool_result.tools:
                available_tools.append(tool.name)
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
                    model=model,
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

                        try:
                            result = await session.call_tool(
                                tool_name,
                                arguments=arguments,
                            )
                            result_text = get_tool_text(result)
                        except Exception as exc:
                            result_text = f"Tool error: {exc}"

                        tool_calls_log.append(
                            {
                                "tool": tool_name,
                                "arguments": arguments,
                                "result": result_text,
                            }
                        )

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result_text,
                            }
                        )

                    continue

                return message.content, available_tools, tool_calls_log


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_request = st.chat_input("Ask about percentages, CGPA, or CS courses...")

with st.sidebar:
    st.header("MCP Tools")
    st.write("The AI can use these tools:")
    st.write("• calculate_percentage")
    st.write("• calculate_cgpa")
    st.write("• get_course_info")
    st.divider()
    st.caption("MCP flow: User → AI Agent → MCP Client → MCP Server → Tool → AI Response")

if user_request:
    st.session_state.messages.append(
        {"role": "user", "content": user_request}
    )

    with st.chat_message("user"):
        st.markdown(user_request)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and using MCP tools..."):
            try:
                answer, available_tools, tool_calls = asyncio.run(
                    run_agent(user_request)
                )

                st.markdown(answer)

                if tool_calls:
                    with st.expander("🔧 MCP tool calls"):
                        st.write("Available tools:", ", ".join(available_tools))
                        for call in tool_calls:
                            st.write(f"**Tool:** {call['tool']}")
                            st.write(f"**Arguments:** {call['arguments']}")
                            st.write(f"**Result:** {call['result']}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as exc:
                error_message = f"Error: {exc}"
                st.error(error_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_message}
                )
