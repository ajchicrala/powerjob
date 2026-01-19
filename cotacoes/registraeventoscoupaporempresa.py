import os
import mysql.connector
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from crypto_utils import Decrypta

# -----------------------------------------------------------
# 🔧 CARREGAR .env
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -----------------------------------------------------------
# ⚙️ CONFIGURAÇÕES
# -----------------------------------------------------------
MAX_NEXT_CLICKS = 3
IDPORTAL_COUPA = 1

LOGIN_URL  = "https://vale.coupahost.com/sessions/supplier_login"
EVENTS_URL = "https://vale.coupahost.com/quote_supplier_land"

# -----------------------------------------------------------
# 🗄️ Configuração do banco
# -----------------------------------------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "charset": os.getenv("DB_CHARSET"),
    "use_unicode": True
}

# -----------------------------------------------------------
# 🔍 Buscar usuários Coupa
# -----------------------------------------------------------
def obter_usuarios_coupa():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT idempresa, login, senha_hash
        FROM portais_usuarios
        WHERE stativo = 1
          AND idportal = %s
        ORDER BY idempresa
    """, (IDPORTAL_COUPA,))

    dados = cursor.fetchall()
    cursor.close()
    conn.close()
    return dados

# -----------------------------------------------------------
# 🔄 Coletar eventos da página
# -----------------------------------------------------------
def coletar_eventos_da_pagina(page):
    eventos = []
    linhas = page.query_selector_all("tbody#quote_request_tbody tr")

    for tr in linhas:
        a = tr.query_selector("a")
        if a:
            eventos.append(int(a.inner_text().strip()))

    return eventos

# -----------------------------------------------------------
# ⏭ Paginação
# -----------------------------------------------------------
def clicar_next_e_esperar(page, timeout=10000):
    btn = page.locator("a.next_page").first
    if btn.count() == 0:
        return False

    classes = btn.get_attribute("class") or ""
    if "disabled" in classes:
        return False

    old_href = btn.get_attribute("href")
    btn.click()

    try:
        page.wait_for_function(
            "(h) => document.querySelector('a.next_page')?.getAttribute('href') !== h",
            arg=old_href,
            timeout=timeout
        )
    except:
        return False

    page.wait_for_selector("tbody#quote_request_tbody a", timeout=timeout)
    return True

# -----------------------------------------------------------
# 🧠 Buscar eventos já existentes da empresa
# -----------------------------------------------------------
def obter_eventos_existentes(idempresa):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT idevento
        FROM empresas_eventos
        WHERE idempresa = %s
          AND idportal = %s
    """, (idempresa, IDPORTAL_COUPA))

    existentes = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return existentes

# -----------------------------------------------------------
# 💾 Inserir novos eventos
# -----------------------------------------------------------
def inserir_novos_eventos(idempresa, eventos):
    if not eventos:
        return 0

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = """
        INSERT INTO empresas_eventos (idempresa, idevento, idportal, dtcriacao)
        VALUES (%s, %s, %s, NOW())
    """

    dados = [(idempresa, ev, IDPORTAL_COUPA) for ev in eventos]
    cursor.executemany(sql, dados)

    inseridos = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return inseridos

# -----------------------------------------------------------
# 🚀 MAIN
# -----------------------------------------------------------
def main():

    usuarios = obter_usuarios_coupa()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for u in usuarios:
            idempresa = u["idempresa"]
            login = u["login"]
            senha = Decrypta(u["senha_hash"])

            print(f"\n🏢 Empresa {idempresa} — login Coupa")

            try:
                # Login
                page.goto(LOGIN_URL)
                page.fill("#user_login", login)
                page.fill("#user_password", senha)
                page.click("#login_button")
                page.wait_for_load_state("networkidle")

                # Eventos
                page.goto(EVENTS_URL)
                page.wait_for_selector("tbody#quote_request_tbody a")

                eventos = []
                eventos.extend(coletar_eventos_da_pagina(page))

                cliques = 0
                while clicar_next_e_esperar(page):
                    cliques += 1
                    if MAX_NEXT_CLICKS and cliques >= MAX_NEXT_CLICKS:
                        break
                    eventos.extend(coletar_eventos_da_pagina(page))

                eventos = set(eventos)
                existentes = obter_eventos_existentes(idempresa)

                novos = eventos - existentes
                inseridos = inserir_novos_eventos(idempresa, novos)

                print(f"📌 Eventos coletados : {len(eventos)}")
                print(f"➕ Novos inseridos  : {inseridos}")

            except Exception as e:
                print(f"❌ Erro empresa {idempresa}: {e}")

        browser.close()

# -----------------------------------------------------------
# ▶️ EXECUTAR
# -----------------------------------------------------------
if __name__ == "__main__":
    main()
