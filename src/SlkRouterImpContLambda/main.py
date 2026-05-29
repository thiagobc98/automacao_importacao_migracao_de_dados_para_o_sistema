# import pymysql, os, json

# db_host = os.getenv('DB_HOST')
# db_user = os.getenv('DB_USER')
# db_password = os.getenv('DB_PASSWORD')

# print("Conexão bem-sucedida ao banco de dados.")

# def lambda_handler(event, context):
#     return {
#         "statusCode": 200,
#         "body": "chegou na lambda"
#     }

# import json
# import os
# import hmac
# import hashlib
# from urllib.parse import parse_qs

# import boto3

# sqs = boto3.client('sqs')

# SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
# QUEUE_URL = os.environ['QUEUE_URL']


# def verify_slack(headers, body):
#     timestamp = headers.get('x-slack-request-timestamp')
#     slack_signature = headers.get('x-slack-signature')

#     sig_basestring = f"v0:{timestamp}:{body}"

#     my_signature = 'v0=' + hmac.new(
#         SLACK_SIGNING_SECRET.encode(),
#         sig_basestring.encode(),
#         hashlib.sha256
#     ).hexdigest()

#     return hmac.compare_digest(my_signature, slack_signature)


# def lambda_handler(event, context):
#     print("🚀 INICIOU ROUTER")

#     body = event['body']
#     headers = {k.lower(): v for k, v in event['headers'].items()}

#     # 🔐 valida Slack
#     if not verify_slack(headers, body):
#         return {"statusCode": 401, "body": "Unauthorized"}

#     # parse
#     data = {k: v[0] for k, v in parse_qs(body).items()}

#     # ✅ RESPONDE RÁPIDO
#     response = {
#         "statusCode": 200,
#         "body": json.dumps({
#             "response_type": "ephemeral",
#             "text": "Processando..."
#         })
#     }

#     # 🚀 ENVIA PRO SQS (depois de montar resposta)
#     try:
#         sqs.send_message(
#             QueueUrl=QUEUE_URL,
#             MessageBody=json.dumps(data),
#             MessageGroupId="default"  # FIFO obrigatório
#         )
#         print("✅ Enviado para SQS com sucesso")

#     except Exception as e:
#         print("❌ Erro ao enviar para SQS:", str(e))

#     return response




import json
import boto3
import os
import time
import hashlib
import hmac
import base64
from urllib.parse import parse_qs

# --- Variáveis de Ambiente ---
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
QUEUE_URL = os.environ['QUEUE_URL']

# --- Clientes AWS ---
sqs = boto3.client('sqs')


def verify_slack_request(headers, body):
    """Verifica a assinatura da requisição do Slack para segurança."""

    # 🔥 normaliza headers (CRÍTICO)
    headers = {k.lower(): v for k, v in headers.items()}

    timestamp = headers.get('x-slack-request-timestamp', '0')
    signature = headers.get('x-slack-signature', '')

    # proteção contra replay attack
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    basestring = f'v0:{timestamp}:{body}'.encode('utf-8')
    slack_signing_secret = SLACK_SIGNING_SECRET.encode('utf-8')

    my_signature = 'v0=' + hmac.new(
        slack_signing_secret,
        basestring,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, signature)


def lambda_handler(event, context):
    print("🚀 INICIOU ROUTER")

    body_str = event.get('body', '')

    # 🔥 trata base64 (API Gateway pode mandar assim)
    if event.get('isBase64Encoded', False):
        body_str = base64.b64decode(body_str).decode('utf-8')

    # 🔐 valida Slack
    if not verify_slack_request(event.get('headers', {}), body_str):
        print("❌ Verificação de assinatura falhou.")
        return {'statusCode': 401, 'body': 'Verificação falhou.'}

    print("✅ Verificação de assinatura OK")

    # parse do body
    parsed_body = {k: v[0] for k, v in parse_qs(body_str).items()}

    trigger_id = parsed_body.get('trigger_id')
    slack_command = parsed_body.get('command', '').replace('/', '').strip().lower()

    print(f"🔎 Comando recebido: {slack_command}")

    # define tipo de comando
    command_type = slack_command

    if slack_command == 'importar_contratos':
        command_type = 'importar-contrato'

    print(f"🧭 Tipo de comando: {command_type}")

    # payload para o worker
    message_payload = {
        'response_url': parsed_body.get('response_url'),
        'user_name': parsed_body.get('user_name'),
        'command_text': parsed_body.get('text', '').strip(),
        'command_type': command_type
    }

    print("📤 Payload enviado para SQS:", json.dumps(message_payload))

    # ✅ responde rápido (ANTES de qualquer risco)
    response = {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response_type": "ephemeral",
            "text": "✅ Solicitação recebida! Processando... ⏳"
        })
    }

    # 🚀 envio para SQS
    try:
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message_payload),
            MessageGroupId='ImportContratosSlack',
            MessageDeduplicationId=trigger_id or str(time.time())
        )
        print("✅ Mensagem enviada para SQS")

    except Exception as e:
        print(f"❌ Erro ao enviar para SQS: {e}")

    return response