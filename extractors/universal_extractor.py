import os
import pandas as pd
from unstructured.partition.auto import partition



import uuid



def extract_text(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    # ==========================
    # EXCEL HANDLING (keep as is)
    # ==========================
    if ext in [".xlsx", ".xls"]:
        return excel_to_rag_chunks(file_path)

    # ==========================
    # PDF / DOC / PPT
    # ==========================
    # "auto" (the default) reads the text layer directly and only falls back
    # to OCR for scanned files; "hi_res" took minutes per PDF
    elements = partition(filename=file_path)

    chunks = []
    current_section = "Unknown"   # 🔥 NEW

    for el in elements:
        if not hasattr(el, "text") or not el.text:
            continue

        content = el.text.strip()

        # 🔥 Track section using Title
        if el.category == "Title":
            current_section = content

        # 🔥 Base metadata
        metadata = {
            "id": str(uuid.uuid4()),
            "section": current_section,
            "type": el.category,
            "page": el.metadata.page_number if el.metadata else None,
            "source": file_path
        }

        # ==========================
        # 🧾 TABLE HANDLING
        # ==========================
        if el.category == "Table":
            lines = content.split("\n")
            headers = lines[0].split()

            for row in lines[1:]:
                values = row.split()

                if len(values) != len(headers):
                    continue

                row_data = [
                    f"{headers[i]}: {values[i]}"
                    for i in range(len(headers))
                ]

                structured_row = " - ".join(row_data)

                chunks.append({
                    "text": f"[{structured_row}]",
                    "metadata": metadata
                })

        # ==========================
        # 📄 NORMAL TEXT
        # ==========================
        else:
            chunks.append({
                "text": content,
                "metadata": metadata
            })

    return chunks


def excel_to_facts(file_path: str) -> str:
    """
    Converts ANY Excel table into natural-language facts.
    Works for:
    - unknown schemas
    - merged cells
    - multi-row headers
    """

    df = pd.read_excel(file_path, header=None)

    # 1️⃣ Handle merged cells
    df = df.ffill().bfill()

    # 2️⃣ Detect header row
    header_row_idx = detect_header_row(df)
    df.columns = df.iloc[header_row_idx]
    df = df.drop(index=range(header_row_idx + 1))
