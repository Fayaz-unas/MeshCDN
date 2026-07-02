from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import os

import sys
from pathlib import Path

if hasattr(sys, "_MEIPASS"):
    load_dotenv(Path(sys._MEIPASS) / ".env")
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)