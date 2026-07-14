import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = "reservas.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                cep TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS espacos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                localizacao TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                espaco_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (espaco_id) REFERENCES espacos(id),
                UNIQUE(usuario_id, espaco_id)
            );

            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                espaco_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                horario TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (espaco_id) REFERENCES espacos(id)
            );
        """)
DATABASE_URL_ORM = "sqlite:///reservas.db"

engine = create_engine(DATABASE_URL_ORM, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
