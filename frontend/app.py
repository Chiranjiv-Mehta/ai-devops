# pyrefly: ignore [missing-import]
import streamlit as st
import requests 
import os
# pyrefly: ignore [missing-import]
from loguru import logger

# Set page config first
st.set_page_config(
    page_title="AI DevOps Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Premium Custom CSS with deep slate and vibrant gradients, glassmorphism, and transitions
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* Apply custom fonts */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}
code, pre, [class*="mono"] {
    font-family: 'JetBrains Mono', monospace !important;
}

/* App background styling */
.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(9, 12, 22, 1) 90%);
    color: #f1f5f9;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.95);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Main title styling */
h1 {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    letter-spacing: -0.05em;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 2rem !important;
}

/* Headers */
h2, h3 {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    color: #e2e8f0;
}

/* Custom card container styling */
.devops-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
}
.devops-card:hover {
    border-color: rgba(79, 172, 254, 0.4);
    box-shadow: 0 8px 32px 0 rgba(79, 172, 254, 0.1);
    transform: translateY(-2px);
}

/* Streamlit Button modifications */
.stButton>button {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
}
.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.45) !important;
    background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%) !important;
}
.stButton>button:active {
    transform: translateY(1px) !important;
}

/* Chat bubble styling overrides */
.stChatMessage {
    border-radius: 12px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
}
.stChatMessage[data-testid="stChatMessage-user"] {
    background-color: rgba(37, 99, 235, 0.15) !important;
    border: 1px solid rgba(37, 99, 235, 0.3) !important;
}
.stChatMessage[data-testid="stChatMessage-assistant"] {
    background-color: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Custom Status Indicator Badge */
.status-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.status-connected {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.status-disconnected {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}
</style>
"""

# Render custom CSS styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper to check backend health status
def check_backend_status():
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return True, data
    except Exception:
        pass
    return False, {}

# Check Status
is_connected, health_data = check_backend_status()

# Sidebar Navigation Panel
st.sidebar.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h2 style='color: #fff;'>🛡️ DevOps AI</h2><p style='color: #64748b; font-size: 14px;'>Automation & Troubleshooting</p></div>", unsafe_allow_html=True)

# Connection Status
if is_connected:
    st.sidebar.markdown(f'<div style="text-align: center; margin-bottom: 1.5rem;"><span class="status-badge status-connected">🟢 API Connected ({health_data.get("default_provider", "LLM")})</span></div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div style="text-align: center; margin-bottom: 1.5rem;"><span class="status-badge status-disconnected">🔴 API Disconnected</span></div>', unsafe_allow_html=True)

menu_option = st.sidebar.radio(
    "Navigation",
    ["💬 DevOps Chatbot", "🔍 Logs & IaC Analyzer", "🛠️ IaC Config Generator"],
    index=0
)

# Configuration settings display in sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")
st.sidebar.caption(f"Backend Service: `{BACKEND_URL}`")
st.sidebar.caption("Google Gemini & OpenAI Integrations")

# Import UI components inside the routing blocks to avoid circular reference or early load
from components.chat_ui import render_chat_ui
from components.analyzer_ui import render_analyzer_ui
from components.generator_ui import render_generator_ui

# Render Selected View
if menu_option == "💬 DevOps Chatbot":
    render_chat_ui(BACKEND_URL)
elif menu_option == "🔍 Logs & IaC Analyzer":
    render_analyzer_ui(BACKEND_URL)
elif menu_option == "🛠️ IaC Config Generator":
    render_generator_ui(BACKEND_URL)
