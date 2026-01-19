from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.db import SessionLocal
from app.models import (
    EmpresaUsuario,
    PortalUsuario,
    EmpresaEvento,
    CotacaoCoupa
)
from app.schemas import (
    LoginRequest,
    UsuarioResponse,
    PortalUsuarioCreate,
    PortalUsuarioResponse,
    OrcamentoResponse,
    AtualizarStatusEventoRequest
)

from crypto_utils import Encrypta

app = FastAPI(title="API PowerJob")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Dependency - Banco
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# Health Check
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}

# =========================
# Buscar usuário por ID
# =========================
@app.get("/usuarios/{idusuario}", response_model=UsuarioResponse)
def obter_usuario(idusuario: int, db: Session = Depends(get_db)):
    usuario = (
        db.query(EmpresaUsuario)
        .filter(EmpresaUsuario.idusuario == idusuario)
        .first()
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    return usuario

# =========================
# LOGIN (email + senha PLANA)
# =========================
@app.post("/login", response_model=UsuarioResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    usuario = (
        db.query(EmpresaUsuario)
        .filter(EmpresaUsuario.email == dados.email)
        .filter(EmpresaUsuario.stativo == 1)
        .first()
    )

    if not usuario or dados.senha != usuario.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos"
        )

    return usuario


@app.post("/portais/usuarios", response_model=PortalUsuarioResponse)
def criar_portal_usuario(
    dados: PortalUsuarioCreate,
    db: Session = Depends(get_db)
):
    # Verifica duplicidade de login por portal
    existe = (
        db.query(PortalUsuario)
        .filter(PortalUsuario.login == dados.login)
        .filter(PortalUsuario.idportal == dados.idportal)
        .first()
    )

    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login já existe para este portal"
        )

    # 🔐 CRIPTOGRAFA A SENHA USANDO SEU MÉTODO
    senha_encriptada = Encrypta(dados.senha)

    novo_usuario = PortalUsuario(
        idempresa=dados.idempresa,
        idportal=dados.idportal,
        login=dados.login,
        senha_hash=senha_encriptada,
        stativo=dados.stativo,
        dtcriacao=datetime.utcnow()
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario

@app.get(
    "/empresas/{idempresa}/orcamentos",
    response_model=List[OrcamentoResponse]
)
def listar_orcamentos_empresa(
    idempresa: int,
    db: Session = Depends(get_db)
):
    resultados = (
        db.query(
            EmpresaEvento.idempresa,
            EmpresaEvento.idevento,
            CotacaoCoupa.descricao,
            CotacaoCoupa.detalhes,
            CotacaoCoupa.quantidade,
            CotacaoCoupa.dtinicio,
            CotacaoCoupa.dtfim,
            EmpresaEvento.idstatus,
        )
        .join(
            CotacaoCoupa,
            CotacaoCoupa.idevento == EmpresaEvento.idevento
        )
        .filter(EmpresaEvento.idempresa == idempresa)
        .all()
    )

    return resultados


@app.put(
    "/empresas/{idempresa}/eventos/{idevento}/status",
    status_code=status.HTTP_204_NO_CONTENT
)
def atualizar_status_evento(
    idempresa: int,
    idevento: int,
    dados: AtualizarStatusEventoRequest,
    db: Session = Depends(get_db)
):
    evento = (
        db.query(EmpresaEvento)
        .filter(EmpresaEvento.idempresa == idempresa)
        .filter(EmpresaEvento.idevento == idevento)
        .filter(EmpresaEvento.idportal == dados.idportal)
        .first()
    )

    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado para os parâmetros informados"
        )

    evento.idstatus = dados.idstatus
    db.commit()

