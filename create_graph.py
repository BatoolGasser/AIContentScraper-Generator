from langgraph.graph import StateGraph, END
from state import State

from nodes import (
    scrape_website,
    analyze_brand_voice,
    answer_question,
    no_context_handler,
    generate_blog_post,
    generate_email_marketing,
    generate_facebook_post,
    generate_instagram_post,
    generate_linkedin_post,
    get_feedback,
    invalid_platform_handler,
    human_node,
    route_platform,
    check_for_url,
)

def create_unified_graph():
    """Create the LangGraph state machine."""
    builder = StateGraph(State)
    
    # Add all nodes
    builder.add_node("scrape_website", scrape_website)
    builder.add_node("analyze_brand_voice", analyze_brand_voice)
    builder.add_node("answer_question", answer_question)
    builder.add_node("no_context", no_context_handler)
    builder.add_node("generate_blog_post", generate_blog_post)
    builder.add_node("generate_linkedin_post", generate_linkedin_post)
    builder.add_node("generate_email_marketing", generate_email_marketing)
    builder.add_node("generate_facebook_post", generate_facebook_post)
    builder.add_node("generate_instagram_post", generate_instagram_post)
    builder.add_node("invalid_platform", invalid_platform_handler)
    builder.add_node("human_node", human_node)
    
    # Set entry point with conditional routing
    builder.set_entry_point("check_input_type")
    builder.add_node("check_input_type", lambda state: state)  # Pass-through node
    
    # Add conditional edges from check_input_type
    builder.add_conditional_edges(
        "check_input_type",
        check_for_url,
        {
            "scrape_website": "scrape_website",
            "generate_content": "generate_content",
            "answer_question": "answer_question",
            "no_context": "no_context"
        }
    )
    
    # Add scrape flow
    builder.add_edge("scrape_website", "analyze_brand_voice")
    builder.add_edge("analyze_brand_voice", END)
    
    # Add question answering flow
    builder.add_edge("answer_question", END)
    builder.add_edge("no_context", END)
    
    # Add content generation routing
    builder.add_node("generate_content", lambda state: state)  # Pass-through node
    builder.add_conditional_edges(
        "generate_content",
        route_platform,
        {
            "generate_blog_post": "generate_blog_post",
            "generate_linkedin_post": "generate_linkedin_post",
            "generate_email_marketing": "generate_email_marketing",
            "generate_facebook_post": "generate_facebook_post",
            "generate_instagram_post": "generate_instagram_post",
            "invalid_platform": "invalid_platform"
        }
    )
    
    # Connect content generation to human feedback
    builder.add_edge("generate_blog_post", "human_node")
    builder.add_edge("generate_linkedin_post", "human_node")
    builder.add_edge("generate_email_marketing", "human_node")
    builder.add_edge("generate_facebook_post", "human_node")
    builder.add_edge("generate_instagram_post", "human_node")
    
    # Add conditional edges from feedback
    builder.add_conditional_edges(
        "human_node",
        get_feedback,
        {
            "end_flow": END,
            "human_node": "check_input_type"  # Allow re-entry based on revision
        }
    )
    
    # Add invalid platform edge
    builder.add_edge("invalid_platform", END)
    
    return builder.compile()
