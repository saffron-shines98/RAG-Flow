# Concepts Jo Seekhe — Poori Journey, Code Se Connected

Ye document wo saari cheezein cover karta hai jo humne theory mein seekhi, aur
ye bhi dikhata hai ki **har concept is project ke kis file mein actually use ho raha hai**.

---

## 1. Tokenization

**Kya hai:** Text ko chote pieces (tokens) mein todna, taaki computer numbers mein convert kar sake.

**Is project mein kahan hai:** `app/services/embedding_service.py` ke andar. Jab hum
`model.encode(texts)` call karte hain, `sentence-transformers` library **internally**
tokenization karti hai — hume manually karne ki zarurat nahi padi, kyunki
Hugging Face ka model ye khud sambhalta hai.

---

## 2. Embeddings & Vectors

**Kya hai:** Har text (word/sentence/chunk) ko numbers ki list (vector) mein badalna,
jo uska **meaning** capture karta hai. Similar meaning wale texts ke vectors paas-paas hote hain.

**Is project mein kahan hai:** `app/services/embedding_service.py`
```python
def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    return model.encode(texts).tolist()
```
Hum `all-MiniLM-L6-v2` (Hugging Face model) use kar rahe hain — ye har chunk aur
har question ko 384-dimension ka vector banata hai.

---

## 3. Self-Attention, Positional Encoding, Transformer

**Kya hai:** Ye woh mechanism hai jo Transformer models (jaise humara embedding
model, aur Groq ka LLM) ke **andar** chalta hai — words ke beech relationship
nikalna, order ka pata rakhna.

**Is project mein kahan hai:** Hum ye khud nahi likhte — ye `sentence-transformers`
model ke andar (jab embeddings banti hain) aur Groq ke `llama-3.1` model ke andar
(jab answer generate hota hai) already implemented hai. Humne isse **use** kiya,
banaya nahi — jaise hum car chalate hain bina engine design kiye.

---

## 4. Encoder vs Decoder, BERT vs GPT

**Kya hai:**
- **Encoder** (BERT jaisa) = bidirectional, samajhne ke liye
- **Decoder** (GPT jaisa) = unidirectional, generate karne ke liye

**Is project mein kahan hai:**
- `all-MiniLM-L6-v2` (jo hum embeddings ke liye use kar rahe hain) ek
  **Encoder-only** model hai — kyunki humein sirf text ko "samajhna" hai
  (vector banana), generate nahi karna.
- `llama-3.1-8b-instant` (jo Groq pe chal raha hai) ek **Decoder-only** model
  hai — kyunki humein final **answer generate** karna hai, ek-ek word karke.

Yehi wajah hai ki humne **2 alag models** use kiye — dono ka kaam alag hai.

---

## 5. Causal LM vs Masked LM

**Kya hai:**
- **Causal LM** (GPT/Groq ka model) — sirf peeche dekh ke agla word predict karna seekha
- **Masked LM** (BERT-family models, jaise humara embedding model) — dono taraf dekh ke seekha

**Is project mein kahan hai:** `llm_service.py` ka Groq model **Causal LM** hai
(isliye generate kar pata hai), `embedding_service.py` ka model **understanding**
ke liye train hua hai (Masked-LM family se related architecture).

---

## 6. Context Window, Temperature, Top-k/Top-p

**Kya hai:** LLM ke generation-control settings.

**Is project mein kahan hai:** `app/services/llm_service.py`
```python
response = client.chat.completions.create(
    model=settings.GROQ_MODEL,
    messages=[...],
    temperature=0.2,   # LOW rakha - factual answers chahiye, creative nahi
)
```
Humne **Temperature = 0.2** (low) rakha hai — kyunki hume document se **accurate**
answer chahiye, kavita/story nahi likhwani. Agar ye RAG kisi creative-writing
assistant ke liye hota, temperature 0.7-0.9 rakhte.

**Context Window:** Groq ko hum sirf top-3 relevant chunks bhejte hain (poora document
nahi) — isi wajah se RAG efficient hai, poora context window use nahi hota.

---

## 7. Hugging Face

**Kya hai:** Pre-trained models ka platform — scratch se train karne ki zarurat nahi.

**Is project mein kahan hai:** `all-MiniLM-L6-v2` embedding model seedha
Hugging Face se download hota hai (`sentence-transformers` library ke through) —
`app/services/embedding_service.py` mein.

---

## 8. RAG (Retrieval-Augmented Generation)

**Kya hai:** Pehle relevant info dhoondo (Retrieve), fir usi context ke base pe
answer generate karo (Generate) — isse model ka knowledge-cutoff aur
private-data limitation solve hoti hai.

**Is project mein poora RAG hai — `app/services/rag_service.py` mein:**
```python
def ask_question(question, top_k):
    question_embedding = embed_texts([question])       # 1. Question embed kiya
    relevant_chunks = search_similar_chunks(...)         # 2. RETRIEVAL
    answer = generate_answer(question, relevant_chunks)  # 3. GENERATION (context ke saath)
    return {...}
```
Yehi is **poore project ka core concept** hai — RAG khud.

---

## 9. Vector Database (ChromaDB)

**Kya hai:** Embeddings ko store karne aur semantic search karne ke liye specialized database.

**Is project mein kahan hai:** `app/services/vector_store_service.py`
```python
def search_similar_chunks(query_embedding, top_k):
    collection = client.get_collection(...)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["documents"][0]
```
ChromaDB andar **cosine similarity** jaisi technique use karke, question ke
vector ke sabse "paas" wale chunks dhoondta hai.

---

## 10. Training (Loss Function, Backpropagation)

**Kya hai:** Model apne andar ke numbers (weights) kaise seekhta hai — prediction
karo, galti naapo (loss), peeche jaake numbers adjust karo (backpropagation).

**Is project mein kahan hai:** Hum **koi model train nahi kar rahe** — hum
already-trained models use kar rahe hain (`all-MiniLM-L6-v2` aur `llama-3.1`).
Ye concept humein samjhata hai ki **ye models internally kaise bane** — jo hum
"consume" kar rahe hain API/library ke through.

---

## Poore Project Ka High-Level Flow

```
1. USER PDF UPLOAD KARTA HAI (POST /ingest)
        ↓
2. pdf_service.py       → PDF se text nikala
        ↓
3. chunking_service.py  → text ko chote chunks mein toda
        ↓
4. embedding_service.py → har chunk ka EMBEDDING (vector) banaya (Hugging Face)
        ↓
5. vector_store_service.py → ChromaDB mein store kiya
        ↓
=========================================================
6. USER SAWAAL POOCHTA HAI (POST /ask)
        ↓
7. embedding_service.py → sawaal ka bhi embedding banaya
        ↓
8. vector_store_service.py → SEMANTIC SEARCH se relevant chunks nikale
        ↓
9. llm_service.py → Groq ke DECODER-ONLY model (Causal LM) ko context+question diya
        ↓
10. Model ne ATTENTION mechanism se context samjha, ek-ek TOKEN generate kiya
        ↓
11. Final ANSWER user ko mila
```

---

## Architecture Ka Design Pattern

Ye project **layered architecture** follow karta hai:

```
routers/     → "kya request aayi, kya response bhejni hai" (HTTP layer)
services/    → "asli kaam kaise hoga" (business logic layer)
schemas/     → "data ka shape kaisa hoga" (validation layer)
core/        → "settings kahan se aayengi" (config layer)
```

Ye pattern isliye use kiya kyunki:
- Har layer ka apna specific kaam hai (**separation of concerns**)
- Kal koi ek part badalna ho (jaise embedding model), baaki sab safe rehta hai
- Naye developer ko samajhna aasan hota hai — "answer generate karna hai? services/llm_service.py dekho"

---

## One-Page Mega Summary

| Seekha Kya | Kahan Use Hua |
|---|---|
| Tokenization | `sentence-transformers` ke andar (automatic) |
| Embeddings/Vectors | `embedding_service.py` |
| Attention/Transformer | Model ke andar (Hugging Face + Groq dono) |
| Encoder (BERT-family) | Embedding model (samajhna) |
| Decoder (GPT-family) | Groq LLM (generate karna) |
| Context Window | Sirf top-k chunks bheje, poora document nahi |
| Temperature | 0.2 rakha — factual answers ke liye |
| Hugging Face | Embedding model yahi se aaya |
| RAG | Poora project isi pe based hai |
| Vector DB (ChromaDB) | `vector_store_service.py` |
| FastAPI + Scalable Structure | Poora `app/` folder |


# UPGRADE_NOTES.md — Multi-Document Aur Conversation Memory

Ye 2 naye features add kiye gaye hain jo real-world RAG systems mein zaroori hote hain.

## 1. Multi-Document Support

**Pehle problem:** Naya PDF upload karne pe, purana poora data delete ho jata tha.

**Ab kya hota hai:** Har PDF ka data, uske **filename ke metadata tag** ke saath
ChromaDB mein store hota hai. Multiple PDFs ek saath rakhe ja sakte hain.

**Kaise check karo kaunsi PDFs upload hain:**
```
GET /documents
```
Response:
```json
{ "documents": ["dispatch_inventory.pdf", "offer_letter.pdf"] }
```

**Ek specific PDF tak search limit karna ho:**
`/ask` request mein `source_filter` do:
```json
{
  "question": "Salary kitni hai?",
  "source_filter": "offer_letter.pdf"
}
```
Agar `source_filter` nahi doge, toh search **sabhi uploaded PDFs** mein hoga
(jo bhi sabse relevant chunk milega, wahi use hoga - chahe kisi bhi PDF se ho).

> **Important:** Agar tumhara purana `chroma_store/` folder already bana hua hai
> (pehle wale run se), use delete kar do ek baar, taaki purana bina-metadata wala
> data conflict na kare:
> ```bash
> rm -rf chroma_store
> ```
> Fir dobara `/ingest` se apni PDFs upload karo.

## 2. Conversation Memory (Session-Based)

**Pehle problem:** Har `/ask` call independent thi - follow-up sawaal poochne
pe model ko pichli baat yaad nahi rehti thi.

**Ab kya hota hai:** Har request mein ek `session_id` bhejo. Same `session_id`
use karne pe, model ko **pichli conversation yaad rahegi**.

**Example flow:**
```json
// Request 1
{ "question": "Ye kis company ka offer letter hai?", "session_id": "chat_001" }
// Answer: "Chetu company ka hai."

// Request 2 - SAME session_id
{ "question": "Uska address kya hai?", "session_id": "chat_001" }
// Model samajhta hai "uska" = Chetu company, kyunki pichli baat yaad hai
```

Agar `session_id` nahi doge, `"default"` use hota hai - matlab agar tum
alag-alag `session_id` nahi bhejte, toh sabki conversation ek hi memory mein
mix ho jayegi.

**Session reset karna ho (naya conversation shuru karna):**
```
POST /ask/reset
{ "session_id": "chat_001" }
```

### Limitation Jo Samajhni Zaroori Hai

Ye memory abhi **RAM mein** hai (`memory_service.py` mein ek Python dictionary).
Matlab:
- ✅ Server chalte time conversation yaad rahegi
- ❌ Server restart hote hi (jaise `--reload` trigger hone pe code change se),
  saari memory **khatam** ho jayegi

Production apps mein isko **Redis** ya **Database** mein store karte hain
(persistent). Learning ke liye, in-memory version samajhna sabse aasan hai -
concept wahi rehta hai, sirf storage jagah badalti hai.

## Updated API Endpoints

| Method | Endpoint | Kaam |
|---|---|---|
| POST | `/ingest` | PDF upload karo (ab multi-doc support ke saath) |
| GET | `/documents` | Kaunsi PDFs abhi tak upload hain, dekhna |
| POST | `/ask` | Sawaal poocho (session_id aur source_filter optional) |
| POST | `/ask/reset` | Kisi session ki memory clear karna |

## Naye Concepts Jo Seekhe

| Concept | Kya Hai | Kahan Hai |
|---|---|---|
| **Metadata Filtering** | Vector DB mein har record ke saath extra info (tags) store karna, aur search ko us tag tak limit karna | `vector_store_service.py` |
| **Session Management** | Har conversation ko ek unique ID se track karna | `memory_service.py`, `session_id` field |
| **Conversation Memory** | Chat history ko LLM ko dobara bhejna, taaki wo context samjhe | `llm_service.py` (messages list mein history add hoti hai) |