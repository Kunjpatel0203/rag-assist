# import os
# import requests
# from urllib.parse import urljoin
# from playwright.sync_api import sync_playwright, TimeoutError

# SUPPORTED_EXTENSIONS = (
#     ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"
# )


# def _direct_download(url, download_dir):
#     """
#     Fallback HTTP download (works for preview/new-tab documents)
#     """
#     try:
#         resp = requests.get(url, timeout=30, stream=True)
#         resp.raise_for_status()

#         filename = url.split("/")[-1].split("?")[0]
#         path = os.path.join(download_dir, filename)

#         with open(path, "wb") as f:
#             for chunk in resp.iter_content(chunk_size=8192):
#                 f.write(chunk)

#         print(f"⬇ Downloaded (direct): {filename}")
#         return path

#     except Exception as e:
#         print(f"⚠ Direct download failed: {e}")
#         return None


# def load_url_with_browser(url, download_dir="data/downloads"):
#     """
#     UNIVERSAL URL LOADER

#     Handles:
#     - Direct downloads
#     - New-tab previews
#     - JS-triggered links
#     - Gov websites
#     """

#     os.makedirs(download_dir, exist_ok=True)

#     page_text = ""
#     downloaded_files = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         context = browser.new_context(
#             accept_downloads=True,
#             ignore_https_errors=True
#         )
#         page = context.new_page()

#         # -----------------------------
#         # Load page (soft load)
#         # -----------------------------
#         try:
#             page.goto(url, timeout=30000)
#         except TimeoutError:
#             print("⚠ Page load timeout — continuing")

#         # Best-effort text extraction
#         try:
#             page_text = page.evaluate("document.body.innerText")
#         except Exception:
#             page_text = ""

#         # -----------------------------
#         # Extract all anchor links
#         # -----------------------------
#         anchors = page.query_selector_all("a[href]")

#         for anchor in anchors:
#             href = anchor.get_attribute("href")
#             if not href:
#                 continue

#             full_url = urljoin(url, href)
#             lower = full_url.lower()

#             if not lower.endswith(SUPPORTED_EXTENSIONS):
#                 continue

#             # -----------------------------
#             # 1️⃣ TRY BROWSER DOWNLOAD
#             # -----------------------------
#             try:
#                 with page.expect_download(timeout=5000) as d_info:
#                     anchor.click()

#                 download = d_info.value
#                 filename = download.suggested_filename
#                 save_path = os.path.join(download_dir, filename)

#                 download.save_as(save_path)
#                 downloaded_files.append(save_path)

#                 print(f"⬇ Downloaded (browser): {filename}")
#                 continue

#             except Exception:
#                 pass  # browser download did not happen

#             # -----------------------------
#             # 2️⃣ FALLBACK: DIRECT HTTP
#             # -----------------------------
#             path = _direct_download(full_url, download_dir)
#             if path:
#                 downloaded_files.append(path)
#             else:
#                 print(f"⚠ Skipped (protected/invalid): {full_url}")

#         browser.close()

#     return page_text, downloaded_files





import os
import re
import uuid
import requests
from urllib.parse import urlparse, unquote
from playwright.sync_api import sync_playwright, TimeoutError

SUPPORTED_EXTENSIONS = (
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".csv"
)

# Server-reported type → extension, for links like /download?id=123
CONTENT_TYPE_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-powerpoint": ".ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/csv": ".csv",
}

# Links without a file extension are only fetched if they look like downloads
DOWNLOAD_HINTS = ("download", "attachment", "file", "export", "document", "pdf", "doc")

MAX_DOCUMENTS = 50        # documents downloaded per page
MAX_UNKNOWN_CHECKS = 30   # extensionless links fetched to check their type


def _extension_from_url(url):
    # look at the path only, so "report.pdf?version=2" still counts
    ext = os.path.splitext(unquote(urlparse(url).path))[1].lower()
    return ext if ext in SUPPORTED_EXTENSIONS else None


def _looks_like_download(url, text):
    haystack = f"{url} {text}".lower()
    return any(hint in haystack for hint in DOWNLOAD_HINTS)


def _filename_from_response(url, headers, ext):
    # prefer the server's name: Content-Disposition: attachment; filename="x.pdf"
    disposition = headers.get("content-disposition", "")
    match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', disposition, re.I)
    name = unquote(match.group(1)) if match else os.path.basename(unquote(urlparse(url).path))

    name = re.sub(r"[^\w.\- ]", "_", name).strip() or "document"
    if not name.lower().endswith(ext):
        name += ext
    return name


def _unique_path(download_dir, name):
    path = os.path.join(download_dir, name)
    base, ext = os.path.splitext(path)
    i = 1
    while os.path.exists(path):
        path = f"{base}_{i}{ext}"
        i += 1
    return path


def _fetch(context, url):
    """
    Fetch through the browser session first (keeps the site's cookies),
    fall back to a plain HTTP request.
    Returns (body, headers) or (None, None).
    """
    try:
        resp = context.request.get(url, timeout=30000)
        if resp.ok:
            return resp.body(), {k.lower(): v for k, v in resp.headers.items()}
    except Exception as e:
        print(f"⚠ Browser fetch failed: {e}")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content, {k.lower(): v for k, v in resp.headers.items()}
    except Exception as e:
        print(f"⚠ Direct download failed: {e}")
        return None, None


def _download(context, url, download_dir, ext):
    body, headers = _fetch(context, url)
    if body is None:
        return None

    content_type = headers.get("content-type", "").split(";")[0].strip().lower()

    # a "document" link that returns a web page (login, error page) is skipped
    if content_type == "text/html":
        return None

    ext = ext or CONTENT_TYPE_EXTENSIONS.get(content_type)
    if not ext:
        return None

    path = _unique_path(download_dir, _filename_from_response(url, headers, ext))
    with open(path, "wb") as f:
        f.write(body)

    print(f"⬇ Downloaded: {os.path.basename(path)}")
    return path


def load_url_with_browser(url, download_dir="data/downloads"):
    # each URL gets its own folder so files from different pages never clash
    download_dir = os.path.join(download_dir, uuid.uuid4().hex[:12])
    os.makedirs(download_dir, exist_ok=True)

    page_text = ""
    downloaded_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            accept_downloads=True,
            ignore_https_errors=True
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=30000)
        except TimeoutError:
            print("⚠ Page load timeout — continuing")

        # Extract visible page text
        try:
            page_text = page.evaluate("document.body.innerText")
        except:
            page_text = ""

        # =====================================================
        # Collect every link on the page (href is already absolute)
        # =====================================================
        try:
            links = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => [e.href, e.innerText || ''])"
            )
        except:
            links = []

        seen = set()
        unknown_checks = 0

        for href, text in links:
            if len(downloaded_files) >= MAX_DOCUMENTS:
                print(f"⚠ Reached {MAX_DOCUMENTS} documents — skipping the rest")
                break

            full_url = href.split("#")[0]
            if not full_url.startswith(("http://", "https://")) or full_url in seen:
                continue
            seen.add(full_url)

            ext = _extension_from_url(full_url)

            if not ext:
                # no extension: only check links that look like downloads
                if not _looks_like_download(full_url, text):
                    continue
                if unknown_checks >= MAX_UNKNOWN_CHECKS:
                    continue
                unknown_checks += 1

            path = _download(context, full_url, download_dir, ext)
            if path:
                downloaded_files.append(path)
            elif ext:
                print(f"⚠ Skipped: {full_url}")

        browser.close()

    return page_text, downloaded_files
