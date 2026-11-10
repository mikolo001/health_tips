import os
import streamlit as st
import mysql.connector as sql
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# ==========================================
# GROQ CONFIGURATION
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-20b"

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

HEALTH_INSTRUCTIONS = """
You are HealthMate AI, a health information assistant.

Explain health topics in clear language.
Help users understand symptoms without diagnosing them.
Explain medicines and general wellness safely.
Never invent medication dosages or claim to be a doctor.
For potentially life-threatening symptoms, recommend immediate
emergency medical care.
Explain uncertainty and encourage professional medical advice.
Protect user privacy and avoid requesting unnecessary identifiers.
"""

# ==========================================
# MYSQL CONFIGURATION
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Enter your MySQL password if you have one
    "database": "healthmateai"
}


def get_db_connection():
    """Create and return a MySQL database connection."""
    return sql.connect(**DB_CONFIG)

# from openai import OpenAI

# # Classroom setup: insert your Groq API key here.
# GROQ_API_KEY = "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"

# MODEL_NAME = "openai/gpt-oss-20b"

# client = OpenAI(
#     api_key=GROQ_API_KEY,
#     base_url="https://api.groq.com/openai/v1"
# )

# TELEGRAM_BOT_TOKEN = "8909184350:AAFT4X9Ta2acvRMr1x8k07Se4ULm4g0jnLs"

# HEALTH_INSTRUCTIONS = """
# You are HealthMate AI, a health information assistant.

# Explain health topics in clear language.
# Help users understand symptoms without diagnosing them.
# Explain medicines and general wellness safely.
# Never invent medication dosages or claim to be a doctor.
# For potentially life-threatening symptoms, recommend immediate
# emergency medical care.
# Explain uncertainty and encourage professional medical advice.
# Protect user privacy and avoid requesting unnecessary identifiers.
# """