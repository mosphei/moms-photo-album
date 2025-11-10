import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Database connection details using environment variables
DB_HOST = os.getenv("DB_HOST",'db') # The service name defined in docker-compose.yml
DB_NAME = os.getenv("DB_NAME",'fastapi_db')
DB_USER = os.getenv("DB_USER",'xxx') 
DB_PASS = os.getenv("DB_PASS",'xxx') 
DB_PORT = 3306        # Default MySQL port

# 2. Construct the database URL using the 'mysql+pymysql' format
# The 'charset=utf8mb4' part is often recommended for full character support
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# 3. Create the SQLAlchemy engine
# The pool_pre_ping=True helps maintain healthy connections in a web application setting
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True # Optional, helps manage connections
)

# 4. Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Define the Base for your models (this can also be in models.py)
Base = declarative_base()

# 6. Dependency to get the database session (used in FastAPI endpoints)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 7. Utility function to create tables
def create_all_tables():
    # This will create tables defined using Base in your models.py file
    Base.metadata.create_all(bind=engine)
