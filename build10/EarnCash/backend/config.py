"""
Application configuration.
All secrets and environment-specific values come from environment
variables (see .env.example). Never commit a real .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- Database ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "earncash")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))

    # --- Auth ---
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "24"))

    # --- Business rules ---
    # Percentage of a course's tuition fee paid out as commission
    # once payment is verified by an admin.
    COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.10"))  # 10%
    MIN_WITHDRAWAL_AMOUNT = float(os.getenv("MIN_WITHDRAWAL_AMOUNT", "500"))

    # --- CORS ---
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5500")

    @staticmethod
    def validate():
        if not Config.JWT_SECRET:
            raise RuntimeError(
                "JWT_SECRET is not set. Copy .env.example to .env and set a "
                "long random value before starting the server."
            )
