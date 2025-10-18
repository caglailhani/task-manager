import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "change-this-in-prod")
    JWTManager(app)

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    # Teşhis: Kayıtlı tüm rotaları göster
    @app.get("/routes")
    def routes():
        return jsonify(sorted([str(r.rule) for r in app.url_map.iter_rules()]))

    # /whoami (JWT zorunlu)
    @app.get("/whoami")
    @jwt_required()
    def whoami():
        return jsonify(get_jwt()), 200

    # Blueprints YALNIZCA burada kayıt edilir
    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from tasks import tasks_bp
    app.register_blueprint(tasks_bp)

    from users import users_bp
    app.register_blueprint(users_bp)

    return app

if __name__ == "__main__":
    # Teşhis: Hangi dosyadan çalışıyoruz?
    print("STARTING APP FROM:", os.path.abspath(__file__))
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
