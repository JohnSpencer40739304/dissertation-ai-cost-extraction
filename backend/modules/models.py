
from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
#from sqlalchemy import JSON
from backend.modules.db import Base



""" # Original Versions
class CleanCostData(Base):
    __tablename__ = "clean_cost_data"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    row_number = Column(Integer)

    # Classic pricing cleaned fields (may not be detected)
    description = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    currency = Column(String)

    # Dates (all set to ISO)
    start_date = Column(String)
    end_date = Column(String)
    renewal_date = Column(String)

    # AI-enriched attributes - attributes that might be used for rating
    ai_attributes = Column(JSONB)

    # Metadata to ensure we can trace data back to the source
    source_format = Column(String)
    page_number = Column(Integer)
"""

"""
class CleanCostData(Base):
    __tablename__ = "clean_cost_data"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    source_format = Column(String, nullable=True)
    page_number = Column(Integer, nullable=True)
    sheet_number = Column(String, nullable=True)
    ai_attributes = Column(JSONB, nullable=True)
"""

class CleanCostData(Base):
    __tablename__ = "clean_cost_data"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    row_number = Column(Integer)
    source_format = Column(String)
    page_number = Column(Integer)
    sheet_number = Column(String)
    ai_attributes = Column(JSONB)


# Below is a simple RAG using PostgreSQL for batch processing of extracted files to normalise them via AI
class BatchMemory(Base):
    __tablename__ = "batch_memory"

    id = Column(Integer, primary_key=True, index=True)
    #file_id = Column(In teger, ForeignKey("files.id"), index=True, nullable=False) # correction to filename
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), index=True, nullable=False)
    
    batch_index = Column(Integer, nullable=False)  
    summary = Column(JSONB, nullable=True) 

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )




"""

#Example below of predefine file structure. This won't be our case. 

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.modules.db import Base

class CleanCostData(Base):
    __tablename__ = "clean_cost_data"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    row_number = Column(Integer)

    description = Column(String)
    category = Column(String)
    material = Column(String)
    dimensions = Column(String)
    weight = Column(Float)

    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    discount = Column(Float)
    currency = Column(String)

    source_format = Column(String)
    page_number = Column(Integer)
"""