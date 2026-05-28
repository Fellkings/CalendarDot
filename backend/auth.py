from sqlalchemy.orm import Session
import bcrypt
from backend.models import User

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

def create_user(db: Session, username: str, email: str, password: str, avatar: str):
    try:
        existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return None 
            
        hashed_pwd = get_password_hash(password)
        # Передаем аватар при создании
        db_user = User(username=username, email=email, hashed_password=hashed_pwd, avatar=avatar)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
        
    except Exception as e:
        print(f"❌ ОШИБКА БАЗЫ ДАННЫХ: {e}")
        db.rollback() 
        return None

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user