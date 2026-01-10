from pydantic import BaseModel, EmailStr

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
