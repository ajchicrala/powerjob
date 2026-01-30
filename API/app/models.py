from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from datetime import datetime
from app.db import Base

class CotacaoStatusHistorico(Base):
    __tablename__ = "cotacoes_status_historico"

    idhistorico = Column(Integer, primary_key=True, autoincrement=True)
    idempresa = Column(Integer, nullable=False)
    idevento = Column(Integer, nullable=False)
    idportal = Column(Integer, nullable=False)
    idstatus_anterior = Column(Integer, nullable=False)
    idstatus_atual = Column(Integer, nullable=False)
    idusuario = Column(Integer, nullable=False)
    dtcriacao = Column(DateTime, default=datetime.utcnow)

class EmpresaEvento(Base):
    __tablename__ = "empresas_eventos"

    idempresa = Column(Integer, primary_key=True)
    idevento = Column(Integer, primary_key=True)
    idportal = Column(Integer, primary_key=True)
    idstatus = Column(Integer, nullable=False)
    dtcriacao = Column(DateTime)


class CotacaoCoupa(Base):
    __tablename__ = "cotacoescoupa"

    ideventocoupa = Column(Integer, primary_key=True)
    idevento = Column(Integer)
    descricao = Column(String)
    detalhes = Column(String)
    quantidade = Column(Integer)
    dtinicio = Column(Date)
    dtfim = Column(Date)

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
