from fastapi import FastAPI, HTTPException, Depends
from typing import List
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from security import verificar_api_key
from database import (get_conn, init_db, engine, Base, get_session)
from models import(
    Usuario,
    UsuarioEntrada,
    LoginEntrada,
    Espaco,
    EspacoEntrada,
    Reserva,
    ReservaEntrada,
    Solicitacao,
    SolicitacaoEntrada,
    UsuarioModel,
    EspacoModel
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="API Reservas Públicas",
    version="1.0.0",
    lifespan=lifespan
)

#------raiz------

@app.get("/")
def raiz():
    return {"mensagem": "API de Reservas funcionando!"}

#------usuários------

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
                INSERT INTO usuarios(nome,email,senha,cep)
                VALUES(?,?,?,?)
                """,
                (dados.nome, dados.email, dados.senha, dados.cep)
            )

            conn.commit()

        except Exception as erro:
            raise HTTPException(
                status_code=400,
                detail=str(erro)
            )


    return Usuario(
        id=cur.lastrowid,
        **dados.model_dump()
    )

@app.get("/usuarios", response_model=List[Usuario])
def listar_usuarios(session: Session = Depends(get_session)):
    return session.query(UsuarioModel).all()

@app.get("/usuarios/{id}", response_model=Usuario)
def buscar_usuario(id:int):

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id=?",
            (id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return Usuario(**dict(row))

@app.put("/usuarios/{id}", response_model=Usuario)
def editar_usuario(id:int, dados:UsuarioEntrada):

    with get_conn() as conn:
        res = conn.execute(
            """
            UPDATE usuarios
            SET nome=?, email=?, senha=?, cep=?
            WHERE id=?
            """,
            (dados.nome, dados.email, dados.senha, dados.cep, id)
        )

        conn.commit()

    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return Usuario(
        id=id,
        **dados.model_dump()
    )

@app.delete("/usuarios/{id}", status_code=204,dependencies=[Depends(verificar_api_key)])
def remover_usuario(id:int):

    with get_conn() as conn:
        res = conn.execute(
            """
            DELETE FROM usuarios
            WHERE id=?
            """,
            (id,)
        )

        conn.commit()

    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

@app.post("/login")
def login(dados:LoginEntrada):

    with get_conn() as conn:
        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
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

#------espaços------

@app.post("/espacos", response_model=Espaco, status_code=201)
def criar_espaco(dados:EspacoEntrada):

    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO espacos(nome,descricao,localizacao)
            VALUES(?,?,?)
            """,
            (dados.nome, dados.descricao, dados.localizacao)
        )

        conn.commit()


    return Espaco(
        id=cur.lastrowid,
        **dados.model_dump()
    )

@app.get("/espacos", response_model=List[Espaco])
def listar_espacos(session:Session = Depends(get_session)):

    return session.query(
        EspacoModel
    ).all()

@app.get("/espacos/{id}", response_model=Espaco)
def buscar_espaco(id:int):

    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM espacos WHERE id=?",
            (id,)
        ).fetchone()


    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Espaço não encontrado."
        )

    return Espaco(**dict(row))

@app.put("/espacos/{id}", response_model=Espaco)
def editar_espaco(id:int, dados:EspacoEntrada):

    with get_conn() as conn:
        res = conn.execute(
            """
            UPDATE espacos
            SET nome=?, descricao=?, localizacao=?
            WHERE id=?
            """,
            (dados.nome, dados.descricao, dados.localizacao, id)
        )

        conn.commit()

    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Espaço não encontrado."
        )

    return Espaco(
        id=id,
        **dados.model_dump()
    )

@app.delete("/espacos/{id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def remover_espaco(id:int):

    with get_conn() as conn:
        res = conn.execute(
            """
            DELETE FROM espacos
            WHERE id=?
            """,
            (id,)
        )

        conn.commit()


    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Espaço não encontrado."
        )
    
#------reservas------

@app.post("/reservas", response_model=Reserva, status_code=201)
def criar_reserva(dados: ReservaEntrada):

    with get_conn() as conn:

        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id=?
            """,
            (dados.usuario_id,)
        ).fetchone()


        if usuario is None:

            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado."
            )


        espaco = conn.execute(
            """
            SELECT *
            FROM espacos
            WHERE id=?
            """,
            (dados.espaco_id,)
        ).fetchone()


        if espaco is None:

            raise HTTPException(
                status_code=404,
                detail="Espaço não encontrado."
            )


        reserva_existente = conn.execute(
            """
            SELECT *
            FROM reservas
            WHERE usuario_id=?
            AND espaco_id=?
            """,
            (
                dados.usuario_id,
                dados.espaco_id
            )
        ).fetchone()


        if reserva_existente:

            raise HTTPException(
                status_code=409,
                detail="Reserva já existente para este usuário e espaço."
            )


        cur = conn.execute(
            """
            INSERT INTO reservas(usuario_id, espaco_id)
            VALUES(?,?)
            """,
            (
                dados.usuario_id,
                dados.espaco_id
            )
        )

        conn.commit()


    return Reserva(
        id=cur.lastrowid,
        **dados.model_dump()
    )



@app.get("/usuarios/{id}/espacos", response_model=List[Espaco])
def espacos_do_usuario(id:int):

    with get_conn() as conn:

        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id=?
            """,
            (id,)
        ).fetchone()


        if usuario is None:

            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado."
            )


        rows = conn.execute(
            """
            SELECT e.*
            FROM espacos e
            INNER JOIN reservas r
            ON e.id = r.espaco_id
            WHERE r.usuario_id=?
            """,
            (id,)
        ).fetchall()


    return [
        Espaco(**dict(row))
        for row in rows
    ]

@app.get("/espacos/{id}/usuarios", response_model=List[Usuario])
def usuarios_do_espaco(id:int):

    with get_conn() as conn:
        espaco = conn.execute(
            """
            SELECT *
            FROM espacos
            WHERE id=?
            """,
            (id,)
        ).fetchone()

        if espaco is None:
            raise HTTPException(
                status_code=404,
                detail="Espaço não encontrado."
            )

        rows = conn.execute(
            """
            SELECT u.*
            FROM usuarios u
            INNER JOIN reservas r
            ON u.id = r.usuario_id
            WHERE r.espaco_id=?
            """,
            (id,)
        ).fetchall()


    return [
        Usuario(**dict(row))
        for row in rows
    ]

@app.delete("/reservas/{id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def cancelar_reserva(id:int):

    with get_conn() as conn:
        res = conn.execute(
            """
            DELETE FROM reservas
            WHERE id=?
            """,
            (id,)
        )

        conn.commit()


    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Reserva não encontrada."
        )

#------solicitações------

@app.post("/solicitacoes", response_model=Solicitacao, status_code=201)
def criar_solicitacao(dados:SolicitacaoEntrada):

    with get_conn() as conn:
        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
            WHERE id=?
            """,
            (dados.usuario_id,)
        ).fetchone()

        if usuario is None:
            raise HTTPException(
                status_code=404,
                detail="Usuário não encontrado."
            )

        espaco = conn.execute(
            """
            SELECT *
            FROM espacos
            WHERE id=?
            """,
            (dados.espaco_id,)
        ).fetchone()

        if espaco is None:
            raise HTTPException(
                status_code=404,
                detail="Espaço não encontrado."
            )

        cur = conn.execute(
            """
            INSERT INTO solicitacoes
            (usuario_id, espaco_id, data, horario, status)
            VALUES(?,?,?,?,?)
            """,
            (dados.usuario_id, dados.espaco_id, dados.data, dados.horario, "pendente")
        )

        conn.commit()


    return Solicitacao(
        id=cur.lastrowid,
        status="pendente",
        **dados.model_dump()
    )



@app.get("/solicitacoes", response_model=List[Solicitacao])
def listar_solicitacoes():

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM solicitacoes
            """
        ).fetchall()


    return [
        Solicitacao(**dict(row))
        for row in rows
    ]



@app.get("/solicitacoes/{id}", response_model=Solicitacao)
def buscar_solicitacao(id:int):

    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM solicitacoes
            WHERE id=?
            """,
            (id,)
        ).fetchone()


    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Solicitação não encontrada."
        )


    return Solicitacao(**dict(row))



@app.put("/solicitacoes/{id}")
def atualizar_status(id:int, status:str):

    if status not in ["aprovada", "recusada"]:
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



@app.delete("/solicitacoes/{id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def remover_solicitacao(id:int):

    with get_conn() as conn:
        res = conn.execute(
            """
            DELETE FROM solicitacoes
            WHERE id=?
            """,
            (id,)
        )

        conn.commit()

    if res.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Solicitação não encontrada."
        )
