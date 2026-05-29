import streamlit as st
import requests

def render_generator_ui(backend_url: str):
    st.markdown("<h1>🛠️ Infrastructure as Code Generator</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #94a3b8; font-size: 16px; margin-top: -1.5rem; margin-bottom: 2rem;'>"
        "Generate clean, secure, production-ready DevOps templates based on best practices. Select your target configuration below."
        "</p>",
        unsafe_allow_html=True
    )

    template_category = st.selectbox(
        "Select Configuration Type",
        ["Dockerfile", "Kubernetes Manifest", "GitHub Actions Workflow", "Terraform Infrastructure"]
    )

    # Initialize state
    payload_details = {}
    type_key = ""

    st.markdown("### 📋 Configuration Parameters")
    
    if template_category == "Dockerfile":
        type_key = "dockerfile"
        col1, col2 = st.columns(2)
        with col1:
            language = st.selectbox("Language / Runtime", ["Python", "Node.js", "Go", "Java (Spring Boot)", "Static Web (Nginx)"])
            port = st.number_input("Exposed Container Port", min_value=1, max_value=65535, value=8000)
            workdir = st.text_input("Working Directory inside container", value="/app")
        with col2:
            multi_stage = st.checkbox("Enable Multi-Stage Build (Highly Recommended)", value=True)
            non_root = st.checkbox("Configure Non-Root User (Security Best Practice)", value=True)
            build_args = st.text_area("Build Arguments (Key-Value, one per line)", placeholder="APP_ENV=production\nVERSION=1.0.0")
            
        payload_details = {
            "language": language,
            "port": int(port),
            "workdir": workdir,
            "multi_stage": multi_stage,
            "non_root": non_root,
            "build_args": build_args.split("\n") if build_args else []
        }

    elif template_category == "Kubernetes Manifest":
        type_key = "kubernetes"
        col1, col2 = st.columns(2)
        with col1:
            app_name = st.text_input("Application Name", value="my-web-app")
            namespace = st.text_input("Kubernetes Namespace", value="default")
            replicas = st.number_input("Replica Count", min_value=1, max_value=100, value=3)
            image = st.text_input("Container Image (including tag)", value="nginx:1.25-alpine")
        with col2:
            service_type = st.selectbox("Service Type", ["ClusterIP", "NodePort", "LoadBalancer"])
            container_port = st.number_input("Container Port", min_value=1, max_value=65535, value=80)
            service_port = st.number_input("Service Port", min_value=1, max_value=65535, value=80)
            health_check = st.checkbox("Include Liveness / Readiness Probes", value=True)
            
        payload_details = {
            "app_name": app_name,
            "namespace": namespace,
            "replicas": int(replicas),
            "image": image,
            "service_type": service_type,
            "container_port": int(container_port),
            "service_port": int(service_port),
            "health_check": health_check
        }

    elif template_category == "GitHub Actions Workflow":
        type_key = "github_actions"
        col1, col2 = st.columns(2)
        with col1:
            workflow_name = st.text_input("Workflow Name", value="Build and Deploy")
            trigger_branch = st.text_input("Trigger Branch", value="main")
            build_runner = st.selectbox("Build Runner OS", ["ubuntu-latest", "windows-latest", "macos-latest"])
        with col2:
            pipeline_steps = st.multiselect(
                "Pipeline Tasks / Stages",
                ["Lint Code", "Run Unit Tests", "Build Docker Image", "Push to Docker Hub / Registry", "Deploy to Kubernetes (kubectl)"],
                default=["Lint Code", "Run Unit Tests", "Build Docker Image"]
            )
            secrets = st.text_area("Secrets / Environment Variables Needed (comma separated)", placeholder="DOCKER_USERNAME, DOCKER_PASSWORD, KUBE_CONFIG")
            
        payload_details = {
            "workflow_name": workflow_name,
            "trigger_branch": trigger_branch,
            "runner": build_runner,
            "steps": pipeline_steps,
            "secrets": [s.strip() for s in secrets.split(",") if s.strip()]
        }

    elif template_category == "Terraform Infrastructure":
        type_key = "terraform"
        col1, col2 = st.columns(2)
        with col1:
            cloud_provider = st.selectbox("Cloud Provider", ["AWS (Amazon Web Services)", "GCP (Google Cloud)", "Azure"])
            region = st.text_input("Region", value="us-east-1" if cloud_provider.startswith("AWS") else "us-central1")
        with col2:
            resources = st.multiselect(
                "Resources to Provision",
                ["VPC / Virtual Network", "Virtual Machines / Compute Instances", "Storage Buckets / Containers", "Managed Kubernetes Cluster"],
                default=["VPC / Virtual Network", "Storage Buckets / Containers"]
            )
            project_env = st.selectbox("Environment", ["Development", "Staging", "Production"])

        payload_details = {
            "provider": cloud_provider,
            "region": region,
            "resources": resources,
            "environment": project_env
        }

    st.markdown("---")
    generate_btn = st.button("⚡ Generate Template", use_container_width=True)

    if generate_btn:
        with st.spinner(f"Writing blueprint for {template_category}..."):
            try:
                payload = {
                    "template_type": type_key,
                    "details": payload_details
                }
                
                response = requests.post(f"{backend_url}/generate", json=payload, timeout=90)
                
                if response.status_code == 200:
                    template_output = response.json().get("template")
                    st.success("Configuration Generated Successfully!")
                    st.markdown("### 💾 Output Template")
                    st.markdown(template_output)
                else:
                    st.error(f"Generation Failed ({response.status_code}): {response.json().get('detail', 'Unknown backend error')}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
