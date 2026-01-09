"""
Este script automatiza a extração de itens de cotações no portal Coupa (Vale)
a partir de eventos previamente armazenados em um banco de dados MySQL.

Fluxo geral do script:
- Carrega credenciais e configurações a partir de variáveis de ambiente (.env).
- Consulta o banco de dados MySQL para obter os eventos do dia atual.
- Realiza login automatizado no portal Coupa utilizando Playwright.
- Para cada evento:
  - Acessa a página da cotação.
  - Expande cada item listado.
  - Extrai informações detalhadas dos itens, como descrição em português,
    quantidade, local de entrega e detalhes adicionais.
- Normaliza e estrutura os dados extraídos.
- Insere os itens de cotação na tabela MySQL, evitando duplicidades.

O script foi projetado para execução automatizada (batch), integrando
scraping web com persistência em banco de dados, e serve como etapa de
ingestão detalhada dos itens vinculados a eventos de cotação.
"""


import os
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import mysql.connector
from enviamensagemtelegram import enviar_mensagem_telegram

# ============================================================
#  CONFIGURAÇÃO DO .ENV
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

USER = os.getenv("COUPA_USER")
PWD  = os.getenv("COUPA_PASS")

if not USER or not PWD:
    enviar_mensagem_telegram("Configure COUPA_USER e COUPA_PASS no arquivo .env")
    raise RuntimeError("❌ Configure COUPA_USER e COUPA_PASS no arquivo .env")
    

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "charset": os.getenv("DB_CHARSET"),
    "use_unicode": True
}

LOGIN_URL = "https://vale.coupahost.com/sessions/supplier_login"


# ============================================================
#  BUSCAR EVENTOS DO BANCO (SUBSTITUIR CSV)
# ============================================================
def obter_eventos_mysql():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT idevento, link, dtinicio, dtfim
        FROM eventoscoupa
        WHERE DATE(dtinsercao) >= DATE_SUB(CURDATE(), INTERVAL 10 DAY)
        AND COTACAO_INCLUIDA = 0
        ORDER BY idevento ASC
    """)

    eventos = cursor.fetchall()

    cursor.close()
    conn.close()
    return eventos



# ============================================================
#  INSERIR LINHA NA TABELA COTACOES
# ============================================================
def inserir_item_cotacao(item):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql = """
        INSERT IGNORE INTO cotacoescoupa (
            idcotacao, idevento, descricao, quantidade, dtinicio, dtfim,
            localentrega, detalhes, valorcotacao,
            responsavel, dtcotacao, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        item["idcotacao"],
        item["idcotacao"],
        item["descricao"],
        item["quantidade"],
        item["dtinicio"],
        item["dtfim"],
        item["localentrega"],
        item["detalhes"],
        item["valorcotacao"],
        item["responsavel"],
        item["dtcotacao"],
        item["status"]
    ))

    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
#  EXTRAIR APENAS DESCRIÇÃO PT
# ============================================================
def extrair_descricao_pt(texto):
    if not texto:
        return ""

    texto = texto.replace("\n", " ").strip()
    marcador_pt = "PT ||"
    pos_pt = texto.find(marcador_pt)

    if pos_pt == -1:
        return texto.strip()

    resto = texto[pos_pt + len(marcador_pt):]

    proximos = ["EN ||", "ES ||"]
    limites = [resto.find(m) for m in proximos if resto.find(m) != -1]

    if limites:
        resto = resto[:min(limites)]

    return resto.replace("*", "").strip()


# ============================================================
#  LOGIN
# ============================================================
def login(page):
    page.goto(LOGIN_URL)
    page.fill("#user_login", USER)
    page.fill("#user_password", PWD)
    page.click("#login_button")
    page.wait_for_load_state("networkidle")
    time.sleep(1)


# ============================================================
#  EXTRAÇÃO DE ITENS — COPIADO EXATAMENTE DO SEU CÓDIGO
# ============================================================
def extrair_itens(page, event_num, link, start_date, end_date):

    page.goto(link, timeout=60000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(800)

    resultados = []
    linhas = page.locator("div.line.s-itemsAndServicesLine")

    for idx in range(linhas.count()):
        linha = linhas.nth(idx)
        data_id = linha.get_attribute("data-id") or linha.get_attribute("data-rbd-draggable-id") or ""

        # 1) ABRIR PAINEL EXPANDIDO
        possiveis_seletores = [
            ".s-expandSidebar-clickable",
            ".s-expandSidebar",
            "div.s-expandSidebar-clickable",
            "button[aria-label='Expand']",
            "button:has-text('>')",
            "div[role='button'] .s-expandSidebar-clickable",
        ]

        seta = None
        for sel in possiveis_seletores:
            loc = linha.locator(sel)
            if loc.count() > 0:
                seta = loc.first
                break

        if not seta:
            glob = page.locator(".s-expandSidebar-clickable")
            if glob.count() > 0:
                seta = glob.nth(min(idx, glob.count() - 1))

        if not seta:
            continue

        clicked = False
        try:
            seta.scroll_into_view_if_needed()
            seta.click(timeout=1500)
            clicked = True
        except:
            try:
                page.evaluate("(el) => el.click()", seta)
                clicked = True
            except:
                clicked = False

        if not clicked:
            continue

        expanded_selector = f"div.line.s-itemsAndServicesLine[data-id='{data_id}'].-expanded"
        try:
            page.wait_for_selector(expanded_selector, timeout=2500)
            expanded = page.locator(expanded_selector).first
        except:
            expanded = page.locator("div.line.s-itemsAndServicesLine.-expanded").first

        if expanded.count() == 0:
            continue

        # DESCRIPTION
        desc_loc = expanded.locator(".s-extended_description p.s-textField").first
        descricao_bruta = desc_loc.inner_text().strip() if desc_loc.count() > 0 else ""
        descricao = extrair_descricao_pt(descricao_bruta)

        # EXPECTED QUANTITY
        qtd_loc = expanded.locator(".s-quantity span.s-value").first
        quantidade = qtd_loc.inner_text().strip() if qtd_loc.count() > 0 else ""

        # SHIP TO ADDRESS
        ship_to_loc = expanded.locator(".s-ship_to_address .addressLines")
        if ship_to_loc.count() > 0:
            ship_to_address = ship_to_loc.inner_text().strip()
        else:
            no_addr = expanded.locator(".s-ship_to_address .placeholderText")
            ship_to_address = no_addr.inner_text().strip() if no_addr.count() > 0 else ""

        # DETAILS
        details_loc = expanded.locator(".s-details .s-attachmentText")
        details = details_loc.inner_text().strip() if details_loc.count() > 0 else ""

        resultados.append({
            "idcotacao": f"{event_num}",             # <- chave única
            "descricao": descricao,
            "quantidade": quantidade,
            "dtinicio": start_date,
            "dtfim": end_date,
            "localentrega": ship_to_address,
            "detalhes": details,
            "valorcotacao": None,
            "responsavel": None,
            "dtcotacao": datetime.now().strftime("%Y-%m-%d"),
            "status": 0
        })

        # FECHA PAINEL
        try:
            page.evaluate("(el) => el.click()", seta)
        except:
            pass

    return resultados


# ============================================================
#  MAIN
# ============================================================
def main():

    print("🔍 Lendo eventos do banco...")
    eventos = obter_eventos_mysql()
    print(f"📌 {len(eventos)} eventos encontrados.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("➡️ Login...")
        login(page)
        print("✅ Login OK.\n")

        for ev in eventos:

            event_num = ev["idevento"]
            link = ev["link"]
            start_date = ev["dtinicio"]
            end_date = ev["dtfim"]

            print(f"➡️ Processando evento {event_num} ...")

            try:
                itens = extrair_itens(page, str(event_num), link, start_date, end_date)

                for item in itens:
                    inserir_item_cotacao(item)

                print(f"   ✔ {len(itens)} itens inseridos.")
            except Exception as e:
                print(f"⚠️ Erro no evento {event_num}: {e}")
                enviar_mensagem_telegram(f"Registraevento: Erro no evento {event_num}: {e}")

        browser.close()

    print("\n🏁 Finalizado.")


# ============================================================
#  EXECUTAR
# ============================================================
if __name__ == "__main__":
    main()
