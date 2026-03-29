from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database (file is next to the app). With `uvicorn --reload`, file-watch restarts on DB
# writes unless you exclude *.db — use backend/run_dev.ps1 or run_dev.bat to avoid the camera restarting.
SQLALCHEMY_DATABASE_URL = "sqlite:///./safety_dashboard.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()