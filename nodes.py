from state import State
from utils import is_valid_url, scrape_url
from langgraph.types import interrupt
from langchain_core.messages import HumanMessage, SystemMessage
from prompts_templates import PROMPTS
from config import model
from prompts_templates import CONTENT_TEMPLATES

def check_for_url(state: State) -> str:
    """Route based on input type and context."""
    user_input = state["messages"][-1].content.strip()
    
    if is_valid_url(user_input):
        return "scrape_website"
    
    if any(platform in user_input.lower() for platform in ['blog', 'email', 'linkedin', 'facebook', 'instagram']):
        return "generate_content"
    
    if state.get("has_scraped", False):
        return "answer_question"
    
    return "no_context"

def scrape_website(state: State) -> State:
    url = state["messages"][-1].content.strip()
    page_text, success = scrape_url(url)  # Fixed: unpacking both return values
    
    if not success:  # Fixed: checking success flag
        return {
            "messages": [HumanMessage(content=f"Failed to retrieve content from {url}. Please check the URL and try again.")],
            "brand_voice": "",
            "full_page_text": "",
            "platform": "",
            "history": state.get("history", []),
            "content_approved": False,
            "url": url,
            "has_scraped": False,
            "draft_content": ""  # Added missing field
        }
    
    # Summarize the content
    summary_prompt = [
        SystemMessage(content=PROMPTS["summarize_website"]),  # Use from PROMPTS dict
        HumanMessage(content=page_text)
    ]
    
    response = model.invoke(summary_prompt)
    summary = response.content  # Extract the content from the response
    
    return {
        "messages": [HumanMessage(content=summary)],  # Wrap the string content in a HumanMessage
        "brand_voice": "",
        "full_page_text": page_text,
        "platform": "",
        "history": state.get("history", []),
        "content_approved": False,
        "url": url,
        "has_scraped": True,
        "draft_content": ""  # Added missing field
    }

def analyze_brand_voice(state: State) -> State:
    summary = state["messages"][-1].content if hasattr(state["messages"][-1], "content") else state["messages"][-1]
    prompt = [
        SystemMessage(content=PROMPTS["analyze_brand_voice"]),  # Use from PROMPTS dict
        HumanMessage(content=summary)
    ]
    
    response = model.invoke(prompt)
    brand_voice_analysis = response.content  # Extract the content from the response
    
    # Create a response that combines the summary and brand voice analysis
    combined_response = f"""
    # Website Summary
    {summary}
    
    # Brand Voice Analysis
    {brand_voice_analysis}
    
    I've analyzed this website and extracted its content. You can now:
    1. Ask questions about the website content
    2. Request content generation for different platforms (blog, email, LinkedIn, Facebook, or Instagram)
    """
    
    return {
        "messages": [HumanMessage(content=combined_response)],
        "brand_voice": brand_voice_analysis,
        "full_page_text": state["full_page_text"],
        "platform": "",
        "history": state.get("history", []),
        "content_approved": False,
        "url": state.get("url", ""),
        "has_scraped": True,
        "draft_content": ""  # Added missing field
    }

def answer_question(state: State) -> State:
    question = state["messages"][-1].content
    
    qa_prompt = [
        SystemMessage(content=PROMPTS["answer_question"]),  # Use from PROMPTS dict
        HumanMessage(content=f"""
        Website Content:
        {state["full_page_text"]}
        
        Question:
        {question}
        """)
    ]
    
    response = model.invoke(qa_prompt)
    answer = response.content  # Extract the content from the response
    
    return {
        "messages": [HumanMessage(content=answer)],  # Wrap the string content in a HumanMessage
        "brand_voice": state["brand_voice"],
        "full_page_text": state["full_page_text"],
        "platform": "",
        "history": state.get("history", []),
        "content_approved": False,
        "url": state.get("url", ""),
        "has_scraped": True,
        "draft_content": ""  # Added missing field
    }

def no_context_handler(state: State) -> State:
    """Handle case when no URL has been provided yet."""
    return {
        "messages": [HumanMessage(content="Please provide a URL to scrape first, then I can answer questions or generate content based on that website.")],
        "brand_voice": "",
        "full_page_text": "",
        "platform": "",
        "history": state.get("history", []),
        "content_approved": False,
        "url": "",
        "has_scraped": False,
        "draft_content": ""
    }

def route_platform(state: State) -> str:
    """Route to specific content generation function based on platform."""
    platform_choice = state["messages"][-1].content.lower()
    platforms = {
        'blog': 'generate_blog_post',
        'email': 'generate_email_marketing',
        'linkedin': 'generate_linkedin_post',
        'facebook': 'generate_facebook_post',
        'instagram': 'generate_instagram_post'
    }
    
    for key, node in platforms.items():
        if key in platform_choice:
            return node
    
    return "invalid_platform"

def create_platform_content(platform: str, state: State) -> State:
    """Generic function to create content for a specific platform."""
    history = state.get('history', [])
    
    # Check if similar content exists in history
    similar_history = [
        item['content'][:100] + "..." 
        for item in history
        if item.get('platform') == platform
    ]
    
    history_text = ""
    # Check for similar content in history
    if similar_history:
        history_text = "\n".join([f"- {item}" for item in similar_history])
        similarity_check_prompt = [
            SystemMessage(content=f"Compare these concepts:\nNew: {state['messages'][-1].content}\nHistory:\n{history_text}\nIs this new content distinct? Answer YES or NO only.")
        ]
        
        similarity_response = model.invoke(similarity_check_prompt)
        
        if "NO" in similarity_response.content.upper():
            return {
                "messages": [HumanMessage(content="This topic seems similar to existing content. Please provide a new angle or different topic.")],
                "brand_voice": state.get("brand_voice", ""),
                "full_page_text": state.get("full_page_text", ""),
                "platform": platform,
                "history": history,
                "content_approved": False,
                "url": state.get("url", ""),
                "has_scraped": state.get("has_scraped", False),
                "draft_content": ""  # Added missing field
            }
    
    # Check if this is a regeneration attempt
    was_rejected = state.get("content_approved") is False and state.get("draft_content") is not None
    
    # Prepare context for content generation
    brand_voice_text = state.get("brand_voice", "No brand voice analysis available")
    website_summary = state.get("full_page_text", "")[:1000] + "..." if len(state.get("full_page_text", "")) > 1000 else state.get("full_page_text", "")
    
    enhanced_prompt = f"""
    Brand Voice Analysis:
    {brand_voice_text}
    
    Website Overview:
    {website_summary}
    
    Previous {platform} Content:
    {history_text if similar_history else 'No previous content found'}
    
    {("Your previous generation was rejected. Please create new content." if was_rejected else "")}
    
    New Content Requirements:
    {CONTENT_TEMPLATES[platform].format(topic=state["messages"][-1].content)}
    
    Guidelines:
    1. Align with the analyzed brand voice and target audience
    2. Avoid repeating previous ideas
    3. Incorporate insights from the website
    4. Keep it engaging and appropriate for the platform
    """
    content_prompt = [SystemMessage(content=enhanced_prompt)]
    response = model.invoke(content_prompt)
    generated_content = response.content  # Extract the content from the response
    
    return {
        "messages": [HumanMessage(content=generated_content)],
        "brand_voice": state.get("brand_voice", ""),
        "full_page_text": state.get("full_page_text", ""),
        "platform": platform,
        "history": history,
        "draft_content": generated_content,
        "content_approved": False,
        "url": state.get("url", ""),
        "has_scraped": state.get("has_scraped", False)
    }

def generate_blog_post(state: State) -> State:
    return create_platform_content("Blog", state)

def generate_linkedin_post(state: State) -> State:
    return create_platform_content("LinkedIn", state)

def generate_email_marketing(state: State) -> State:
    return create_platform_content("Email", state)

def generate_facebook_post(state: State) -> State:
    return create_platform_content("Facebook", state)

def generate_instagram_post(state: State) -> State:
    return create_platform_content("Instagram", state)

def invalid_platform_handler(state: State) -> State:
    return {
        "messages": [HumanMessage(content="Please specify a valid platform (blog, email, linkedin, facebook, instagram)")],
        "brand_voice": state.get("brand_voice", ""),
        "full_page_text": state.get("full_page_text", ""),
        "platform": "Invalid",
        "history": state.get("history", []),
        "content_approved": False,
        "url": state.get("url", ""),
        "has_scraped": state.get("has_scraped", False),
        "draft_content": ""
    }

def human_node(state: State):
    """Handle human feedback on generated content."""
    value = interrupt({"text_to_revise": state["draft_content"]})    
    return {"draft_content": value}

def get_feedback(state: State) -> str:
    """Determine whether to end flow or continue based on feedback."""
    if state.get("content_approved", False):
        return "end_flow"
    return "human_node"
