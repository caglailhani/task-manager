from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import create_user, get_user_by_email, verify_password
import datetime
from users import users_bp


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role = data.get("role","basic")
    if not email or not password:
        return {"msg":"email/password required"}, 400
    try:
        create_user(email, password, role)
        return {"msg":"registered"}, 201
    except Exception as e:
        print("REGISTER_ERROR:", repr(e))
        return {"msg":"email exists or db error"}, 400


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email","")
    password = data.get("password","")
    u = get_user_by_email(email)
    if not u or not verify_password(password, u["password_hash"]):
        return {"msg":"bad credentials"}, 401
    token = create_access_token(
    identity=str(u["id"]),

        additional_claims={"email":u["email"], "role":u["role"]},
        expires_delta=datetime.timedelta(hours=12)
    )
    return jsonify(access_token=token), 200
