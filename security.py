import hashlib
from fastapi import Header, HTTPException


API_KEY_HASH = hashlib.sha256(
    "minha-chave-teste".encode()
).hexdigest()


def verificar_api_key(x_api_key: str = Header(...)):

    hash_recebido = hashlib.sha256(
        x_api_key.encode()
    ).hexdigest()

    if hash_recebido != API_KEY_HASH:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida."
        )
