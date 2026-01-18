"""
Este script automatiza o login no portal Coupa (Vale) utilizando Playwright,
navega pela listagem de eventos (cotações), percorre múltiplas páginas por meio
de paginação controlada, extrai informações básicas de cada evento e persiste
esses dados em um banco de dados MySQL.

Principais funcionalidades:
- Realiza autenticação no portal Coupa com credenciais armazenadas em variáveis
  de ambiente (.env).
- Acessa a página de eventos/cotações do fornecedor.
- Coleta, em cada página, o identificador do evento, link de acesso e datas
  de início e fim.
- Controla a navegação entre páginas por meio de uma variável configurável
  (MAX_NEXT_CLICKS), permitindo limitar ou coletar todas as páginas disponíveis.
- Normaliza datas para o formato compatível com MySQL (YYYY-MM-DD).
- Remove eventos duplicados antes da persistência.
- Insere apenas novos registros no banco de dados, evitando duplicidades.

O script foi desenvolvido para execução automatizada (batch), podendo ser
agendado via cron ou integrado a pipelines de dados.
"""


import os
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime
import mysql.connector
from enviamensagemtelegram import enviar_mensagem_telegram

# -----------------------------------------------------------
# 🔧 CARREGAR .env do MESMO DIRETÓRIO DO SCRIPT
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ENV = os.path.join(BASE_DIR, ".env")
load_dotenv(CAMINHO_ENV)

# -----------------------------------------------------------
# ⚙️ CONFIGURAÇÕES
# -----------------------------------------------------------
MAX_NEXT_CLICKS = 2  # Quantos cliques no botão "Next" serão feitos
# None = coletar todas as páginas
# MAX_NEXT_CLICKS = None

# -----------------------------------------------------------
# 🎯 URLs
# -----------------------------------------------------------
LOGIN_URL = "https://vale.coupahost.com/sessions/supplier_login"
EVENTS_URL = "https://vale.coupahost.com/quote_supplier_land"

# -----------------------------------------------------------
# 🔧 Função para formatar datas para MySQL (YYYY-MM-DD)
# -----------------------------------------------------------
def formatar_data(data):
    """Converte MM/DD/YY para YYYY-MM-DD (MySQL)."""
    if not data or data.strip() == "":
        return None
    try:
        dt = datetime.strptime(data.strip(), "%m/%d/%y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

# -----------------------------------------------------------
# 🔄 Coleta dos eventos da página
# -----------------------------------------------------------
def coletar_eventos_da_pagina(page):
    eventos = []
    linhas = page.query_selector_all("tbody#quote_request_tbody tr")

    for tr in linhas:
        a = tr.query_selector("a")
        if not a:
            continue

        numero = a.inner_text().strip()
        link = f"https://vale.coupahost.com/quotes/external_responses/{numero}"

        start_td = tr.query_selector("td.s-datatable-cell-start_time")
        end_td   = tr.query_selector("td.s-datatable-cell-end_time")

        raw_start = start_td.inner_text().strip() if start_td else ""
        raw_end   = end_td.inner_text().strip() if end_td else ""

        eventos.append({
            "idevento": int(numero),
            "link": link,
            "dtinicio": formatar_data(raw_start),
            "dtfim": formatar_data(raw_end)
        })

    return eventos

# -----------------------------------------------------------
# ⏭ Lógica de paginação: clicar "Next"
# -----------------------------------------------------------
def clicar_next_e_esperar(page, timeout=10000):
    next_locator = page.locator("a.next_page")

    if next_locator.count() == 0:
        return False

    btn = next_locator.first
    old_href = btn.get_attribute("href")
    if not old_href:
        return False

    classes = btn.get_attribute("class") or ""
    if "disabled" in classes:
        return False

    try:
        btn.click()
    except Exception:
        page.evaluate("el => el.click()", btn)

    try:
        page.wait_for_function(
            "(oldHref) => { "
            "   const el = document.querySelector('a.next_page'); "
            "   return el && el.getAttribute('href') !== oldHref; "
            "}",
            arg=old_href,
            timeout=timeout
        )
    except Exception:
        if btn.get_attribute("href") == old_href:
            return False

    page.wait_for_selector("tbody#quote_request_tbody a", timeout=timeout)
    return True

# -----------------------------------------------------------
# 🗄️ INSERIR EVENTOS NO MYSQL
# -----------------------------------------------------------
def inserir_eventos_mysql(eventos):

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")),
        charset=os.getenv("DB_CHARSET"),
        use_unicode=True
    )

    cursor = conn.cursor()

    sql = """
        INSERT IGNORE INTO eventoscoupa (idevento, link, dtinicio, dtfim)
        VALUES (%s, %s, %s, %s)
    """

    inseridos = 0

    for ev in eventos:
        cursor.execute(sql, (
            ev["idevento"],
            ev["link"],
            ev["dtinicio"],
            ev["dtfim"]
        ))

        if cursor.rowcount == 1:
            inseridos += 1

    conn.commit()
    cursor.close()
    conn.close()

    print(f"💾 Inseridos {inseridos} novos eventos no MySQL.")
    enviar_mensagem_telegram("Processo de coleta de eventos Coupa finalizado.")

# -----------------------------------------------------------
# 🚀 PROGRAMA PRINCIPAL
# -----------------------------------------------------------
def main():

    user = os.getenv("COUPA_USER")
    pwd  = os.getenv("COUPA_PASS")

    if not user or not pwd:
        raise RuntimeError("Defina COUPA_USER e COUPA_PASS no arquivo .env")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Login
        page.goto(LOGIN_URL)
        page.fill("#user_login", user)
        page.fill("#user_password", pwd)
        page.click("#login_button")
        page.wait_for_load_state("networkidle")

        # Página de eventos
        page.goto(EVENTS_URL)
        page.wait_for_selector("tbody#quote_request_tbody a")

        eventos_total = []

        # Primeira página (sem clique)
        eventos_total.extend(coletar_eventos_da_pagina(page))

        # Paginação controlada
        cliques_realizados = 0

        while True:
            if MAX_NEXT_CLICKS is not None and cliques_realizados >= MAX_NEXT_CLICKS:
                break

            if not clicar_next_e_esperar(page):
                break

            eventos_total.extend(coletar_eventos_da_pagina(page))
            cliques_realizados += 1

            print(f"➡️ Página coletada ({cliques_realizados})")

        # Remover duplicados
        df = pd.DataFrame(eventos_total).drop_duplicates(subset=["idevento"])
        eventos_unicos = df.to_dict(orient="records")

        # Inserir no banco
        inserir_eventos_mysql(eventos_unicos)

        browser.close()

# -----------------------------------------------------------
# ▶️ EXECUTAR
# -----------------------------------------------------------
if __name__ == "__main__":
    main()
