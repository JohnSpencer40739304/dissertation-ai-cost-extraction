from sqlalchemy.orm import Session
#from .models import BatchMemory
from backend.modules.models import BatchMemory
from backend.modules.db import TableHeader

# This is a primitive RAG so that AI does not loose context during batch processing  

class MemoryStore:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    # Summary of the data so AI does not loose context
    def get_previous_summary(self, file_id: int, batch_index: int):
        if batch_index == 0:
            return None

        db: Session = self.db_session_factory()
        try:
            prev = (
                db.query(BatchMemory)
                .filter(
                    BatchMemory.file_id == file_id,
                    BatchMemory.batch_index == batch_index - 1,
                )
                .first()
            )
            return prev.summary if prev else None
        finally:
            db.close()

    def save_summary(self, file_id: int, batch_index: int, summary):
        db: Session = self.db_session_factory()
        try:
            existing = (
                db.query(BatchMemory)
                .filter(
                    BatchMemory.file_id == file_id,
                    BatchMemory.batch_index == batch_index,
                )
                .first()
            )
            if existing:
                existing.summary = summary
            else:
                mem = BatchMemory(
                    file_id=file_id,
                    batch_index=batch_index,
                    summary=summary,
                )
                db.add(mem)

            db.commit()
        finally:
            db.close()

    #Header saved to remind AI what the fields are
    def get_header(self, file_id: int, table_index: int):
        db = self.db_session_factory()
        try:
            h = (
                db.query(TableHeader)
                .filter(
                    TableHeader.file_id == file_id,
                    TableHeader.table_index == table_index
                )
                .first()
            )
            return h.header if h else None
        finally:
            db.close()

    def save_header(self, file_id: int, table_index: int, header):
        db = self.db_session_factory()
        try:
            existing = (
                db.query(TableHeader)
                .filter(
                    TableHeader.file_id == file_id,
                    TableHeader.table_index == table_index
                )
                .first()
            )
            if existing:
                existing.header = header
            else:
                db.add(TableHeader(
                    file_id=file_id,
                    table_index=table_index,
                    header=header
                ))
            db.commit()
        finally:
            db.close()


    def get_all_summaries(self, file_id: int):
        db = self.db_session_factory()
        try:
            summaries = (
                db.query(BatchMemory)
                .filter(BatchMemory.file_id == file_id)
                .order_by(BatchMemory.batch_index.asc())
                .all()
            )
            return [s.summary for s in summaries]
        finally:
            db.close()

