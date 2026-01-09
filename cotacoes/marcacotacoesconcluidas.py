"""
Script responsável por verificar eventos pendentes de cotação
e marcar como concluídos aqueles que já possuem registros
na tabela de cotações.

Regra de negócio:
- eventoscoupa.cotacao_incluida = 0  → pendente
- eventoscoupa.cotacao_incluida = 1  → concluída
"""

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from enviamensagemtelegram import enviar_mensagem_telegram

# ============================================================
# CONFIGURAÇÃO DO AMBIENTE (.env)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "charset": os.getenv("DB_CHARSET"),
    "use_unicode": True
}

# ============================================================
# BUSCAR EVENTOS COM COTAÇÃO NÃO INCLUÍDA
# ============================================================

def buscar_eventos_pendentes():
    """
    Retorna todos os eventos onde cotacao_incluida = 0
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT idevento
        FROM eventoscoupa
        WHERE cotacao_incluida = 0
        ORDER BY idevento
    """)

    eventos = cursor.fetchall()
    cursor.close()
    conn.close()

    return eventos

# ============================================================
# VERIFICAR SE EXISTE COTAÇÃO PARA O EVENTO
# ============================================================

def cotacao_existe(idevento):
    """
    Retorna True se existir pelo menos uma cotação
    para o idevento informado
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM cotacoescoupa
        WHERE idevento = %s
    """, (idevento,))

    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return total > 0

# ============================================================
# MARCAR EVENTO COMO CONCLUÍDO
# ============================================================

def marcar_evento_como_concluido(idevento):
    """
    Atualiza o evento marcando cotacao_incluida = 1
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE eventoscoupa
        SET cotacao_incluida = 1
        WHERE idevento = %s
    """, (idevento,))

    conn.commit()
    cursor.close()
    conn.close()

# ============================================================
# MAIN
# ============================================================

def main():
    try:
        eventos = buscar_eventos_pendentes()
        print(f"📌 Eventos pendentes encontrados: {len(eventos)}")

        for ev in eventos:
            idevento = ev["idevento"]
            print(f"➡️ Verificando evento {idevento}...")

            if cotacao_existe(idevento):
                marcar_evento_como_concluido(idevento)
                #print("   ✔ Cotação encontrada → evento marcado como concluído")
            #else:
                #print("   ⏳ Nenhuma cotação encontrada")

        print("🏁 Processo finalizado com sucesso.")

    except Error as e:
        print("❌ ERRO MYSQL:", e)
        enviar_mensagem_telegram("Erro em marcacotacoesconcluidas. Erro mysql.")

    except Exception as e:
        print("❌ ERRO GERAL:", e)
        enviar_mensagem_telegram("Erro em marcacotacoesconcluidas. Erro geral.")

# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
