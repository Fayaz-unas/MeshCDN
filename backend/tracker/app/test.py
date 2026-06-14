from app.db.database import engine

with engine.connect() as connection:
    print("Database connected successfully!")