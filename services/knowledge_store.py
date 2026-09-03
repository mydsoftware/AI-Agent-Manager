from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

class KnowledgeStore:
    """Knowledge Base سبک و قابل مهاجرت با جستجوی متنی SQLite."""
    SCOPES={"global","workspace","project","agent"}
    def __init__(self,database_path: str="data/manager.db") -> None:
        self.database_path=Path(database_path); self.database_path.parent.mkdir(parents=True,exist_ok=True); self._initialize()
    def _connect(self):
        db=sqlite3.connect(self.database_path); db.row_factory=sqlite3.Row; return db
    def _initialize(self):
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS knowledge_documents (id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, scope_id TEXT NOT NULL DEFAULT '', title TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'manual', mime_type TEXT NOT NULL DEFAULT 'text/plain', content TEXT NOT NULL, metadata TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_scope ON knowledge_documents(scope,scope_id)")
    def add(self,scope:str,scope_id:str,title:str,content:str,source:str="manual",mime_type:str="text/plain",metadata:dict[str,Any]|None=None)->dict[str,Any]:
        import json
        scope=scope.strip().lower(); title=title.strip(); content=content.strip()
        if scope not in self.SCOPES: raise ValueError("scope نامعتبر است.")
        if not title or not content: raise ValueError("title و content الزامی هستند.")
        with self._connect() as db:
            cur=db.execute("INSERT INTO knowledge_documents(scope,scope_id,title,source,mime_type,content,metadata) VALUES(?,?,?,?,?,?,?)",(scope,scope_id.strip(),title,source.strip() or "manual",mime_type.strip() or "text/plain",content,json.dumps(metadata or {},ensure_ascii=False,default=str)))
            row=db.execute("SELECT * FROM knowledge_documents WHERE id=?",(cur.lastrowid,)).fetchone()
        return self._row(row)
    def list(self,scope:str|None=None,scope_id:str|None=None,limit:int=100)->list[dict[str,Any]]:
        q="SELECT id,scope,scope_id,title,source,mime_type,metadata,created_at,updated_at FROM knowledge_documents"; p=[]; w=[]
        if scope: w.append("scope=?"); p.append(scope)
        if scope_id is not None: w.append("scope_id=?"); p.append(scope_id)
        if w:q+=" WHERE "+" AND ".join(w)
        q+=" ORDER BY updated_at DESC LIMIT ?";p.append(max(1,min(int(limit),500)))
        with self._connect() as db: rows=db.execute(q,p).fetchall()
        return [self._row(r) for r in rows]
    def search(self,query:str,scope:str|None=None,scope_id:str|None=None,limit:int=20)->list[dict[str,Any]]:
        terms=[t for t in query.lower().split() if len(t)>1]
        if not terms:return []
        with self._connect() as db:
            rows=db.execute("SELECT * FROM knowledge_documents ORDER BY updated_at DESC").fetchall()
        result=[]
        for row in rows:
            item=self._row(row)
            if scope and item["scope"]!=scope: continue
            if scope_id is not None and item["scope_id"]!=scope_id: continue
            hay=(item["title"]+" "+item["content"]).lower(); score=sum(hay.count(t) for t in terms)
            if score: item["score"]=score; result.append(item)
        return sorted(result,key=lambda x:(-x["score"],x["updated_at"]))[:max(1,min(int(limit),100))]
    def get(self,document_id:int):
        with self._connect() as db: row=db.execute("SELECT * FROM knowledge_documents WHERE id=?",(document_id,)).fetchone()
        return self._row(row) if row else None
    def delete(self,document_id:int)->bool:
        with self._connect() as db: cur=db.execute("DELETE FROM knowledge_documents WHERE id=?",(document_id,))
        return cur.rowcount>0
    @staticmethod
    def _row(row):
        import json
        item=dict(row); item["metadata"]=json.loads(item["metadata"] or "{}"); return item
