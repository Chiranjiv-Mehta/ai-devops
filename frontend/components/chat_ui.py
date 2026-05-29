import streamlit as st
import requests

def render_chat_ui(backend_url: str):
    st.markdown("<h1>💬 DevOps AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 16px; margin-top: -1.5rem; margin-bottom: 2rem;'>"
        "Ask questions about Docker, Kubernetes, Terraform, Cloud Providers (AWS/GCP/Azure), bash commands, or CI/CD pipelines."
        "</p>",
        unsafe_allow_html=True
    )

    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Sidebar clear button
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    with col1:
        # Display greeting if history is empty
        if not st.session_state.chat_messages:
            st.markdown(
                '<div class="devops-card">'
                '<h3>👋 Welcome, Cloud Engineer!</h3>'
                '<p>How can I help you today? Here are some suggested questions to get started:</p>'
                '<ul>'
                '<li><i>"How do I debug a Kubernetes CrashLoopBackOff error?"</i></li>'
                '<li><i>"Draft a multi-stage Dockerfile for a Go application."</i></li>'
                '<li><i>"Explain how to structure Terraform environments."</i></li>'
                '<li><i>"What is the best way to securely manage secrets in GitHub Actions?"</i></li>'
                '</ul>'
                '</div>',
                unsafe_allow_html=True
            )

    # Display chat messages from history on app rerun
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a DevOps question..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Generate assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.markdown("*AI is searching knowledge base...*")
            
            try:
                # Prepare payload with past history
                # We limit to last 10 turns to avoid hitting prompt size limits
                history_payload = []
                for msg in st.session_state.chat_messages[:-1]:
                    history_payload.append({
                        "role": msg["role"] if msg["role"] == "user" else "assistant",
                        "content": msg["content"]
                    })
                
                payload = {
                    "message": prompt,
                    "history": history_payload[-10:]
                }
                
                response = requests.post(f"{backend_url}/chat", json=payload, timeout=60)
                
                if response.status_code == 200:
                    assistant_response = response.json().get("response", "No response content received.")
                    response_placeholder.markdown(assistant_response)
                    # Add assistant response to chat history
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                else:
                    error_detail = response.json().get("detail", "Unknown server error.")
                    response_placeholder.error(f"Error ({response.status_code}): {error_detail}")
            except Exception as e:
                response_placeholder.error(f"Failed to connect to backend: {str(e)}")
