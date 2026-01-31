import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models

def init_db():
    print(f"Creating database tables in: {engine.url}")
    # Drop all first to ensure clean state if schema changed
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
