# models/

Ye folder abhi khali hai kyunki humara RAG system SQL database use nahi karta
(sab kuch ChromaDB mein hai).

**Kab use hoga:** Agar kal tum users, chat history, ya document metadata ko
SQL database (jaise SQLite/PostgreSQL) mein save karna chaho, toh yahan
SQLAlchemy models banoge, jaise:

```python
# models/document.py
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    uploaded_at = Column(String)
```

Isliye ye folder abhi se rakha gaya hai - taaki project **scale** karne pe
sab kuch sahi jagah pe already ready ho.
