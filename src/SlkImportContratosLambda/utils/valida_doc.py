from time import sleep
import pandas as pd
import requests
import re
from datetime import datetime


# def validar_data(data_str):

#     if not data_str:
#         return True

#     formato = "%Y-%m-%d"
#     if re.match(formato, data_str):
#         return True
#     else:
#         return False

def validar_data(data_str):

    if not data_str:
        return True

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            datetime.strptime(str(data_str), fmt)
            return True
        except:
            pass
    return False


def valida_formato_br(valor):
    if not isinstance(valor, str):
        return False
    padrao = r'^\d{1,3}(\.\d{3})*,\d{2}%$'
    return bool(re.match(padrao, valor))


def valida_numero_br(valor):
    """Aceita vazio/NaN ou qualquer número em formato BR (ex: 1,0 | 1.350,00 | 10.5)."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)) or str(valor).strip() == '':
        return True
    try:
        float(str(valor).replace('.', '').replace(',', '.'))
        return True
    except (ValueError, AttributeError):
        return False


def validar_int(valor):
    if not valor:
        return True
    try:
        int(valor)
        return True
    except ValueError:
        return False


def validar_float(valor):
    if not valor:
        return True
    try:
        float(valor)
        return True
    except ValueError:
        return False


def is_cpf(string):
    return True if re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', str(string)) or re.match(r'^\d{11}$', str(string)) else False


def is_cnpj(string):
    return True if re.match(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', str(string)) or re.match(r'^\d{15}$', str(string)) else False


def is_rg(rg):
    return True if re.match(r'\d{2}\.\d{3}\.\d{3}-\d', str(rg)) else False


def is_email(email):
    email = email.strip()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.fullmatch(pattern, email))


def validar_cpf(cpf):
    # Verifica se está no formato correto: xxx.xxx.xxx-xx
    if not re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        return False

    # Remove máscara
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma1 * 10) % 11
    digito1 = 0 if digito1 == 10 else digito1

    soma2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma2 * 10) % 11
    digito2 = 0 if digito2 == 10 else digito2

    return int(cpf[9]) == digito1 and int(cpf[10]) == digito2


def validar_cnpj(cnpj):
    # Verifica se está no formato correto: xx.xxx.xxx/xxxx-xx
    if not re.fullmatch(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', cnpj):
        return False

    # Remove máscara
    cnpj = re.sub(r'\D', '', cnpj)

    if len(cnpj) != 14:
        return False

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    digito1 = 11 - (soma1 % 11)
    digito1 = digito1 if digito1 < 10 else 0

    pesos2 = [6] + pesos1
    soma2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    digito2 = 11 - (soma2 % 11)
    digito2 = digito2 if digito2 < 10 else 0

    return int(cnpj[12]) == digito1 and int(cnpj[13]) == digito2


def valida_cep(cep: str) -> str:

    if not re.match(r'^\d{5}-\d{3}$', str(cep)):
        return False
    return True
    # cep = str(cep).strip()
    # url = f"https://viacep.com.br/ws/{cep}/json/"

    # tentativas_maximas = 2
    # for tentativa in range(tentativas_maximas):
    #    try:
    #        response = requests.get(url, timeout=10)
    #        response.raise_for_status()
    #    except requests.exceptions.RequestException as e:
    #        print(f"Erro ao fazer requisição: {e}. Tentativa {tentativa + 1} de {tentativas_maximas}. Tentando novamente em 60 segundos...")
    #        sleep(100)

    # return f"Todas as tentativas esgotadas."


# INQUILINO
def validar_estado_civil(valor):
    import pandas as pd

    if pd.isna(valor) or valor in [1, 2, 3, 4, 5, 6]:
        return True

    return False


def validar_genero(valor):
    import pandas as pd

    if pd.isna(valor) or valor in ['F', 'M']:
        return True

    return False


def valida_dados(row):
    res = {"documento_inquilino_original": row.documento_inquilino}

    # Validando CPF ou CNPJ
    res['documento_inquilino'] = is_cpf(
        row.documento_inquilino) or is_cnpj(row.documento_inquilino)

    res['emails_inquilino'] = True
    for email in str(row.emails_inquilino).split(';'):
        email = email.strip()
        if not is_email(email):
            res['emails_inquilino'] = False
            break

    # Validando CEP
    res['cep_end'] = valida_cep(row['cep_end'])

    # Validando colunas vazias
    colunas_vazias = []
    for col_name in [
        'inquilino_principal', 'documento_inquilino', 'nome_inquilino',
        'telefone_inquilino', 'emails_inquilino', 'cep_end', 'rua_end',
        'numero_end', 'bairro_end', 'cidade_end', 'estado_end'
    ]:
        value = row[col_name]
        if pd.isna(value) or str(value).strip() == "":
            colunas_vazias.append(col_name)
    res['col_vazias'] = colunas_vazias

    # Validando estado civil
    res['estado_civil_inquilino'] = validar_estado_civil(
        row['estado_civil_inquilino'])

    # Validando gênero
    res['genero_inquilino'] = validar_genero(row['genero_inquilino'])

    return res


def validar_estado(estado):
    return bool(re.fullmatch(r'[A-Z]{2}', estado.strip()))


def validar_cep(cep):
    return bool(re.fullmatch(r'\d{5}-?\d{3}', cep.strip()))


def validar_texto_sem_barras(texto):
    return "/" not in texto and "\\" not in texto


def validar_numero(numero):
    try:
        int(numero)
        return True
    except ValueError:
        return False


def validar_cpf_ou_cnpj(valor):
    valor = str(valor).strip()
    return validar_cpf(valor) or validar_cnpj(valor)


def validar_telefone(telefone):
    pattern = r'^\(\d{2}\) \d{4,5}-\d{4}$'
    return bool(re.match(pattern, str(telefone).strip()))


def validar_emails(emails):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    lista = [e.strip() for e in str(emails).split(';')]
    return all(re.match(email_pattern, e) for e in lista)
