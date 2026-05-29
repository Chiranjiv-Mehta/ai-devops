import json
import re
# pyrefly: ignore [missing-import]
from loguru import logger

class LogParser:
    @staticmethod
    def detect_log_type(log_content: str) -> str:
        """
        Detects the type of log content (e.g., Python stack trace, Java traceback, Docker build, Nginx/Apache, JSON).
        """
        if not log_content:
            return "empty"
        
        # Check for JSON logs
        try:
            # Check if first non-whitespace line looks like JSON
            first_line = log_content.strip().split("\n")[0]
            if first_line.startswith("{") and first_line.endswith("}"):
                json.loads(first_line)
                return "json"
        except Exception:
            pass

        # Check for Python stack traces
        if "Traceback (most recent call last):" in log_content:
            return "python_traceback"
        
        # Check for Java exceptions
        if re.search(r"at [a-zA-Z0-9_.]+\.[a-zA-Z0-9_]+\([a-zA-Z0-9_]+\.java:\d+\)", log_content):
            return "java_stacktrace"
        
        # Check for Docker build errors
        if "Step " in log_content or "ERROR: failed to solve" in log_content or "failed to solve with frontend" in log_content:
            return "docker_build_log"
        
        # Check for Kubernetes container logs (often starts with RFC3339 timestamps)
        k8s_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+"
        if re.search(k8s_pattern, log_content, re.MULTILINE):
            return "kubernetes_log"

        # Check for syslog / Linux auth logs
        if re.search(r"^[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}", log_content):
            return "syslog"

        return "generic_text"

    @staticmethod
    def clean_log(log_content: str, max_lines: int = 200) -> str:
        """
        Cleans and truncates a log file to extract relevant debug information.
        Prioritizes lines with errors, exceptions, failures, or tracebacks.
        """
        if not log_content:
            return ""
            
        lines = log_content.split("\n")
        total_lines = len(lines)
        
        if total_lines <= max_lines:
            return log_content
            
        # If the log is too long, we extract lines near critical terms or slice the end.
        logger.info(f"Log has {total_lines} lines. Truncating to focus on errors.")
        
        critical_keywords = [
            "error", "exception", "fatal", "critical", "fail", "failed", 
            "traceback", "stacktrace", "caused by", "stderr"
        ]
        
        # Find indices of matching lines
        matching_indices = set()
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in critical_keywords):
                # Add the line itself and a few lines of context around it
                for c_idx in range(max(0, idx - 3), min(total_lines, idx + 5)):
                    matching_indices.add(c_idx)
        
        # If we have no error indicators, take the last max_lines lines
        if not matching_indices:
            logger.info("No errors detected. Returning the last segment of the logs.")
            return "\n".join(lines[-max_lines:])
            
        # Sort indices and build log snippet
        sorted_indices = sorted(list(matching_indices))
        
        cleaned_chunks = []
        last_idx = -2
        
        for idx in sorted_indices:
            if idx > last_idx + 1:
                # Add separator indicating skipped lines
                if cleaned_chunks:
                    cleaned_chunks.append("\n--- [Lines skipped] ---\n")
            cleaned_chunks.append(lines[idx])
            last_idx = idx
            
            # Prevent going way over max_lines
            if len(cleaned_chunks) >= max_lines:
                break
                
        return "\n".join(cleaned_chunks)
