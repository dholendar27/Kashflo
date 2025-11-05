from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from agents import kashflo_supervisor_agent
from agents.context import UserDetails
from utils import get_db, get_current_user
from models import User
from schema.agents import AgentQuerySchema

agents_router = APIRouter(prefix="/agents", tags=["AI Agents"])


@agents_router.post("")
def query_kashflo_supervisor(
        query: AgentQuerySchema,
        user: User = Depends(get_current_user),
):
    """
    Query the Kashflo AI Supervisor for personalized assistance.
    """
    try:
        # Create UserDetails context
        user_details = UserDetails(
            user_id=str(user.id),
            user_name=f"{user.first_name} {user.last_name}"
        )

        # Invoke the supervisor agent with context
        response = kashflo_supervisor_agent.invoke(
            {"messages": [{"role": "user", "content": query.query}]},
            config={"configurable": {"user_details": user_details}}
        )

        # Extract content from response
        content = None

        if isinstance(response, dict):
            # Check if it has messages array
            if "messages" in response and response["messages"]:
                latest_message = response["messages"][-1]

                # Handle different message types
                if hasattr(latest_message, 'content'):
                    content = latest_message.content
                elif hasattr(latest_message, 'text'):
                    content = latest_message.text
                elif isinstance(latest_message, dict):
                    content = latest_message.get('content') or latest_message.get('text')

            # If no messages, check for output key
            elif "output" in response:
                content = response["output"]

        # Fallback to string conversion
        if not content:
            content = str(response)

        return JSONResponse(
            content={
                "response": content,
                "user_name": f"{user.first_name} {user.last_name}"
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        print(f"Error in query_kashflo_supervisor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )