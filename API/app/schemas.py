from pydantic import BaseModel, EmailStr

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
