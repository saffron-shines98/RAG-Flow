# TrackFlow RAG — Complete Project

Ye ek **full RAG (Retrieval-Augmented Generation) system** hai jo PDF upload
lekar us par sawaal-jawab karta hai — FastAPI, Hugging Face, ChromaDB, aur
Groq LLM se bana hua.

## 📁 Is Project Mein 3 Documentation Files Hain

| File | Padho Jab |
|---|---|
| **README.md** (ye file) | Project structure aur architecture samajhna ho |
| **COMMANDS.md** | Bas run karna ho, step-by-step commands chahiye |
| **CONCEPTS_LEARNED.md** | Poori theory (tokenization se RAG tak) ko is code se connect karke revise karna ho |

**Sabse pehle `COMMANDS.md` khol ke seedha run kar sakte ho.**

---

## Folder Structure

```
trackflow_rag/
├── app/
│   ├── __init__.py
│   ├── main.py                    → Entry point: FastAPI app + routers register
│   │
│   ├── core/
│   │   └── config.py               → Saari settings ek jagah (.env se load)
│   │
│   ├── dependencies/
│   │   └── file_handler.py         → Shared reusable logic (file save karna)
│   │
│   ├── models/
│   │   └── README.md               → Future SQL DB models ke liye placeholder
│   │
│   ├── routers/
│   │   ├── ingest.py               → POST /ingest endpoint
│   │   └── ask.py                  → POST /ask endpoint
│   │
│   ├── schemas/
│   │   └── rag_schemas.py          → Request/Response validation (Pydantic)
│   │
│   ├── services/                   → ASLI BUSINESS LOGIC yahan hai
│   │   ├── pdf_service.py           → PDF se text nikalna
│   │   ├── chunking_service.py      → Text ko chunks mein todna
│   │   ├── embedding_service.py     → Hugging Face embeddings
│   │   ├── vector_store_service.py  → ChromaDB operations
│   │   ├── llm_service.py           → Groq LLM se answer generate
│   │   └── rag_service.py           → Sabko orchestrate karta hai
│   │
│   └── utils/
│       └── logger.py                → Chota reusable helper
│
├── data/                            → Uploaded PDFs yahan save hote hain
├── chroma_store/                    → ChromaDB ka persistent data (auto-banta hai)
├── .env.example                     → Environment variable template
├── requirements.txt
└── README.md
```

## Ye Structure "Scalable" Kyun Hai?

| Agar Kal Ye Chahiye Ho... | Toh Kya Karoge |
|---|---|
| Naya endpoint (jaise `/summarize`) | Bas `routers/summarize.py` banao, `main.py` mein include karo |
| Embedding model badalna (OpenAI ka try karna) | Sirf `services/embedding_service.py` badlo, baaki kuch touch nahi hoga |
| LLM provider badalna (Groq se OpenAI) | Sirf `services/llm_service.py` badlo |
| User login/auth add karna | `dependencies/auth.py` banao, jahan chahiye wahan use karo |
| Database add karna | `models/` mein SQLAlchemy models banao |

**Core idea:** Har cheez ka apna specific ghar hai — kisi bhi ek part ko badalne
se doosre parts touch nahi hote. Isi ko "**separation of concerns**" kehte hain.

## Setup

### 1. Virtual environment banao (recommended)
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Dependencies install karo
```bash
pip install -r requirements.txt
```

### 3. .env file banao
```bash
cp .env.example .env
```
Fir `.env` file kholke apni Groq API key daalo (free key: https://console.groq.com):
```
GROQ_API_KEY=your_actual_key_here
```

### 4. Server run karo
```bash
uvicorn app.main:app --reload
```

> Note: Ab command `app.main:app` hai (`app:app` nahi), kyunki `main.py` ab
> `app/` folder ke andar hai.

### 5. Test karo
Browser mein kholo: `http://127.0.0.1:8000/docs`

- `/ingest` — PDF upload karo
- `/ask` — sawaal poocho, jaise: `{"question": "Dispatch Planning kya hai?", "top_k": 3}`

## Request Flow — Ek Sawaal Kaise Process Hota Hai

```
User → POST /ask (routers/ask.py)
              ↓
    services/rag_service.py (ask_question)
              ↓
    services/embedding_service.py → question ko vector mein badla
              ↓
    services/vector_store_service.py → ChromaDB se similar chunks nikale
              ↓
    services/llm_service.py → Groq ko context+question diya, answer mila
              ↓
    schemas/rag_schemas.py (AnswerResponse) → response format hua
              ↓
    User ko JSON answer mila
```

Har layer ka apna kaam hai — router sirf request/response handle karta hai,
service business logic karti hai, schema data ka shape define karta hai.



# MULTI_FORMAT_SUPPORT.md — Multiple File Types Handle Karna

Ab ye RAG system sirf PDF nahi, **PDF, DOCX, TXT, aur Images (JPG/PNG)** sab
handle kar sakta hai.

## Architecture — "Loader" Pattern

```
app/services/
├── document_loader_service.py   → DISPATCHER (extension dekh ke sahi loader choose karta hai)
└── loaders/
    ├── pdf_loader.py             → PDF se text (pypdf)
    ├── docx_loader.py            → Word docs se text (python-docx)
    ├── txt_loader.py             → Plain text files
    └── image_loader.py           → Images se OCR text (pytesseract)
```

**Design principle:** `rag_service.py` ko ye pata hi nahi ki file kaunsa format hai -
wo sirf `document_loader_service.extract_text(file_path)` call karta hai, aur
dispatcher andar se sahi loader chala deta hai. Isse **naya format add karna**
bahut aasan hai - sirf ek naya loader file banao aur dispatcher mein register karo,
baaki KUCH touch nahi karna.

## Setup — Images (OCR) Ke Liye Extra Step

PDF, DOCX, TXT ke liye koi extra setup nahi chahiye - `pip install -r requirements.txt`
se kaam ho jayega.

**Images ke liye, ek system-level program install karna hoga** (Tesseract OCR engine):

1. https://github.com/UB-Mannheim/tesseract/wiki se Windows installer download karo
2. Install karo (default options)
3. `app/services/loaders/image_loader.py` file mein, ye lines UNCOMMENT karo aur
   apna install-path daalo:
```python
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Mac:** `brew install tesseract` (uske baad koi extra config nahi chahiye)
**Linux:** `sudo apt install tesseract-ocr`

## Test Karne Ka Tarika

`/ingest` endpoint mein ab koi bhi supported file bhej sakte ho:

```bash
curl -X POST "http://127.0.0.1:8000/ingest" -F "file=@resume.docx"
curl -X POST "http://127.0.0.1:8000/ingest" -F "file=@notes.txt"
curl -X POST "http://127.0.0.1:8000/ingest" -F "file=@scanned_page.jpg"
```

Agar unsupported format bhejo (jaise `.mp3`), clear error milega:
```json
{ "detail": "Ye format supported nahi hai. Supported formats: .pdf, .docx, .txt, .png, .jpg, .jpeg" }
```

## Naya Format Add Karna Ho (Future) — Example: Excel/.csv

1. `app/services/loaders/csv_loader.py` banao:
```python
import csv

def extract_text(file_path: str) -> str:
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return "\n".join(", ".join(row) for row in reader)
```

2. `document_loader_service.py` mein register karo:
```python
from app.services.loaders import csv_loader
SUPPORTED_LOADERS[".csv"] = csv_loader.extract_text
```

Bas! Koi aur file touch nahi karni padegi.

## OCR Ki Limitation Samajhna Zaroori

- **Image quality** matter karti hai - dhundhla/tedha photo se galat text nikal sakta hai
- **Handwriting** OCR se acche se nahi padhi jati (Tesseract printed text ke liye best hai)
- Agar OCR ka result kharab lage, image ko crop/straighten/higher-resolution karke try karo