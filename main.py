# from dotenv import load_dotenv
# load_dotenv()

# from rag.pipeline import ingest_blocks, query_blocks
# from structured.router import route_question
# from phase2_runner import run_phase2


# def get_blocks():
#     blocks = []
#     for i in range(1, 6):
#         print(f"\nBlock {i}")
#         t = input("Type (url/pdf/doc/xls/ppt/skip): ").lower()

#         if t == "skip":
#             blocks.append({"block_id": i, "type": None, "value": None})
#             continue

#         value = input("Enter URL or file path: ").strip()
#         blocks.append({
#             "block_id": i,
#             "type": t.upper(),
#             "value": value
#         })
#     return blocks


# blocks = get_blocks()
# store = ingest_blocks(blocks, compliance_id="c1")

# while True:
#     q = input("\nAsk a question (or exit): ")
#     if q.lower() == "exit":
#         break
#     ans = run_phase2(q, compliance_id="c1", rag_store=store)
#     print("\nANSWER:\n", ans)
    






### dynamic cli for mutiple blocks

# from dotenv import load_dotenv
# load_dotenv()

# from rag.pipeline import ingest_blocks, query_blocks
# from phase2_runner import run_phase2
# # from rag.pipeline import ingest_blocks, query_blocks
# from structured.router import route_question
# # from phase2_runner import run_phase2


# def get_blocks():
#     blocks = []
#     for i in range(1, 6):
#         print(f"\nBlock {i}")
#         t = input("Type (url/pdf/doc/xls/ppt/skip): ").lower()

#         if t == "skip":
#             blocks.append({"block_id": i, "type": None, "value": None})
#             continue

#         value = input("Enter URL or file path: ").strip()
#         blocks.append({
#             "block_id": i,
#             "type": t.upper(),
#             "value": value
#         })
#     return blocks


# blocks = get_blocks()
# store = ingest_blocks(blocks, compliance_id="c1")

# while True:
#     q = input("\nAsk a question (or exit): ")
#     if q.lower() == "exit":
#         break

#     ans = run_phase2(q, compliance_id="c1", rag_store=store)
#     print("\nANSWER:\n", ans)




from dotenv import load_dotenv
load_dotenv()

from rag.pipeline import ingest_blocks
from phase2_runner import run_phase2


# ---------------------------------------
# Detect block type automatically
# ---------------------------------------
def detect_type(value: str):
    value = value.strip()

    # URL
    if value.startswith("http://") or value.startswith("https://"):
        return "URL"

    # File extension
    ext = value.split(".")[-1].lower()

    if ext in ["pdf"]:
        return "PDF"

    if ext in ["doc", "docx"]:
        return "DOC"

    if ext in ["ppt", "pptx"]:
        return "PPT"

    if ext in ["xls", "xlsx", "csv"]:
        return "XLS"

    # Code files → treat as unstructured
    if ext in ["py", "java", "js", "ts", "cpp", "c", "cs", "go", "html", "css", "json", "xml"]:
        return "DOC"

    # Default → unstructured file
    return "DOC"


# ---------------------------------------
# Dynamic block input (Unlimited)
# ---------------------------------------
def get_blocks():
    print("\n📂 Add documents (type 'done' when finished)\n")

    blocks = []
    block_id = 1

    while True:
        value = input("Enter file path or URL: ").strip()

        if value.lower() == "done":
            break

        if not value:
            continue

        block_type = detect_type(value)

        blocks.append({
            "block_id": block_id,
            "type": block_type,
            "value": value
        })

        block_id += 1

    return blocks


# ---------------------------------------
# MAIN EXECUTION
# ---------------------------------------
if __name__ == "__main__":

    compliance_id = "c1"

    blocks = get_blocks()

    if not blocks:
        print("No documents provided.")
        exit()

    store = ingest_blocks(blocks, compliance_id=compliance_id)

    print("\n💬 Ask questions (type 'exit' to quit)\n")

    while True:
        q = input("Ask a question (or exit): ")

        if q.lower() == "exit":
            break

        ans = run_phase2(q, compliance_id=compliance_id, rag_store=store)

        print("\nANSWER:\n", ans)
