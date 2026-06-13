from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.modules.db import get_db
from backend.modules.models import (
    CleanCostData,
    CleanCostDataAttributes,
    CleanCostDataCorrectionsCore,
    CleanCostDataCorrectionsAttributes,
)
from backend.app.services.corrections_service import CorrectionBatch

router = APIRouter()

@router.post("/corrections")
def apply_corrections(payload: CorrectionBatch, db: Session = Depends(get_db)):
    applied = 0

    try:
        for c in payload.corrections:
            row = db.query(CleanCostData).filter(
                CleanCostData.id == c.source_row_id
            ).first()
            if not row:
                raise HTTPException(400, f"Row {c.source_row_id} not found")
            if row.file_id != c.file_id:
                raise HTTPException(400, "file_id mismatch")

            # Fields modified within core or cleancostdata
            if c.field_type == "core":
                if not c.field_name:
                    raise HTTPException(400, "field_name required for core correction")

                if not hasattr(row, c.field_name):
                    raise HTTPException(400, f"Unknown core field: {c.field_name}")

                setattr(row, c.field_name, c.new_value)

                log = CleanCostDataCorrectionsCore(
                    source_row_id=c.source_row_id,
                    file_id=c.file_id,
                    field_name=c.field_name,
                    old_value=c.old_value,
                    new_value=c.new_value,
                    user_id=c.user,
                )
                db.add(log)

            # Updating extended attribute data fields 
            elif c.field_type == "attribute":
                if not c.attribute_name:
                    raise HTTPException(400, "attribute_name required for attribute correction")
                attr = (
                    db.query(CleanCostDataAttributes)
                    .filter(
                        CleanCostDataAttributes.cost_item_id == c.source_row_id,
                        CleanCostDataAttributes.attribute_name == c.attribute_name,
                    )
                    .first()
                )
                if attr:
                    attr.attribute_value = c.new_value
                else:
                    attr = CleanCostDataAttributes(
                        cost_item_id=c.source_row_id,
                        attribute_name=c.attribute_name,
                        attribute_value=c.new_value,
                    )
                    db.add(attr)
                log = CleanCostDataCorrectionsAttributes(
                    source_row_id=c.source_row_id,
                    file_id=c.file_id,
                    attribute_name=c.attribute_name,
                    old_value=c.old_value,
                    new_value=c.new_value,
                    user_id=c.user,
                )
                db.add(log)
            else:
                raise HTTPException(400, "Invalid field_type")
            applied += 1

        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"status": "success", "applied": applied}
