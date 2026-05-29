# import pymysql
# import os

# HOST_DB = os.environ['DB_HOST']
# DATABSE = os.environ['DB_NAME']
# USER_DB = os.environ['DB_USER']
# PASS_DB = os.environ['DB_PASSWORD']


# def get_connection():
#     try:
#         print(f"🔌 Tentando conectar ao banco: host={HOST_DB}, db={DATABSE}, user={USER_DB}")
#         connection = pymysql.connect(
#             host=HOST_DB, database=DATABSE, user=USER_DB, password=PASS_DB,
#             connect_timeout=10)
#         print("✅ Conexão com o banco estabelecida com sucesso!")
#         return connection
#     except Exception as erro:
#         print(f"❌ ERRO ao conectar no banco: {type(erro).__name__}: {erro}")
#         return None


# def inserir_proprietario(connection, documento_prop, nome_prop, rg_prop,
#                          nacionalidade_prop, telefone_prop, emails_prop,
#                          estado_civil_prop, regime_casamento_prop,
#                          profissao_prop, inscricao_estadual='', razao_social_empresa='',
#                          nome_representante_empresa='', documento_representante_empresa='',
#                          vinculo_empresa='', commit=True):
#     sql = """
#         INSERT INTO proprietarios
#         (documento_prop, nome_prop, rg_prop, nacionalidade_prop, telefone_prop, emails_prop,
#         estado_civil_prop, regime_cassamento_prop, profissao_prop, exc_prop, user_add_prop,
#         uuid_prop, inscricao_estadual, razao_social_empresa, nome_represntante_empresa,
#         documento_representante_empresa, vinculo_empresa)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UNHEX(REPLACE(UUID(),'-','')), %s, %s, %s, %s, %s)
#     """

#     exc_prop = 'F'
#     user_add_prop = None

#     dados = (documento_prop, nome_prop, rg_prop,
#              nacionalidade_prop, telefone_prop, emails_prop,
#              estado_civil_prop, regime_casamento_prop, profissao_prop,
#              exc_prop, user_add_prop, inscricao_estadual,
#              razao_social_empresa, nome_representante_empresa,
#              documento_representante_empresa, vinculo_empresa)

#     id = __inserir_dados(connection, "Proprietário", dados, sql, commit=commit)
#     return id


# def inserir_endereco(connection, fk_id_cat_pessoascategorias, cep, rua, numero, bairro, cidade, estado, complemento, ator_id, commit=True):

#     sql = """INSERT INTO enderecos
#         (cep_end, rua_end, numero_end, bairro_end, cidade_end, estado_end,
#         complemento_end, fk_id_cat_pessoascategorias, id_ator)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#     dados = (cep, rua, numero, bairro, cidade, estado,
#              complemento, fk_id_cat_pessoascategorias, ator_id)

#     id = __inserir_dados(connection, "Endereço", dados, sql, commit=commit)
#     return id


# def inserir_conta_bancaria(connection, fk_id_cat_pessoascategorias, fk_id_banco_bancos, numero_conta, agencia, tipo_conta, titular, documento, ator_id, commit=True):

#     sql = """INSERT INTO contasbancarias
#         (fk_id_banco_bancos, numerocc_conta, agencia_conta, tipo_conta, titular_conta,
#         documento_conta, fk_id_cat_pessoascategorias, id_ator)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         """

#     dados = (fk_id_banco_bancos, numero_conta, agencia, tipo_conta,
#              titular, documento, fk_id_cat_pessoascategorias, ator_id)

#     id = __inserir_dados(connection, "Conta Bancária", dados, sql, commit=commit)
#     return id


# def inserir_imovel(connection, fk_id_prop, fk_id_parceiro, valor_do_aluguel, taxa_de_contrato, local_das_chaves, observacoes_contratuais,
#                    nome_condominio, valor_condominio, valor_do_iptu, dados_do_condominio, commit=True):

#     sql = """INSERT INTO imoveis
#         (fk_id_prop_proprietarios,
#         fk_id_parceiro_parceiros,
#         valor_condominio_imovel,
#         valor_iptu_imovel,
#         nome_condominio_imovel,
#         valor_aluguel_imovel,
#         taxa_contrato_imovel,
#         local_chaves_imovel,
#         dados_condominio,
#         obs_internas,
#         dados_cond_imovel,
#         observacoes_imovel)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """
#     dados_cond_imovel = ""
#     observacoes_imovel = ""
#     dados = (fk_id_prop, fk_id_parceiro, valor_condominio, valor_do_iptu, nome_condominio,
#              valor_do_aluguel, taxa_de_contrato, local_das_chaves, dados_do_condominio,
#              observacoes_contratuais, dados_cond_imovel, observacoes_imovel)

#     id_imovel = __inserir_dados(connection, "imóvel", dados, sql, commit=commit)
#     return id_imovel


# def __inserir_dados(connection, tabela, dados: list, sql, commit=True):
#     cursor = None
#     try:
#         cursor = connection.cursor()
#         cursor.execute(sql, dados)
#         id = cursor.lastrowid
#         if commit:
#             connection.commit()
#         print(f"{tabela} inserido com sucesso!")
#         return id
#     except pymysql.Error as erro:
#         print(f"Erro ao inserir {tabela}: {erro}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()


# def obter_id_banco_por_numero(connection, numero_banco):
#     sql = "SELECT id_banco FROM bancos WHERE numero_banco = %s"
#     return __obter_id(connection, 'banco', numero_banco, sql)


# def obter_id_proprietario(connection, cpf):
#     sql = "SELECT p.id_prop  FROM proprietarios p WHERE p.documento_prop = %s AND p.exc_prop = 'F'"
#     return __obter_id(connection, 'proprietario', cpf, sql)


# def obter_id_parceiro(connection, cpf):
#     sql = "SELECT * FROM parceiros p WHERE p.documento_parceiro = %s AND p.exc_parceiro = 'F'"
#     return __obter_id(connection, 'parceiro', cpf, sql)


# def __obter_id(connection, tabela, var, sql):
#     cursor = None
#     try:
#         cursor = connection.cursor()

#         dados = (var,)
#         cursor.execute(sql, dados)

#         resultado = cursor.fetchone()
#         if resultado:
#             return resultado[0]

#         print(f"Nenhum {tabela} encontrado com o valor especificado. {var}")
#         return None

#     except pymysql.Error as erro:
#         print(f"Erro ao obter o id do {tabela}: {erro}")
#         return None
#     finally:
#         if cursor:
#             cursor.fetchall()
#             cursor.close()


# # INQUILINO
# def inserir_inquilino(connection, documento_inquilino, nome_inquilino, rg_inquilino,
#                       nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
#                       estado_civil_inquilino, regime_cassamento_inquilino,
#                       profissao_inquilino, dtnascimento_inquilino, genero_inquilino,
#                       nome_representante, documento_representante, exc_inquilino, date_lastupdate_inquilino,
#                       date_lastupdate_gpay_inquilino, fk_id_pretendente_pretendentes, user_add_inquilino,
#                       foto_documento, foto_inquilino_documento, foto_comprovante_renda, commit=True):

#     cursor = None
#     try:
#         cursor = connection.cursor()

#         sql = """
#         INSERT INTO inquilinos
#         (documento_inquilino, nome_inquilino, rg_inquilino,
#             nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
#              estado_civil_inquilino, regime_cassamento_inquilino,
#              profissao_inquilino, dtnascimento_inquilino , genero_inquilino,
#              nome_representante, documento_representante,
#              exc_inquilino, date_lastupdate_inquilino, date_lastupdate_gpay_inquilino,
#              fk_id_pretendente_pretendentes, user_add_inquilino,
#              foto_documento, foto_inquilino_documento, foto_comprovante_renda)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """

#         nome_representante = None
#         documento_representante = None
#         exc_inquilino = 'F'
#         date_lastupdate_inquilino = None
#         date_lastupdate_gpay_inquilino = None
#         fk_id_pretendente_pretendentes = None
#         user_add_inquilino = None
#         foto_documento = None
#         foto_inquilino_documento = None
#         foto_comprovante_renda = None

#         data = (documento_inquilino, nome_inquilino, rg_inquilino,
#                 nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
#                 estado_civil_inquilino, regime_cassamento_inquilino, profissao_inquilino,
#                 dtnascimento_inquilino, genero_inquilino, nome_representante, documento_representante,
#                 exc_inquilino, date_lastupdate_inquilino, date_lastupdate_gpay_inquilino,
#                 fk_id_pretendente_pretendentes, user_add_inquilino,
#                 foto_documento, foto_inquilino_documento, foto_comprovante_renda)

#         cursor.execute(sql, data)
#         id_inquilino = cursor.lastrowid
#         if commit:
#             connection.commit()
#         print(f"Inquilino inserido com sucesso! {id_inquilino}")
#         return id_inquilino
#     except pymysql.Error as erro:
#         print(f"Erro ao inserir o inquilino: {erro}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()


# def obter_contratos_db(connection):
#     if connection is None:
#         print("❌ Conexão com o banco é None. Não é possível obter contratos.")
#         return []
#     cursor = None
#     try:
#         cursor = connection.cursor()
#         cursor.execute("SELECT codigo_contrato FROM contratos")
#         resultado = cursor.fetchall()
#         return [str(row[0]) for row in resultado]
#     except pymysql.Error as erro:
#         print(f"Erro ao obter contratos do banco: {erro}")
#         return []
#     finally:
#         if cursor:
#             cursor.close()


# def inserir_endereco_inquilino(connection, cep, rua, numero, bairro, cidade, estado, complemento, ator_id, commit=True):
#     cursor = None
#     try:
#         cursor = connection.cursor()

#         sql = """INSERT INTO enderecos
#             (cep_end, rua_end, numero_end, bairro_end, cidade_end, estado_end,
#             complemento_end, fk_id_cat_pessoascategorias, id_ator)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """

#         fk_id_cat_pessoascategorias = 2
#         dados = (cep, rua, numero, bairro, cidade, estado,
#                  complemento, fk_id_cat_pessoascategorias, ator_id)

#         cursor.execute(sql, dados)
#         id_end = cursor.lastrowid
#         if commit:
#             connection.commit()
#         print(f"Endereco inserido com sucesso!")
#         return id_end
#     except pymysql.Error as erro:
#         print(f"Erro ao inserir endereco: {erro}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()

# import mysql.connector
import pymysql
import os

HOST_DB = os.getenv("DB_HOST")
DATABSE = os.getenv("DB_NAME")
USER_DB = os.getenv("DB_USER")
PASS_DB = os.getenv("DB_PASSWORD")


def get_connection():
    try:
        connection = pymysql.connect(
            host=HOST_DB, database=DATABSE, user=USER_DB, password=PASS_DB)
        return connection
    except pymysql.Error as erro:
        print(f"Ao fazer conexão no banco:\n {erro}")
        return None


def inserir_proprietario(connection, documento_prop, nome_prop, rg_prop,
                         nacionalidade_prop, telefone_prop, emails_prop,
                         estado_civil_prop, regime_casamento_prop,
                         profissao_prop, inscricao_estadual='', razao_social_empresa='',
                         nome_representante_empresa='', documento_representante_empresa='',
                         vinculo_empresa='', commit=True):
    sql = """
        INSERT INTO proprietarios
        (documento_prop, nome_prop, rg_prop, nacionalidade_prop, telefone_prop, emails_prop, 
        estado_civil_prop, regime_cassamento_prop, profissao_prop, exc_prop, user_add_prop, 
        uuid_prop, inscricao_estadual, razao_social_empresa, nome_represntante_empresa, 
        documento_representante_empresa, vinculo_empresa) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, UNHEX(REPLACE(UUID(),'-','')), %s, %s, %s, %s, %s)
    """

    exc_prop = 'F'
    user_add_prop = None

    dados = (documento_prop, nome_prop, rg_prop,
             nacionalidade_prop, telefone_prop, emails_prop,
             estado_civil_prop, regime_casamento_prop, profissao_prop,
             exc_prop, user_add_prop, inscricao_estadual,
             razao_social_empresa, nome_representante_empresa,
             documento_representante_empresa, vinculo_empresa)

    id = __inserir_dados(connection, "Proprietário", dados, sql, commit=commit)
    return id


def inserir_endereco(connection, fk_id_cat_pessoascategorias, cep, rua, numero, bairro, cidade, estado, complemento, ator_id, commit=True):

    sql = """INSERT INTO enderecos
        (cep_end, rua_end, numero_end, bairro_end, cidade_end, estado_end,
        complemento_end, fk_id_cat_pessoascategorias, id_ator)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    dados = (cep, rua, numero, bairro, cidade, estado,
             complemento, fk_id_cat_pessoascategorias, ator_id)

    id = __inserir_dados(connection, "Endereço", dados, sql, commit=commit)
    return id


def inserir_conta_bancaria(connection, fk_id_cat_pessoascategorias, fk_id_banco_bancos, numero_conta, agencia, tipo_conta, titular, documento, ator_id, commit=True):

    sql = """INSERT INTO contasbancarias
        (fk_id_banco_bancos, numerocc_conta, agencia_conta, tipo_conta, titular_conta,
        documento_conta, fk_id_cat_pessoascategorias, id_ator)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

    dados = (fk_id_banco_bancos, numero_conta, agencia, tipo_conta,
             titular, documento, fk_id_cat_pessoascategorias, ator_id)

    id = __inserir_dados(connection, "Conta Bancária",
                         dados, sql, commit=commit)
    return id

##########
def inserir_imovel(connection, fk_id_prop, fk_id_parceiro, valor_do_aluguel, taxa_de_contrato, local_das_chaves, observacoes_contratuais,
                   nome_condominio, valor_condominio, valor_do_iptu, dados_do_condominio, commit=True):

    sql = """INSERT INTO imoveis
        (fk_id_prop_proprietarios,
        fk_id_parceiro_parceiros,
        valor_condominio_imovel,
        valor_iptu_imovel,
        nome_condominio_imovel,
        valor_aluguel_imovel,
        taxa_contrato_imovel,
        local_chaves_imovel,
        dados_condominio,
        obs_internas,
        dados_cond_imovel,
        observacoes_imovel)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    dados_cond_imovel = ""
    observacoes_imovel = ""
    dados = (fk_id_prop, fk_id_parceiro, valor_condominio, valor_do_iptu, nome_condominio,
             valor_do_aluguel, taxa_de_contrato, local_das_chaves, dados_do_condominio,
             observacoes_contratuais, dados_cond_imovel, observacoes_imovel)

    id_imovel = __inserir_dados(
        connection, "imóvel", dados, sql, commit=commit)
    return id_imovel
##########

def inserir_contrato_iptu(connection, fk_id_contrato, valor_iptu_imovel,
                          fk_id_status_lancamento_iptu=1, primeira_parcela=0,
                          modelo_pagamento=None, qtd_parcelas_a_pagar=None,
                          ativo=None, fk_id_modelo_cobranca_iptu=None, commit=True):

    sql = """INSERT INTO contratos_iptu
        (fk_id_contrato, valor_iptu_imovel, fk_id_status_lancamento_iptu,
        primeira_parcela, modelo_pagamento, qtd_parcelas_a_pagar,
        ativo, fk_id_modelo_cobranca_iptu)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    dados = (fk_id_contrato, valor_iptu_imovel, fk_id_status_lancamento_iptu,
             primeira_parcela, modelo_pagamento, qtd_parcelas_a_pagar,
             ativo, fk_id_modelo_cobranca_iptu)

    id_contrato_iptu = __inserir_dados(
        connection, "contrato IPTU", dados, sql, commit=commit)
    return id_contrato_iptu

##########

def __inserir_dados(connection, tabela, dados: list, sql, commit=True):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(sql, dados)
        id = cursor.lastrowid
        if commit:
            connection.commit()
        print(f"{tabela} inserido com sucesso!")
        return id
    except pymysql.Error as erro:
        print(f"Erro ao inserir {tabela}: {erro}")
        raise
    finally:
        if cursor:
            cursor.close()


def obter_id_banco_por_numero(connection, numero_banco):
    sql = "SELECT id_banco FROM bancos WHERE numero_banco = %s"
    return __obter_id(connection, 'banco', numero_banco, sql)


def obter_id_proprietario(connection, cpf):
    sql = "SELECT p.id_prop  FROM proprietarios p WHERE p.documento_prop = %s AND p.exc_prop = 'F'"
    return __obter_id(connection, 'proprietario', cpf, sql)


def obter_id_parceiro(connection, cpf):
    sql = "SELECT * FROM parceiros p WHERE p.documento_parceiro = %s AND p.exc_parceiro = 'F'"
    return __obter_id(connection, 'parceiro', cpf, sql)


def __obter_id(connection, tabela, var, sql):
    try:
        print()
        cursor = connection.cursor()

        dados = (var,)
        cursor.execute(sql, dados)

        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]

        print(f"Nenhum {tabela} encontrado com o valor especificado. {var}")
        return None

    except pymysql.Error as erro:
        print(f"Erro ao obter o id do {tabela}: {erro}")
        return None
    finally:
        if cursor:
            cursor.fetchall()
            cursor.close()


# INQUILINO
def inserir_inquilino(connection, documento_inquilino, nome_inquilino, rg_inquilino,
                      nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
                      estado_civil_inquilino, regime_cassamento_inquilino,
                      profissao_inquilino, dtnascimento_inquilino, genero_inquilino,
                      nome_representante, documento_representante, exc_inquilino, date_lastupdate_inquilino,
                      date_lastupdate_gpay_inquilino, fk_id_pretendente_pretendentes, user_add_inquilino,
                      foto_documento, foto_inquilino_documento, foto_comprovante_renda, commit=True):

    cursor = None
    try:
        cursor = connection.cursor()

        sql = """
        INSERT INTO inquilinos
        (documento_inquilino, nome_inquilino, rg_inquilino,
            nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
             estado_civil_inquilino, regime_cassamento_inquilino,
             profissao_inquilino, dtnascimento_inquilino , genero_inquilino,
             nome_representante, documento_representante,
             exc_inquilino, date_lastupdate_inquilino, date_lastupdate_gpay_inquilino,
             fk_id_pretendente_pretendentes, user_add_inquilino,
             foto_documento, foto_inquilino_documento, foto_comprovante_renda)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        nome_representante = None
        documento_representante = None
        exc_inquilino = 'F'
        date_lastupdate_inquilino = None
        date_lastupdate_gpay_inquilino = None
        fk_id_pretendente_pretendentes = None
        user_add_inquilino = None
        foto_documento = None
        foto_inquilino_documento = None
        foto_comprovante_renda = None

        data = (documento_inquilino, nome_inquilino, rg_inquilino,
                nacionalidade_inquilino, telefone_inquilino, emails_inquilino,
                estado_civil_inquilino, regime_cassamento_inquilino, profissao_inquilino,
                dtnascimento_inquilino, genero_inquilino, nome_representante, documento_representante,
                exc_inquilino, date_lastupdate_inquilino, date_lastupdate_gpay_inquilino,
                fk_id_pretendente_pretendentes, user_add_inquilino,
                foto_documento, foto_inquilino_documento, foto_comprovante_renda)

        cursor.execute(sql, data)
        id_inquilino = cursor.lastrowid
        if commit:
            connection.commit()
        print(f"Inquilino inserido com sucesso! {id_inquilino}")
        return id_inquilino
    except pymysql.Error as erro:
        print(f"Erro ao inserir o inquilino: {erro}")
        raise
    finally:
        if cursor:
            cursor.close()


def obter_contratos_db(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT codigo_contrato FROM contratos")
        resultado = cursor.fetchall()
        return [str(row[0]) for row in resultado]
    except pymysql.Error as erro:
        print(f"Erro ao obter contratos do banco: {erro}")
        return []
    finally:
        cursor.close()


def inserir_endereco_inquilino(connection, cep, rua, numero, bairro, cidade, estado, complemento, ator_id, commit=True):
    cursor = None
    try:
        cursor = connection.cursor()

        sql = """INSERT INTO enderecos
            (cep_end, rua_end, numero_end, bairro_end, cidade_end, estado_end,
            complemento_end, fk_id_cat_pessoascategorias, id_ator)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

        fk_id_cat_pessoascategorias = 2
        dados = (cep, rua, numero, bairro, cidade, estado,
                 complemento, fk_id_cat_pessoascategorias, ator_id)

        cursor.execute(sql, dados)
        id_end = cursor.lastrowid
        if commit:
            connection.commit()
        print(f"Endereco inserido com sucesso!")
        return id_end
    except pymysql.Error as erro:
        print(f"Erro ao inserir endereco: {erro}")
        raise
    finally:
        if cursor:
            cursor.close()
