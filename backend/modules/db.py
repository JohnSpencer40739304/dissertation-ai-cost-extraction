#Week 2 - DB creation script - OBSOLETE IN WEEK 3
#import psycopg2
#from psycopg2.extras import RealDictCursor

#def get_connection():
#    return psycopg2.connect(
#        host="localhost",
#        database="cost_dissertation_db",
#        user="postgres",
#       password="postgres"
#    )

#--------------------------------------------------------
# WEEK 3- Extraction Scripts
# Adds extracted content to the DB - First effort tacking onto the above - did not work
#from sqlalchemy import Column, Integer, Text, JSON, DateTime, ForeignKey

#class ExtractedContent(Base):
#    __tablename__ = "extracted_content"

#    id = Column(Integer, primary_key=True, index=True)
#    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
#    raw_text = Column(Text, nullable=True)
#    raw_tables = Column(JSON, nullable=True)
#    extraction_status = Column(Text)
#    created_at = Column(DateTime)

#--------------------------------------------------------
# WEEK 3- Extraction Scripts - Complete rewrite of the above
# modules/db.py

#packages
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime


# SQLAlchemy Base and Engine
DATABASE_URL = "postgresql://postgres:postgres@localhost/cost_dissertation_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Fast API section 
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Week 2 upload file part reintegrated
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cost_dissertation_db",
        user="postgres",
        password="postgres"
    )

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    #file_name = Column(String, nullable=False) # minor week 3 correction in order to match field name in DB
    filename = Column(String, nullable=False) 
    file_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# WEEK 3 MODEL  Extracted Content
class ExtractedContent(Base):
    __tablename__ = "extracted_content"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    raw_text = Column(Text, nullable=True)
    raw_tables = Column(JSON, nullable=True)
    extraction_status = Column(String, default="success")
    created_at = Column(DateTime, default=datetime.utcnow)

# create the resulting tables
def init_db():
    Base.metadata.create_all(bind=engine)



