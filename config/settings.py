# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists in the project root 
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# SECURITY WARNING: keep the secret key used in production secret!
PDF_PASSWORD = os.getenv('PDF_PASSWORD')

# Define input and output directories
INPUTS_DIR = BASE_DIR / "data" / "inputs"
OUTPUTS_DIR = BASE_DIR / "data" / "outputs"

if not PDF_PASSWORD:
    raise ValueError("PDF_PASSWORD environment variable is not set. Please set it in the .env file.")

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', "")
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', "")

if not EMAIL_ADDRESS:
    raise ValueError("EMAIL_ADDRESS environment variable is not set. Please set it in the .env file.")

if not EMAIL_PASSWORD:
    raise ValueError("EMAIL_PASSWORD environment variable is not set. Please set it in the .env file.")