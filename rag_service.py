# from dotenv import load_dotenv
# load_dotenv()

# from fastapi import FastAPI, UploadFile, File, Form
# from pydantic import BaseModel
# from typing import List, Optional
# import os
# import shutil
# import uuid

# from rag.pipeline import ingest_blocks
# from phase2_runner import run_phase2
# from vectorstore.faiss_store import load_vector_store


# import asyncio

# app = FastAPI(title="RAG Engine API")

# UPLOAD_DIR = "temp_uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# # ============================
# # Request Schema for /ask
# # ============================
# class AskRequest(BaseModel):
#     compliance_id: str
#     question: str
#     chatHistory: str

# # ============================
# # Health Check
# # ============================



# # @app.post("/ingest")
# # async def ingest_documents(
# #     compliance_id: str = Form(...),
# #     files: Optional[List[UploadFile]] = File(None),
# #     urls: Optional[str] = Form(None)
# # ):
# #     blocks = []
# #     block_id = 1

# #     if files:
# #         for file in files:
# #             file_path = os.path.join(UPLOAD_DIR, file.filename)

# #             with open(file_path, "wb") as buffer:
# #                 shutil.copyfileobj(file.file, buffer)

# #             ext = file.filename.split(".")[-1].lower()

# #             if ext in ["pdf"]:
# #                 block_type = "PDF"
# #             elif ext in ["doc", "docx"]:
# #                 block_type = "DOC"
# #             elif ext in ["ppt", "pptx"]:
# #                 block_type = "PPT"
# #             elif ext in ["xls", "xlsx", "csv"]:
# #                 block_type = "XLS"
# #             else:
# #                 block_type = "DOC"

# #             blocks.append({
# #                 "block_id": block_id,
# #                 "type": block_type,
# #                 "value": file_path
# #             })

# #             block_id += 1

# #     if urls:
# #         for url in urls.split(","):
# #             url = url.strip()
# #             if url:
# #                 blocks.append({
# #                     "block_id": block_id,
# #                     "type": "URL",
# #                     "value": url
# #                 })
# #                 block_id += 1

# #     if not blocks:
# #         return {"message": "No files or URLs provided."}

# #     # ✅ Run ingestion in separate thread (fix for Playwright sync)
# #     await asyncio.to_thread(ingest_blocks, blocks, compliance_id)

# #     return {"message": "Ingestion completed successfully."}


# # ============================
# # Ingest Endpoint
# # ============================
# @app.post("/ingest")
# async def ingest_documents(
#     workspace_id: str = Form(...),
#     files: Optional[List[UploadFile]] = File(None),
#     urls: Optional[str] = Form(None)
# ):
#     blocks = []
#     block_id = 1

#     # ---- Handle file uploads ----
#     if files:
#         for file in files:

#             # Save uploaded file
#             file_path = os.path.join(UPLOAD_DIR, file.filename)

#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)

#             ext = file.filename.split(".")[-1].lower()

#             # Normalize block type
#             if ext in ["pdf"]:
#                 block_type = "PDF"
#             elif ext in ["doc", "docx"]:
#                 block_type = "DOC"
#             elif ext in ["ppt", "pptx"]:
#                 block_type = "PPT"
#             elif ext in ["xls", "xlsx", "csv"]:
#                 block_type = "XLS"
#             elif ext in ["py", "java", "js", "ts", "cpp", "c", "cs", "go", "html", "css", "json", "xml"]:
#                 block_type = "DOC"  # treat code as text
#             else:
#                 block_type = "DOC"

#             blocks.append({
#                 "block_id": block_id,
#                 "type": block_type,
#                 "value": file_path
#             })

#             block_id += 1

#     # ---- Handle URLs ----
#     if urls:
#         for url in urls.split(","):
#             url = url.strip()
#             if url:
#                 blocks.append({
#                     "block_id": block_id,
#                     "type": "URL",
#                     "value": url
#                 })
#                 block_id += 1

#     if not blocks:
#         return {"message": "No files or URLs provided."}

#     # ---- Run ingestion ----
#     try:
#         ingest_blocks(blocks, workspace_id)
#     except Exception as e:
#         return {"error": str(e)}

#     return {"message": "Ingestion completed successfully."}


# # ============================
# # Ask Endpoint
# # ============================
# @app.post("/ask")
# def ask_question(req: AskRequest):

#     embed_path = f"data/embeddings/compliance_{req.compliance_id}"

#     if not os.path.exists(embed_path):
#         return {"answer": "No knowledge base found for this workspace."}

#     try:
#         store = load_vector_store(embed_path)
#     except Exception as e:
#         return {"answer": f"Error loading vector store: {str(e)}"}

#     try:
#         full_query = f"""
#     Chat History:
#     {req.chatHistory}

#     User Question:
#     {req.question}
#     """

#         answer = run_phase2(
#             question=full_query,
#             compliance_id=req.compliance_id,
#             rag_store=store
#         )

#     except Exception as e:
#         return {"answer": f"Error generating answer: {str(e)}"}

#     return {"answer": answer}










##version 2 with workspace_id instead of compliance_id
from dotenv import load_dotenv

from processing.llm import get_llm
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import uuid   # ✅ used to generate unique ids
from fastapi.middleware.cors import CORSMiddleware

from rag.pipeline import ingest_blocks
from phase2_runner import run_phase2
from vectorstore.faiss_store import load_vector_store
from langchain_openai import ChatOpenAI
from fastapi.responses import FileResponse


from fastapi import Query
import os

import asyncio


llm =get_llm()

app = FastAPI(title="RAG Engine API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Temporary upload directory
# -------------------------------
# This folder stores uploaded files temporarily
# before they are processed into chunks and embeddings
UPLOAD_DIR = "data/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================
# Request Schema for /ask
# ============================
# NOTE: changed compliance_id → workspace_id
# because ingestion endpoint already uses workspace_id
class AskRequest(BaseModel):
    workspace_id: str
    question: str
    chatHistory: str = ""   # optional


# ============================
# Ingest Endpoint
# ============================
@app.post("/ingest")
async def ingest_documents(
    workspace_id: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    urls: Optional[str] = Form(None)
):
    blocks = []

    # --------------------------------------------------
    # FIX: block_id previously started from 1 each time
    # which caused chunk files to overwrite each other
    # Now we generate a unique block id
    # --------------------------------------------------
   

    saved_files = []  # keep track so we can delete them later

    # ---- Handle file uploads ----
    if files:
        for file in files:
            
            block_id = uuid.uuid4().hex
            # --------------------------------------------------
            # FIX: create unique filename to prevent overwrite
            # --------------------------------------------------
            unique_name = f"{uuid.uuid4().hex}_{file.filename}"
            #file_path = os.path.join(UPLOAD_DIR, unique_name)

            workspace_dir = f"{UPLOAD_DIR}/compliance_{workspace_id}"
            os.makedirs(workspace_dir, exist_ok=True)

            file_path = os.path.join(workspace_dir, unique_name)






            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_files.append(file_path)

            ext = file.filename.split(".")[-1].lower()

            # Normalize block type
            if ext in ["pdf"]:
                block_type = "PDF"
            elif ext in ["doc", "docx"]:
                block_type = "DOC"
            elif ext in ["ppt", "pptx"]:
                block_type = "PPT"
            elif ext in ["xls", "xlsx", "csv"]:
                block_type = "XLS"
            elif ext in ["py", "java", "js", "ts", "cpp", "c", "cs", "go", "html", "css", "json", "xml"]:
                block_type = "DOC"  # treat code as text
            else:
                block_type = "DOC"

            # --------------------------------------------------
            # Add document to ingestion blocks
            # --------------------------------------------------
            blocks.append({
                "block_id": block_id,
                "type": block_type,
                "value": file_path
            })


    # ---- Handle URLs ----
    if urls:
        for url in urls.split(","):
            url = url.strip()
            if url:
                blocks.append({
                    "block_id": uuid.uuid4().hex,  # unique block id for each url
                    "type": "URL",
                    "value": url
                })


    if not blocks:
        return {"message": "No files or URLs provided."}

    # ---- Run ingestion ----
    try:
        # --------------------------------------------------
        # This function performs:
        # chunking
        # embedding generation
        # storing into FAISS vector store
        # --------------------------------------------------
        print("🚀 Starting ingestion...")

        for block in blocks:
            print("Processing:", block["value"])
            ingest_blocks([block], workspace_id)

        print("✅ All files processed")
    except Exception as e:
        return {"error": str(e)}

    # --------------------------------------------------
    # CLEANUP: delete temporary uploaded files
    # This keeps temp_uploads folder from growing forever
    # --------------------------------------------------
    #for path in saved_files:
     #   if os.path.exists(path):
      #      os.remove(path)

    return {"message": "Ingestion completed successfully."}


# ============================
# Ask Endpoint
# ============================



# @app.post("/ask")
# def ask_question(req: AskRequest):

#     embed_path = f"data/embeddings/compliance_{req.compliance_id}"

#     if not os.path.exists(embed_path):
#         return {"answer": "No knowledge base found for this workspace."}

#     try:
#         store = load_vector_store(embed_path)
#     except Exception as e:
#         return {"answer": f"Error loading vector store: {str(e)}"}

#     try:
#         full_query = f"""
#     Chat History:
#     {req.chatHistory}

#     User Question:
#     {req.question}
#     """

#         answer = run_phase2(
#             question=full_query,
#             compliance_id=req.compliance_id,
#             rag_store=store
#         )

#     except Exception as e:
#         return {"answer": f"Error generating answer: {str(e)}"}

#     return {"answer": answer}




# def rewrite_query(question, history):

#     if not history:
#         return question

#     prompt = f"""
# Rewrite the following follow-up question into a standalone question.

# Conversation:
# {history}

# Follow-up Question:
# {question}

# Rewritten standalone question:
# """

#     try:
#         response = llm.invoke(prompt)   # your LLM (same as used in pipeline)
#         return response.content.strip()
#     except:
#         return question

def rewrite_query(question, history):

    if not history:
        return question

    prompt = f"""
Rewrite the follow-up question into a standalone question.

Conversation:
{history}

Follow-up Question:
{question}

Standalone Question:
"""

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print("Rewrite error:", e)
        return question


# @app.post("/ask")
# def ask_question(req: AskRequest):

#     workspace = req.workspace_id

#     embed_path = f"data/embeddings/compliance_{workspace}"

#     if not os.path.exists(embed_path):
#         return {"answer": "No knowledge base found for this workspace."}

#     try:
#         store = load_vector_store(embed_path)
#     except Exception as e:
#         return {"answer": f"Error loading vector store: {str(e)}"}

#     try:
#         rewritten_question = rewrite_query(req.question, req.chatHistory)

#         answer = run_phase2(
#             question=rewritten_question,   # ✅ FIXED
#             compliance_id=workspace,
#             rag_store=store
#         )

#     except Exception as e:
#         return {"answer": f"Error generating answer: {str(e)}"}

#     return {"answer": answer}
@app.post("/ask")
def ask_question(req: AskRequest):

    workspace = req.workspace_id

    embed_path = f"data/embeddings/compliance_{workspace}"

    if not os.path.exists(embed_path):
        return {"answer": "No knowledge base found for this workspace."}

    store = load_vector_store(embed_path)

    # ✅ ADD THIS LINE
    rewritten_question = rewrite_query(req.question, req.chatHistory)

    print("Original:", req.question)
    print("Rewritten:", rewritten_question)

    answer = run_phase2(
        question=rewritten_question,   # ✅ USE REWRITTEN
        compliance_id=workspace,
        rag_store=store
    )

    return {"answer": answer}

# @app.post("/ask")
# def ask_question(req: AskRequest):

#     embed_path = f"data/embeddings/compliance_{req.workspace_id}"

#     if not os.path.exists(embed_path):
#         return {"answer": "No knowledge base found for this workspace."}

#     try:
#         store = load_vector_store(embed_path)

#     except Exception as e:
#         return {"answer": f"Error loading vector store: {str(e)}"}

#     # DEBUG CHECK
#     docs = store.docstore._dict.values()

#     for doc in docs:
#         if doc.metadata.get("source") is None:
#             print("⚠️ BAD DOCUMENT:", doc.metadata)

#     try:

#         # -------- conversational query expansion --------
#         history_text = req.chatHistory or ""

#         last_context = ""
#         if history_text:
#             lines = history_text.split("\n")
#             if len(lines) > 0:
#                 last_context = lines[-1]

#         question_lower = req.question.lower()

#         reference_words = [" it ", " they ", " them ", " those ", " that ", " these "]

#         expanded_question = req.question

#         if any(w in f" {question_lower} " for w in reference_words):
#             expanded_question = last_context + " " + req.question


#         # -------- run RAG pipeline --------
#         answer = run_phase2(
#             question=expanded_question,
#             compliance_id=req.workspace_id,
#             rag_store=store
#         )

#     except Exception as e:
#         return {"answer": f"Error generating answer: {str(e)}"}

#     return {"answer": answer}


@app.get("/documents/{workspace_id}")
def list_documents(workspace_id: str):

    embed_path = f"data/embeddings/compliance_{workspace_id}"

    if not os.path.exists(embed_path):
        return {"documents": []}

    try:
        store = load_vector_store(embed_path)
    except Exception as e:
        return {"error": str(e)}

    docs = store.docstore._dict.values()

    unique_docs = {}

    for doc in docs:

        metadata = doc.metadata

        block_id = metadata.get("block_id")
        source = metadata.get("source")
        doc_type = metadata.get("type")

        if block_id not in unique_docs:
            unique_docs[block_id] = {
                "block_id": block_id,
                "name": os.path.basename(source),
                "type": doc_type,
                "source": source
            }

    return {"documents": list(unique_docs.values())}





# @app.delete("/documents/{workspace_id}/{block_id}")
# def delete_document(workspace_id: str, block_id: str):

#     embed_path = f"data/embeddings/compliance_{workspace_id}"

#     if not os.path.exists(embed_path):
#         return {"message": "Workspace not found"}

#     store = load_vector_store(embed_path)

#     docs = store.docstore._dict

#     ids_to_delete = []

#     for doc_id, doc in docs.items():

#         metadata = doc.metadata

#         if metadata.get("block_id") == block_id:
#             ids_to_delete.append(doc_id)

#     if not ids_to_delete:
#         return {"message": "Document not found"}

#     # remove from FAISS
#     store.delete(ids_to_delete)

#     store.save_local(embed_path)

#     # remove chunk file
#     chunk_dir = f"data/chunks/compliance_{workspace_id}"

#     for file in os.listdir(chunk_dir):

#         if block_id in file:
#             os.remove(os.path.join(chunk_dir, file))

#     return {"message": "Document deleted successfully"}


@app.delete("/documents/{workspace_id}/{block_id}")
def delete_document(workspace_id: str, block_id: str):

    embed_path = f"data/embeddings/compliance_{workspace_id}"

    if not os.path.exists(embed_path):
        return {"message": "Workspace not found"}

    store = load_vector_store(embed_path)

    docs = store.docstore._dict

    ids_to_delete = []
    file_path = None   # ← will store original file path

    for doc_id, doc in docs.items():

        metadata = doc.metadata

        if metadata.get("block_id") == block_id:

            ids_to_delete.append(doc_id)

            # capture original file path (only once)
            if file_path is None:
                file_path = metadata.get("source")

    if not ids_to_delete:
        return {"message": "Document not found"}

    # remove from FAISS
    store.delete(ids_to_delete)

    store.save_local(embed_path)

    # remove chunk file
    chunk_dir = f"data/chunks/compliance_{workspace_id}"

    if os.path.exists(chunk_dir):
        for file in os.listdir(chunk_dir):

            if block_id in file:
                os.remove(os.path.join(chunk_dir, file))

    # remove original uploaded file
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    return {"message": "Document deleted successfully"}





@app.get("/document/open")
def open_document(path: str = Query(...)):

    if not os.path.exists(path):
        return {"error": "File not found"}

    return FileResponse(
        path,
        media_type="application/pdf",
        
    )






@app.get("/documents/{workspace_id}/{block_id}/open")
def open_document(workspace_id: str, block_id: str):

    embed_path = f"data/embeddings/compliance_{workspace_id}"

    if not os.path.exists(embed_path):
        return {"error": "Workspace not found"}

    store = load_vector_store(embed_path)

    docs = store.docstore._dict.values()

    for doc in docs:

        metadata = doc.metadata

        if metadata.get("block_id") == block_id:

            file_path = metadata.get("source")

            if os.path.exists(file_path):

                return FileResponse(
                    file_path,
                    media_type="application/pdf",
                    filename=os.path.basename(file_path)
                )

    return {"error": "Document not found"}