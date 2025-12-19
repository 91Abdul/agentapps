# 1. Install dependencies
pip install streamlit agentapps

# 2. Save the code as agentapps_ui.py

# 3. Run it
streamlit run agentapps_ui.py
```

## 📸 What It Looks Like

- **Beautiful gradient background** (purple)
- **Card-based UI** for agents
- **Sidebar** with configuration
- **Tool badges** showing available tools
- **Real-time stats** (agents, teams, chats)
- **Export/Import** configurations

## 🎯 How to Use

### 1. **Setup**
- Enter OpenAI API key in sidebar
- Select model (GPT-4, GPT-3.5-turbo)

### 2. **Create Agent**
- Go to "Create Agent" tab
- Fill in name, role
- Select tools (Web Search, Scraper, Calculator)
- Add instructions
- Click "Create Agent"

### 3. **Create Team**
- Go to "Create Team" tab
- Select 2+ agents
- Define workflow
- Click "Create Team"

### 4. **Chat**
- Go to "Chat" tab
- Select agent or team
- Type your query
- Get responses!

## 💡 Example Workflow
```
1. Create "Search Agent" with WebSearchTool
2. Create "Scraper Agent" with WebScraperTool  
3. Create "Research Team" with both agents
4. Chat: "Research NVIDIA AI chips"
5. Watch the team work sequentially!
