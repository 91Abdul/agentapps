# AgentApps

AgenticAI - A flexible multi-agent orchestration framework for building intelligent agent applications.

## Features

- 🤖 **Simple Agent Creation** - Clean, intuitive
- 👥 **Team Collaboration** - Multiple agents working together
- 🔄 **Sequential Workflows** - Automatic multi-step execution
- 🛠️ **Built-in Tools** - Web search, scraping, calculations
- 🎯 **Custom Tools** - Easy tool creation
- 📊 **Streaming Support** - Real-time responses
- 🔍 **Web Search** - DuckDuckGo integration
- 🌐 **Web Scraping** - Extract content from any URL

## Steamlit UI

- 🎯 **Steamlit UserInterface** - https://github.com/91Abdul/agentapps/tree/main/Steamlit 

## Installation
```bash
pip install agentapps
```

This installs all dependencies:
- `openai` - OpenAI API client
- `ddgs` - DuckDuckGo search
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests

## Quick Start
```python
from agentapps import Agent
from agentapps.model import OpenAIChat
from agentapps.tools import SearchSummaryTool

# Create an agent
agent = Agent(
    name="Stock Analyst",
    role="Analyze stocks",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[SearchSummaryTool()],
    instructions=["Include price targets and analyst ratings"]
)

agent.print_response("Analyze NVDA stock with latest news and recommendations")
```

## Available Tools

### SearchSummaryTool
Search the web and get detailed snippets:
```python
from agentapps.tools import SearchSummaryTool

agent = Agent(
    name="Searcher",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[SearchSummaryTool()]
)
```

### WebScraperTool
Scrape content from URLs:
```python
from agentapps.tools import WebScraperTool

agent = Agent(
    name="Scraper",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[WebScraperTool()]
)
```

### CalculatorTool
Perform calculations:
```python
from agentapps.tools import CalculatorTool

agent = Agent(
    name="Calculator",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[CalculatorTool()]
)
```

## Team Agents

Create teams that work together sequentially:
```python
from agentapps import Agent
from agentapps.model import OpenAIChat
from agentapps.tools import SearchSummaryTool, WebScraperTool

# Create specialist agents
search_agent = Agent(
    name="Search Agent",
    role="Search the web",
    model=OpenAIChat(id="gpt-4", api_key="your-key"),
    tools=[SearchSummaryTool()]
)

scraper_agent = Agent(
    name="Scraper Agent",
    role="Read web pages",
    model=OpenAIChat(id="gpt-4", api_key="your-key"),
    tools=[WebScraperTool()]
)

# Create team with sequential workflow
team = Agent(
    team=[search_agent, scraper_agent],
    instructions=[
        "First, search for relevant URLs",
        "Then, scrape content from those URLs",
        "Finally, provide comprehensive answer"
    ],
    show_tool_calls=True
)

# Team automatically: searches → scrapes → answers
team.print_response("Research NVIDIA's latest AI developments")
```

## Custom Tools

Create your own tools easily:
```python
from agentapps import Tool

class WeatherTool(Tool):
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="Get weather for a city"
        )
    
    def execute(self, city: str) -> str:
        # Your implementation
        return f"Weather in {city}: Sunny, 72°F"
    
    def get_parameters(self):
        return {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }

# Use it
agent = Agent(
    name="Weather Agent",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[WeatherTool()]
)
```

## Examples

### Stock Analysis
```python
agent = Agent(
    name="Stock Analyst",
    role="Analyze stocks",
    model=OpenAIChat(id="gpt-4", api_key="key"),
    tools=[SearchSummaryTool()],
    instructions=["Include price targets and analyst ratings"]
)

agent.print_response("Analyze NVDA stock with latest news and recommendations")
```

### Research Assistant
```python
research_team = Agent(
    team=[search_agent, scraper_agent],
    instructions=[
        "Search for academic sources",
        "Read full articles",
        "Provide comprehensive summary with citations"
    ]
)

research_team.print_response("What are the latest breakthroughs in quantum computing?")
```

## API Reference

### Agent
```python
Agent(
    name: str = "Agent",
    role: str = "General Assistant",
    model: Model = None,
    tools: List[Tool] = None,
    instructions: List[str] = None,
    team: List[Agent] = None,
    show_tool_calls: bool = False,
    markdown: bool = False,
    temperature: float = None
)
```

### Methods

- `run(message: str, stream: bool = False)` - Execute agent
- `print_response(message: str, stream: bool = False)` - Print response
- `clear_history()` - Clear conversation history
- `add_tool(tool: Tool)` - Add a tool
- `get_info()` - Get agent information

## Requirements

- Python >= 3.8
- OpenAI API key

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.


## Projects

1. **Powershell Agent**  
   An automation-focused agent built using PowerShell for executing system-level tasks and workflows.  

   **Source Code:**  
   🔗 https://github.com/91Abdul/agentapps/tree/main/Projects

2. **CodeFix Agent** *(by Sabaunissa)*  
   An AI-powered agent designed to analyze code, identify issues, and suggest automated fixes.  

   **Source Code:**  
   🔗 https://github.com/sabaunissa04/Git_CodeFix_Agent  

   **🎥 Demo Video:**  
   🔗 https://www.linkedin.com/feed/update/urn:li:activity:7423333349051559936/


  
### 🤝 Agent Contributions

We welcome contributions from developers building innovative agents.  
If you would like to contribute your agent, please **send us a message** with a brief description and GitHub repository link.

## Links

- GitHub: https://github.com/91Abdul/agentapps
- PyPI: https://pypi.org/project/agentapps
- Issues: https://github.com/91Abdul/agentapps/issues
