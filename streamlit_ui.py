import streamlit as st
from langchain_core.messages import HumanMessage
from create_graph import create_unified_graph

def initialize_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hello! I can help you analyze websites and generate content. Please provide a URL to get started.",
            "platform": None
        }]

    if "approved_content" not in st.session_state:
        st.session_state.approved_content = []

    if "last_user_prompt" not in st.session_state:
        st.session_state.last_user_prompt = ""

    if "regenerate_platform" not in st.session_state:
        st.session_state.regenerate_platform = None

    if "brand_voice" not in st.session_state:
        st.session_state.brand_voice = ""

    if "scraped_text" not in st.session_state:
        st.session_state.scraped_text = ""

    if "current_url" not in st.session_state:
        st.session_state.current_url = ""

    if "has_scraped" not in st.session_state:
        st.session_state.has_scraped = False
        
    # Initialize the graph instance
    if "graph" not in st.session_state:
        st.session_state.graph = create_unified_graph()

def handle_regeneration():
    """Handle content regeneration requests."""
    if st.session_state.regenerate_platform is not None and st.session_state.last_user_prompt:
        platform = st.session_state.regenerate_platform
        prompt = st.session_state.last_user_prompt
        
        with st.spinner(f"Regenerating {platform} content..."):
            try:
                # Prepare state with platform indicator in prompt
                platform_prompt = f"{prompt} for {platform}"
                state = {
                    "messages": [HumanMessage(content=platform_prompt)],
                    "platform": platform,
                    "history": st.session_state.approved_content,
                    "brand_voice": st.session_state.brand_voice,
                    "full_page_text": st.session_state.scraped_text,
                    "has_scraped": st.session_state.has_scraped,
                    "url": st.session_state.current_url,
                    "draft_content": "",
                    "content_approved": False
                }
                
                # FIX: Use the graph instance from session state instead of calling create_unified_graph as a function
                final_state = st.session_state.graph.invoke(state)
                response = final_state["messages"][-1].content
                
                # Add as draft
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "platform": platform,
                    "needs_approval": True
                })
                
                # Reset regeneration state
                st.session_state.regenerate_platform = None
                st.session_state.last_user_prompt = ""
                st.rerun()
                
            except Exception as e:
                st.error(f"Error regenerating content: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error while regenerating {platform} content. Please try again.",
                    "platform": "Error"
                })
                st.session_state.regenerate_platform = None
                st.session_state.last_user_prompt = ""

def handle_user_input(prompt: str):
    """Process user input and update UI."""
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "platform": None
    })
    
    # Generate response
    with st.spinner("Processing your request..."):
        try:
            # Prepare state
            state = {
                "messages": [HumanMessage(content=prompt)],
                "platform": "",
                "history": st.session_state.approved_content,
                "brand_voice": st.session_state.brand_voice,
                "full_page_text": st.session_state.scraped_text,
                "content_approved": False,
                "has_scraped": st.session_state.has_scraped,
                "url": st.session_state.current_url,
                "draft_content": ""
            }
            
            # FIX: Use the graph instance from session state
            final_state = st.session_state.graph.invoke(state)
            
            # Update session state with scraped content if applicable
            if "full_page_text" in final_state and final_state["full_page_text"]:
                st.session_state.scraped_text = final_state["full_page_text"]
                
            if "brand_voice" in final_state and final_state["brand_voice"]:
                st.session_state.brand_voice = final_state["brand_voice"]
                
            if "url" in final_state and final_state["url"]:
                st.session_state.current_url = final_state["url"]
                
            if "has_scraped" in final_state:
                st.session_state.has_scraped = final_state["has_scraped"]
            
            response = final_state["messages"][-1].content
            platform = final_state.get("platform", "")
            
            # Add response to chat
            needs_approval = platform in ["Blog", "LinkedIn", "Email", "Facebook", "Instagram"]
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "platform": platform,
                "needs_approval": needs_approval
            })
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}. Please try again.",
                "platform": "Error"
            })

def setup_ui_style():
    """Set up the UI style for the application."""
    st.set_page_config(page_title="Smart Content Generator", page_icon="🤖", layout="wide")
    
    st.markdown("""
    <style>
        .draft-content { border-left: 4px solid #FFC107; padding-left: 1rem; margin: 1rem 0; }
        .approved-content { border-left: 4px solid #4CAF50; padding-left: 1rem; margin: 1rem 0; }
        .stButton>button { margin-top: 0.5rem; }
        .css-1d391kg { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🤖 Smart Website Analyzer & Content Generator")
