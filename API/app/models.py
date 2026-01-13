from sqlalchemy import Column, Integer, String, DateTime
from app.db import Base

class PortalUsuario(Base):
    __tablename__ = "portais_usuarios"

    idportalusuario = Column(Integer, primary_key=True, index=True)
    idempresa = Column(Integer, nullable=False)
    idportal = Column(Integer, nullable=False)
    login = Column(String(255), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    stativo = Column(Integer, nullable=False)
    dtcriacao = Column(DateTime)
    dtutilizacao = Column(DateTime)

class EmpresaUsuario(Base):
    __tablename__ = "empresas_usuarios"

    idusuario = Column(Integer, primary_key=True, index=True)
    idempresa = Column(Integer, nullable=False)
    idtipo = Column(Integer, nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    senha_hash = Column(String(255), nullable=False)
    stativo = Column(Integer, nullable=False)
