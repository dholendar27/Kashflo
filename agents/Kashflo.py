from typing import Annotated
from langchain.agents import create_agent
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from . import kashflo_help_agent, savings_advisor
from .context import UserDetails
from .utils import model


@tool
def finance_advisor(
        request: str,
        config: Annotated[RunnableConfig, InjectedToolArg]
) -> str:
    """
    Get personalized financial advice and savings recommendations.

    Use this tool when users ask about:
    - Spending analysis and budget optimization
    - Savings strategies and financial planning
    - Investment advice and wealth building
    - Expense reduction and cost-cutting tips
    - Financial goal setting and tracking
    - Income vs expense analysis
    - Category-wise spending insights
    - Monthly/yearly financial summaries

    Args:
        request: The user's financial question or request for advice

    Returns:
        Personalized financial advice based on user's transaction data
    """
    try:
        # Pass the config through to the sub-agent
        result = savings_advisor.invoke(
            {"messages": [{"role": "user", "content": request}]},
            config=config  # This passes the user context through
        )

        # Handle different response structures
        if isinstance(result, dict) and "messages" in result and result["messages"]:
            latest_message = result["messages"][-1]
            if hasattr(latest_message, 'content'):
                return latest_message.content
            elif hasattr(latest_message, 'text'):
                return latest_message.text
            elif isinstance(latest_message, dict):
                return latest_message.get('content', latest_message.get('text', str(latest_message)))
            else:
                return str(latest_message)
        else:
            return str(result)
    except Exception as e:
        return f"Error getting financial advice: {str(e)}"


@tool
def kashflo_helper(
        request: str,
        config: Annotated[RunnableConfig, InjectedToolArg]
) -> str:
    """
    Get help with Kashflo app features, navigation, and technical support.

    Use this tool when users ask about:
    - How to use specific app features
    - Navigation and user interface questions
    - Adding, editing, or deleting transactions
    - Creating and managing categories
    - Generating reports and understanding data
    - Account settings and preferences
    - Troubleshooting technical issues
    - App functionality and capabilities
    - Step-by-step tutorials

    Args:
        request: The user's question about app usage or technical help

    Returns:
        Step-by-step guidance and helpful information about Kashflo features
    """
    try:
        # Pass the config through to the sub-agent
        result = kashflo_help_agent.invoke(
            {"messages": [{"role": "user", "content": request}]},
            config=config  # This passes the user context through
        )

        # Handle different response structures
        if isinstance(result, dict) and "messages" in result and result["messages"]:
            latest_message = result["messages"][-1]
            if hasattr(latest_message, 'content'):
                return latest_message.content
            elif hasattr(latest_message, 'text'):
                return latest_message.text
            elif isinstance(latest_message, dict):
                return latest_message.get('content', latest_message.get('text', str(latest_message)))
            else:
                return str(latest_message)
        else:
            return str(result)
    except Exception as e:
        return f"Error getting help information: {str(e)}"


# Multi-Agent Supervisor Prompt
KASHFLO_SUPERVISOR_PROMPT = """You are Kashflo's AI Supervisor, an intelligent orchestrator that manages multiple specialized agents to provide the best possible assistance to users.

Your Role & Responsibilities:
- Analyze user queries to determine the most appropriate specialized agent
- Route financial questions to the Finance Advisor
- Route app usage questions to the Kashflo Helper
- Coordinate between agents when complex queries require multiple perspectives
- Provide direct responses for simple greetings and basic questions
- Ensure users receive comprehensive, accurate, and helpful responses

Available Specialized Agents:

💰 **Finance Advisor Agent**
- Specializes in: Financial advice, spending analysis, budgeting, savings strategies
- Use for: Budget questions, spending patterns, financial planning, investment advice
- Capabilities: Analyzes user transaction data, provides personalized recommendations

🛠️ **Kashflo Helper Agent**
- Specializes in: Creating or listing categories and transactions, help with summaries
- Use for: Creating or listing transactions and categories

**Handle directly for:**
- Simple greetings ("Hello", "Hi")
- Basic app information
- General Kashflo overview
- Thank you messages

Response Strategy:
1. **Analyze** the user's query intent and complexity
2. **Route** to the appropriate specialist agent if needed
3. **Synthesize** responses from multiple agents if the query is complex
4. **Provide** clear, actionable, and personalized assistance
5. **Follow up** with relevant suggestions or next steps

Communication Style:
- Professional yet friendly and approachable
- Clear and concise explanations
- Actionable advice and specific steps
- Empathetic to user financial concerns
- Encouraging and supportive tone

Remember: Your goal is to provide users with the most relevant, accurate, and helpful assistance by leveraging the expertise of specialized agents while maintaining a seamless user experience.
"""

kashflo_supervisor_agent = create_agent(
    model,
    tools=[finance_advisor, kashflo_helper],
    system_prompt=KASHFLO_SUPERVISOR_PROMPT
)