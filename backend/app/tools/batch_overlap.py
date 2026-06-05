"""
Create overlapping batches of rows.
Example:
IF batch_size = 300
Then overlap_ratio = 0.2 → overlap = 60
 step = 300 - 60 = 240
"""

#def create_overlapping_batches(rows, batch_size, overlap_ratio=0.2):
#    if batch_size <= 0:
#        raise ValueError("batch_size must be > 0")

#    overlap = int(batch_size * overlap_ratio)
#    step = batch_size - overlap


#    batches = []
#    for i in range(0, len(rows), step):
#        batch = rows[i:i + batch_size]
#        if batch:
#            batches.append(batch)

#    return batches


# Overlap fails to return all records when batch size is too small
def create_overlapping_batches(rows, batch_size, overlap_ratio=0.2):
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    # Dynamic overlap rules
    if batch_size <= 10:
        overlap = 5
    elif batch_size <= 20:
        overlap = 4
    elif batch_size <= 40:
        overlap = 3
    else:
        overlap = int(batch_size * overlap_ratio)

    # Ensure overlap is never zero
    overlap = max(overlap, 2)

    step = batch_size - overlap

    batches = []
    for i in range(0, len(rows), step):
        batch = rows[i:i + batch_size]
        if batch:
            batches.append(batch)

    return batches

