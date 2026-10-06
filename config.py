import os
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
MAX_PARALLEL = int(os.getenv("MAX_PARALLEL", 2))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
