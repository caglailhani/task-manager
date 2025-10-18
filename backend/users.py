# backend/users.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import get_db

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

def is_admin():
    return get_jwt().get("role") == "admin"

@users_bp.get("")
@jwt_required()
def list_users():
    claims = get_jwt()
    print("USERS_LIST role=", claims.get("role"))  # <-- debug: terminalde görülecek
    if claims.get("role") != "admin":
        return {"msg": "forbidden"}, 403
    with get_db().cursor() as c:
        c.execute("SELECT id, email, role, created_at FROM users ORDER BY id DESC")
        return jsonify(items=c.fetchall()), 200
@users_bp.delete("/<int:uid>")
@jwt_required()
def delete_user(uid: int):
    if not is_admin():
        return {"msg": "forbidden"}, 403
    with get_db().cursor() as c:
        c.execute("DELETE FROM users WHERE id=%s", (uid,))
    return {"msg": "deleted"}, 200
