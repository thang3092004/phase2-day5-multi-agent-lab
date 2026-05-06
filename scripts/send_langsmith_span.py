"""Send a test trace/span to LangSmith for diagnostics.

Run:
  python scripts/send_langsmith_span.py

This script loads `.env` (if present), constructs a LangSmith client, and attempts
to create a simple span or run so you can verify traces appear in the dashboard.
"""
from dotenv import load_dotenv
import os
import sys

load_dotenv('.env')

try:
    from langsmith import Client
except Exception as e:
    print("ERROR: cannot import langsmith:", e)
    sys.exit(2)

API_KEY = os.getenv('LANGSMITH_API_KEY')
PROJECT = os.getenv('LANGSMITH_PROJECT', 'multi-agent-research-lab')

print(f"Using LANGSMITH_API_KEY present: {bool(API_KEY)}")
print(f"Using project: {PROJECT}")

if not API_KEY:
    print("No LANGSMITH_API_KEY found in environment or .env — please set it and retry.")
    sys.exit(1)

client = Client(api_key=API_KEY)

# Try to create a simple span/run depending on available API
try:
    # preferred: span context manager
    with client.span(name="sanity-check", project_name=PROJECT) as span:
        try:
            span.log({"msg": "sanity check from local script"})
        except Exception:
            pass
    print("OK: span created (sanity-check). Check LangSmith 'Runs' for project and refresh.")
    sys.exit(0)
except Exception as err:
    print("span API failed:", err)

# fallback: try direct run creation
try:
    run = client.create_run(name="sanity-check", project_name=PROJECT)
    print("OK: run created id=", getattr(run, 'id', run))
    sys.exit(0)
except Exception as err2:
    print("create_run API failed:", err2)
    sys.exit(3)
