from sqlalchemy.orm import Session
#from .models import BatchMemory
from backend.modules.models import BatchMemory


class MemoryStore:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

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
