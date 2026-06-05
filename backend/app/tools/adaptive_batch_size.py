
"""
Because file size is variable, adaptive batch size:
If ≤ 40 rows: one batch
If 41 to 200 rows then fixed 40
IF > 200 rows: 5% of total, min 80, max 500
"""

def get_adaptive_batch_size(total_rows: int) -> int:
    
    if total_rows <= 40:
        return total_rows

    if total_rows <= 200:
        return 15

    batch_size = int(total_rows * 0.05)
    batch_size = max(batch_size, 80)
    batch_size = min(batch_size, 500)

    return batch_size

"""
# MOVED TO A SEPERATE TOOL
# This will set the overlap the batches at about  20%
def create_overlapping_batches(rows, batch_size, overlap_ratio=0.2):
    overlap = int(batch_size * overlap_ratio)
    step = batch_size - overlap

    batches = []
    for i in range(0, len(rows), step):
        batch = rows[i:i + batch_size]
        if batch:
            batches.append(batch)

    return batches
"""


