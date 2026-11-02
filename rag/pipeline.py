# import os

# # ===== Existing loaders (DO NOT REMOVE) =====
# from loaders.url_loader import load_url
# from loaders.file_loader import download_file

# # ===== New browser-based loader (ADDED) =====
# from loaders.url_loader_browser import load_url_with_browser

# from extractors.universal_extractor import extract_text
# from extractors.excel_metadata_extractor import extract_excel_metadata

# from processing.chunker import chunk_text
# from processing.embedder import get_embedder
# from processing.llm import get_llm

# from vectorstore.faiss_store import create_vector_store, load_vector_store
# from rag.prompt import build_prompt
# from structured.store import save_structured_file


# # =============================
# # 🔧 CONFIG
# # =============================
# USE_BROWSER = True   # ✅ Toggle safely (True = Playwright, False = old loader)

# BASE_CHUNK_DIR = "data/chunks"
# BASE_EMBED_DIR = "data/embeddings"



# import hashlib
# import re




# # =============================
# # 🧩 Helper: Save Chunks
# # =============================
# def save_chunks(compliance_id, block_id, source_name, chunks):
#     os.makedirs(f"{BASE_CHUNK_DIR}/compliance_{compliance_id}", exist_ok=True)
    

#     file_path = (
#         f"{BASE_CHUNK_DIR}/compliance_{compliance_id}/"
#         f"block_{block_id}_{source_name}.txt"
#     )

#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(f"COMPLIANCE ID: {compliance_id}\n")
#         f.write(f"BLOCK ID: {block_id}\n")
#         f.write(f"SOURCE: {source_name}\n")
#         f.write("=" * 50 + "\n\n")

#         for i, chunk in enumerate(chunks, 1):
#             f.write(f"[CHUNK {i}]\n{chunk}\n\n")


# # =============================
# # 🧠 INGEST BLOCKS
# # =============================
# def ingest_blocks(blocks, compliance_id):
#     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"

#     # ✅ Reuse embeddings if present
#     if os.path.exists(f"{embed_path}/index.faiss"):
#         print("✔ Loading existing embeddings (no OpenAI cost)")
#         return load_vector_store(embed_path)

#     print("⏳ Creating embeddings...")

#     all_chunks = []
#     all_metadata = []

#     for block in blocks:
#         if not block.get("type"):
#             continue

#         block_type = block["type"].upper()
#         block_id = block["block_id"]
#         value = block["value"]

#         # ==================================================
#         # 📊 STRUCTURED FILES (EXCEL / CSV / GSHEET)
#         # ==================================================
#         if block_type in ["XLS", "XLSX", "CSV", "GSHEET"]:
#             # 1️⃣ Save for NLQ (structured)
#             save_structured_file(block, compliance_id)

#             # 2️⃣ Extract metadata / merged headers → RAG
#             try:
#                 metadata_text = extract_excel_metadata(value)
#             except Exception as e:
#                 print("[EXCEL METADATA ERROR]", e)
#                 continue

#             if metadata_text and metadata_text.strip():
#                 meta_chunks = chunk_text(metadata_text)
#                 source_name = (
#                     os.path.basename(value).replace(".", "_") + "_metadata"
#                 )

#                 save_chunks(compliance_id, block_id, source_name, meta_chunks)

#                 for c in meta_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "block_id": block_id,
#                         "source": value,
#                         "type": "excel_metadata"
#                     })

#             # 🚫 DO NOT fall through to unstructured handling
#             continue

#         # ==================================================
#         # 🌐 URL INGESTION (SAFE HYBRID)
#         # ==================================================
#         if block_type == "URL":
#             if USE_BROWSER:
#                 page_text, downloaded_docs = load_url_with_browser(value)
#             else:
#                 page_text, downloaded_docs = load_url(value)

#             # Page text → chunks
#             page_chunks = chunk_text(page_text)
#             save_chunks(compliance_id, block_id, "url_page", page_chunks)

#             for c in page_chunks:
#                 all_chunks.append(c)
#                 all_metadata.append({
#                     "compliance_id": compliance_id,
#                     "block_id": block_id,
#                     "source": value,
#                     "type": "url_page"
#                 })

#             # Downloaded docs (PDF / XLS / PPT etc.)
#             for path in downloaded_docs:
#                 try:
#                     text = extract_text(path)
#                 except Exception as e:
#                     print("[DOC EXTRACT ERROR]", e)
#                     continue

#                 doc_chunks = chunk_text(text)
#                 name = os.path.basename(path).replace(".", "_")

#                 save_chunks(compliance_id, block_id, name, doc_chunks)

#                 for c in doc_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "block_id": block_id,
#                         "source": path,
#                         "type": "url_document"
#                     })

#             continue

#         # ==================================================
#         # 📄 PDF / DOC / PPT (UNSTRUCTURED)
#         # ==================================================
#         try:
#             text = extract_text(value)
#         except Exception as e:
#             print("[FILE EXTRACT ERROR]", e)
#             continue

#         chunks = chunk_text(text)
#         name = os.path.basename(value).replace(".", "_")

#         save_chunks(compliance_id, block_id, name, chunks)

#         for c in chunks:
#             all_chunks.append(c)
#             all_metadata.append({
#                 "compliance_id": compliance_id,
#                 "block_id": block_id,
#                 "source": value,
#                 "type": "unstructured"
#             })

#     # ==================================================
#     # 🚫 No RAG content
#     # ==================================================
#     if not all_chunks:
#         print("ℹ No unstructured documents found. Skipping vector store creation.")
#         return None

#     # ==================================================
#     # 🧠 Create Vector Store
#     # ==================================================
#     embedder = get_embedder()
#     store = create_vector_store(all_chunks, all_metadata, embedder)

#     os.makedirs(embed_path, exist_ok=True)
#     store.save_local(embed_path)

#     print("✅ Embeddings saved locally")
#     return store


# # =============================
# # 🔍 QUERY UNSTRUCTURED (RAG)
# # =============================
# #1. 
# def query_blocks(store, question, compliance_id):
#     if store is None:
#         return "No unstructured documents available for this compliance."

#     # 1️⃣ Primary retrieval
#     docs = store.similarity_search(
#         question,
#         k=10,
#         filter={"compliance_id": compliance_id}
#     )

#     # 2️⃣ If nothing found, try semantic fallback
#     if not docs:
#         semantic_fallback = f"{question} related information"
#         docs = store.similarity_search(
#             semantic_fallback,
#             k=10,
#             filter={"compliance_id": compliance_id}
#         )

#     if not docs:
#         return "Not found in provided documents."

#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)
#     llm = get_llm()

#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found in provided documents."






























# ##############################
# import os

# # Loaders
# from loaders.url_loader import load_url
# from loaders.file_loader import download_file
# from loaders.url_loader_browser import load_url_with_browser

# # Extractors
# from extractors.universal_extractor import extract_text
# from extractors.excel_metadata_extractor import extract_excel_metadata

# # Processing
# from processing.chunker import chunk_text
# from processing.embedder import get_embedder
# from processing.llm import get_llm

# # Vector store
# from vectorstore.faiss_store import create_vector_store, load_vector_store

# # Prompt
# from rag.prompt import build_prompt

# # Structured storage
# from structured.store import save_structured_file


# # =============================
# # CONFIG
# # =============================
# USE_BROWSER = True
# BASE_CHUNK_DIR = "data/chunks"
# BASE_EMBED_DIR = "data/embeddings"


# # =============================
# # Save chunks to disk
# # =============================
# def save_chunks(compliance_id, block_id, source_name, chunks):
#     os.makedirs(f"{BASE_CHUNK_DIR}/compliance_{compliance_id}", exist_ok=True)

#     file_path = (
#         f"{BASE_CHUNK_DIR}/compliance_{compliance_id}/"
#         f"block_{block_id}_{source_name}.txt"
#     )

#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(f"COMPLIANCE ID: {compliance_id}\n")
#         f.write(f"BLOCK ID: {block_id}\n")
#         f.write(f"SOURCE: {source_name}\n")
#         f.write("=" * 50 + "\n\n")

#         for i, chunk in enumerate(chunks, 1):
#             f.write(f"[CHUNK {i}]\n{chunk}\n\n")


# # =============================
# # INGESTION
# # =============================
# def ingest_blocks(blocks, compliance_id):
#     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"

#     # Reuse embeddings if present
#     if os.path.exists(f"{embed_path}/index.faiss"):
#         print("✔ Loading existing embeddings (no OpenAI cost)")
#         return load_vector_store(embed_path)

#     print("⏳ Creating embeddings...")

#     all_chunks = []
#     all_metadata = []

#     for block in blocks:
#         if not block.get("type"):
#             continue

#         block_type = block["type"].upper()
#         block_id = block["block_id"]
#         value = block["value"]

#         # ========================================
#         # STRUCTURED FILES (EXCEL / CSV / GSHEET)
#         # ========================================
#         if block_type in ["XLS", "XLSX", "CSV", "GSHEET"]:
#             # Save structured copy for Phase-2 NLQ
#             save_structured_file(block, compliance_id)

#             # Extract metadata text for RAG
#             try:
#                 metadata_text = extract_excel_metadata(value)
#             except Exception as e:
#                 print("[EXCEL METADATA ERROR]", e)
#                 continue

#             if metadata_text.strip():
#                 meta_chunks = chunk_text(metadata_text)
#                 source_name = os.path.basename(value).replace(".", "_") + "_metadata"

#                 save_chunks(compliance_id, block_id, source_name, meta_chunks)

#                 for c in meta_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "block_id": block_id,
#                         "source": value,
#                         "type": "excel_metadata"
#                     })

#             continue

#         # ========================================
#         # URL INGESTION
#         # ========================================
#         if block_type == "URL":
#             if USE_BROWSER:
#                 page_text, downloaded_docs = load_url_with_browser(value)
#             else:
#                 page_text, downloaded_docs = load_url(value)

#             # Page text
#             page_chunks = chunk_text(page_text)
#             save_chunks(compliance_id, block_id, "url_page", page_chunks)

#             for c in page_chunks:
#                 all_chunks.append(c)
#                 all_metadata.append({
#                     "compliance_id": compliance_id,
#                     "block_id": block_id,
#                     "source": value,
#                     "type": "url_page"
#                 })

#             # Downloaded documents from URL
#             for path in downloaded_docs:
#                 try:
#                     text = extract_text(path)
#                 except Exception as e:
#                     print("[DOC EXTRACT ERROR]", e)
#                     continue

#                 doc_chunks = chunk_text(text)
#                 name = os.path.basename(path).replace(".", "_")

#                 save_chunks(compliance_id, block_id, name, doc_chunks)

#                 for c in doc_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "block_id": block_id,
#                         "source": path,
#                         "type": "url_document"
#                     })

#             continue

#         # ========================================
#         # FILE INGESTION (PDF / DOC / PPT)
#         # ========================================
#         try:
#             text = extract_text(value)
#         except Exception as e:
#             print("[FILE EXTRACT ERROR]", e)
#             continue

#         chunks = chunk_text(text)
#         name = os.path.basename(value).replace(".", "_")

#         save_chunks(compliance_id, block_id, name, chunks)

#         for c in chunks:
#             all_chunks.append(c)
#             all_metadata.append({
#                 "compliance_id": compliance_id,
#                 "block_id": block_id,
#                 "source": value,
#                 "type": "unstructured"
#             })

#     # ========================================
#     # Create Vector Store
#     # ========================================
#     if not all_chunks:
#         print("ℹ No RAG content found.")
#         return None

#     embedder = get_embedder()
#     store = create_vector_store(all_chunks, all_metadata, embedder)

#     os.makedirs(embed_path, exist_ok=True)
#     store.save_local(embed_path)

#     print("✅ Embeddings saved locally")
#     return store


# # =============================
# # QUERY
# # =============================
# def query_blocks(store, question, compliance_id):
#     if store is None:
#         return "No unstructured documents available."

#     docs = store.similarity_search(
#         question,
#         k=5,
#         filter={"compliance_id": compliance_id}
#     )

#     if not docs:
#         return "Not found in provided documents."

#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)
#     llm = get_llm()

#     answer = llm.invoke(prompt).content.strip()
#     return answer if answer else "Not found in provided documents."




































import os

# ===== Existing loaders =====
from loaders.url_loader import load_url
from loaders.file_loader import download_file
from loaders.url_loader_browser import load_url_with_browser

from extractors.universal_extractor import extract_text

from processing import embedder
from processing.chunker import chunk_text
from processing.embedder import get_embedder
from processing.llm import get_llm

from vectorstore.faiss_store import create_vector_store, load_vector_store
from rag.prompt import build_prompt

from structured.store import save_structured_file

# ✅ NEW IMPORTS
from extractors.excel_semantic_extractor import excel_semantic_extractor
from processing.numeric_aggregator import numeric_aggregate
from processing.hybrid_retriever import load_all_chunks, bm25_search



# =============================
# CONFIG
# =============================
USE_BROWSER = True

BASE_CHUNK_DIR = "data/chunks"
BASE_EMBED_DIR = "data/embeddings"

















#### intent aware rewriting  start



def rewrite_query_for_retrieval(question: str, llm) -> str:
    """
    Rewrite the user question into multiple semantically equivalent
    search-style queries to improve document retrieval.
    This is retrieval-focused, NOT answering-focused.
    """

    prompt = f"""
You are helping a search engine retrieve documents.

Rewrite the user question into 2-3 alternative search queries
that might match how the same information is written in documents.

Do NOT answer the question.
Do NOT add new facts.
Only rewrite for retrieval.

User question:
{question}

Return the rewritten queries in one line.
"""

    rewritten = llm.invoke(prompt).content.strip()

    # Combine original + rewritten for broader semantic match
    return question + " " + rewritten




# def rewrite_query_for_retrieval(question: str, llm) -> str:
#     """
#     Rewrite the user question into alternative search-style queries
#     to improve document retrieval.
#     """
#     prompt = f"""
# You are helping a search engine retrieve documents.

# Rewrite the user question into 2-3 alternative search queries
# that might match how the same information is written in documents.

# Do NOT answer the question.
# Return only the rewritten search queries.

# User question:
# {question}
# """

#     try:
#         rewritten = llm.invoke(prompt).content.strip()
#         return question + " " + rewritten
#     except:
#         # fallback if LLM fails
#         return question

#### intent aware rewriting end


#### rerank start
def rerank_documents(question: str, docs: list, llm, top_n: int = 6):
    """
    LLM-based reranking of retrieved documents.
    Improves precision without changing ingestion or embeddings.
    """
    scored = []

    for doc in docs:
        prompt = f"""
Rate how well the following passage answers the question.

Question:
{question}

Passage:
{doc.page_content}

Score relevance from 0 to 10.
Return ONLY the number.
"""
        try:
            score = float(llm.invoke(prompt).content.strip())
        except:
            score = 0.0

        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_n]]




# def rerank_documents(question: str, docs: list, llm, top_n: int = 6):
#     """
#     LLM-based reranking of retrieved documents.
#     Uses batch scoring to reduce latency.
#     """

#     passages = "\n\n".join(
#         [f"Passage {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)]
#     )

#     prompt = f"""
# You are ranking document passages for relevance.

# Question:
# {question}

# Below are passages retrieved from documents.

# {passages}

# Return the passage numbers sorted from MOST relevant to LEAST relevant.
# Example output:
# 3,1,5,2,4
# Only return numbers separated by commas.
# """

#     try:
#         result = llm.invoke(prompt).content.strip()

#         order = [int(x.strip()) - 1 for x in result.split(",") if x.strip().isdigit()]

#         ranked = [docs[i] for i in order if i < len(docs)]

#         return ranked[:top_n]

#     except:
#         return docs[:top_n]

#### rerank end














# =============================
# Save Chunks
# =============================
def save_chunks(compliance_id, block_id, source_name, chunks):
    os.makedirs(f"{BASE_CHUNK_DIR}/compliance_{compliance_id}", exist_ok=True)

    file_path = (
        f"{BASE_CHUNK_DIR}/compliance_{compliance_id}/"
        f"block_{block_id}_{source_name}.txt"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks, 1):
            f.write(f"[CHUNK {i}]\n{chunk}\n\n")


# =============================
# Chunk extracted elements
# =============================
def chunk_elements(elements):
    """
    extract_text() returns a list of {"text", "metadata"} elements.
    Group consecutive elements of the same section and page, then
    chunk each group so every chunk keeps its section/page metadata.
    Small neighbouring groups are packed together so short headings
    don't become tiny chunks of their own.
    Returns (chunks, metadatas).
    """
    groups = []
    for el in elements:
        meta = el["metadata"]
        key = (meta.get("section"), meta.get("page"))
        if groups and groups[-1]["key"] == key:
            groups[-1]["texts"].append(el["text"])
            groups[-1]["types"].append(meta.get("type"))
        else:
            groups.append({
                "key": key,
                "texts": [el["text"]],
                "types": [meta.get("type")],
                "metadata": meta
            })

    # pack small groups up to the chunk size (800, see processing/chunker.py);
    # a packed group keeps the section/page of its first part
    packed = []
    for g in groups:
        size = sum(len(t) for t in g["texts"])
        if packed and packed[-1]["size"] + size < CHUNK_SIZE:
            packed[-1]["texts"] += g["texts"]
            packed[-1]["types"] += g["types"]
            packed[-1]["size"] += size
        else:
            packed.append({**g, "size": size})
    groups = packed

    chunks = []
    metadatas = []
    for g in groups:
        section = g["metadata"].get("section") or "Unknown"
        # the heading itself is a Title; describe the group by its body
        body_types = [t for t in g["types"] if t != "Title"]
        content_type = body_types[0] if body_types else "Title"

        for piece in chunk_text("\n".join(g["texts"])):
            # a heading split off on its own adds nothing: it is prefixed below
            if piece.strip() == section and len(g["texts"]) > 1:
                continue
            # prefix the section title so the chunk carries its own context
            if section != "Unknown" and not piece.startswith(section):
                piece = f"{section}\n{piece}"
            chunks.append(piece)
            metadatas.append({
                "section": section,
                "page": g["metadata"].get("page"),
                "content_type": content_type,
            })

    return chunks, metadatas


EXCEL_EXTENSIONS = (".xlsx", ".xls", ".csv")
CHUNK_SIZE = 800


# =============================
# INGEST BLOCKS
# =============================
def ingest_blocks(blocks, compliance_id):
    embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"
    store = None
    # Reuse embeddings if already exist
    if os.path.exists(f"{embed_path}/index.faiss"):
        print("✔ Loading existing embeddings (no OpenAI cost)")
        store = load_vector_store(embed_path)

    print("⏳ Creating embeddings...")

    all_chunks = []
    all_metadata = []

    for block in blocks:
        if not block.get("type"):
            continue

        block_type = block["type"].upper()
        block_id = block["block_id"]
        value = block["value"]

        # ==================================================
        # 📊 EXCEL / CSV / GSHEET → SEMANTIC ROW EXTRACTION
        # ==================================================
        if block_type in ["XLS", "XLSX", "CSV", "GSHEET"]:

            # Save original file
            save_structured_file(block, compliance_id)

            # 🔹 Extract semantic row chunks
            row_chunks, row_metadata = excel_semantic_extractor(value)

            # Save chunk text (debug)
            save_chunks(compliance_id, block_id, "excel_rows", row_chunks)

            # Add into vector store
            for chunk, meta in zip(row_chunks, row_metadata):
                all_chunks.append(chunk)
                all_metadata.append({
                    "compliance_id": compliance_id,
                    "block_id": block_id,
                    "source": value,
                    "type": "excel_row",
                    "numeric": meta["numeric"]
                })

            continue

        # ==================================================
        # 🌐 URL INGESTION
        # ==================================================
        if block_type == "URL":
            if USE_BROWSER:
                page_text, downloaded_docs = load_url_with_browser(value)
            else:
                page_text, downloaded_docs = load_url(value)

            page_chunks = chunk_text(page_text)
            save_chunks(compliance_id, block_id, "url_page", page_chunks)

            for c in page_chunks:
                all_chunks.append(c)
                all_metadata.append({
                    "compliance_id": compliance_id,
                    "block_id": block_id,
                    "source": value,
                    "type": "url_page"
                })

            for path in downloaded_docs:
                name = os.path.basename(path).replace(".", "_")

                # Spreadsheets linked from the page use the row extractor
                if path.lower().endswith(EXCEL_EXTENSIONS):
                    try:
                        row_chunks, row_metadata = excel_semantic_extractor(path)
                    except Exception as e:
                        print("[DOC EXTRACT ERROR]", e)
                        continue

                    save_chunks(compliance_id, block_id, name, row_chunks)

                    for chunk, meta in zip(row_chunks, row_metadata):
                        all_chunks.append(chunk)
                        all_metadata.append({
                            "compliance_id": compliance_id,
                            "block_id": block_id,
                            "source": path,
                            "type": "excel_row",
                            "numeric": meta["numeric"]
                        })
                    continue

                try:
                    elements = extract_text(path)
                except Exception as e:
                    print("[DOC EXTRACT ERROR]", e)
                    continue

                doc_chunks, doc_metadata = chunk_elements(elements)
                save_chunks(compliance_id, block_id, name, doc_chunks)

                for c, meta in zip(doc_chunks, doc_metadata):
                    all_chunks.append(c)
                    all_metadata.append({
                        "compliance_id": compliance_id,
                        "block_id": block_id,
                        "source": path,
                        **meta,
                        "type": "url_document"
                    })

            continue

        # ==================================================
        # 📄 PDF / DOC / PPT
        # ==================================================
        try:
            elements = extract_text(value)
        except Exception as e:
            print("[FILE EXTRACT ERROR]", e)
            continue

        chunks, chunk_metadata = chunk_elements(elements)
        name = os.path.basename(value).replace(".", "_")
        save_chunks(compliance_id, block_id, name, chunks)

        for c, meta in zip(chunks, chunk_metadata):
            all_chunks.append(c)
            all_metadata.append({
                "compliance_id": compliance_id,
                "block_id": block_id,
                "source": value,
                # 🔥 NEW METADATA (section, page, content_type)
                **meta,
                "type": "unstructured"
            })

    # ==================================================
    # CREATE VECTOR STORE
    # ==================================================
    if not all_chunks:
        print("No content found.")
        return None

    embedder = get_embedder()
    # If embeddings already exist → append
    if store is not None:
        print("➕ Adding new documents to existing vector store")
        store.add_texts(all_chunks, all_metadata)

    else:
        print("🆕 Creating new vector store")
        store = create_vector_store(all_chunks, all_metadata, embedder)

    os.makedirs(embed_path, exist_ok=True)
    store.save_local(embed_path)

    print("✅ Embeddings saved locally")
    return store


# =============================
# QUERY BLOCKS (HYBRID RAG) 1)
# =============================
# def query_blocks(store, question, compliance_id):
#     if store is None:
#         return "No documents available."



#     #### intent aware rewriting start
#     llm = get_llm()
    
#     rewritten_query = rewrite_query_for_retrieval(question, llm)
#     #### intent aware rewriting end




#     docs = store.similarity_search(
#         question,
#         k=12,
#         filter={"compliance_id": compliance_id}
#     )

#     retrieved_metadata = [d.metadata for d in docs] if docs else []

#     # ==================================================
#     # 🔹 ALWAYS TRY NUMERIC AGGREGATION FIRST
#     # ==================================================
#     structured_path = f"data/structured/compliance_{compliance_id}"
#     excel_files = [f for f in os.listdir(structured_path) if f.endswith(".xlsx")]

#     structured_excel_path = (
#         os.path.join(structured_path, excel_files[0])
#         if excel_files else None
#     )

#     numeric_answer = numeric_aggregate(
#         retrieved_metadata,
#         question,
#         structured_excel_path
#     )

#     if numeric_answer:
#         return numeric_answer

#     # ==================================================
#     # 🔹 IF NOT NUMERIC → NORMAL RAG
#     # ==================================================
#     if not docs:
#         return "Not found in provided documents."

#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)
#     llm = get_llm()

#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found."






# =============================
# QUERY BLOCKS (HYBRID RAG) 2)
# =============================
# def query_blocks(store, question, compliance_id):
#     if store is None:
#         return "No documents available."

#     llm = get_llm()

#     # ==================================================
#     # 🔹 INTENT-AWARE QUERY REWRITING
#     # ==================================================
#     rewritten_query = rewrite_query_for_retrieval(question, llm)

#     # ==================================================
#     # 🔹 BROAD RETRIEVAL (TOP-20)
#     # ==================================================
#     docs = store.similarity_search(
#         rewritten_query,   # ✅ FIX: use rewritten query
#         k=20,
#         filter={"compliance_id": compliance_id}
#     )

#     retrieved_metadata = [d.metadata for d in docs] if docs else []

#     # ==================================================
#     # 🔹 ALWAYS TRY NUMERIC AGGREGATION FIRST (EXCEL SAFE)
#     # ==================================================
#     structured_path = f"data/structured/compliance_{compliance_id}"
#     excel_files = [f for f in os.listdir(structured_path) if f.endswith(".xlsx")]

#     structured_excel_path = (
#         os.path.join(structured_path, excel_files[0])
#         if excel_files else None
#     )

#     numeric_answer = numeric_aggregate(
#         retrieved_metadata,
#         question,
#         structured_excel_path
#     )

#     if numeric_answer:
#         return numeric_answer

#     # ==================================================
#     # 🔹 RERANK FOR PRECISION
#     # ==================================================
#     if not docs:
#         return "Not found in provided documents."

#     docs = rerank_documents(question, docs, llm, top_n=6)

#     # ==================================================
#     # 🔹 FINAL ANSWER GENERATION
#     # ==================================================
#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)
#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found."












def query_blocks(store, question, compliance_id):
    if store is None:
        return "No documents available."

    llm = get_llm()

    # ---------- INTENT REWRITE ----------
    rewritten_query = rewrite_query_for_retrieval(question, llm)

    # ---------- DENSE SEARCH ----------
    dense_docs = store.similarity_search(
        rewritten_query,
        k=15,
        filter={"compliance_id": compliance_id}
    )

    # ---------- SPARSE SEARCH ----------
    chunk_dir = f"data/chunks/compliance_{compliance_id}"
    keyword_chunks = []

    if os.path.exists(chunk_dir):
        all_chunks = load_all_chunks(chunk_dir)
        keyword_chunks = bm25_search(rewritten_query, all_chunks, k=10)

    class TempDoc:
        def __init__(self, text):
            self.page_content = text
            self.metadata = {"type": "keyword"}

    sparse_docs = [TempDoc(c) for c in keyword_chunks]

    # ---------- MERGE ----------
    docs = dense_docs + sparse_docs

    # ---------- NUMERIC (ONLY DENSE DOCS) ----------
    retrieved_metadata = [d.metadata for d in dense_docs] if dense_docs else []

    structured_path = f"data/structured/compliance_{compliance_id}"
    excel_files = []
    if os.path.exists(structured_path):
        excel_files = [f for f in os.listdir(structured_path) if f.endswith(".xlsx")]

    structured_excel_path = (
        os.path.join(structured_path, excel_files[0])
        if excel_files else None
    )

    numeric_answer = numeric_aggregate(
        retrieved_metadata,
        question,
        structured_excel_path
    )

    if numeric_answer:
        return numeric_answer

    # ---------- REMOVE DUPLICATES ----------
    unique = {}
    for d in docs:
        unique[d.page_content[:500]] = d
    docs = list(unique.values())

    if not docs:
        return "Not found in provided documents."

    # ---------- RERANK ----------
    docs = rerank_documents(question, docs, llm, top_n=6)

    # ---------- FINAL ANSWER ----------
    context = "\n".join(d.page_content for d in docs)

    prompt = build_prompt(context, question)
    answer = llm.invoke(prompt).content.strip()

    return answer if answer else "Not found."


# def query_blocks(store, question, compliance_id):

#     if store is None:
#         return "No documents available."

#     llm = get_llm()

#     # ---------- NO QUERY REWRITE ----------
#     rewritten_query = question


#     # ---------- DENSE SEARCH ----------
#     dense_docs = store.similarity_search(
#         rewritten_query,
#         k=15,
#         filter={"compliance_id": compliance_id}
#     )
#     # remove docs with invalid metadata
#     dense_docs = [
#         d for d in dense_docs
#         if d.metadata and d.metadata.get("source") is not None
#     ]

#     # ---------- SPARSE SEARCH ----------
#     chunk_dir = f"data/chunks/compliance_{compliance_id}"
#     keyword_chunks = []

#     if os.path.exists(chunk_dir):
#         all_chunks = load_all_chunks(chunk_dir)
#         keyword_chunks = bm25_search(rewritten_query, all_chunks, k=10)


#     class TempDoc:
#         def __init__(self, text):
#             self.page_content = text
#             self.metadata = {"type": "keyword"}


#     sparse_docs = [TempDoc(c) for c in keyword_chunks]


#     # ---------- MERGE RESULTS ----------
#     docs = dense_docs + sparse_docs


#     # ---------- NUMERIC AGGREGATION ----------
#     retrieved_metadata = [d.metadata for d in dense_docs] if dense_docs else []

#     structured_path = f"data/structured/compliance_{compliance_id}"
#     excel_files = []

#     if os.path.exists(structured_path):
#         excel_files = [f for f in os.listdir(structured_path) if f.endswith(".xlsx")]

#     structured_excel_path = (
#         os.path.join(structured_path, excel_files[0])
#         if excel_files else None
#     )

#     numeric_answer = numeric_aggregate(
#         retrieved_metadata,
#         question,
#         structured_excel_path
#     )

#     if numeric_answer:
#         return numeric_answer


#     # ---------- REMOVE DUPLICATES ----------
#     unique = {}

#     for d in docs:
#         unique[d.page_content[:500]] = d

#     docs = list(unique.values())


#     if not docs:
#         return "Not found in provided documents."


#     # ---------- FINAL ANSWER ----------
#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)

#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found."


##### this version with bm25 +reranking  
# def query_blocks(store, question, compliance_id):

#     if store is None:
#         return "No documents available."

#     llm = get_llm()
#     embedder = get_embedder()

#     # -----------------------------
#     # QUERY NORMALIZATION
#     # -----------------------------
#     q = question.lower().strip()

#     # -----------------------------
#     # FOLLOW-UP QUESTION HANDLING
#     # -----------------------------
#     reference_words = [" it ", " they ", " them ", " those ", " that ", " these "]

#     expanded_query = question

#     if any(w in f" {q} " for w in reference_words):
#         expanded_query = question + " context information explanation"

#     # -----------------------------
#     # DENSE RETRIEVAL (FAISS)
#     # -----------------------------
#     dense_docs = store.similarity_search(
#         expanded_query,
#         k=10,
#         filter={"compliance_id": compliance_id}
#     )

#     # -----------------------------
#     # SPARSE RETRIEVAL (BM25)
#     # -----------------------------
#     chunk_dir = f"data/chunks/compliance_{compliance_id}"
#     sparse_docs = []

#     if os.path.exists(chunk_dir):

#         all_chunks = load_all_chunks(chunk_dir)

#         keyword_chunks = bm25_search(expanded_query, all_chunks, k=10)

#         class TempDoc:
#             def __init__(self, text):
#                 self.page_content = text
#                 self.metadata = {"type": "keyword"}

#         sparse_docs = [TempDoc(c) for c in keyword_chunks]

#     # -----------------------------
#     # MERGE RESULTS
#     # -----------------------------
#     docs = dense_docs + sparse_docs

#     # -----------------------------
#     # REMOVE DUPLICATES
#     # -----------------------------
#     unique = {}

#     for d in docs:
#         key = d.page_content[:300]
#         unique[key] = d

#     docs = list(unique.values())

#     if not docs:
#         return "Not found in provided documents."

#     # -----------------------------
#     # EMBEDDING RERANKING
#     # -----------------------------
#     query_vec = embedder.embed_query(expanded_query)

#     def score(doc):
#         doc_vec = embedder.embed_query(doc.page_content[:1000])
#         return sum(a * b for a, b in zip(query_vec, doc_vec))

#     docs = sorted(docs, key=score, reverse=True)

#     # -----------------------------
#     # LIMIT CONTEXT
#     # -----------------------------
#     docs = docs[:6]

#     context = "\n".join(d.page_content for d in docs)

#     # -----------------------------
#     # LLM ANSWER
#     # -----------------------------
#     prompt = build_prompt(context, question)

#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found."


#####version over









# def query_blocks(store, question, compliance_id):

#     if store is None:
#         return "No documents available."

#     llm = get_llm()

#     # -------------------------
#     # INTENT-AWARE REWRITE
#     # -------------------------
#     rewritten_query = rewrite_query_for_retrieval(question, llm)

#     # -------------------------
#     # DENSE SEARCH (FAISS)
#     # -------------------------
#     dense_docs = store.similarity_search(
#         rewritten_query,
#         k=12,
#         filter={"compliance_id": compliance_id}
#     )

#     # remove docs with bad metadata
#     dense_docs = [
#         d for d in dense_docs
#         if d.metadata and d.metadata.get("source") is not None
#     ]

#     # -------------------------
#     # SPARSE SEARCH (BM25)
#     # -------------------------
#     chunk_dir = f"data/chunks/compliance_{compliance_id}"
#     keyword_chunks = []

#     if os.path.exists(chunk_dir):
#         all_chunks = load_all_chunks(chunk_dir)
#         keyword_chunks = bm25_search(rewritten_query, all_chunks, k=8)

#     class TempDoc:
#         def __init__(self, text):
#             self.page_content = text
#             self.metadata = {"type": "keyword"}

#     sparse_docs = [TempDoc(c) for c in keyword_chunks]

#     # -------------------------
#     # MERGE RESULTS
#     # -------------------------
#     docs = dense_docs + sparse_docs

#     # -------------------------
#     # NUMERIC AGGREGATION
#     # -------------------------
#     retrieved_metadata = [d.metadata for d in dense_docs] if dense_docs else []

#     structured_path = f"data/structured/compliance_{compliance_id}"
#     excel_files = []

#     if os.path.exists(structured_path):
#         excel_files = [f for f in os.listdir(structured_path) if f.endswith(".xlsx")]

#     structured_excel_path = (
#         os.path.join(structured_path, excel_files[0])
#         if excel_files else None
#     )

#     numeric_answer = numeric_aggregate(
#         retrieved_metadata,
#         question,
#         structured_excel_path
#     )

#     if numeric_answer:
#         return numeric_answer

#     # -------------------------
#     # REMOVE DUPLICATES
#     # -------------------------
#     unique = {}

#     for d in docs:
#         key = d.page_content[:500]
#         unique[key] = d

#     docs = list(unique.values())

#     if not docs:
#         return "No relevant information found in uploaded documents."

#     # -------------------------
#     # LIGHT RERANK (embedding)
#     # -------------------------
#     embedder = get_embedder()
#     query_vec = embedder.embed_query(rewritten_query)

#     def score(doc):
#         doc_vec = embedder.embed_query(doc.page_content[:800])
#         return sum(a*b for a, b in zip(query_vec, doc_vec))

#     docs = sorted(docs, key=score, reverse=True)

#     # keep only best chunks
#     docs = docs[:6]

#     # -------------------------
#     # FINAL LLM ANSWER
#     # -------------------------
#     context = "\n".join(d.page_content for d in docs)

#     prompt = build_prompt(context, question)

#     try:
#         answer = llm.invoke(prompt).content.strip()
#     except:
#         return "Error generating answer."

#     return answer if answer else "Not found in provided documents."







    # if numeric_answer:
    #     return numeric_answer

    # # ==================================================
    # # 🔹 NORMAL RAG ANSWER
    # # ==================================================
    # context = "\n".join(d.page_content for d in docs)

    # prompt = build_prompt(context, question)
    # llm = get_llm()

    # answer = llm.invoke(prompt).content.strip()

    # return answer if answer else "Not found."






# # # 2.
# # # def query_blocks(store, question, compliance_id):
# # #     if store is None:
# # #         return "No unstructured documents available for this compliance."

# # #     # 1️⃣ Retrieve candidates (semantic search)
# # #     docs = store.similarity_search(
# # #         question,
# # #         k=15,
# # #         filter={"compliance_id": compliance_id}
# # #     )

# # #     if not docs:
# # #         return "Not found in provided documents."

# # #     # 2️⃣ RERANK using LLM (lightweight scoring)
# # #     llm = get_llm()

# # #     scored_docs = []

# # #     for d in docs:
# # #         score_prompt = f"""
# # # You are scoring relevance.

# # # Question:
# # # {question}

# # # Chunk:
# # # {d.page_content}

# # # Give a relevance score from 0 to 1.
# # # Only output a number.
# # # """
# # #         try:
# # #             score_text = llm.invoke(score_prompt).content.strip()
# # #             score = float(score_text)
# # #         except:
# # #             score = 0.0

# # #         scored_docs.append((score, d))

# # #     # 3️⃣ Sort by relevance score
# # #     scored_docs.sort(key=lambda x: x[0], reverse=True)

# # #     # 4️⃣ Confidence thresholds
# # #     HIGH_CONF = 0.6
# # #     MED_CONF = 0.35

# # #     top_score = scored_docs[0][0]

# # #     # 5️⃣ Select chunks based on confidence
# # #     if top_score >= HIGH_CONF:
# # #         selected = [d.page_content for s, d in scored_docs[:4]]
# # #         confidence_mode = "HIGH"
# # #     elif top_score >= MED_CONF:
# # #         selected = [d.page_content for s, d in scored_docs[:3]]
# # #         confidence_mode = "MEDIUM"
# # #     else:
# # #         return "Not found in provided documents."

# # #     context = "\n".join(selected)

# # #     # 6️⃣ Confidence-aware prompt
# # #     if confidence_mode == "HIGH":
# # #         prompt = build_prompt(context, question)
# # #     else:
# # #         prompt = f"""
# # # You are a compliance assistant.

# # # The exact answer may not be explicitly stated.
# # # Use the context to provide the closest relevant information.
# # # Clearly mention that the exact wording is not present.

# # # Context:
# # # {context}

# # # Question:
# # # {question}

# # # Answer:
# # # """

# # #     answer = llm.invoke(prompt).content.strip()

# # #     return answer if answer else "Not found in provided documents."



# # def query_blocks(store, question, compliance_id):
# #     if store is None:
# #         return "No unstructured documents available for this compliance."

# #     # 1️⃣ Retrieve more candidates (semantic search)
# #     docs = store.similarity_search(
# #         question,
# #         k=20,
# #         filter={"compliance_id": compliance_id}
# #     )

# #     if not docs:
# #         return "Not found in provided documents."

# #     llm = get_llm()
# #     scored = []

# #     # 2️⃣ Rerank chunks by relevance
# #     for d in docs:
# #         score_prompt = f"""
# # Score how relevant this chunk is to the question.

# # Question:
# # {question}

# # Chunk:
# # {d.page_content}

# # Score from 0 to 1.
# # Only output a number.
# # """
# #         try:
# #             score = float(llm.invoke(score_prompt).content.strip())
# #         except:
# #             score = 0.0

# #         scored.append((score, d))

# #     # 3️⃣ Sort by relevance
# #     scored.sort(key=lambda x: x[0], reverse=True)

# #     top_score = scored[0][0]

# #     # 4️⃣ Confidence thresholds
# #     HIGH = 0.6
# #     MEDIUM = 0.35

# #     if top_score < MEDIUM:
# #         return "Not found in provided documents."

# #     # 5️⃣ Select best unique chunks
# #     selected_chunks = []
# #     seen = set()

# #     for score, doc in scored:
# #         text = doc.page_content.strip()
# #         if text not in seen:
# #             selected_chunks.append(text)
# #             seen.add(text)
# #         if len(selected_chunks) == 4:
# #             break

# #     context = "\n".join(selected_chunks)

# #     # 6️⃣ Confidence-aware prompting
# #     if top_score >= HIGH:
# #         prompt = build_prompt(context, question)
# #     else:
# #         prompt = f"""
# # You are a compliance assistant.

# # The exact answer is not explicitly stated.
# # Use the context to provide the closest relevant information.
# # Clearly state this limitation.

# # Context:
# # {context}

# # Question:
# # {question}

# # Answer:
# # """

# #     answer = llm.invoke(prompt).content.strip()
# #     return answer if answer else "Not found in provided documents."




# #######################################. eventfallback 
# # import os
# # from collections import OrderedDict
# # from typing import List

# # from vectorstore.faiss_store import create_vector_store, load_vector_store
# # from processing.embedder import get_embedder
# # from rag.prompt import build_prompt


# # BASE_CHUNK_DIR = "data/chunks"
# # BASE_EMBED_DIR = "data/embeddings"


# # # ---------------------------------------------------------
# # # INGESTION (UNCHANGED BEHAVIOR – SAFE)
# # # ---------------------------------------------------------
# # def ingest_blocks(blocks, compliance_id):
# #     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"

# #     if os.path.exists(f"{embed_path}/index.faiss"):
# #         print("✔ Loading existing embeddings (no OpenAI cost)")
# #         return load_vector_store(embed_path)

# #     print("⏳ Creating embeddings...")

# #     all_chunks = []
# #     all_metadata = []

# #     for block in blocks:
# #         if not block["type"]:
# #             continue

# #         block_type = block["type"].upper()
# #         block_id = block["block_id"]

# #         # Structured files are handled elsewhere
# #         if block_type in ["XLS", "CSV", "GSHEET"]:
# #             continue

# #         text = block.get("extracted_text", "")
# #         chunks = block.get("chunks", [])

# #         for c in chunks:
# #             all_chunks.append(c)
# #             all_metadata.append({
# #                 "compliance_id": compliance_id,
# #                 "block_id": block_id,
# #                 "source": block.get("value")
# #             })

# #     if not all_chunks:
# #         return None

# #     embedder = get_embedder()
# #     store = create_vector_store(all_chunks, all_metadata, embedder)

# #     os.makedirs(embed_path, exist_ok=True)
# #     store.save_local(embed_path)

# #     print("✅ Embeddings saved locally")
# #     return store


# # # ---------------------------------------------------------
# # # 🔥 SEMANTIC + CONFIDENCE-AWARE QUERYING
# # # ---------------------------------------------------------
# # def query_blocks(store, question: str, compliance_id: str) -> str:
# #     """
# #     Semantic RAG with:
# #     - closest-information fallback
# #     - list completeness
# #     - confidence awareness
# #     - no duplicate answers
# #     """

# #     if store is None:
# #         return "No unstructured documents available."

# #     # 🔹 1. SEMANTIC SEARCH (NOT KEYWORD MATCH)
# #     docs = store.similarity_search(
# #         question,
# #         k=8,
# #         filter={"compliance_id": compliance_id}
# #     )

# #     if not docs:
# #         return "Not found in provided documents."

# #     # 🔹 2. MERGE + CLEAN CONTEXT
# #     context_chunks = []
# #     seen = set()

# #     for d in docs:
# #         text = d.page_content.strip()
# #         if text and text not in seen:
# #             seen.add(text)
# #             context_chunks.append(text)

# #     context = "\n".join(context_chunks)

# #     # 🔹 3. CONFIDENCE HEURISTIC
# #     # If keywords overlap but exact phrasing differs → closest answer mode
# #     q_tokens = set(question.lower().split())
# #     ctx_tokens = set(context.lower().split())

# #     overlap_ratio = len(q_tokens & ctx_tokens) / max(len(q_tokens), 1)

# #     # Thresholds chosen conservatively
# #     if overlap_ratio < 0.08:
# #         return "Not found in provided documents."

# #     # 🔹 4. PROMPT-BASED SYNTHESIS (STRICT BUT HELPFUL)
# #     prompt = build_prompt(context, question)

# #     llm = get_llm()
# #     answer = llm.invoke(prompt).content.strip()

# #     # 🔹 5. FINAL SAFETY NET
# #     if not answer or answer.lower().startswith("not found"):
# #         return (
# #             "The exact information is not explicitly mentioned in the documents. "
# #             "However, closely related information is available:\n\n"
# #             + context_chunks[0]
# #         )

# #     return answer


# # # ---------------------------------------------------------
# # # LAZY IMPORT (avoids circular import issues)
# # # ---------------------------------------------------------
# # def get_llm():
# #     from processing.llm import get_llm as _get_llm
# #     return _get_llm()








# #.  pretty close version but no chunk saved 
# # import os
# # from typing import List

# # from extractors.universal_extractor import extract_text
# # from processing.chunker import chunk_text
# # from vectorstore.faiss_store import create_vector_store, load_vector_store
# # from processing.embedder import get_embedder
# # from rag.prompt import build_prompt



# # BASE_EMBED_DIR = "data/embeddings"


# # # =====================================================
# # # INGESTION (UNCHANGED – SAFE)
# # # =====================================================
# # def ingest_blocks(blocks, compliance_id):
# #     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"

# #     if os.path.exists(f"{embed_path}/index.faiss"):
# #         print("✔ Loading existing embeddings (no OpenAI cost)")
# #         return load_vector_store(embed_path)

# #     print("⏳ Creating embeddings...")

# #     all_chunks = []
# #     all_metadata = []

# #     for block in blocks:
# #         if not block.get("type"):
# #             continue

# #         block_type = block["type"].upper()
# #         source = block["value"]

# #         # 🚫 Skip structured here
# #         if block_type in ["XLS", "CSV", "GSHEET"]:
# #             continue

# #         # ✅ EXTRACT TEXT
# #         try:
# #             text = extract_text(source)
# #         except Exception as e:
# #             print(f"⚠ Failed to extract {source}: {e}")
# #             continue

# #         if not text.strip():
# #             continue

# #         # ✅ CHUNK TEXT
# #         chunks = chunk_text(text)

# #         for c in chunks:
# #             all_chunks.append(c)
# #             all_metadata.append({
# #                 "compliance_id": compliance_id,
# #                 "source": source
# #             })

# #     if not all_chunks:
# #         print("ℹ No unstructured documents found.")
# #         return None

# #     store = create_vector_store(
# #         all_chunks,
# #         all_metadata,
# #         get_embedder()
# #     )

# #     os.makedirs(embed_path, exist_ok=True)
# #     store.save_local(embed_path)

# #     print("✅ Embeddings saved locally")
# #     return store


# # # =====================================================
# # # 🔥 SEMANTIC + CONFIDENCE-AWARE RAG
# # # =====================================================
# # def query_blocks(store, question: str, compliance_id: str) -> str:
# #     """
# #     Robust semantic RAG with:
# #     - semantic similarity (not keyword)
# #     - closest-information fallback
# #     - controlled output size
# #     - no hallucination
# #     """

# #     if store is None:
# #         return "No unstructured documents available."

# #     # 1️⃣ Semantic retrieval
# #     docs = store.similarity_search(
# #         question,
# #         k=8,
# #         filter={"compliance_id": compliance_id}
# #     )

# #     if not docs:
# #         return "Not found in provided documents."

# #     # 2️⃣ Deduplicate + keep only most relevant text
# #     seen = set()
# #     context_chunks: List[str] = []

# #     for d in docs:
# #         text = d.page_content.strip()
# #         if text and text not in seen:
# #             seen.add(text)
# #             context_chunks.append(text)
# #         if len(context_chunks) == 4:  # hard limit
# #             break

# #     context = "\n".join(context_chunks)

# #     # 3️⃣ Confidence heuristic (semantic overlap)
# #     q_tokens = set(question.lower().split())
# #     ctx_tokens = set(context.lower().split())

# #     overlap = len(q_tokens & ctx_tokens) / max(len(q_tokens), 1)

# #     if overlap < 0.07:
# #         return "Not found in provided documents."

# #     # 4️⃣ Ask LLM with STRICT rules
# #     llm = _get_llm()
# #     prompt = build_prompt(context, question)
# #     answer = llm.invoke(prompt).content.strip()

# #     # 5️⃣ Controlled fallback (closest info only)
# #     if not answer or answer.lower().startswith("not found"):
# #         return (
# #             "The exact information is not explicitly mentioned in the documents. "
# #             "However, closely related information is available:\n\n"
# #             + context_chunks[0]
# #         )

# #     return answer


# # # =====================================================
# # # Lazy import (prevents circular imports)
# # # =====================================================
# # def _get_llm():
# #     from processing.llm import get_llm
# #     return get_llm()










# #chunks saved 
# # import os
# # from typing import List

# # from extractors.universal_extractor import extract_text
# # from processing.chunker import chunk_text
# # from vectorstore.faiss_store import create_vector_store, load_vector_store
# # from processing.embedder import get_embedder
# # from rag.prompt import build_prompt


# # BASE_EMBED_DIR = "data/embeddings"
# # BASE_CHUNK_DIR = "data/chunks"


# # # =====================================================
# # # INGESTION (FIXED – CHUNKS ARE SAVED)
# # # =====================================================
# # def ingest_blocks(blocks, compliance_id):
# #     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"
# #     chunk_path = f"{BASE_CHUNK_DIR}/compliance_{compliance_id}"

# #     # If embeddings already exist, load them
# #     if os.path.exists(f"{embed_path}/index.faiss"):
# #         print("✔ Loading existing embeddings (no OpenAI cost)")
# #         return load_vector_store(embed_path)

# #     print("⏳ Creating embeddings...")

# #     os.makedirs(chunk_path, exist_ok=True)

# #     all_chunks = []
# #     all_metadata = []

# #     for block in blocks:
# #         if not block.get("type"):
# #             continue

# #         block_type = block["type"].upper()
# #         source = block["value"]

# #         # 🚫 Skip structured files here
# #         if block_type in ["XLS", "CSV", "GSHEET"]:
# #             continue

# #         # ✅ Extract text
# #         try:
# #             text = extract_text(source)
# #         except Exception as e:
# #             print(f"⚠ Failed to extract {source}: {e}")
# #             continue

# #         if not text.strip():
# #             print(f"⚠ Empty text extracted from {source}")
# #             continue

# #         # ✅ Chunk text
# #         chunks = chunk_text(text)

# #         if not chunks:
# #             continue

# #         # ✅ Save chunks to disk (FOR DEBUGGING & TRACEABILITY)
# #         safe_name = os.path.basename(source).replace("/", "_").replace(" ", "_")
# #         chunk_file = os.path.join(chunk_path, f"{safe_name}.txt")

# #         with open(chunk_file, "w", encoding="utf-8") as f:
# #             for i, chunk in enumerate(chunks, start=1):
# #                 f.write(f"[CHUNK {i}]\n")
# #                 f.write(chunk.strip())
# #                 f.write("\n\n" + "=" * 80 + "\n\n")

# #         # ✅ Prepare for embeddings
# #         for c in chunks:
# #             all_chunks.append(c)
# #             all_metadata.append({
# #                 "compliance_id": compliance_id,
# #                 "source": source
# #             })

# #     if not all_chunks:
# #         print("ℹ No unstructured documents found.")
# #         return None

# #     store = create_vector_store(
# #         all_chunks,
# #         all_metadata,
# #         get_embedder()
# #     )

# #     os.makedirs(embed_path, exist_ok=True)
# #     store.save_local(embed_path)

# #     print("✅ Embeddings saved locally")
# #     print(f"📄 Chunks saved at: {chunk_path}")

# #     return store


# # # =====================================================
# # # SEMANTIC + CONFIDENCE-AWARE RAG (UNCHANGED)
# # # =====================================================
# # def query_blocks(store, question: str, compliance_id: str) -> str:
# #     if store is None:
# #         return "No unstructured documents available."

# #     docs = store.similarity_search(
# #         question,
# #         k=8,
# #         filter={"compliance_id": compliance_id}
# #     )

# #     if not docs:
# #         return "Not found in provided documents."

# #     seen = set()
# #     context_chunks: List[str] = []

# #     for d in docs:
# #         text = d.page_content.strip()
# #         if text and text not in seen:
# #             seen.add(text)
# #             context_chunks.append(text)
# #         if len(context_chunks) == 4:
# #             break

# #     context = "\n".join(context_chunks)

# #     q_tokens = set(question.lower().split())
# #     ctx_tokens = set(context.lower().split())
# #     overlap = len(q_tokens & ctx_tokens) / max(len(q_tokens), 1)

# #     if overlap < 0.07:
# #         return "Not found in provided documents."

# #     llm = _get_llm()
# #     prompt = build_prompt(context, question)
# #     answer = llm.invoke(prompt).content.strip()

# #     if not answer or answer.lower().startswith("not found"):
# #         return (
# #             "The exact information is not explicitly mentioned in the documents. "
# #             "However, closely related information is available:\n\n"
# #             + context_chunks[0]
# #         )

# #     return answer


# # # =====================================================
# # # Lazy import (prevents circular imports)
# # # =====================================================
# # def _get_llm():
# #     from processing.llm import get_llm
# #     return get_llm()







# # import os
# # import re
# # from typing import List

# # from extractors.universal_extractor import extract_text
# # from processing.chunker import chunk_text
# # from vectorstore.faiss_store import create_vector_store, load_vector_store
# # from processing.embedder import get_embedder
# # from rag.prompt import build_prompt

# # BASE_EMBED_DIR = "data/embeddings"
# # BASE_CHUNK_DIR = "data/chunks"


# # # =====================================================
# # # INGESTION (SAFE + TRACEABLE)
# # # =====================================================
# # def ingest_blocks(blocks, compliance_id):
# #     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"
# #     chunk_path = f"{BASE_CHUNK_DIR}/compliance_{compliance_id}"

# #     if os.path.exists(f"{embed_path}/index.faiss"):
# #         print("✔ Loading existing embeddings (no OpenAI cost)")
# #         return load_vector_store(embed_path)

# #     print("⏳ Creating embeddings...")

# #     os.makedirs(chunk_path, exist_ok=True)

# #     all_chunks = []
# #     all_metadata = []

# #     for block in blocks:
# #         if not block.get("type"):
# #             continue

# #         block_type = block["type"].upper()
# #         source = block["value"]

# #         if block_type in ["XLS", "CSV", "GSHEET"]:
# #             continue

# #         try:
# #             text = extract_text(source)
# #         except Exception as e:
# #             print(f"⚠ Failed to extract {source}: {e}")
# #             continue

# #         if not text.strip():
# #             continue

# #         chunks = chunk_text(text)
# #         if not chunks:
# #             continue

# #         # Save chunks for inspection
# #         safe_name = os.path.basename(source).replace(" ", "_")
# #         with open(
# #             os.path.join(chunk_path, f"{safe_name}.txt"),
# #             "w",
# #             encoding="utf-8",
# #         ) as f:
# #             for i, c in enumerate(chunks, 1):
# #                 f.write(f"[CHUNK {i}]\n{c}\n\n{'='*80}\n\n")

# #         for c in chunks:
# #             all_chunks.append(c)
# #             all_metadata.append({
# #                 "compliance_id": compliance_id,
# #                 "source": source
# #             })

# #     if not all_chunks:
# #         print("ℹ No unstructured documents found.")
# #         return None

# #     store = create_vector_store(
# #         all_chunks,
# #         all_metadata,
# #         get_embedder()
# #     )

# #     os.makedirs(embed_path, exist_ok=True)
# #     store.save_local(embed_path)

# #     print("✅ Embeddings saved locally")
# #     print(f"📄 Chunks saved at: {chunk_path}")
# #     return store


# # # =====================================================
# # # 🔥 ENTITY-FIRST SEMANTIC RAG (FIXED)
# # # =====================================================
# # def query_blocks(store, question: str, compliance_id: str) -> str:
# #     if store is None:
# #         return "No unstructured documents available."

# #     # 1️⃣ Semantic retrieval
# #     docs = store.similarity_search(
# #         question,
# #         k=12,
# #         filter={"compliance_id": compliance_id}
# #     )

# #     if not docs:
# #         return "Not found in provided documents."

# #     # 2️⃣ Extract key entities from question
# #     entities = _extract_entities(question)

# #     # 3️⃣ Entity-first filtering
# #     entity_matched = []
# #     for d in docs:
# #         text = d.page_content.lower()
# #         if any(e in text for e in entities):
# #             entity_matched.append(d)

# #     # Fallback if entity not explicitly found
# #     if entity_matched:
# #         docs = entity_matched

# #     # 4️⃣ Build focused context
# #     context_chunks: List[str] = []
# #     seen = set()

# #     for d in docs:
# #         text = d.page_content.strip()
# #         if text and text not in seen:
# #             seen.add(text)
# #             context_chunks.append(text)
# #         if len(context_chunks) == 3:
# #             break

# #     if not context_chunks:
# #         return "Not found in provided documents."

# #     context = "\n\n".join(context_chunks)

# #     # 5️⃣ Ask LLM with STRICT prompt
# #     llm = _get_llm()
# #     prompt = build_prompt(context, question)
# #     answer = llm.invoke(prompt).content.strip()

# #     # 6️⃣ Controlled fallback
# #     if not answer or answer.lower().startswith("not found"):
# #         return (
# #             "The exact information is not explicitly mentioned in the documents. "
# #             "However, closely related information is available:\n\n"
# #             + context_chunks[0]
# #         )

# #     return answer


# # # =====================================================
# # # UTILITIES
# # # =====================================================
# # def _extract_entities(question: str) -> List[str]:
# #     """
# #     Lightweight entity extractor:
# #     - Acronyms
# #     - Capitalized terms
# #     - Keywords longer than 3 chars
# #     """
# #     q = question.lower()

# #     acronyms = re.findall(r"\b[A-Z]{2,}\b", question)
# #     keywords = re.findall(r"\b[a-z]{4,}\b", q)

# #     entities = set(a.lower() for a in acronyms)
# #     entities.update(keywords)

# #     return list(entities)


# # def _get_llm():
# #     from processing.llm import get_llm
# #     return get_llm()








# import os
# from typing import List

# from extractors.universal_extractor import extract_text
# from loaders.url_loader_browser import load_url_with_browser
# from processing.chunker import chunk_text
# from vectorstore.faiss_store import create_vector_store, load_vector_store
# from processing.embedder import get_embedder
# from rag.prompt import build_prompt


# BASE_EMBED_DIR = "data/embeddings"
# BASE_CHUNK_DIR = "data/chunks"


# # =====================================================
# # INGESTION (STABLE + URL RESTORED)
# # =====================================================
# def ingest_blocks(blocks, compliance_id):
#     embed_path = f"{BASE_EMBED_DIR}/compliance_{compliance_id}"
#     chunk_path = f"{BASE_CHUNK_DIR}/compliance_{compliance_id}"

#     # Reuse embeddings if already present
#     if os.path.exists(f"{embed_path}/index.faiss"):
#         print("✔ Loading existing embeddings (no OpenAI cost)")
#         return load_vector_store(embed_path)

#     print("⏳ Creating embeddings...")
#     os.makedirs(chunk_path, exist_ok=True)

#     all_chunks = []
#     all_metadata = []

#     for block in blocks:
#         if not block.get("type"):
#             continue

#         block_type = block["type"].upper()
#         source = block["value"]

#         # =========================
#         # 🌐 URL HANDLING (FIXED)
#         # =========================
#         if block_type == "URL":
#             try:
#                 page_text, downloaded_files = load_url_with_browser(source)
#             except Exception as e:
#                 print(f"⚠ Failed to load URL {source}: {e}")
#                 continue

#             # Page content
#             if page_text.strip():
#                 page_chunks = chunk_text(page_text)
#                 _save_chunks(chunk_path, source, page_chunks)

#                 for c in page_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "source": source,
#                         "type": "url_page"
#                     })

#             # Downloaded documents (PDF, XLS, etc.)
#             for file_path in downloaded_files:
#                 try:
#                     text = extract_text(file_path)
#                 except Exception as e:
#                     print(f"⚠ Failed to extract {file_path}: {e}")
#                     continue

#                 doc_chunks = chunk_text(text)
#                 _save_chunks(chunk_path, file_path, doc_chunks)

#                 for c in doc_chunks:
#                     all_chunks.append(c)
#                     all_metadata.append({
#                         "compliance_id": compliance_id,
#                         "source": file_path,
#                         "type": "url_document"
#                     })

#             continue  # IMPORTANT

#         # =========================
#         # 📊 STRUCTURED FILES
#         # =========================
#         if block_type in ["XLS", "CSV", "GSHEET"]:
#             # handled elsewhere (DO NOT TOUCH)
#             continue

#         # =========================
#         # 📄 FILES (PDF / DOC / PPT)
#         # =========================
#         try:
#             text = extract_text(source)
#         except Exception as e:
#             print(f"⚠ Failed to extract {source}: {e}")
#             continue

#         if not text.strip():
#             continue

#         chunks = chunk_text(text)
#         _save_chunks(chunk_path, source, chunks)

#         for c in chunks:
#             all_chunks.append(c)
#             all_metadata.append({
#                 "compliance_id": compliance_id,
#                 "source": source,
#                 "type": "file"
#             })

#     if not all_chunks:
#         print("ℹ No unstructured documents found.")
#         return None

#     store = create_vector_store(
#         all_chunks,
#         all_metadata,
#         get_embedder()
#     )

#     os.makedirs(embed_path, exist_ok=True)
#     store.save_local(embed_path)

#     print("✅ Embeddings saved locally")
#     print(f"📄 Chunks saved at: {chunk_path}")
#     return store


# # =====================================================
# # QUERY (UNCHANGED – SAFE)
# # =====================================================
# def query_blocks(store, question: str, compliance_id: str) -> str:
#     if store is None:
#         return "No unstructured documents available."

#     docs = store.similarity_search(
#         question,
#         k=5,
#         filter={"compliance_id": compliance_id}
#     )

#     if not docs:
#         return "Not found in provided documents."

#     context = "\n\n".join(d.page_content for d in docs)

#     llm = _get_llm()
#     prompt = build_prompt(context, question)
#     answer = llm.invoke(prompt).content.strip()

#     return answer if answer else "Not found in provided documents."


# # =====================================================
# # UTILITIES
# # =====================================================
# def _save_chunks(chunk_path, source, chunks):
#     safe_name = os.path.basename(source).replace("/", "_").replace(" ", "_")
#     file_path = os.path.join(chunk_path, f"{safe_name}.txt")

#     with open(file_path, "w", encoding="utf-8") as f:
#         for i, c in enumerate(chunks, 1):
#             f.write(f"[CHUNK {i}]\n{c}\n\n{'='*60}\n\n")


# def _get_llm():
#     from processing.llm import get_llm
#     return get_llm()
