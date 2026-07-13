import hashlib
from fastapi import Header, HTTPException


API_KEY_HASH = "aa9c02821247579e02f7c6af1236820c9d8a3f2ebf852685f5cddaf760534257"


def verificar_api_key(x_api_key: str = Header(...)):

    hash_recebido = hashlib.sha256(
        x_api_key.encode()
    ).hexdigest()

    if hash_recebido != API_KEY_HASH:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida."
        )
