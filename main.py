from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List

from database import get_conn, init_db
from models import (
    Usuario, UsuarioEntrada, LoginEntrada,
    Espaco, EspacoEntrada
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="API Reservas Públicas",
    version="1.0.0",
    lifespan=lifespan
)

# ═══════════════════ RAIZ ═══════════════════

@app.get("/")
def raiz():
    return {"mensagem": "API Reservas Públicas"}

# ═══════════════════ USUÁRIOS ═══════════════════

@app.post("/usuarios", response_model=Usuario, status_code=201)
def criar_usuario(dados: UsuarioEntrada):

    with get_conn() as conn:

        if len(dados.senha) < 6:
            raise HTTPException(
                status_code=400,
                detail="Senha deve possuir no mínimo 6 caracteres."
            )

        cur = conn.execute(
            """
            INSERT INTO usuarios(nome,email,senha)
            VALUES(?,?,?)
            """,
            (dados.nome, dados.email, dados.senha)
        )

        conn.commit()

    return Usuario(id=cur.lastrowid, **dados.model_dump())


@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios():

    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()

    return [Usuario(**dict(r)) for r in rows]


@app.get("/usuarios/{id}", response_model=Usuario)
def buscar_usuario(id: int):

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id=?",
            (id,)
        ).fetchone()

    if row is None:
        raise HTTPException(404, "Usuário não encontrado")

    return Usuario(**dict(row))


@app.post("/login")
def login(dados: LoginEntrada):

    with get_conn() as conn:

        usuario = conn.execute(
            """
            SELECT * FROM usuarios
            WHERE email=? AND senha=?
            """,
            (dados.email, dados.senha)
        ).fetchone()

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha inválidos."
        )

    return {"mensagem": "Login realizado com sucesso!"}

# ═══════════════════ ESPAÇOS ═══════════════════

@app.post("/espacos", response_model=Espaco, status_code=201)
def criar_espaco(dados: EspacoEntrada):

    with get_conn() as conn:

        cur = conn.execute(
            """
            INSERT INTO espacos(nome,descricao,localizacao)
            VALUES(?,?,?)
            """,
            (
                dados.nome,
                dados.descricao,
                dados.localizacao
            )
        )

        conn.commit()

    return Espaco(id=cur.lastrowid, **dados.model_dump())


@app.get("/espacos", response_model=List[Espaco])
def listar_espacos():

    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM espacos").fetchall()

    return [Espaco(**dict(r)) for r in rows]


@app.get("/espacos/{id}", response_model=Espaco)
def buscar_espaco(id: int):

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM espacos WHERE id=?",
            (id,)
        ).fetchone()

    if row is None:
        raise HTTPException(404, "Espaço não encontrado")

    return Espaco(**dict(row))