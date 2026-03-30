# Envio Automático de mensagens via WhatsApp Web
Automatiza o envio de mensagens e imagens para uma lista de contatos via WhatsApp Web, com logs de envio e delays configuráveis.

## Funcionalidades

- Envia mensagens personalizadas para cada contato com o nome do convidado.
- Envia imagens ou convites digitais junto com a mensagem.
- Logging de envio, registrando sucesso ou erro por contato.
- Delays configuráveis para evitar bloqueios pelo WhatsApp.
- Funciona sem precisar da API oficial do WhatsApp (somente para uso pessoal e testes).

---

## Pré-requisitos

- Python 3.9+  
- Google Chrome instalado  
- Bibliotecas Python:
  ```bash
  pip install selenium pandas pyautogui webdriver-manager
