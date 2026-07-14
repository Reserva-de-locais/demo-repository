from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text
from database import Base

class UsuarioEntrada(BaseModel):
    nome: str
    email: str
    senha: str
    cep: str

class Usuario(UsuarioEntrada):
    id: int
    model_config = {"from_attributes": True}

class LoginEntrada(BaseModel):
    email: str
    senha: str

class EspacoEntrada(BaseModel):
    nome: str
    descricao: str
    localizacao: str

class Espaco(EspacoEntrada):
    id: int
    model_config = {"from_attributes": True}

class ReservaEntrada(BaseModel):
    usuario_id: int
    espaco_id: int

class Reserva(ReservaEntrada):
    id: int

class SolicitacaoEntrada(BaseModel):
    usuario_id: int
    espaco_id: int
    data: str
    horario: str

class Solicitacao(SolicitacaoEntrada):
    id: int
    status: str

class UsuarioModel(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    senha = Column(String(100), nullable=False)
    cep = Column(String(20), nullable=False)

class EspacoModel(Base):
    __tablename__ = "espacos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    localizacao = Column(String(200), nullable=False)
