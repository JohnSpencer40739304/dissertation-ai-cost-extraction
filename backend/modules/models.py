
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from backend.modules.db import Base

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