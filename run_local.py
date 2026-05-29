"""
Runner local para o SlkImportContratosLambda.

Uso:
    python run_local.py <codigo_planilha_google_sheets>

Exemplo:
    python run_local.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms

Pré-requisitos:
    1. Criar .env.local com as variáveis de ambiente (copie de .env.local.example)
    2. Ter o arquivo de credenciais do Google (JSON da service account)
    3. Ter MySQL rodando localmente com o banco configurado
    4. Instalar dependências: pip install -r src/SlkImportContratosLambda/requirements.txt
"""

import json
import os
import sys


# -----------------------------------------------------------------------
# 1. Carrega .env.local antes de qualquer import do projeto
# -----------------------------------------------------------------------
def _load_env_file(path: str) -> None:
    if not os.path.exists(path):
        print(f"❌ Arquivo {path} não encontrado.")
        print(f"   Copie .env.local.example para .env.local e preencha os valores.")
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

    print("✅ Variáveis de ambiente carregadas de .env.local")


_load_env_file('.env.local')


# -----------------------------------------------------------------------
# 2. Adiciona o diretório da Lambda ao path para imports relativos
# -----------------------------------------------------------------------
LAMBDA_DIR = os.path.join(os.path.dirname(__file__), 'src', 'SlkImportContratosLambda')
sys.path.insert(0, LAMBDA_DIR)


# -----------------------------------------------------------------------
# 3. Monta o evento fake (simula mensagem SQS com o payload do Slack)
# -----------------------------------------------------------------------
def _build_event(command_text: str) -> dict:
    payload = {
        "command_type": "importar-contrato",
        "command_text": command_text,
        "response_url": None,  # sem Slack local — notificações são ignoradas
    }

    return {
        "Records": [
            {
                "messageId": "local-test-001",
                "body": json.dumps(payload),
                "attributes": {
                    "MessageGroupId": "local",
                    "SequenceNumber": "1",
                },
            }
        ]
    }


# -----------------------------------------------------------------------
# 4. Executa
# -----------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python run_local.py <codigo_planilha_google_sheets>")
        print("Exemplo: python run_local.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms")
        sys.exit(1)

    command_text = sys.argv[1]
    print(f"\n🚀 Iniciando execução local para: {command_text}\n")

    # Importa o handler da Lambda (depois de setar as env vars)
    from main import lambda_handler  # noqa: E402

    event = _build_event(command_text)
    result = lambda_handler(event, {})

    print(f"\n✅ Execução finalizada: {result}")
