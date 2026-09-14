# Commands — Step by Step (Copy-Paste Karo)

Terminal mein project folder ke andar jaake, ye commands **isi order** mein chalao.

## 1. Virtual Environment Banao

Ye isolated Python environment banata hai, taaki tumhare system ke doosre projects se conflict na ho.

```bash
python -m venv venv
```

## 2. Virtual Environment Activate Karo

**Mac/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

Activate hone ke baad terminal ke shuru mein `(venv)` dikhega — matlab sahi environment mein ho.

## 3. Saari Dependencies Install Karo

```bash
pip install -r requirements.txt
```

Isme ye sab install hoga: FastAPI, Uvicorn, ChromaDB, Sentence-Transformers, Groq, PyPDF, python-dotenv.
Pehli baar thoda time lagega (~2-5 min), kyunki `sentence-transformers` heavy hai.

## 4. `.env` File Banao (API Key Ke Liye)

```bash
cp .env.example .env
```

Ab `.env` file ko kisi text editor mein kholo aur apni **Groq API key** daalo:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

**Free key kaise lein:**
1. https://console.groq.com pe jaao
2. Signup/Login karo (free hai)
3. "API Keys" section mein jaake "Create API Key" click karo
4. Jo key mile, wahi `.env` mein paste karo

## 5. Server Start Karo

```bash
uvicorn app.main:app --reload
```

Terminal mein ye dikhna chahiye:
```
[embedding_service] Loading model: all-MiniLM-L6-v2 ...
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

> Pehli baar chalane pe Hugging Face se embedding model download hoga (~80MB) — internet chahiye, ek baar hi hota hai.

## 6. Browser Mein Test Karo

Browser kholo aur jaao:
```
http://127.0.0.1:8000/docs
```

Ye FastAPI ka interactive testing page hai (Swagger UI).

### A) PDF Upload Karo
- `/ingest` endpoint pe click karo
- "Try it out" button dabao
- "Choose File" se `data/dispatch_inventory.pdf` select karo
- "Execute" dabao
- Response mein `"chunks_created": 14` jaisa kuch dikhega — matlab PDF process ho gaya

### B) Sawaal Poocho
- `/ask` endpoint pe click karo
- "Try it out" dabao
- Request body mein likho:
```json
{
  "question": "Dispatch Planning page pe kya hota hai?",
  "top_k": 3
}
```
- "Execute" dabao — niche `answer` aur `sources_used` milega

## Terminal Se Test Karna Ho (curl commands)

Naya terminal tab kholo (server wale terminal ko band mat karo), fir:

**PDF upload:**
```bash
curl -X POST "http://127.0.0.1:8000/ingest" -F "file=@data/dispatch_inventory.pdf"
```

**Sawaal poochna:**
```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "PO receiving kaise hoti hai?", "top_k": 3}'
```

## Server Band Karna Ho Toh

Terminal mein jahan server chal raha hai, wahan dabao:
```
Ctrl + C
```

## Agli Baar Jab Kaam Karna Ho

Sirf ye 2 commands chahiye (venv already bana hua hai):
```bash
source venv/bin/activate      # environment activate karo
uvicorn app.main:app --reload # server start karo
```

## Common Errors Aur Solutions

| Error | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Terminal `final_project/` folder ke andar hona chahiye (jahan `app/` dikh raha ho) |
| `GROQ_API_KEY set nahi hai` | `.env` file check karo, key sahi se paste hui ya nahi |
| `Address already in use` | Port 8000 pe pehle se kuch chal raha hai — `uvicorn app.main:app --reload --port 8001` try karo |
| Model download bahut slow | Internet connection check karo, ya thoda wait karo (ek baar hi hota hai) |
