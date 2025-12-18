"""
PowerShell Execution Tool

Purpose:
This tool enables an AI agent to execute PowerShell commands on a Windows system
and return the command output in real time. It provides a controlled interface
for interacting with the Windows operating system using natural-language-driven
agent workflows.

How It Helps:
By exposing PowerShell execution as a structured agent tool with a defined
parameter schema, the agent can translate user requests (such as checking disk
usage or listing running services) into PowerShell commands without manual
intervention.

Value:
The tool reduces manual operational effort, accelerates troubleshooting, and
standardizes Windows automation by allowing repeatable, governed execution of
PowerShell commands through an AI agent.

Where to Use:
Ideal for IT operations, DevOps automation, ITSM remediation, system diagnostics,
Windows server management, and monitoring scenarios where read-only or controlled
administrative access is required.
"""



from agentapps import Agent, Tool
from agentapps.model import OpenAIChat
import subprocess

class PowerShellTool(Tool):
    def __init__(self):
        super().__init__(
            name="run_powershell",
            description="Run a PowerShell command or script on Windows"
        )

    def execute(self, command: str) -> str:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True
        )
        return result.stdout or result.stderr

    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "PowerShell command to execute"
                }
            },
            "required": ["command"]
        }


openAIapikey="sk-proj" # Your OpenAI API Key

agent = Agent(
    name="Windows Automation Agent",
    role="Execute PowerShell commands on Windows",
    model=OpenAIChat(
        id="gpt-4",
        api_key=openAIapikey
    ),
    tools=[PowerShellTool()],
    instructions=[
        "Only run safe diagnostic or read-only PowerShell commands",
        "Create a powershell command revelant to prompt",
        "Always explain what the command does before running it",
        "After executing the powershell command summarize it"
    ],
    show_tool_calls=True
)

agent.print_response("what is the ipaddress")   # Your prompt
