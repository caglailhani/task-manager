# backend/tasks.py
import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import get_db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")

@tasks_bp.get("")
@jwt_required()
def list_tasks():
    claims = get_jwt()
    role = claims.get("role")
    email = claims.get("email")
    with get_db().cursor() as c:
        if role == "admin":
            c.execute("""SELECT t.*, u.email AS owner_email
                         FROM tasks t JOIN users u ON u.id=t.user_id
                         ORDER BY t.created_at DESC""")
        else:
            c.execute("""SELECT t.*, u.email AS owner_email
                         FROM tasks t JOIN users u ON u.id=t.user_id
                         WHERE u.email=%s
                         ORDER BY t.created_at DESC""", (email,))
        return jsonify(items=c.fetchall()), 200

@tasks_bp.post("")
@jwt_required()
def create_task():
    d = request.get_json() or {}
    title = d.get("title")
    if not title:
        return {"msg":"title required"}, 400
    desc = d.get("description","")
    status = d.get("status","todo")
    email = get_jwt().get("email")

    with get_db().cursor() as c:
        c.execute("SELECT id FROM users WHERE email=%s", (email,))
        u = c.fetchone()
        if not u: return {"msg":"user not found"}, 404
        c.execute("""INSERT INTO tasks(title,description,status,user_id,created_at)
                     VALUES(%s,%s,%s,%s,%s)""",
                  (title, desc, status, u["id"], datetime.datetime.utcnow()))
    return {"msg":"created"}, 201

@tasks_bp.put("/<int:tid>")
@jwt_required()
def update_task(tid):
    d = request.get_json() or {}
    title = d.get("title")
    desc  = d.get("description")
    status= d.get("status","todo")
    claims = get_jwt()
    role = claims.get("role")
    email = claims.get("email")

    with get_db().cursor() as c:
        c.execute("""SELECT t.id, u.email AS owner_email
                     FROM tasks t JOIN users u ON u.id=t.user_id
                     WHERE t.id=%s""", (tid,))
        row = c.fetchone()
        if not row: return {"msg":"not found"}, 404
        if role != "admin" and row["owner_email"] != email:
            return {"msg":"forbidden"}, 403
        c.execute("""UPDATE tasks
                     SET title=%s, description=%s, status=%s, updated_at=%s
                     WHERE id=%s""",
                  (title, desc, status, datetime.datetime.utcnow(), tid))
    return {"msg":"updated"}, 200

@tasks_bp.delete("/<int:tid>")
@jwt_required()
def delete_task(tid):
    claims = get_jwt()
    role = claims.get("role")
    email = claims.get("email")
    with get_db().cursor() as c:
        c.execute("""SELECT t.id, u.email AS owner_email
                     FROM tasks t JOIN users u ON u.id=t.user_id
                     WHERE t.id=%s""", (tid,))
        row = c.fetchone()
        if not row: return {"msg":"not found"}, 404
        if role != "admin" and row["owner_email"] != email:
            return {"msg":"forbidden"}, 403
        c.execute("DELETE FROM tasks WHERE id=%s", (tid,))
    return {"msg":"deleted"}, 200
