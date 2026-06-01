import streamlit as st
import requests

def render_analyzer_ui(backend_url: str):
    st.markdown("<h1>🔍 Logs & IaC Analyzer</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 16px; margin-top: -1.5rem; margin-bottom: 2rem;'>"
        "Upload deployment logs, build outputs, or paste configuration files. Our diagnostic engine detects errors and suggests immediate solutions."
        "</p>",
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📝 Paste Log/Config", "📂 Upload Log/Config File", "📁 Upload Project Archive"])
    # Setup loading triggers
    analysis_result = None
    log_type_detected = None
    cleaned_fragment = None
    error_occurred = False
    error_message = ""

    with tab1:
        log_text = st.text_area(
            "Paste log lines or file content (Docker build outputs, K8s events, Python/Java tracebacks, Terraform plans, etc.):",
            height=250,
            placeholder="[ERROR] database connection failed at host db.local:5432..."
        )
        submit_text = st.button("🚀 Analyze Pasted Text", key="submit_pasted_text")

        if submit_text:
            if not log_text.strip():
                st.warning("Please paste some content before analyzing.")
            else:
                with st.spinner("Analyzing text patterns and generating diagnosis..."):
                    try:
                        payload = {"content": log_text}
                        response = requests.post(f"{backend_url}/analyze/text", json=payload, timeout=90)
                        if response.status_code == 200:
                            data = response.json()
                            analysis_result = data.get("analysis")
                            log_type_detected = data.get("log_type")
                            cleaned_fragment = data.get("cleaned_log")
                        else:
                            error_occurred = True
                            error_message = response.json().get("detail", "Error in backend processing")
                    except Exception as e:
                        error_occurred = True
                        error_message = f"Failed to connect to backend: {str(e)}"

    with tab2:
        uploaded_file = st.file_uploader(
            "Choose a log or configuration file", 
            type=["log", "txt", "yaml", "yml", "json", "dockerfile", "tf"]
        )
        submit_file = st.button("🚀 Analyze Uploaded File", key="submit_uploaded_file")

        if submit_file:
            if not uploaded_file:
                st.warning("Please select a file to upload first.")
            else:
                with st.spinner(f"Uploading and analyzing {uploaded_file.name}..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(f"{backend_url}/analyze/file", files=files, timeout=90)
                        if response.status_code == 200:
                            data = response.json()
                            analysis_result = data.get("analysis")
                            log_type_detected = data.get("log_type")
                            cleaned_fragment = data.get("cleaned_log")
                        else:
                            error_occurred = True
                            error_message = response.json().get("detail", "Error in backend processing")
                    except Exception as e:
                        error_occurred = True
                        error_message = f"Failed to connect to backend: {str(e)}"
    with tab3:
        project_zip = st.file_uploader(
            "Upload a zipped project archive",
            type=["zip"]
        )
        submit_project = st.button("🚀 Analyze Project Archive", key="submit_project_archive")

        if submit_project:
            if not project_zip:
                st.warning("Please select a ZIP archive first.")
            else:
                with st.spinner(f"Uploading and analyzing {project_zip.name}..."):
                    try:
                        files = {"file": (project_zip.name, project_zip.getvalue(), project_zip.type)}
                        response = requests.post(f"{backend_url}/analyze/project", files=files, timeout=180)
                        if response.status_code == 200:
                            data = response.json()
                            analysis_result = data.get("analysis")
                            log_type_detected = data.get("log_type")
                            cleaned_fragment = data.get("cleaned_log")
                        else:
                            error_occurred = True
                            error_message = response.json().get("detail", "Error in backend processing")
                    except Exception as e:
                        error_occurred = True
                        error_message = f"Failed to connect to backend: {str(e)}"
    # Render results if present
    if error_occurred:
        st.error(f"Analysis Failed: {error_message}")
        
    if analysis_result:
        st.success("Analysis Complete!")
        
        # Display meta details
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"**Detected Format:** `{log_type_detected.replace('_', ' ').title()}`")
        with col2:
            st.markdown(f"**Status:** `Success`")
            
        st.markdown("---")
        
        # Grid layout for Cleaned Log Fragment vs AI Diagnosis
        res_col1, res_col2 = st.columns([1, 1])
        
        with res_col1:
            st.markdown("### 📋 Extracted Relevant Fragment")
            st.caption("Logs filtered to focus on error tracebacks and crash locations:")
            st.code(cleaned_fragment, language="log" if log_type_detected != "json" else "json")
            
        with res_col2:
            st.markdown("### 🤖 Diagnostic & Repair Report")
            st.markdown(analysis_result)
