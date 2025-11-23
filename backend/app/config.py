import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / "data"
EXCEL_FILE = DATA_DIR / "ilocos_chatbot_dataset.xlsx"
PROLOG_KB = BASE_DIR / "app" / "prolog" / "kb.pl"

# Database
DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"

# API settings
API_TITLE = "Ilocos Tourism Chatbot API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Tourism chatbot with Prolog knowledge base integration"