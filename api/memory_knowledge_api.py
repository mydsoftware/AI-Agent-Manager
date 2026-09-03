from __future__ import annotations
from flask import Flask, jsonify, request
from services.memory_store import MemoryStore
from services.knowledge_store import KnowledgeStore

def register_memory_knowledge_api(app: Flask, database_path: str = "data/manager.db") -> None:
    memories, knowledge = MemoryStore(database_path), KnowledgeStore(database_path)

    @app.get("/api/memory")
    def list_memory():
        try: return jsonify(memories.list(request.args.get("scope"), request.args.get("scope_id"), request.args.get("limit",100)))
        except ValueError as e: return jsonify({"error":str(e)}),400

    @app.post("/api/memory")
    def save_memory():
        p=request.get_json(silent=True) or {}
        try: return jsonify(memories.upsert(str(p.get("scope","project")),str(p.get("scope_id","")),str(p.get("key","")),p.get("value"),int(p.get("importance",5)),str(p.get("source","user")))),201
        except (ValueError,TypeError) as e: return jsonify({"error":str(e)}),400

    @app.get("/api/memory/<int:memory_id>")
    def get_memory(memory_id):
        item=memories.get(memory_id); return jsonify(item) if item else (jsonify({"error":"حافظه پیدا نشد."}),404)

    @app.delete("/api/memory/<int:memory_id>")
    def delete_memory(memory_id):
        return jsonify({"deleted":memories.delete(memory_id),"id":memory_id})

    @app.get("/api/knowledge")
    def list_knowledge():
        return jsonify(knowledge.list(request.args.get("scope"),request.args.get("scope_id"),request.args.get("limit",100)))

    @app.post("/api/knowledge")
    def add_knowledge():
        p=request.get_json(silent=True) or {}
        try:
            item=knowledge.add(str(p.get("scope","project")),str(p.get("scope_id","")),str(p.get("title","")),str(p.get("content","")),str(p.get("source","manual")),str(p.get("mime_type","text/plain")),p.get("metadata") if isinstance(p.get("metadata"),dict) else {})
            return jsonify(item),201
        except ValueError as e: return jsonify({"error":str(e)}),400

    @app.get("/api/knowledge/search")
    def search_knowledge():
        q=str(request.args.get("q","")).strip()
        if not q:return jsonify({"error":"q الزامی است."}),400
        return jsonify(knowledge.search(q,request.args.get("scope"),request.args.get("scope_id"),request.args.get("limit",20)))

    @app.get("/api/knowledge/<int:document_id>")
    def get_knowledge(document_id):
        item=knowledge.get(document_id); return jsonify(item) if item else (jsonify({"error":"سند پیدا نشد."}),404)

    @app.delete("/api/knowledge/<int:document_id>")
    def delete_knowledge(document_id):
        return jsonify({"deleted":knowledge.delete(document_id),"id":document_id})
