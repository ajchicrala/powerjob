from pydantic import BaseModel, EmailStr
from datetime import date

class CriarStatusHistoricoRequest(BaseModel):
    idempresa: int
    idevento: int
    idportal: int
    idstatus_anterior: int
    idstatus_atual: int
    idusuario: int

class AtualizarStatusEventoRequest(BaseModel):
    idportal: int
    idstatus: int

class OrcamentoResponse(BaseModel):
    idempresa: int
    idevento: int
    descricao: str
    detalhes: str
    quantidade: int
    dtinicio: date
    dtfim: date
    idstatus: int

class PortalUsuarioCreate(BaseModel):
    idempresa: int
    idportal: int
    login: str
    senha: str
    stativo: int = 1

class PortalUsuarioResponse(BaseModel):
    idportalusuario: int
    idempresa: int
    idportal: int
    login: str
    stativo: int

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResponse(BaseModel):
    idusuario: int
    idempresa: int
    idtipo: int
    nome: str
    email: str
    stativo: int

class Config:
    from_attributes = True
