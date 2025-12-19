"""
AgentApps UI - Web Interface (Fixed & Enhanced)
A beautiful UI for AgentApps using Streamlit

Installation:
pip install streamlit

Run:
streamlit run agentapps_ui.py

Features:
- Edit agents
- Persistent storage (survives refresh)
- Better colors for blue background
- Custom tool creation
"""

import streamlit as st
import json
from typing import List, Dict, Any
import os
import pickle
from pathlib import Path

# Import AgentApps (assumes it's installed)
try:
    from agentapps import Agent, Tool
    from agentapps.model import OpenAIChat
    from agentapps.tools import SearchSummaryTool, WebScraperTool, CalculatorTool
except ImportError:
    st.error("AgentApps not installed! Install with: pip install agentapps")
    st.stop()


# Storage path for persistence
STORAGE_DIR = Path.home() / ".agentapps"
STORAGE_DIR.mkdir(exist_ok=True)
STORAGE_FILE = STORAGE_DIR / "config.pkl"

# Page Configuration
st.set_page_config(
    page_title="AgentApps Studio",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Better colors for blue background
st.markdown("""
<style>
    /* App Background */
    .stApp {
        background: #f9fafb; /* soft white-gray */
    }

    /* Header */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f2937; /* dark gray */
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #4b5563; /* muted gray */
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    /* Agent Cards */
    .agent-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }

    /* Buttons */
    .stButton > button {
        background: #2563eb; /* primary blue */
        color: #ffffff;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 600;
        transition: background 0.3s, box-shadow 0.3s, transform 0.2s;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    .stButton > button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* Tool Badges */
    .tool-badge {
        background: #e0e7ff; /* light indigo */
        color: #1e3a8a;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        margin: 0.25rem;
        display: inline-block;
        font-weight: 600;
    }

    /* Success Badge */
    .success-badge {
        background: #dcfce7; /* light green */
        color: #065f46;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Sidebar */
    div[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    div[data-testid="stSidebar"] * {
        color: #1f2937 !important;
    }

    .sidebar .element-container {
        background: #f3f4f6;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.5rem 0;
    }

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        background: #ffffff !important;
        border: 1.5px solid #d1d5db !important;
        border-radius: 8px !important;
        color: #111827 !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }
</style>

""", unsafe_allow_html=True)

# Helper functions for persistence
def save_data():
    """Save all data to disk (config only, not live objects)"""
    try:
        # Extract only serializable data (no Agent objects)
        agents_config = []
        for agent in st.session_state.agents:
            agents_config.append({
                'name': agent['name'],
                'role': agent['role'],
                'tools': agent['tools'],
                'instructions': agent['instructions'],
                'model': agent.get('model', 'gpt-4'),
                'temperature': agent.get('temperature', 0.7),
                'show_tool_calls': agent.get('show_tool_calls', True),
                'markdown': agent.get('markdown', True)
            })
        
        teams_config = []
        for team in st.session_state.teams:
            teams_config.append({
                'name': team['name'],
                'members': team['members'],
                'instructions': team['instructions'],
                'workflow': team.get('workflow', 'Sequential')
            })
        
        custom_tools_config = []
        for tool in st.session_state.custom_tools:
            custom_tools_config.append({
                'name': tool['name'],
                'description': tool['description'],
                'param_name': tool['param_name'],
                'param_type': tool['param_type'],
                'param_description': tool['param_description'],
                'param_required': tool['param_required'],
                'function_code': tool['function_code']
            })
        
        data = {
            'agents': agents_config,
            'teams': teams_config,
            'custom_tools': custom_tools_config,
            'api_key': st.session_state.api_key
        }
        
        # Use JSON instead of pickle (more reliable)
        with open(STORAGE_FILE.with_suffix('.json'), 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def load_data():
    """Load data from disk and recreate Agent objects"""
    try:
        json_file = STORAGE_FILE.with_suffix('.json')
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
                return data
        # Try old pickle format for backward compatibility
        elif STORAGE_FILE.exists():
            with open(STORAGE_FILE, 'rb') as f:
                data = pickle.load(f)
                return data
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def recreate_agent_from_config(agent_config, api_key):
    """Recreate Agent object from saved configuration"""
    try:
        # Build available tools dict
        available_tools = {
            "Web Search": SearchSummaryTool(),
            "Web Scraper": WebScraperTool(),
            "Calculator": CalculatorTool()
        }
        
        # Add custom tools
        for custom_tool in st.session_state.custom_tools:
            available_tools[custom_tool['name']] = custom_tool['tool_obj']
        
        # Get tools for this agent
        tools = [available_tools[t] for t in agent_config['tools'] if t in available_tools]
        
        # Create agent
        agent = Agent(
            name=agent_config['name'],
            role=agent_config['role'],
            model=OpenAIChat(
                id=agent_config.get('model', 'gpt-4'),
                api_key=api_key
            ),
            tools=tools,
            instructions=agent_config['instructions'],
            show_tool_calls=agent_config.get('show_tool_calls', True),
            markdown=agent_config.get('markdown', True),
            temperature=agent_config.get('temperature', 0.7)
        )
        
        return agent
    except Exception as e:
        st.error(f"Error recreating agent '{agent_config['name']}': {str(e)}")
        return None

def recreate_custom_tool(tool_config):
    """Recreate custom tool from configuration"""
    try:
        class DynamicTool(Tool):
            def __init__(self, name, description, param_name, param_type, param_description, function_code):
                super().__init__(name=name, description=description)
                self.param_name = param_name
                self.param_type = param_type
                self.param_description = param_description
                self.function_code = function_code
            
            def execute(self, **kwargs):
                local_vars = kwargs.copy()
                try:
                    exec(self.function_code, {}, local_vars)
                    return local_vars.get('result', str(local_vars))
                except Exception as e:
                    return f"Error: {str(e)}"
            
            def get_parameters(self):
                return {
                    "type": "object",
                    "properties": {
                        self.param_name: {
                            "type": self.param_type,
                            "description": self.param_description
                        }
                    },
                    "required": [self.param_name] if tool_config.get('param_required', True) else []
                }
        
        tool_obj = DynamicTool(
            tool_config['name'],
            tool_config['description'],
            tool_config['param_name'],
            tool_config['param_type'],
            tool_config['param_description'],
            tool_config['function_code']
        )
        
        return tool_obj
    except Exception as e:
        st.error(f"Error recreating tool '{tool_config['name']}': {str(e)}")
        return None

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Initialize empty state first
    st.session_state.agents = []
    st.session_state.teams = []
    st.session_state.custom_tools = []
    st.session_state.api_key = os.getenv('OPENAI_API_KEY', '')
    st.session_state.chat_history = []
    st.session_state.editing_agent = None
    
    # Try to load saved data
    saved_data = load_data()
    
    if saved_data:
        st.session_state.api_key = saved_data.get('api_key', os.getenv('OPENAI_API_KEY', ''))
        
        # Recreate custom tools first (needed by agents)
        if 'custom_tools' in saved_data:
            for tool_config in saved_data['custom_tools']:
                tool_obj = recreate_custom_tool(tool_config)
                if tool_obj:
                    st.session_state.custom_tools.append({
                        **tool_config,
                        'tool_obj': tool_obj
                    })
        
        # Recreate agents from config
        if 'agents' in saved_data and st.session_state.api_key:
            for agent_config in saved_data['agents']:
                agent_obj = recreate_agent_from_config(agent_config, st.session_state.api_key)
                if agent_obj:
                    # IMPORTANT: Include 'agent' key
                    st.session_state.agents.append({
                        'name': agent_config['name'],
                        'role': agent_config['role'],
                        'tools': agent_config['tools'],
                        'instructions': agent_config['instructions'],
                        'model': agent_config.get('model', 'gpt-4'),
                        'temperature': agent_config.get('temperature', 0.7),
                        'show_tool_calls': agent_config.get('show_tool_calls', True),
                        'markdown': agent_config.get('markdown', True),
                        'agent': agent_obj  # CRITICAL: This must be present
                    })
        
        # Recreate teams from config
        if 'teams' in saved_data and st.session_state.api_key:
            for team_config in saved_data['teams']:
                # Get agent objects for team members
                team_agents = [
                    a['agent'] for a in st.session_state.agents 
                    if a['name'] in team_config['members']
                ]
                
                if len(team_agents) >= 2:
                    try:
                        team_obj = Agent(
                            name=team_config['name'],
                            team=team_agents,
                            instructions=team_config['instructions'],
                            show_tool_calls=True,
                            markdown=True
                        )
                        
                        st.session_state.teams.append({
                            'name': team_config['name'],
                            'members': team_config['members'],
                            'instructions': team_config['instructions'],
                            'workflow': team_config.get('workflow', 'Sequential'),
                            'team': team_obj  # CRITICAL: This must be present
                        })
                    except Exception as e:
                        st.warning(f"Could not recreate team '{team_config['name']}': {str(e)}")

# Header
st.markdown('<h1 class="main-header">🤖 AgentApps Studio</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Build and Deploy AI Agents Visually - No Code Required</p>', unsafe_allow_html=True)

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Enter your OpenAI API key"
    )
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        save_data()
    
    # Model Selection
    model = st.selectbox(
        "Model",
        ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"],
        help="Select the OpenAI model to use"
    )
    
    st.divider()
    
    # Available Tools (including custom)
    st.subheader("🛠️ Available Tools")
    
    # Built-in tools
    st.markdown("**Built-in:**")
    for tool_name in ["Web Search", "Web Scraper", "Calculator"]:
        st.markdown(f'<span class="tool-badge">{tool_name}</span>', unsafe_allow_html=True)
    
    # Custom tools
    if st.session_state.custom_tools:
        st.markdown("**Custom:**")
        for tool in st.session_state.custom_tools:
            st.markdown(f'<span class="tool-badge">{tool["name"]}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Quick Stats
    st.subheader("📊 Stats")
    st.metric("Agents", len(st.session_state.agents))
    st.metric("Teams", len(st.session_state.teams))
    st.metric("Custom Tools", len(st.session_state.custom_tools))
    st.metric("Chats", len(st.session_state.chat_history))
    
    st.divider()
    
    # Save/Load
    if st.button("💾 Save All", use_container_width=True):
        save_data()
        st.success("✅ Saved!")

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Agents", "👥 Teams", "🛠️ Custom Tools", "💬 Chat", "📋 Manage"])

# TAB 1: Create/Edit Agent
with tab1:
    st.header("🤖 Create or Edit Agent")
    
    # Check if editing
    if st.session_state.editing_agent is not None:
        st.info(f"✏️ Editing: {st.session_state.editing_agent['name']}")
        if st.button("❌ Cancel Editing"):
            st.session_state.editing_agent = None
            st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Pre-fill if editing
        default_name = st.session_state.editing_agent['name'] if st.session_state.editing_agent else ""
        default_role = st.session_state.editing_agent['role'] if st.session_state.editing_agent else ""
        default_tools = st.session_state.editing_agent['tools'] if st.session_state.editing_agent else []
        default_instructions = '\n'.join(st.session_state.editing_agent['instructions']) if st.session_state.editing_agent else ""
        
        agent_name = st.text_input("Agent Name", value=default_name, placeholder="e.g., Research Assistant")
        agent_role = st.text_input("Agent Role", value=default_role, placeholder="e.g., Search and analyze information")
        
        # Tool Selection
        st.subheader("Select Tools")
        
        # Build available tools dict
        available_tools = {
            "Web Search": SearchSummaryTool(),
            "Web Scraper": WebScraperTool(),
            "Calculator": CalculatorTool()
        }
        
        # Add custom tools
        for custom_tool in st.session_state.custom_tools:
            available_tools[custom_tool['name']] = custom_tool['tool_obj']
        
        selected_tools = st.multiselect(
            "Tools",
            list(available_tools.keys()),
            default=default_tools,
            help="Select tools this agent can use"
        )
        
        # Instructions
        st.subheader("Instructions")
        instructions = st.text_area(
            "Agent Instructions (one per line)",
            value=default_instructions,
            placeholder="Always include sources\nBe comprehensive\nUse tables for data",
            height=100
        )
        
        # Advanced Settings
        with st.expander("Advanced Settings"):
            show_tool_calls = st.checkbox("Show Tool Calls", value=True)
            use_markdown = st.checkbox("Use Markdown", value=True)
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    
    with col2:
        st.subheader("Preview")
        st.markdown(f"""
        **Name:** {agent_name or 'Not set'}  
        **Role:** {agent_role or 'Not set'}  
        **Model:** {model}  
        **Tools:** {len(selected_tools)}  
        **Temperature:** {temperature}
        """)
        
        if selected_tools:
            st.markdown("**Selected Tools:**")
            for tool in selected_tools:
                st.markdown(f"- {tool}")
    
    # Create or Update button
    button_text = "💾 Update Agent" if st.session_state.editing_agent else "➕ Create Agent"
    if st.button(button_text, use_container_width=True):
        if not st.session_state.api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar!")
        elif not agent_name:
            st.error("❌ Please enter an agent name!")
        else:
            # Create agent
            tools = [available_tools[t] for t in selected_tools]
            instructions_list = [i.strip() for i in instructions.split('\n') if i.strip()]
            
            try:
                agent = Agent(
                    name=agent_name,
                    role=agent_role,
                    model=OpenAIChat(id=model, api_key=st.session_state.api_key),
                    tools=tools,
                    instructions=instructions_list,
                    show_tool_calls=show_tool_calls,
                    markdown=use_markdown,
                    temperature=temperature
                )
                
                agent_data = {
                    'name': agent_name,
                    'role': agent_role,
                    'agent': agent,
                    'tools': selected_tools,
                    'instructions': instructions_list,
                    'model': model,
                    'temperature': temperature,
                    'show_tool_calls': show_tool_calls,
                    'markdown': use_markdown
                }
                
                if st.session_state.editing_agent:
                    # Update existing agent
                    idx = st.session_state.editing_agent['index']
                    st.session_state.agents[idx] = agent_data
                    st.session_state.editing_agent = None
                    save_data()
                    st.success(f"✅ Agent '{agent_name}' updated successfully!")
                else:
                    # Create new agent
                    st.session_state.agents.append(agent_data)
                    save_data()
                    st.success(f"✅ Agent '{agent_name}' created successfully!")
                
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# TAB 2: Create Team
with tab2:
    st.header("👥 Create Agent Team")
    
    if len(st.session_state.agents) < 2:
        st.warning("⚠️ You need at least 2 agents to create a team. Create agents first!")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            team_name = st.text_input("Team Name", placeholder="e.g., Research Team")
            
            # Select team members
            st.subheader("Select Team Members")
            agent_names = [a['name'] for a in st.session_state.agents]
            selected_agents = st.multiselect(
                "Team Members",
                agent_names,
                help="Select agents to include in the team"
            )
            
            # Team Instructions
            st.subheader("Team Instructions")
            team_instructions = st.text_area(
                "Team Workflow (one per line)",
                placeholder="First, search for information\nThen, scrape relevant URLs\nFinally, provide comprehensive answer",
                height=100
            )
            
            workflow_type = st.radio(
                "Workflow Type",
                ["Sequential (Step by step)", "Parallel (All at once)"],
                help="Sequential: Agents work one after another. Parallel: All agents work simultaneously."
            )
        
        with col2:
            st.subheader("Team Preview")
            st.markdown(f"**Name:** {team_name or 'Not set'}")
            st.markdown(f"**Members:** {len(selected_agents)}")
            if selected_agents:
                st.markdown("**Team Members:**")
                for agent_name in selected_agents:
                    agent_data = next(a for a in st.session_state.agents if a['name'] == agent_name)
                    st.markdown(f"- {agent_name}")
                    st.markdown(f"  *Tools: {', '.join(agent_data['tools'])}*")
        
        if st.button("➕ Create Team", use_container_width=True):
            if not team_name:
                st.error("❌ Please enter a team name!")
            elif len(selected_agents) < 2:
                st.error("❌ Please select at least 2 agents!")
            else:
                # Get agent objects
                team_agents = [
                    a['agent'] for a in st.session_state.agents 
                    if a['name'] in selected_agents
                ]
                
                # Create team
                team_instructions_list = [i.strip() for i in team_instructions.split('\n') if i.strip()]
                
                try:
                    team = Agent(
                        name=team_name,
                        team=team_agents,
                        instructions=team_instructions_list,
                        show_tool_calls=True,
                        markdown=True
                    )
                    
                    st.session_state.teams.append({
                        'name': team_name,
                        'team': team,
                        'members': selected_agents,
                        'instructions': team_instructions_list,
                        'workflow': workflow_type
                    })
                    
                    save_data()
                    st.success(f"✅ Team '{team_name}' created successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Error creating team: {str(e)}")

# TAB 3: Custom Tools
with tab3:
    st.header("🛠️ Create Custom Tool")
    
    st.info("💡 Create custom tools by defining their name, description, and a simple function.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tool_name = st.text_input("Tool Name", placeholder="e.g., weather_checker")
        tool_description = st.text_area(
            "Tool Description",
            placeholder="Get current weather for a city",
            height=80
        )
        
        st.subheader("Parameters")
        st.markdown("Define what inputs your tool needs:")
        
        param_name = st.text_input("Parameter Name", placeholder="e.g., city")
        param_type = st.selectbox("Parameter Type", ["string", "number", "boolean"])
        param_description = st.text_input("Parameter Description", placeholder="e.g., City name")
        param_required = st.checkbox("Required Parameter", value=True)
        
        st.subheader("Function Code")
        st.markdown("Write Python code that will execute when the tool is called:")
        
        function_code = st.text_area(
            "Function Implementation",
            placeholder="""# Available variables: city (your parameter)
# Example:
return f"Weather in {city}: Sunny, 72°F"
""",
            height=150
        )
        
    with col2:
        st.subheader("Preview")
        st.markdown(f"**Name:** {tool_name or 'Not set'}")
        st.markdown(f"**Description:** {tool_description or 'Not set'}")
        if param_name:
            st.markdown(f"**Parameter:** {param_name} ({param_type})")
        
        st.info("💡 Your tool will be available to add to any agent!")
    
    if st.button("➕ Create Custom Tool", use_container_width=True):
        if not tool_name or not tool_description or not function_code:
            st.error("❌ Please fill in all fields!")
        else:
            try:
                # Create a custom tool class dynamically
                class DynamicTool(Tool):
                    def __init__(self, name, description, param_name, param_type, function_code):
                        super().__init__(name=name, description=description)
                        self.param_name = param_name
                        self.param_type = param_type
                        self.function_code = function_code
                    
                    def execute(self, **kwargs):
                        # Execute the user's code
                        local_vars = kwargs.copy()
                        try:
                            exec(self.function_code, {}, local_vars)
                            # If there's a return value in the last expression
                            return local_vars.get('result', str(local_vars))
                        except Exception as e:
                            return f"Error: {str(e)}"
                    
                    def get_parameters(self):
                        return {
                            "type": "object",
                            "properties": {
                                self.param_name: {
                                    "type": self.param_type,
                                    "description": param_description
                                }
                            },
                            "required": [self.param_name] if param_required else []
                        }
                
                # Create the tool instance
                custom_tool_obj = DynamicTool(tool_name, tool_description, param_name, param_type, function_code)
                
                # Save to session state
                st.session_state.custom_tools.append({
                    'name': tool_name,
                    'description': tool_description,
                    'param_name': param_name,
                    'param_type': param_type,
                    'param_description': param_description,
                    'param_required': param_required,
                    'function_code': function_code,
                    'tool_obj': custom_tool_obj
                })
                
                save_data()
                st.success(f"✅ Custom tool '{tool_name}' created successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error creating tool: {str(e)}")
    
    # Display existing custom tools
    if st.session_state.custom_tools:
        st.divider()
        st.subheader("Your Custom Tools")
        
        for idx, tool in enumerate(st.session_state.custom_tools):
            with st.expander(f"🛠️ {tool['name']}"):
                st.markdown(f"**Description:** {tool['description']}")
                st.markdown(f"**Parameter:** {tool['param_name']} ({tool['param_type']})")
                st.code(tool['function_code'], language='python')
                
                if st.button(f"🗑️ Delete", key=f"delete_custom_tool_{idx}"):
                    st.session_state.custom_tools.pop(idx)
                    save_data()
                    st.rerun()

# TAB 4: Chat
with tab4:
    st.header("💬 Chat with Agents")
    
    # Select agent or team
    all_entities = (
        [{'name': a['name'], 'type': 'agent', 'obj': a['agent']} for a in st.session_state.agents] +
        [{'name': t['name'], 'type': 'team', 'obj': t['team']} for t in st.session_state.teams]
    )
    
    if not all_entities:
        st.warning("⚠️ No agents or teams available. Create one first!")
    else:
        selected_entity = st.selectbox(
            "Select Agent/Team",
            [e['name'] for e in all_entities],
            format_func=lambda x: f"{'👥' if next(e for e in all_entities if e['name'] == x)['type'] == 'team' else '🤖'} {x}"
        )
        
        # Chat interface
        st.divider()
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**🧑 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 {message['agent']}:** {message['content']}")
                st.divider()
        
        # Input
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_area("Your message", placeholder="Ask anything...", height=100, key="chat_input")
        with col2:
            stream_response = st.checkbox("Stream", value=False)
            send_button = st.button("Send 🚀", use_container_width=True)
        
        if send_button and user_input:
            # Get selected entity
            entity = next(e for e in all_entities if e['name'] == selected_entity)
            
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'agent': 'You'
            })
            
            # Get response
            with st.spinner(f"🤔 {selected_entity} is thinking..."):
                try:
                    response = entity['obj'].run(user_input, stream=stream_response)
                    
                    # Add response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'agent': selected_entity
                    })
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Clear chat
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

# TAB 5: Manage
with tab5:
    st.header("📋 Manage Agents & Teams")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 Agents")
        if not st.session_state.agents:
            st.info("No agents created yet.")
        else:
            for idx, agent_data in enumerate(st.session_state.agents):
                with st.expander(f"🤖 {agent_data['name']}", expanded=False):
                    st.markdown(f"**Role:** {agent_data['role']}")
                    st.markdown(f"**Model:** {agent_data.get('model', 'gpt-4')}")
                    st.markdown(f"**Tools:** {', '.join(agent_data['tools'])}")
                    st.markdown(f"**Instructions:**")
                    for inst in agent_data['instructions']:
                        st.markdown(f"- {inst}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"✏️ Edit", key=f"edit_agent_{idx}"):
                            st.session_state.editing_agent = {**agent_data, 'index': idx}
                            st.rerun()
                    with col_b:
                        if st.button(f"🗑️ Delete", key=f"delete_agent_{idx}"):
                            st.session_state.agents.pop(idx)
                            save_data()
                            st.rerun()
    
    with col2:
        st.subheader("👥 Teams")
        if not st.session_state.teams:
            st.info("No teams created yet.")
        else:
            for idx, team_data in enumerate(st.session_state.teams):
                with st.expander(f"👥 {team_data['name']}", expanded=False):
                    st.markdown(f"**Members:** {', '.join(team_data['members'])}")
                    st.markdown(f"**Workflow:** {team_data.get('workflow', 'Sequential')}")
                    st.markdown(f"**Instructions:**")
                    for inst in team_data['instructions']:
                        st.markdown(f"- {inst}")
                    
                    if st.button(f"🗑️ Delete", key=f"delete_team_{idx}"):
                        st.session_state.teams.pop(idx)
                        save_data()
                        st.rerun()
    
    st.divider()
    
    # Export/Import
    st.subheader("💾 Export/Import Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export All", use_container_width=True):
            config = {
                'agents': [
                    {
                        'name': a['name'],
                        'role': a['role'],
                        'tools': a['tools'],
                        'instructions': a['instructions'],
                        'model': a.get('model', 'gpt-4'),
                        'temperature': a.get('temperature', 0.7)
                    }
                    for a in st.session_state.agents
                ],
                'teams': [
                    {
                        'name': t['name'],
                        'members': t['members'],
                        'instructions': t['instructions'],
                        'workflow': t.get('workflow', 'Sequential')
                    }
                    for t in st.session_state.teams
                ],
                'custom_tools': [
                    {
                        'name': t['name'],
                        'description': t['description'],
                        'param_name': t['param_name'],
                        'param_type': t['param_type'],
                        'param_description': t['param_description'],
                        'param_required': t['param_required'],
                        'function_code': t['function_code']
                    }
                    for t in st.session_state.custom_tools
                ]
            }
            
            st.download_button(
                label="⬇️ Download Config",
                data=json.dumps(config, indent=2),
                file_name="agentapps_config.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import Config", type=['json'])
        if uploaded_file:
            try:
                config = json.loads(uploaded_file.read())
                st.success("✅ Config loaded!")
                
                if st.button("Apply Configuration"):
                    # This would require recreating all agents from config
                    st.info("Import feature coming soon!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col3:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            if st.checkbox("⚠️ Confirm deletion"):
                st.session_state.agents = []
                st.session_state.teams = []
                st.session_state.custom_tools = []
                st.session_state.chat_history = []
                save_data()
                st.success("✅ All data cleared!")
                st.rerun()

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #4b5563; padding: 2rem;">
    <p style="font-size: 0.9rem;">
        Built with ❤️ using AgentApps |
        <a href="https://github.com/91abdul/agentapps"
           style="color: #2563eb; text-decoration: underline;">
            GitHub
        </a> |
        <a href="https://pypi.org/project/agentapps"
           style="color: #2563eb; text-decoration: underline;">
            PyPI
        </a>
    </p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem; color: #6b7280;">
        💾 Data saved to: {}
    </p>
</div>

""".format(str(STORAGE_FILE.with_suffix('.json'))), unsafe_allow_html=True)
