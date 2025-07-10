import os
from datetime import datetime

def generate_po_id(file_path="last_po_id.txt"):
    current_year = datetime.now().year

    # Always read the file when generating PO ID
    if not os.path.exists(file_path):
        last_number = 0
    else:
        with open(file_path, "r") as f:
            last_po_id = f.read().strip()
            if last_po_id:
                last_year, last_number = last_po_id.split("-")
                last_year = int(last_year)
                last_number = int(last_number)
                if last_year != current_year:
                    last_number = 0
            else:
                last_number = 0

    new_number = last_number + 1

    # Update file with current year and new number
    with open(file_path, "w") as f:
        f.write(f"{current_year}-{new_number}")

    po_id = f"PO-{current_year}-{new_number:04d}"
    return po_id
