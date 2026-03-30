import pandas as pd
import time
import random
import os
import csv
from datetime import datetime
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# CONFIGURAÇÃO
# =========================
MIN_DELAY = 40  # Delay mínimo entre envios em segundos
MAX_DELAY = 80  # Delay máximo entre envios em segundos
MAX_RETRIES = 3  # Tentativas por contato

CSV_PATH = "contatos.csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGEM_PATH = os.path.join(BASE_DIR, "convite.jpeg")
LOG_FILE = os.path.join(BASE_DIR, "log_envios.csv")

MENSAGEM = """{nome}, estamos muito felizes em poder compartilhar a data do nosso casamento!
Esse dia será ainda mais especial com a presença de vocês, por isso já reservem a data 07/11/2026. 
Com carinho,
Luara e Vinícius
"""

# =========================
# LOG
# =========================
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["nome", "numero", "status", "mensagem_erro", "timestamp"])

def registrar_log(nome, numero, status, mensagem_erro=""):
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            nome,
            numero,
            status,
            mensagem_erro,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

# =========================
# FUNÇÕES
# =========================
def numero_valido(numero):
    return str(numero).isdigit() and (12 <= len(str(numero)) <= 13)

def iniciar_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 40)
    driver.get("https://web.whatsapp.com")
    input("Escaneie o QR Code e pressione ENTER quando estiver logado...")
    return driver, wait

def abrir_conversa(driver, wait, numero):
    driver.get(f"https://web.whatsapp.com/send?phone={numero}")
    time.sleep(8)
    wait.until(EC.presence_of_element_located((By.XPATH, '//footer')))
    time.sleep(2)

def enviar_mensagem(driver, wait, mensagem):
    caixa_msg = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//footer//div[@contenteditable="true"]')
    ))
    caixa_msg.click()
    time.sleep(0.5)
    caixa_msg.send_keys(mensagem)
    caixa_msg.send_keys(Keys.ENTER)

def enviar_imagem_explorer(driver, wait, caminho_imagem):

    # 1️⃣ Clicar no botão de anexar
    attach_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[@aria-label="Attach"]')
    ))
    attach_btn.click()
    time.sleep(1)

    # 2️⃣ Clicar em Foto/Vídeo
    foto_video_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@aria-label="Photos & videos"]')
    ))
    foto_video_btn.click()
    time.sleep(1)

    # 3️⃣ Preencher o caminho da imagem usando PyAutoGUI
    print(f"📂 Preenchendo caminho da imagem: {caminho_imagem}")
    pyautogui.write(caminho_imagem)
    time.sleep(0.5)
    pyautogui.press('enter')

    # 4️⃣ Esperar preview carregar e enviar
    send_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@role="button" and @aria-label="Send"]')
    ))
    time.sleep(1)
    driver.execute_script("arguments[0].click();", send_btn)
    time.sleep(2)

def processar_contato(driver, wait, nome, numero):
    print(f"\n➡️ {nome} ({numero})")

    sucesso = False
    for tentativa in range(MAX_RETRIES):
        try:
            print(f"Tentativa {tentativa + 1}")

            abrir_conversa(driver, wait, numero)
            print("✔ Chat aberto")

            # Enviar mensagem
            mensagem = MENSAGEM.format(nome=nome)
            print("💬 Enviando mensagem...")
            enviar_mensagem(driver, wait, mensagem)
            print("✅ Mensagem enviada")

            # Enviar imagem
            print("🖼️ Enviando imagem...")
            enviar_imagem_explorer(driver, wait, IMAGEM_PATH)
            print("✅ Imagem enviada")

            registrar_log(nome, numero, "SUCESSO")
            sucesso = True
            break
        except Exception as e:
            print(f"❌ Erro na tentativa {tentativa + 1}: {e}")
            time.sleep(5)

    if not sucesso:
        registrar_log(nome, numero, "ERRO", str(e))
        print(f"🚫 Falha ao enviar para {nome}")

# =========================
# MAIN
# =========================
def main():
    driver, wait = iniciar_driver()
    contatos = pd.read_csv(CSV_PATH)

    for _, row in contatos.iterrows():
        nome = row["nome"]
        numero = str(row["telefone"])

        if not numero_valido(numero):
            print(f"[INVÁLIDO] {nome} - {numero}")
            registrar_log(nome, numero, "INVÁLIDO")
            continue

        processar_contato(driver, wait, nome, numero)

        delay = random.randint(MIN_DELAY, MAX_DELAY)
        print(f"⏳ Aguardando {delay}s antes do próximo envio...\n")
        time.sleep(delay)

    print("🎉 Todos os envios finalizados!")
    driver.quit()

if __name__ == "__main__":
    main()