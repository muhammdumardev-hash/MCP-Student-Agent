# MCP Student Agent

A simple MCP-powered AI Student Assistant built for learning the Model Context Protocol (MCP).

## What this project demonstrates

- An MCP server
- Custom MCP tools
- An AI agent connected to the MCP server
- Automatic tool selection by the AI model
- Successful MCP tool calls
- A multi-tool workflow

## MCP tools

1. `calculate_percentage`
2. `calculate_cgpa`
3. `get_course_info`

## Architecture

```
User
  |
  v
AI Agent (Groq)
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

The MCP client starts the MCP server as a local subprocess using STDIO. The current Python MCP SDK provides this client/server pattern through `ClientSession`, `StdioServerParameters`, and `stdio_client`.

## Setup

### 1. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Groq API key

Create an environment variable:

Windows Command Prompt:

```cmd
set GROQ_API_KEY=your_groq_api_key_here
```

PowerShell:

```powershell
$env:GROQ_API_KEY="your_groq_api_key_here"
```

You can also set `GROQ_MODEL` if you want to use another Groq tool-calling model.

## Run

From the project folder:

```bash
python agent.py
```

Then try:

```
Calculate the percentage for 680 marks out of 800.
```

### Multi-tool example

Try:

```
Calculate my percentage for 680 out of 800 and tell me about Data Communication.
```

The AI can call more than one MCP tool and then combine the results into one final response.

## Run the MCP server separately

For a basic server-running demonstration:

```bash
python mcp_server.py
```

The server uses STDIO, so it is normally launched by the MCP client/agent rather than through a browser.

## Suggested internship screenshots

Capture:

1. MCP server running
2. Available MCP tools
3. AI agent connected to the MCP server
4. A successful tool call
5. A multi-tool workflow
6. The final AI response

## Safety note

The tools in this project only perform simple calculations and return predefined course information. They do not modify files, access private accounts, or perform external actions. This keeps the first MCP project simple and safe.

## Learning goal

The main goal is to understand this flow:

**User request -> AI decides which tool to use -> MCP client calls MCP server -> tool returns result -> AI gives final answer.**
