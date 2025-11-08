# MCP Weather Agent

A **production‑ready, scalable** example of using **Model Context Protocol (MCP)** with **LangGraph** for intelligent tool orchestration.  
This project demonstrates **clean architecture principles** and serves as a **blueprint** for building agent‑based systems that integrate tools dynamically through MCP.

## Project Structure

```
mcp-weather-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                          # Entry point
│   ├── config.py                        # Centralized configuration
│   ├── graph/                           # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py                     # Agent state schema
│   │   ├── graph_builder.py             # Graph assembly
│   │   ├── nodes/                       # Graph nodes
│   │   │   ├── __init__.py
│   │   │   ├── agent.py                 # Agent node (model invocation)
│   │   │   └── tools.py                 # Tool execution node
│   │   └── edges/                       # Conditional routing
│   │       ├── __init__.py
│   │       └── agent_to_tools.py        # Agent → Tools decision logic
│   ├── tools/                           # External tools
│   │   ├── __init__.py
│   │   └── weather_mcp/
│   │       ├── __init__.py
│   │       ├── client.py                # MCP client initialization
│   │       └── server.py                # MCP server with weather tools
│   └── utils/                           # Utilities
│       ├── __init__.py
│       └── logger.py                    # Centralized logging
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## The Tools

| Tool                                   | Purpose                       | Returns                                                  |
| -------------------------------------- | ----------------------------- | -------------------------------------------------------- |
| `get_current_weather(location)`        | Temperature, wind, conditions | Temp, feels-like, wind speed/direction                   |
| `get_atmospheric_conditions(location)` | Air properties                | Humidity, pressure, cloud, visibility, precipitation, UV |
| `get_astronomical_data(location)`      | Sun and moon data             | Sunrise, sunset, moonrise, moonset, moon phase           |
| `get_air_quality(location)`            | Pollution levels              | CO, NO₂, O₃, SO₂, PM2.5, PM10, air quality index         |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

- **Weather**: Free key from [weatherapi.com](https://www.weatherapi.com)
- **LLM**: Free tier from [openrouter.ai](https://openrouter.ai)

### 3. Configure

Copy `.env.example` and add your API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your keys:

```
WEATHER_API_KEY=your_key_here
MODEL_API_KEY=your_key_here
```

### 4. Run

```bash
python -m src.main
```

## How It Works

### **Execution Flow**

```
1. Initialize MCP Client
   └─ Load weather tools from MCP server

2. Build LangGraph
   ├─ Create Agent Node (LLM + tools)
   ├─ Create Tool Node (tool execution)
   └─ Create Agent→Tools Edge (routing)

3. Execute Graph
   ├─ Agent processes user query
   ├─ Agent decides which tools to call
   ├─ Tool Node executes selected tools (concurrently)
   ├─ Results returned to Agent
   └─ Agent generates final response
```

This design decouples the **MCP client**, **tools**, and **graph logic**, enabling scalability and extensibility with clear boundaries.

### **Async Execution**

The tool execution node runs tools **concurrently** using async/await:

```python
# src/graph/nodes/tools.py
async def process_tool_calls(state: AgentState) -> AgentState:
    """Execute multiple tools in parallel."""
    # If the agent calls multiple tools, they run concurrently
    # Example: compare_air_quality() calls get_air_quality(Tehran) + get_air_quality(NewYork)
    # Both API calls happen simultaneously, not sequentially
```

**Note:** The system executes tools concurrently by default. However, if tools have dependencies or order matters, you can modify the tool execution logic to run them sequentially when needed.

## Scalable Graph Structure

**Nodes – State Transformers**

- `agent.py` – LLM invocation with registered tools
- `tools.py` – Tool execution engine
- Add more as needed: `validation.py`, `formatting.py`, etc.

**Edges – Routing Logic**

- `agent_to_tools.py` – Determines if tools are required
- Extend easily: `tools_to_validator.py`, `validator_to_formatter.py`, etc.

**Why This Matters**

- Each node/edge has a **single responsibility**
- New nodes can be added **without refactoring**
- Guarantees **clear data flow** through the LangGraph agent

## Agent State Schema (`graph/state.py`)

The **state** is the data flowing through the graph. It's defined using TypedDict for type safety:

```python
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for the weather agent workflow."""
    messages: list[BaseMessage]
```

**How It Works:**

- **`messages`** – A list of conversation messages (user queries, agent responses, tool results)
- **Append-only pattern** – Each node adds new messages to the state rather than replacing it
- **Clear history** – All messages are preserved, making the conversation flow transparent and debuggable

**Example State Evolution:**

```
Step 1 (Initial):
  messages = [HumanMessage("Compare air quality between Amsterdam and New York")]

Step 2 (After Agent Node):
  messages = [HumanMessage(...), AIMessage(tool_calls=[call_1, call_2])]

Step 3 (After Tool Node):
  messages = [HumanMessage(...), AIMessage(...), ToolMessage("Result 1"), ToolMessage("Result 2")]

Step 4 (Final):
  messages = [HumanMessage(...), AIMessage(...), ToolMessage(...), ToolMessage(...), AIMessage("Final Answer")]
```

**Extending the State:**

As your agent grows, you can add more fields:

```python
class AdvancedAgentState(TypedDict):
    messages: list[BaseMessage]
    user_id: str                    # Track which user made the request
    metadata: dict                  # Store query metadata
    tool_calls_count: int           # Monitor tool usage
```

## Configuration System (`config.py`)

Single source of truth for all application settings:

- Easy to override via environment variables
- Type‑safe using dataclasses

```python
@dataclass
class ModelConfig:
    model_name: str
    base_url: Optional[str]
    api_key: Optional[str]
    temperature: float
    max_tokens: int
```

**Why:** Validated at creation time and easy to understand from code, ensuring predictable runtime behavior.

## Unified Logging System (`utils/logger.py`)

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)  # Used everywhere
```

- Centralized logging configuration
- Log level controlled via `LOG_LEVEL` environment variable
- Consistent formatting across the entire application
- Easily extendable (file handlers, cloud logging, etc.)

## Design Patterns Used

### 1. **Factory Pattern (Nodes)**

```python
def create_agent_node(model_with_tools):
    def agent_node(state):
        # Node logic
        pass
    return agent_node
```

**Why:** Keeps the model context within the node, avoiding globals and repeat setup.

### 2. **Configuration as Code**

Type‑safe configuration objects make runtime setup predictable and extensible.

```python
@dataclass
class ModelConfig:
    model_name: str
    base_url: Optional[str]
    api_key: Optional[str]
    temperature: float
    max_tokens: int
```

**Why:** Configuration remains explicit and validated.

### 3. **Dependency Injection**

Tools are passed dynamically to `build_graph()` rather than hardcoded.

**Why:** Improves testability, flexibility, and separation of concerns.

## Extending the Agent

### Adding a New Node

1. Create `src/graph/nodes/your_node.py`
2. Implement the node function
3. Register it in `graph_builder.py`

Example:

```python
# src/graph/nodes/formatter.py
def create_formatter_node():
    def formatter_node(state: AgentState) -> AgentState:
        # Format the response
        return {"messages": state["messages"] + [formatted]}
    return formatter_node
```

### Adding a New Edge

1. Create `src/graph/edges/your_edge.py`
2. Implement the routing function
3. Export in `src/graph/edges/__init__.py`
4. Add to `graph_builder.py`

Example:

```python
# src/graph/edges/tools_to_formatter.py
def should_format(state: AgentState) -> str:
    # Conditional routing
    return "formatter" if condition else END
```

### Adding a New MCP Tool

1. Add tool function in `src/tools/weather_mcp/server.py`
2. Decorate with `@mcp.tool()`
3. Include a clear, detailed docstring
4. Tool auto‑registers with the MCP client on startup

To expand beyond weather, simply add new tool packages:

- `src/tools/finance_mcp/`
- `src/tools/drug_mcp/`

Each MCP toolset remains isolated and portable.

### Adding New Utilities

Add new files in `src/utils/` for shared logic:

- `src/utils/validators.py` → Data validation
- `src/utils/formatters.py` → Response formatting

These utilities can be imported anywhere to maintain a **consistent infrastructure layer**.

## Key Insights: Designing MCP Servers

### 1. **Create Focused, Single-Purpose Tools**

Split functionality into specialized functions rather than one monolithic tool:

**Poor Design:**

```python
@mcp.tool()
def get_all_weather(location):
    # Returns everything: temperature, air quality, astronomy...
    # Agent can't distinguish what's relevant
```

**Good Design:**

```python
@mcp.tool()
def get_current_weather(location):
    # Only temperature, wind, and weather conditions

@mcp.tool()
def get_current_air_quality(location):
    # Only pollution data
```

**Why:** The agent intelligently selects only what it needs, enabling guided interactions that lead to clearer semantics and reduced reasoning complexity.

### 2. **Write Clear, Detailed Descriptions**

Comprehensive docstrings enable the LLM to understand when and how to use each tool:

**Good Description:**

```python
@mcp.tool()
def get_current_air_quality(location: str) -> dict:
    """
    Get current air quality data for a given location.

    Args:
        location: The city name or location (e.g., "New York", "London", "Tehran")

    Returns:
        A dictionary containing:
        - CO (Carbon Monoxide) levels
        - NO2 (Nitrogen Dioxide) levels
        - O3 (Ozone) levels
        - SO2 (Sulfur Dioxide) levels
        - PM2.5 (Fine Particulate Matter) levels
        - PM10 (Coarse Particulate Matter) levels
        - EPA Air Quality Index
        - GB DEFRA Air Quality Index
    """
```

**Poor Description:**

```python
@mcp.tool()
def get_current_air_quality(location: str) -> dict:
    """Get air quality information."""  # No details about what data is returned!
```

**Why:** The LLM relies on descriptions to make tool selection decisions. Better descriptions = smarter routing.

## Autonomous Tool Selection in Action

With focused tools and clear descriptions, the agent automatically routes queries correctly:

- `"What's the weather in London?"` → `get_current_weather(location="London")`
- `"Is the air quality good in Tehran?"` → `get_current_air_quality(location="Tehran")`
- `"Compare air quality between Tehran and New York"` → `get_current_air_quality(location="Tehran")` + `get_current_air_quality(location="New York")`
- `"Tell me about weather and air quality in Paris"` → `get_current_weather(location="Paris")` + `get_current_air_quality(location="Paris")`

No hardcoded logic required—the agent figures it out from your tool descriptions.

## Extend This Blueprint

Adapt this architecture for your own domain:

- Replace `weather_mcp` with custom MCP tools
- Add domain‑specific nodes or edges
- Modify configurations in `config.py`
- Reuse `logger` and `graph_builder` patterns

This architecture **scales cleanly** and offers a clear, extensible foundation for multi‑tool, domain‑specific agents.

## Using This Architecture Without MCP

While this project uses MCP (Model Context Protocol), the core architecture works **perfectly fine without it**. Here's how to adapt it:

### **Step 1: Replace the MCP Client**

Instead of `src/tools/weather_mcp/client.py`, create direct tool implementations:

```python
# src/tools/direct_tools.py
from langchain_core.tools import tool

@tool
def get_current_weather(location: str) -> dict:
    """Get current weather for a location."""
    # Direct API call or local logic
    response = requests.get(f"https://api.weatherapi.com/v1/current.json", ...)
    return response.json()

@tool
def get_air_quality(location: str) -> dict:
    """Get air quality data for a location."""
    # Your implementation
    pass

# Create tool list
tools = [get_current_weather, get_air_quality]
```

### **Step 2: Update Main.py**

Replace MCP initialization with direct tool loading:

```python
# src/main.py (without MCP)
async def main():
    logger.info("Loading tools...")
    from src.tools.direct_tools import tools  # Direct import instead of MCP

    logger.info("Building agent graph...")
    compiled_graph = build_graph(tools)

    # Rest remains the same...
```

### **Step 3: Graph Builder Works As-Is**

The `graph_builder.py` requires no changes as it accepts tools from any origin (MCP, REST, or inline):

```python
# src/graph/graph_builder.py - Works with both MCP and direct tools
def build_graph(tools):  # Tools can come from anywhere
    model = ChatOpenAI(...)
    model_with_tools = model.bind_tools(tools)  # Works regardless of tool source
    # ... rest of graph building
```

## MCP Server/Client Lifecycle

| Component      | Runs In             | Managed By              | Purpose / Responsibility                |
| -------------- | ------------------- | ----------------------- | --------------------------------------- |
| **MCP Client** | Agent main process  | `MultiServerMCPClient`  | Discovers and loads available MCP tools |
| **MCP Server** | Separate subprocess | MCP framework (spawned) | Executes tool logic, returns results    |

This lifecycle ensures your agent is fault-tolerant — if one server process fails, the client can reconnect or selectively retry without taking down your main agent flow.

### **Comparison MCP vs Direct Tools**

| Aspect                | MCP                                                    | Direct Tools                                     |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| **Fault Isolation**   | Tool crashes don't affect agent                        | Tool crash crashes entire agent                  |
| **Language Support**  | Multi-language tools (JS, Rust, Python, etc.)          | Python only                                      |
| **Performance**       | Slight IPC overhead                                    | Faster (no inter-process overhead)               |
| **Setup & Debugging** | More complex (separate processes)                      | Simpler (single process, easier debugging)       |
| **Best For**          | Production systems, distributed tools, fault-tolerance | Prototyping, simple projects, Python-only stacks |
