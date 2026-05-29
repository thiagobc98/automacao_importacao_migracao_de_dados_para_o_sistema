try:
    import unzip_requirements  # necessário quando zip: true
except ImportError:
    pass

import json
import boto3
import os
import requests
import sys
from typing import Any, Callable
from urllib.parse import parse_qs

sys.path.append(os.path.dirname(__file__))

# --- Variáveis de Ambiente ---
GOOGLE_SECRET_ARN: str = os.environ['GOOGLE_SECRET_ARN']

# --- Clientes AWS e Cache ---
#secrets_manager = boto3.client('secretsmanager')
_secrets_manager = None
CACHED_SECRET: dict | None = None

####
def _get_secrets_manager():
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = boto3.client('secretsmanager')
    return _secrets_manager

#####
# ===============================================================
# 🔐 GOOGLE AUTH
# ===============================================================
def get_google_credentials_dict() -> dict:
    global CACHED_SECRET

    if CACHED_SECRET:
        return CACHED_SECRET

####    
    # Modo local: carrega credenciais de arquivo JSON em vez do Secrets Manager
    local_creds_path = os.environ.get('LOCAL_GOOGLE_CREDENTIALS_PATH')
    if local_creds_path:
        print(f"🔐 Carregando credenciais do Google do arquivo local: {local_creds_path}")
        with open(local_creds_path, 'r', encoding='utf-8') as f:
            CACHED_SECRET = json.load(f)
        return CACHED_SECRET
####

    print("🔐 Buscando credenciais do Google...")


#    response = secrets_manager.get_secret_value(SecretId=GOOGLE_SECRET_ARN)
####
    response = _get_secrets_manager().get_secret_value(SecretId=GOOGLE_SECRET_ARN)
####
    CACHED_SECRET = json.loads(response['SecretString'])

    return CACHED_SECRET


# ===============================================================
# 📢 SLACK RESPONSE
# ===============================================================
def notify_slack(response_url: str | None, message: str) -> None:
    if not response_url:
        print("⚠️ response_url não encontrado")
        return

    try:
        payload = {
            "text": message,
            "response_type": "in_channel"
        }

        requests.post(
            response_url,
            json=payload,
            headers={'Content-type': 'application/json'},
            timeout=3  # 🔥 evita travamento
        )

    except Exception as e:
        print(f"⚠️ Erro ao notificar Slack: {e}")


# ===============================================================
# 🚀 PROCESSAMENTO PRINCIPAL
# ===============================================================
def processar_importar_contrato(payload: dict) -> None:
    response_url = payload.get('response_url')
    command_text = payload.get('command_text', '').strip()

    notify_slack(response_url, f"⚡ Iniciando importação: *{command_text}*")

    try:
        from google.oauth2.service_account import Credentials
        import gspread

        creds_dict = get_google_credentials_dict()

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=scopes
        )

        gc = gspread.authorize(credentials)

        from logs import Logger
        import importador

        logger = Logger(command_text)

        print(f"📊 Iniciando importação: {command_text}")

        def _slack(msg: str) -> None:
            notify_slack(response_url, msg)

        importador.executar_importacao(command_text, gc, credentials, logger, notify_slack=_slack)

    except Exception as e:
        import traceback
        print(f"❌ ERRO importação: {e}")
        print(f"❌ TRACEBACK COMPLETO:")
        traceback.print_exc()
        notify_slack(response_url, f"❌ Falha na importação: {str(e)}")


# ===============================================================
# 🧠 DISPATCHER
# ===============================================================
COMMAND_DISPATCHER: dict[str, Callable[[dict], None]] = {
    'importar-contrato': processar_importar_contrato
}


# ===============================================================
# 🔥 HANDLER PRINCIPAL
# ===============================================================
def lambda_handler(event: dict, context: Any) -> dict:
    print("🚀 Evento recebido:", json.dumps(event))

    records = event.get('Records', [event])

    for record in records:
        try:
            payload_body = record.get('body') if isinstance(record, dict) else record

            payload = json.loads(payload_body) if isinstance(payload_body, str) else payload_body

            print("📦 Payload:", json.dumps(payload, indent=2))

            command_type = payload.get('command_type', '').strip().lower()
            command_text = payload.get('command_text', '').lower()

            # 🔥 fallback inteligente
            if not command_type:
                if 'importar' in command_text:
                    command_type = 'importar-contrato'

            response_url = payload.get('response_url')

            if not command_type:
                msg = "❌ command_type não identificado"
                print(msg)
                notify_slack(response_url, msg)
                continue

            print(f"🧭 Executando comando: {command_type}")

            if command_type in COMMAND_DISPATCHER:
                COMMAND_DISPATCHER[command_type](payload)
            else:
                available = ', '.join(COMMAND_DISPATCHER.keys())
                msg = f"❌ Comando desconhecido: {command_type}\nDisponíveis: {available}"
                print(msg)
                notify_slack(response_url, msg)

        except Exception as e:
            print(f"🔥 ERRO CRÍTICO: {e}")

            try:
                response_url = payload.get('response_url')
                notify_slack(response_url, f"❌ Erro inesperado: {str(e)}")
            except:
                pass

    return {
        'statusCode': 200,
        'body': 'Processamento concluído'
    }