
#from sqlalchemy import Column, Integer, Float, String, Text, ForeignKey
#from sqlalchemy.dialects.postgresql import JSONB
#from sqlalchemy.orm import relationship
#from sqlalchemy import JSON
#from backend.modules.db import Base


from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    ForeignKey,
    DateTime,
    func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
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

""" Replaced below in Week 8
class CleanCostData(Base):
    __tablename__ = "clean_cost_data"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"))
    row_number = Column(Integer)
    source_format = Column(String)
    page_number = Column(Integer)
    sheet_number = Column(String)
    ai_attributes = Column(JSONB)
"""

# Week 8  modification
#class CleanCostData(Base):
#    __tablename__ = "clean_cost_data"
#    id = Column(Integer, primary_key=True, index=True)
#    file_id = Column(Integer, index=True, nullable=False)
#    sheet_name = Column(String, nullable=True)
#    table_index = Column(Integer, nullable=True)
#    row_number = Column(Integer, nullable=False)
#    ai_attributes = Column(JSONB, nullable=False)
#    confidence = Column(Float, nullable=True)


# target schema for cost data. This is the core table that all sources fit
class CleanCostData(Base):
    __tablename__ = "clean_cost_data"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, index=True, nullable=False)
    sheet_name = Column(String, nullable=True)
    table_index = Column(Integer, nullable=True)
    row_index = Column(Integer, nullable=True)
    item_description = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    quantity = Column(Float, nullable=True)
    ai_confidence_overall = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    attributes = relationship(
        "CleanCostDataAttributes",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

# extended data for all the other fields an input contains
class CleanCostDataAttributes(Base):
    __tablename__ = "clean_cost_data_attributes"

    id = Column(Integer, primary_key=True, index=True)
    cost_item_id = Column(Integer, ForeignKey("clean_cost_data.id"), nullable=False)
    attribute_name = Column(String, nullable=False)
    #attribute_value = Column(String, nullable=True)
    attribute_value = Column(JSONB, nullable=True)

    extraction_method = Column(String, nullable=True)  # deterministic / ai / ocr
    confidence_score = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("CleanCostData", back_populates="attributes")




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

# WEEK 8  save the AI normalised content
class NormalisedContent(Base):
    __tablename__ = "normalised_content"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("uploaded_files.id"), nullable=False)
    #file_id = Column(Integer, ForeignKey("uploaded_files.id", ondelete="CASCADE"), nullable=False)
    row_index = Column(Integer, nullable=False)
    attributes = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=True)
    source_format = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())



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

class CleanCostDataCorrectionsCore(Base):
    __tablename__ = "clean_cost_data_corrections_core"

    id = Column(Integer, primary_key=True, index=True)
    source_row_id = Column(Integer, ForeignKey("clean_cost_data.id"), nullable=False, index=True)
    file_id = Column(Integer, nullable=False, index=True)
    field_name = Column(String, nullable=False)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("CleanCostData")


class CleanCostDataCorrectionsAttributes(Base):
    __tablename__ = "clean_cost_data_corrections_attributes"

    id = Column(Integer, primary_key=True, index=True)
    source_row_id = Column(Integer, ForeignKey("clean_cost_data.id"), nullable=False, index=True)
    file_id = Column(Integer, nullable=False, index=True)
    attribute_name = Column(String, nullable=False)
    old_value = Column(JSONB, nullable=True)
    new_value = Column(JSONB, nullable=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("CleanCostData")

