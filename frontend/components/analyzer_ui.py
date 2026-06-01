import streamlit as st
import requests


def render_analyzer_ui(backend_url: str):
    """Render the logs and IaC analyzer UI with 4 analysis tabs."""
    st.markdown("<h1>🔍 Logs & IaC Analyzer</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 16px; margin-top: -1.5rem; margin-bottom: 2rem;'>"
        "Upload deployment logs, build outputs, or paste configuration files. Our diagnostic engine detects errors and suggests immediate solutions."
        "</p>",
        unsafe_allow_html=True
    )

    # Initialize state variables
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'log_type_detected' not in st.session_state:
        st.session_state.log_type_detected = None
    if 'cleaned_fragment' not in st.session_state:
        st.session_state.cleaned_fragment = None
    if 'error_occurred' not in st.session_state:
        st.session_state.error_occurred = False
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""

    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Paste Log/Config",
        "📂 Upload Log/Config File",
        "📁 Upload Project Archive",
        "🔗 Import from GitHub"
    ])

    # Tab 1: Paste log text
    with tab1:
        log_text = st.text_area(
            "Paste log lines or file content:",
            height=250,
            placeholder="[ERROR] database connection failed at host db.local:5432..."
        )
        if st.button("🚀 Analyze Pasted Text", key="submit_pasted_text"):
            if not log_text.strip():
                st.warning("Please paste some content before analyzing.")
            else:
                with st.spinner("Analyzing text patterns and generating diagnosis..."):
                    try:
                        payload = {"content": log_text}
                        response = requests.post(f"{backend_url}/analyze/text", json=payload, timeout=90)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.analysis_result = data.get("analysis")
                            st.session_state.log_type_detected = data.get("log_type")
                            st.session_state.cleaned_fragment = data.get("cleaned_log")
                            st.session_state.error_occurred = False
                        else:
                            st.session_state.error_occurred = True
                            st.session_state.error_message = response.json().get("detail", "Error in backend")
                    except Exception as e:
                        st.session_state.error_occurred = True
                        st.session_state.error_message = f"Failed to connect to backend: {str(e)}"

    # Tab 2: Upload file
    with tab2:
        uploaded_file = st.file_uploader(
            "Choose a log or configuration file",
            type=["log", "txt", "yaml", "yml", "json", "dockerfile", "tf"]
        )
        if st.button("🚀 Analyze Uploaded File", key="submit_uploaded_file"):
            if not uploaded_file:
                st.warning("Please select a file to upload first.")
            else:
                with st.spinner(f"Uploading and analyzing {uploaded_file.name}..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{backend_url}/analyze/file", files=files, timeout=90)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.analysis_result = data.get("analysis")
                            st.session_state.log_type_detected = data.get("log_type")
                            st.session_state.cleaned_fragment = data.get("cleaned_log")
                            st.session_state.error_occurred = False
                        else:
                            st.session_state.error_occurred = True
                            st.session_state.error_message = response.json().get("detail", "Error in backend")
                    except Exception as e:
                        st.session_state.error_occurred = True
                        st.session_state.error_message = f"Failed to connect to backend: {str(e)}"

    # Tab 3: Upload project archive
    with tab3:
        project_zip = st.file_uploader("Upload a zipped project archive", type=["zip"])
        if st.button("🚀 Analyze Project Archive", key="submit_project_archive"):
            if not project_zip:
                st.warning("Please select a ZIP archive first.")
            else:
                with st.spinner(f"Uploading and analyzing {project_zip.name}..."):
                    try:
                        files = {"file": (project_zip.name, project_zip.getvalue(), project_zip.type)}
                        response = requests.post(f"{backend_url}/analyze/project", files=files, timeout=180)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.analysis_result = data.get("analysis")
                            st.session_state.log_type_detected = data.get("log_type")
                            st.session_state.cleaned_fragment = data.get("cleaned_log")
                            st.session_state.error_occurred = False
                        else:
                            st.session_state.error_occurred = True
                            st.session_state.error_message = response.json().get("detail", "Error in backend")
                    except Exception as e:
                        st.session_state.error_occurred = True
                        st.session_state.error_message = f"Failed to connect to backend: {str(e)}"

    # Tab 4: GitHub import
    with tab4:
        repo_url = st.text_input("GitHub repository URL", placeholder="https://github.com/owner/repo")
        branch = st.text_input("Branch", value="main")
        github_token = st.text_input("GitHub token (optional)", type="password")
        if st.button("🚀 Analyze GitHub Repo", key="submit_github_repo"):
            if not repo_url.strip():
                st.warning("Please enter a GitHub repository URL.")
            else:
                with st.spinner("Downloading and analyzing repository..."):
                    try:
                        payload = {
                            "repo_url": repo_url.strip(),
                            "branch": branch.strip() or "main",
                            "github_token": github_token.strip() or None
                        }
                        response = requests.post(f"{backend_url}/analyze/github", json=payload, timeout=180)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.analysis_result = data.get("analysis")
                            st.session_state.log_type_detected = data.get("log_type")
                            st.session_state.cleaned_fragment = data.get("cleaned_log")
                            st.session_state.error_occurred = False
                        else:
                            st.session_state.error_occurred = True
                            st.session_state.error_message = response.json().get("detail", "Error in backend")
                    except Exception as e:
                        st.session_state.error_occurred = True
                        st.session_state.error_message = f"Failed to connect to backend: {str(e)}"

    # Render results
    st.markdown("---")
    if st.session_state.error_occurred:
        st.error(f"Analysis Failed: {st.session_state.error_message}")

    if st.session_state.analysis_result:
        st.success("Analysis Complete!")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**Detected Format:** `{st.session_state.log_type_detected}`")
        with col2:
            st.markdown(f"**Status:** `Success`")

        res_col1, res_col2 = st.columns([1, 1])
        with res_col1:
            st.markdown("### 📋 Extracted Fragment")
            st.code(st.session_state.cleaned_fragment, language="log")
        with res_col2:
            st.markdown("### 🤖 Diagnostic Report")
            st.markdown(st.session_state.analysis_result)