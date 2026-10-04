import asyncio
import html
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
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Design tokens + CSS
# ----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');

:root {
    --ink: #14213D;
    --paper: #F4F6FB;
    --card: #FFFFFF;
    --line: #DDE3F0;
    --muted: #5B6783;
    --marker: #FFD84D;
    --blue: #2F4BFF;
}

html, body, .stApp, [class*="st-"] {
    font-family: 'DM Sans', system-ui, sans-serif;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
}

#MainMenu, footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 820px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* ---------- Hero ---------- */

.hero {
    margin-bottom: 1.4rem;
}

.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(2rem, 6vw, 3.1rem);
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin: 0 0 .6rem 0;
    padding: 0;
}

.hero h1 span {
    background: linear-gradient(
        transparent 62%,
        var(--marker) 62%,
        var(--marker) 92%,
        transparent 92%
    );
    padding: 0 .15em;
    margin-left: -.15em;
}

.hero p {
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
    max-width: 52ch;
}

/* ---------- Starter prompts ---------- */

.stButton > button {
    background: var(--card);
    color: var(--ink);
    border: 1.5px solid var(--line);
    border-radius: 14px;
    padding: .9rem 1rem;
    text-align: left;
    font-weight: 500;
    width: 100%;
    min-height: 4.4rem;
    transition: border-color .15s ease, transform .15s ease;
}

.stButton > button:hover {
    border-color: var(--ink);
    color: var(--ink);
    transform: translateY(-1px);
}

.stButton > button:focus-visible {
    outline: 3px solid var(--blue);
    outline-offset: 2px;
}

.stButton > button p {
    text-align: left;
}

/* ---------- Chat ---------- */

[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 1rem 1.15rem;
    margin-bottom: .8rem;
    background: var(--card);
    border: 1.5px solid var(--line);
}

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) {
    background: var(--ink);
    border-color: var(--ink);
}

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) p,
[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) li {
    color: #FFFFFF;
}

[data-testid="stChatMessage"] p {
    line-height: 1.6;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
    border: 1.5px solid var(--line);
    background: var(--card);
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--ink);
}

/* ---------- Tool calls ---------- */

.chips {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    margin-top: .6rem;
}

.chip {
    background: #FFF6CC;
    border: 1.5px solid var(--marker);
    color: var(--ink);
    border-radius: 999px;
    padding: .15rem .7rem;
    font-size: .82rem;
    font-weight: 600;
}

[data-testid="stExpander"] {
    border: 1.5px solid var(--line);
    border-radius: 12px;
    background: #FAFBFE;
    margin-top: 1rem !important;
    margin-bottom: .25rem !important;
    overflow: visible !important;
}

[data-testid="stExpander"] summary {
    min-height: 2.75rem;
    padding: .7rem 1rem !important;
    line-height: 1.4 !important;
    align-items: center;
}

[data-testid="stExpander"] summary p {
    margin: 0 !important;
    line-height: 1.4 !important;
}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 0 1rem 1rem 1rem !important;
}

.toolcall {
    display: block;
    width: 100%;
    box-sizing: border-box;
    padding: .8rem 0;
    border-top: 1px dashed var(--line);
    line-height: 1.5;
}

.toolcall:first-child {
    border-top: none;
}

.toolcall b {
    font-family: 'Bricolage Grotesque', sans-serif;
}

.toolcall .label {
    color: var(--muted);
    font-size: .8rem;
}

.toolcall pre {
    background: #EEF1F9;
    border-radius: 8px;
    padding: .5rem .7rem;
    font-size: .82rem;
    white-space: pre-wrap;
    margin: .2rem 0 .5rem 0;
    color: var(--ink);
}

/* ---------- Sidebar ---------- */

[data-testid="stSidebar"] {
    background: var(--ink);
}

[data-testid="stSidebar"] * {
    color: #E9EDF8;
}

[data-testid="stSidebar"] h2 {
    font-family: 'Bricolage Grotesque', sans-serif;
    color: #FFFFFF;
    font-size: 1.25rem;
    margin-bottom: .2rem;
}

.tool-card {
    border: 1.5px solid rgba(255,255,255,.18);
    border-radius: 12px;
    padding: .7rem .85rem;
    margin-bottom: .6rem;
}

.tool-card b {
    color: #FFFFFF;
    display: block;
}

.tool-card span {
    color: #B8C1DA;
    font-size: .85rem;
}

.flow {
    color: #B8C1DA;
    font-size: .8rem;
    line-height: 1.7;
}

[data-testid="stSidebar"] .stButton > button {
    background: transparent;
    border: 1.5px solid rgba(255,255,255,.35);
    color: #FFFFFF;
    min-height: 0;
    padding: .5rem 1rem;
    text-align: center;
}

[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--marker);
    color: var(--marker);
}

@media (prefers-reduced-motion: reduce) {
    .stButton > button {
        transition: none;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Tool metadata
# ----------------------------------------------------------------------------

TOOL_INFO = {
    "calculate_percentage": (
        "🧮",
        "Percentage",
        "Marks, scores and ratios",
    ),
    "calculate_cgpa": (
        "📈",
        "CGPA",
        "Grade points across courses",
    ),
    "get_course_info": (
        "📚",
        "Course info",
        "CS course details",
    ),
}

STARTERS = [
    ("🧮", "What percentage is 432 out of 500?"),
    (
        "📈",
        "Calculate my CGPA: A in 3 credits, B+ in 4 credits, A- in 3 credits",
    ),
    ("📚", "Tell me about the Data Structures course"),
]


def tool_label(name):
    icon, label, _ = TOOL_INFO.get(
        name,
        ("🔧", name.replace("_", " ").title(), ""),
    )
    return f"{icon} {label}"


# ----------------------------------------------------------------------------
# MCP helpers
# ----------------------------------------------------------------------------

def get_tool_text(result):
    parts = []

    for item in result.content:
        if hasattr(item, "text"):
            parts.append(item.text)

    if parts:
        return "\n".join(parts)

    return str(
        result.structured_content
        if hasattr(result, "structured_content")
        else result
    )


def get_exception_details(exc):
    """
    Extract the real error from ExceptionGroup / TaskGroup errors.
    """
    details = [f"{type(exc).__name__}: {exc}"]

    if hasattr(exc, "exceptions"):
        for inner in exc.exceptions:
            details.append(
                f"{type(inner).__name__}: {inner}"
            )

            if hasattr(inner, "exceptions"):
                for nested in inner.exceptions:
                    details.append(
                        f"  {type(nested).__name__}: {nested}"
                    )

    return "\n".join(details)


# ----------------------------------------------------------------------------
# MCP + Groq agent
# ----------------------------------------------------------------------------

async def run_agent(history):

    # Get API key from Streamlit Secrets first
    try:
        api_key = st.secrets.get(
            "GROQ_API_KEY",
            os.getenv("GROQ_API_KEY"),
        )
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. "
            "Add it in Streamlit Cloud → Settings → Secrets."
        )

    # Get model
    try:
        model = st.secrets.get(
            "GROQ_MODEL",
            os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ),
        )
    except Exception:
        model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

    client = Groq(api_key=api_key)

    # MCP server parameters
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "mcp_server.py",
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path],
    )

    tool_calls_log = []

    try:

        async with stdio_client(server_params) as (read, write):

            async with ClientSession(read, write) as session:

                # Connect to MCP server
                await session.initialize()

                # Get available MCP tools
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
                            "You may call more than one tool when a request "
                            "needs multiple steps. "
                            "After receiving tool results, "
                            "give a clear final answer."
                        ),
                    },
                    *history,
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

                    # --------------------------------------------------------
                    # AI requested MCP tool(s)
                    # --------------------------------------------------------

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

                            # Parse arguments
                            try:
                                arguments = json.loads(
                                    call.function.arguments or "{}"
                                )
                            except json.JSONDecodeError:
                                arguments = {}

                            # Call MCP tool
                            try:

                                result = await session.call_tool(
                                    tool_name,
                                    arguments=arguments,
                                )

                                result_text = get_tool_text(result)

                            except Exception as exc:

                                result_text = (
                                    f"Tool error: "
                                    f"{get_exception_details(exc)}"
                                )

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

                    # --------------------------------------------------------
                    # Final AI answer
                    # --------------------------------------------------------

                    return (
                        message.content,
                        available_tools,
                        tool_calls_log,
                    )

    except Exception as exc:

        # Show the actual MCP / TaskGroup error
        raise RuntimeError(
            "MCP connection failed.\n\n"
            + get_exception_details(exc)
        ) from exc


# ----------------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------------

def render_tool_calls(tool_calls):

    if not tool_calls:
        return

    chips = "".join(
        f'<span class="chip">'
        f'{html.escape(tool_label(c["tool"]))}'
        f'</span>'
        for c in tool_calls
    )

    st.markdown(
        f'<div class="chips">{chips}</div>',
        unsafe_allow_html=True,
    )

    count = len(tool_calls)

    with st.expander(
        f"See how this was worked out "
        f"({count} tool call{'s' if count != 1 else ''})"
    ):

        blocks = []

        for c in tool_calls:

            args = html.escape(
                json.dumps(
                    c["arguments"],
                    indent=2,
                    ensure_ascii=False,
                )
            )

            result = html.escape(
                str(c["result"])
            )

            blocks.append(
                f'<div class="toolcall">'
                f'<b>{html.escape(tool_label(c["tool"]))}</b>'
                f'<div class="label">Input</div>'
                f'<pre>{args}</pre>'
                f'<div class="label">Result</div>'
                f'<pre>{result}</pre>'
                f'</div>'
            )

        st.markdown(
            "".join(blocks),
            unsafe_allow_html=True,
        )


def render_message(m):

    avatar = (
        "🧑‍🎓"
        if m["role"] == "user"
        else "🎓"
    )

    with st.chat_message(
        m["role"],
        avatar=avatar,
    ):

        if m.get("error"):
            st.error(m["content"])
        else:
            st.markdown(m["content"])

        render_tool_calls(
            m.get("tool_calls")
        )


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------

with st.sidebar:

    st.header("Tools")

    st.caption(
        "The assistant picks the right one for each question."
    )

    for icon, label, desc in TOOL_INFO.values():

        st.markdown(
            f'<div class="tool-card">'
            f'<b>{icon} {label}</b>'
            f'<span>{desc}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="flow">'
        'Your question → AI agent → MCP client → '
        'MCP server → tool → answer'
        '</p>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Clear chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# ----------------------------------------------------------------------------
# State
# ----------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

typed = st.chat_input(
    "Ask about percentages, CGPA, or CS courses"
)

user_request = typed or st.session_state.pop(
    "queued",
    None,
)

if user_request:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_request,
        }
    )


# ----------------------------------------------------------------------------
# Main page
# ----------------------------------------------------------------------------

st.markdown(
    """
<div class="hero">
    <h1><span>Student Assistant</span></h1>
    <p>
        Work out percentages, calculate your CGPA,
        or look up a CS course.
        Powered by Groq and MCP tools.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


if not st.session_state.messages:

    st.write("Try one of these:")

    cols = st.columns(
        len(STARTERS)
    )

    for i, (col, (icon, prompt)) in enumerate(
        zip(cols, STARTERS)
    ):

        with col:

            if st.button(
                f"{icon}  {prompt}",
                key=f"starter_{i}",
            ):

                st.session_state.queued = prompt
                st.rerun()


# Display previous messages

for m in st.session_state.messages:
    render_message(m)


# ----------------------------------------------------------------------------
# Answer newest question
# ----------------------------------------------------------------------------

if user_request:

    # Send recent conversation to AI
    history = [
        {
            "role": m["role"],
            "content": m["content"],
        }
        for m in st.session_state.messages
        if not m.get("error")
    ][-12:]

    with st.chat_message(
        "assistant",
        avatar="🎓",
    ):

        with st.spinner(
            "Working on it..."
        ):

            try:

                answer, _, tool_calls = asyncio.run(
                    run_agent(history)
                )

                reply = {
                    "role": "assistant",
                    "content": (
                        answer
                        or
                        "I couldn't produce an answer. "
                        "Try rephrasing your question."
                    ),
                    "tool_calls": tool_calls,
                }

            except Exception as exc:

                # IMPORTANT:
                # Show actual underlying error instead of
                # only "unhandled errors in a TaskGroup"

                error_details = get_exception_details(exc)

                reply = {
                    "role": "assistant",
                    "content": (
                        "Something went wrong:\n\n"
                        + error_details
                    ),
                    "error": True,
                }

        if reply.get("error"):

            st.error(
                reply["content"]
            )

        else:

            st.markdown(
                reply["content"]
            )

            render_tool_calls(
                reply["tool_calls"]
            )

    st.session_state.messages.append(
        reply
    )
