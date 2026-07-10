from fastapi import Depends
from security import verificar_api_key
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List

from database import get_conn, init_db
from models import (
    Usuario,
    UsuarioEntrada,
    LoginEntrada,
    Espaco,
    EspacoEntrada,
    Solicitacao,
    SolicitacaoEntrada
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

        try:
            cur = conn.execute(
                """
                INSERT INTO usuarios(nome,email,senha)
                VALUES(?,?,?)
                """,
                (dados.nome, dados.email, dados.senha)
            )

            conn.commit()

        except Exception:
            raise HTTPException(
                status_code=400,
                detail="E-mail já cadastrado."
            )

    return Usuario(
        id=cur.lastrowid,
        **dados.model_dump()
    )


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

    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": dict(usuario)
    }
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

@app.post("/solicitacoes", response_model=Solicitacao, status_code=201)
def criar_solicitacao(dados: SolicitacaoEntrada):

    with get_conn() as conn:

        cur = conn.execute(
            """
            INSERT INTO solicitacoes
            (usuario_id, espaco_id, data, horario, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                dados.usuario_id,
                dados.espaco_id,
                dados.data,
                dados.horario,
                "Pendente"
            )
        )

        conn.commit()

    return Solicitacao(
        id=cur.lastrowid,
        status="Pendente",
        **dados.model_dump()
    )
    
@app.get("/solicitacoes", response_model=list[Solicitacao])
def listar_solicitacoes():

    with get_conn() as conn:

        rows = conn.execute(
            "SELECT * FROM solicitacoes"
        ).fetchall()

    return [Solicitacao(**dict(r)) for r in rows]
@app.put("/solicitacoes/{id}")
def atualizar_status(id: int, status: str):

    if status not in ["Aprovada", "Recusada"]:

        raise HTTPException(
            status_code=400,
            detail="Status inválido."
        )

    with get_conn() as conn:

        res = conn.execute(
            """
            UPDATE solicitacoes
            SET status=?
            WHERE id=?
            """,
            (status, id)
        )

        conn.commit()

    if res.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Solicitação não encontrada."
        )

    return {"mensagem": "Status atualizado."}

@app.delete("/usuarios/{id}", status_code=204)
def remover_usuario(id: int):

    with get_conn() as conn:

        res = conn.execute(
            "DELETE FROM usuarios WHERE id=?",
            (id,)
        )

        conn.commit()

    if res.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )
@app.delete("/espacos/{id}", status_code=204)
def remover_espaco(id: int):

    with get_conn() as conn:

        res = conn.execute(
            "DELETE FROM espacos WHERE id=?",
            (id,)
        )

        conn.commit()

    if res.rowcount == 0:

        raise HTTPException(
            status_code=404,
            detail="Espaço não encontrado."
        )
