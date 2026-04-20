import os

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./platform.db")
BUILD_SHA: str = os.getenv("BUILD_SHA", "dev")
