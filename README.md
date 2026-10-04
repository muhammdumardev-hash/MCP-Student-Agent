# MCP Student Agent

A simple MCP-powered AI Student Assistant built with Streamlit, Groq, and the Model Context Protocol (MCP).

## Features

- Streamlit web interface
- MCP server with custom tools
- Groq AI agent
- Automatic MCP tool selection
- Successful MCP tool calls
- Multi-tool workflow

## MCP tools

1. `calculate_percentage`
2. `calculate_cgpa`
3. `get_course_info`

## Architecture

```text
User
  |
  v
Streamlit App
  |
  v
Groq AI Agent
  |
  v
MCP Client
  |
  v
MCP Server
  |
  +--> calculate_percentage
  +--> calculate_cgpa
  +--> get_course_info
```

## Streamlit deployment

### 1. Deploy the repository

On Streamlit Community Cloud, select this repository and set the main file to:

```text
app.py
```

### 2. Add the Groq API key

In Streamlit Cloud:

**App → Settings → Secrets**

Add:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL = "openai/gpt-oss-120b"
```

Do not upload your real API key to GitHub.

## Local setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Example questions

```text
Calculate the percentage for 680 marks out of 800.

Calculate my CGPA if I have 256.6 grade points and 90 credit hours.

Tell me about Data Communication.

Calculate my percentage for 680 out of 800 and tell me about Data Communication.
```

The last example demonstrates a multi-tool workflow because the AI can use more than one MCP tool before producing the final answer.

## Internship screenshots

Capture:

1. Streamlit app running
2. MCP tools visible
3. Successful MCP tool call
4. Multi-tool workflow
5. Final AI response

## Safety

The MCP tools only perform simple calculations and return predefined course information. They do not modify files, access private accounts, or perform external actions.

## Learning flow

**User request → AI decides which tool to use → MCP client calls MCP server → tool returns result → AI gives final answer.**
