# MCP Weather Agent

A practical example of using Model Context Protocol (MCP) with LangGraph for intelligent tool orchestration.

## The Tools

| Tool                                   | Purpose                       | Returns                                                  |
| -------------------------------------- | ----------------------------- | -------------------------------------------------------- |
| `get_current_weather(location)`        | Temperature, wind, conditions | Temp, feels-like, wind speed/direction                   |
| `get_atmospheric_conditions(location)` | Air properties                | Humidity, pressure, cloud, visibility, precipitation, UV |
| `get_astronomical_data(location)`      | Sun and moon data             | Sunrise, sunset, moonrise, moonset, moon phase           |
| `get_air_quality(location)`            | Pollution levels              | CO, NO₂, O₃, SO₂, PM2.5, PM10, air quality index         |

## How It Works

1. **weather_server.py** - Exposes 4 tools via MCP over stdio (the default transport).
2. **agent.py** - LangGraph agent that:
   - At start-up asks the MCP server for its tool list; this list is refreshed automatically whenever the server adds or removes tools.
   - Receives user query
   - Decides which tools to call
   - Executes tools asynchronously
   - Combines results into response

The agent is smart - it only calls tools relevant to the question.

Currently the server only publishes Tools; Resources and Prompts are not used in this example.

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
OPENROUTER_API_KEY=your_key_here
```

### 4. Run

```bash
python agent.py
```

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

**Why?** The agent intelligently selects only what it needs, enabling guided interactions that lead to clearer semantics and reduced reasoning complexity.

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

**Why?** The LLM relies on descriptions to make tool selection decisions. Better descriptions = smarter routing.

## Autonomous Tool Selection in Action

With focused tools and clear descriptions, the agent automatically routes queries correctly:

- `"What's the weather in London?"` → `get_current_weather(location="London")`
- `"Is the air quality good in Tehran?"` → `get_current_air_quality(location="Tehran")`
- `"Compare air quality between Tehran and New York"` → `get_current_air_quality(location="Tehran")` + `get_current_air_quality(location="New York")`
- `"Tell me about weather and air quality in Paris"` → `get_current_weather(location="Paris")` + `get_current_air_quality(location="Paris")`

No hardcoded logic required—the agent figures it out from your tool descriptions.
