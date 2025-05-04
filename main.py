from streamlit_ui import setup_ui_style, initialize_session_state
import streamlit as st
from create_graph import create_unified_graph
from streamlit_ui import handle_regeneration, handle_user_input
from datetime import datetime

def main():
    """Main application function."""
    setup_ui_style()
    initialize_session_state()

    # Create a two-column layout
    col1, col2 = st.columns([2, 1])

    # Initialize the unified graph
    unified_graph = create_unified_graph()

    # Main interaction area
    with col1:
        # Display chat history
        for idx, msg in enumerate(st.session_state.messages):
            avatar = "🤖" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                if msg.get("platform"):
                    st.subheader(f"{msg['platform']} Content")

                # Show content with appropriate styling
                content_class = "draft-content" if msg.get("needs_approval") else ""
                st.markdown(f"<div class='{content_class}'>{msg['content']}</div>", unsafe_allow_html=True)

                # Approval buttons for drafts
                if msg.get("needs_approval"):
                    cols = st.columns([1, 1, 2])
                    with cols[0]:
                        if st.button(f"✅ Approve", key=f"approve_{idx}"):
                            st.session_state.approved_content.append({
                                "content": msg["content"],
                                "platform": msg["platform"],
                                "timestamp": datetime.now().isoformat(),
                                "url": st.session_state.current_url
                            })
                            st.session_state.messages[idx]["needs_approval"] = False
                            st.rerun()
                    with cols[1]:
                        if st.button(f"🔄 Regenerate", key=f"regen_{idx}"):
                            platform_to_regenerate = msg["platform"]
                            last_user_prompt = ""

                            # Find the last user prompt for this content
                            for i in range(idx - 1, -1, -1):
                                if st.session_state.messages[i]["role"] == "user":
                                    last_user_prompt = st.session_state.messages[i]["content"]
                                    break

                            # Set regeneration parameters
                            st.session_state.regenerate_platform = platform_to_regenerate
                            st.session_state.last_user_prompt = last_user_prompt

                            # Remove the message
                            del st.session_state.messages[idx]
                            st.rerun()

        # Handle regeneration
        handle_regeneration()

        # Chat input
        if prompt := st.chat_input("Enter a URL, ask a question, or request content generation"):
            handle_user_input(prompt)

    # Sidebar for content management and info
    with col2:
        st.subheader("Content Management")

        # Show current website info
        if st.session_state.current_url:
            st.info(f"Current Website: {st.session_state.current_url}")

        if st.session_state.brand_voice:
            with st.expander("📢 Brand Voice Analysis"):
                st.write(st.session_state.brand_voice)

        # Content history
        st.subheader("Approved Content History")
        if st.session_state.approved_content:
            for idx, item in enumerate(reversed(st.session_state.approved_content)):
                with st.expander(f"{item['platform']} - {item['timestamp'][:10]}"):
                    st.write(item["content"])
                    if st.button("Delete", key=f"delete_{idx}"):
                        index_to_remove = len(st.session_state.approved_content) - 1 - idx
                        st.session_state.approved_content.pop(index_to_remove)
                        st.rerun()
        else:
            st.caption("No approved content yet")

        # Clear history button
        if st.button("🧹 Clear All History"):
            st.session_state.messages = [{
                "role": "assistant",
                "content": "Chat history cleared. Ready for new requests!",
                "platform": None
            }]
            st.session_state.approved_content = []
            st.session_state.brand_voice = ""
            st.session_state.scraped_text = ""
            st.session_state.current_url = ""
            st.session_state.has_scraped = False
            st.session_state.regenerate_platform = None
            st.session_state.last_user_prompt = ""
            st.rerun()

        st.divider()

        # Platform guidelines
        st.subheader("Platform Guidelines")
        st.markdown("""
        - **Blog**: Long-form, structured content  
        - **Email**: Clear CTAs, concise messaging  
        - **LinkedIn**: Professional tone  
        - **Facebook**: Conversational, community-building  
        - **Instagram**: Visual, trendy with hashtags  
        """)


if __name__ == "__main__":
    main()