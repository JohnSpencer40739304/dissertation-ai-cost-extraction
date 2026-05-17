"""
Create overlapping batches of rows.
Example:
IF batch_size = 300
Then overlap_ratio = 0.2 → overlap = 60
 step = 300 - 60 = 240
"""

def create_overlapping_batches(rows, batch_size, overlap_ratio=0.2):
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    overlap = int(batch_size * overlap_ratio)
    step = batch_size - overlap


    batches = []
    for i in range(0, len(rows), step):
        batch = rows[i:i + batch_size]
        if batch:
            batches.append(batch)

    return batches
