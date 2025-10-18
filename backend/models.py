import os, bcrypt, pymysql
from dotenv import load_dotenv
load_dotenv()

def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST","127.0.0.1"),
        port=int(os.getenv("DB_PORT","3306")),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASS","changeme"),
        database=os.getenv("DB_NAME","taskdb"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def create_user(email: str, password: str, role: str = "basic"):
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with get_db().cursor() as c:
        c.execute("INSERT INTO users(email,password_hash,role) VALUES(%s,%s,%s)",
                  (email, pw_hash, role))

def get_user_by_email(email: str):
    with get_db().cursor() as c:
        c.execute("SELECT id,email,password_hash,role,created_at FROM users WHERE email=%s",(email,))
        return c.fetchone()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
