from passlib.context import CryptContext

# 配置密码加密工具：使用 bcrypt 算法（最安全、最常用）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 明文密码 → 哈希密码（存数据库用）
def get_hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)
