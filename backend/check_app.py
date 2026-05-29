import sys
import os

# Prevent protobuf from trying to import broken C extension on Python 3.14
sys.modules['google._upb._message'] = None

# Adjust path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.log_parser import LogParser
from backend.utils.config import settings

def test_log_parser():
    print("Executing LogParser Verification...")
    
    # 1. Test log format detection
    python_log = "Traceback (most recent call last):\n  File \"app.py\", line 4, in <module>\n    1/0\nZeroDivisionError: division by zero"
    detected_type = LogParser.detect_log_type(python_log)
    print(f"  - Detected type for Python log: {detected_type}")
    assert detected_type == "python_traceback", f"Expected python_traceback, got {detected_type}"

    json_log = '{"level":"error", "message": "Failed to connect to db", "timestamp": "2026-05-28"}'
    detected_type = LogParser.detect_log_type(json_log)
    print(f"  - Detected type for JSON log: {detected_type}")
    assert detected_type == "json", f"Expected json, got {detected_type}"
    
    k8s_log = "2026-05-28T10:00:00.000000Z Starting container..."
    detected_type = LogParser.detect_log_type(k8s_log)
    print(f"  - Detected type for K8s log: {detected_type}")
    assert detected_type == "kubernetes_log", f"Expected kubernetes_log, got {detected_type}"

    # 2. Test log cleaning / truncation
    long_log_lines = [f"Line {i} info log messaging" for i in range(500)]
    long_log_lines[250] = "[ERROR] database connection timed out"
    long_log = "\n".join(long_log_lines)
    
    cleaned = LogParser.clean_log(long_log, max_lines=50)
    print(f"  - Cleaned log lines count: {len(cleaned.split(chr(10)))}")
    assert "database connection timed out" in cleaned, "Error line was not preserved during cleaning!"
    print("  - LogParser verification passed!")

def test_config_loader():
    print("Executing Config Loader Verification...")
    print(f"  - Host: {settings.API_HOST}")
    print(f"  - Port: {settings.API_PORT}")
    print(f"  - Default provider configured: {settings.DEFAULT_PROVIDER}")
    print(f"  - Upload Dir: {settings.UPLOAD_DIR}")
    assert settings.API_PORT > 0, "Invalid API port configuration"
    print("  - Config loader verification passed!")

def test_backend_routers():
    print("Executing Router Import Verification...")
    try:
        from backend.main import app
        print("  - Successfully imported FastAPI app object!")
        assert app.title == "AI DevOps Assistant API", "FastAPI App title mismatch"
        print("  - Router import verification passed!")
    except Exception as e:
        print(f"  - Failed to import main app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== STARTING AI DEVOPS ASSISTANT VERIFICATION ===")
    test_log_parser()
    print("-" * 50)
    test_config_loader()
    print("-" * 50)
    test_backend_routers()
    print("=== ALL VERIFICATIONS PASSED SUCCESSFULLY! ===")
    sys.exit(0)
