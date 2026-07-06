from pydantic import BaseModel


class UsuarioEntrada(BaseModel):
    nome: str
    email: str
    senha: str


class Usuario(UsuarioEntrada):
    id: int


class LoginEntrada(BaseModel):
    email: str
    senha: str


class EspacoEntrada(BaseModel):
    nome: str
    descricao: str
    localizacao: str


class Espaco(EspacoEntrada):
    id: int


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