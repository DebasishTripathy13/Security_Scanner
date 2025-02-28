import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent  # Root directory of the project

# Directory paths
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
WORDLISTS_DIR = os.path.expanduser("/usr/share/wordlists/dirb")

# File paths
LOG_FILE = os.path.join(LOGS_DIR, "audit.log")
WORDLIST_FILE = os.path.join(WORDLISTS_DIR, "common.txt")

# Define the allowed scanning scope
ALLOWED_DOMAINS = os.getenv("TARGET_DOMAINS", "google.com,yahoo.com,example.com").split(",")
ALLOWED_IPS = os.getenv("TARGET_IPS", "192.168.0.0/24,10.0.0.0/24").split(",")

# Application settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))