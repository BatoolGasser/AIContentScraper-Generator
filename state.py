from typing import Annotated, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph.message import add_messages

class State(TypedDict):
    """State definition for the LangGraph state machine."""
    messages: Annotated[list[AnyMessage], add_messages]
    platform: str
    history: List[Dict[str, Any]]
    brand_voice: str
    full_page_text: str
    draft_content: str  # Renamed from some_text for clarity
    content_approved: bool
    url: Optional[str]
    has_scraped: bool