"""
Configuration and Application Settings for FamilyCare AI.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# App Information
APP_TITLE = "FamilyCare AI"
APP_TAGLINE = "Smart Elderly Care & Family Coordination Platform"
APP_VERSION = "1.0.0-hackathon"
APP_DESCRIPTION = (
    "A multi-city family care coordination platform helping families stay "
    "connected, track daily elderly wellness, manage medications, and coordinate "
    "care activities with Google Gemini AI intelligence."
)

# Database
DB_PATH = BASE_DIR / "familycare.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Default Preferences
DEFAULT_CHECKIN_HOUR = 9  # 9:00 AM
DEFAULT_GRACE_PERIOD_MINS = 60  # 60 minutes grace period
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "America/Chicago")

# Visual Design Color Palette (Soft Lavender, Teal, Blue, Warm White)
THEME_COLORS = {
    "primary": "#7052E6",        # Rich Lavender Purple
    "primary_light": "#9B86EE",  # Soft Lavender
    "primary_dark": "#4C2882",
    "teal": "#0D9488",           # Deep Teal
    "teal_light": "#2DD4BF",     # Bright Teal / Mint
    "blue": "#0284C7",           # Sky Blue
    "blue_light": "#38BDF8",     # Bright Blue
    "accent_warm": "#F59E0B",    # Warm Amber
    "danger": "#EF4444",         # Alert Coral Red
    "success": "#10B981",        # Emerald Green
    "warning": "#F59E0B",        # Amber Warning
    "bg_light": "#F8FAFC",       # Warm White / Light Slate
    "card_bg": "#FFFFFF",
    "text_dark": "#0F172A",      # Slate 900
    "text_muted": "#64748B",     # Slate 500
    "border_glass": "rgba(255, 255, 255, 0.4)",
}
