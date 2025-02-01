from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the SQLite URL. This will create a file named "test.db" in the current working directory.
DATABASE_URL = "sqlite:///./test.db"

# Create the SQLAlchemy engine.
# For SQLite, we need to set check_same_thread to False.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our ORM models.
Base = declarative_base()

# Helper function to initialize the database.
def init_db():
    # Import all modules that define models so that they are registered with Base.
    import app.models  # Ensure that models.py is in the same package.
    # Create all tables in the database.
    Base.metadata.create_all(bind=engine)
