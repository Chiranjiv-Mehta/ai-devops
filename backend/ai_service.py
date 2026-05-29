import google.generativeai as genai
from openai import OpenAI
from loguru import logger
from backend.utils.config import settings

class AIService:
    def __init__(self):
        self.provider = settings.DEFAULT_PROVIDER
        self.gemini_configured = False
        self.openai_configured = False
        
        # Configure Gemini
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_configured = True
            except Exception as e:
                logger.error(f"Error configuring Gemini SDK: {e}")
                
        # Configure OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                self.openai_configured = True
            except Exception as e:
                logger.error(f"Error configuring OpenAI SDK: {e}")
                
    def _call_gemini(self, system_instruction: str, prompt: str, history: list = None) -> str:
        """Helper to call Google Gemini API"""
        if not self.gemini_configured:
            return "Error: Gemini API key is not configured. Please add it to your `.env` file."
            
        try:
            model_name = settings.GEMINI_MODEL
            logger.info(f"Calling Gemini ({model_name})...")
            
            # Use GenerativeModel with system instruction
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            
            # Format chat history if present
            if history:
                contents = []
                for turn in history:
                    role = "user" if turn.get("role") == "user" else "model"
                    contents.append({
                        "role": role,
                        "parts": [{"text": turn.get("content", "")}]
                    })
                # Append current prompt
                contents.append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })
                response = model.generate_content(contents)
            else:
                response = model.generate_content(prompt)
                
            return response.text
        except Exception as e:
            error_msg = f"Gemini API Error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _call_openai(self, system_instruction: str, prompt: str, history: list = None) -> str:
        """Helper to call OpenAI API"""
        if not self.openai_configured:
            return "Error: OpenAI API key is not configured. Please add it to your `.env` file."
            
        try:
            model_name = settings.OPENAI_MODEL
            logger.info(f"Calling OpenAI ({model_name})...")
            
            messages = [{"role": "system", "content": system_instruction}]
            
            if history:
                for turn in history:
                    messages.append({
                        "role": turn.get("role"),
                        "content": turn.get("content")
                    })
                    
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"OpenAI API Error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _generate_response(self, system_instruction: str, prompt: str, history: list = None) -> str:
        """Routes the call to the configured default provider, or falls back if needed."""
        # Fall back check
        if self.provider == "gemini":
            if self.gemini_configured:
                return self._call_gemini(system_instruction, prompt, history)
            elif self.openai_configured:
                logger.warning("Gemini API key not found. Falling back to OpenAI.")
                return self._call_openai(system_instruction, prompt, history)
        elif self.provider == "openai":
            if self.openai_configured:
                return self._call_openai(system_instruction, prompt, history)
            elif self.gemini_configured:
                logger.warning("OpenAI API key not found. Falling back to Gemini.")
                return self._call_gemini(system_instruction, prompt, history)
                
        return (
            "Error: No AI model provider configured or keys are invalid. "
            "Please configure GEMINI_API_KEY or OPENAI_API_KEY in your backend/.env file."
        )

    def run_devops_chat(self, user_prompt: str, chat_history: list) -> str:
        """
        Interactive DevOps-focused chat session.
        """
        system_instruction = (
            "You are an expert DevOps engineer and Site Reliability Engineer (SRE). "
            "Your domain knowledge covers: Docker, Kubernetes, Linux command-line, AWS, GCP, Azure, "
            "CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins), Terraform, Ansible, Nginx, databases, and general system design.\n\n"
            "Provide helpful, concise, and technically accurate responses. Always use markdown formatting, "
            "use code blocks for commands or configurations, and explain the commands you suggest."
        )
        return self._generate_response(system_instruction, user_prompt, chat_history)

    def analyze_log(self, log_content: str, log_type: str = "generic_text") -> str:
        """
        Analyzes a log file to extract explanations and potential fixes.
        """
        system_instruction = (
            "You are a DevOps Log Diagnostic Assistant. Your task is to analyze the provided log dump "
            "and diagnose issues, crashes, or deployment failures.\n\n"
            "Respond in structured markdown with the following sections:\n"
            "### 🔍 Log Analysis Summary\n"
            "Provide a concise, plain-English summary of what error occurred.\n\n"
            "### 🕵️ Root Cause Analysis\n"
            "Identify why the error occurred, pointing out specific stack traces, error codes, "
            "or file paths mentioned in the logs.\n\n"
            "### 💡 Recommended Fix\n"
            "Give step-by-step instructions on how to resolve the issue. Be specific.\n\n"
            "### 🛠️ Code/Config Modification\n"
            "Provide a copy-pasteable script, CLI command, config file patch, or modified Dockerfile/YAML snippet that resolves the problem. "
            "Use syntax highlighting in markdown code blocks."
        )
        
        prompt = f"LOG TYPE: {log_type}\n\nLOG CONTENT:\n```\n{log_content}\n```"
        return self._generate_response(system_instruction, prompt)

    def generate_iac_template(self, template_type: str, details: dict) -> str:
        """
        Generates Infrastructure as Code templates (Docker, K8s, CI/CD, Terraform).
        """
        system_instruction = (
            "You are a DevOps Automation expert. Your job is to write clean, secure, production-ready, "
            "and well-commented infrastructure-as-code configurations.\n"
            "Always follow modern security best practices:\n"
            "- Do not run as root inside Docker containers.\n"
            "- Use multi-stage builds when applicable to minimize image sizes.\n"
            "- Pin exact base image versions (avoid tags like 'latest').\n"
            "- Use secure parameters and avoid hardcoded secrets (use placeholder variables instead).\n\n"
            "Explain the configuration structure and instructions on how to apply it after generating it."
        )
        
        prompt = (
            f"Generate a configuration template of type: '{template_type}'.\n"
            f"Details provided by user:\n{json.dumps(details, indent=2)}\n\n"
            "Output the generated configuration in standard syntax code blocks (e.g. ```dockerfile or ```yaml) "
            "accompanied by brief descriptions of the sections."
        )
        
        return self._generate_response(system_instruction, prompt)
# Singleton instance
ai_service = AIService()
