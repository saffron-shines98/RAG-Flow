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
