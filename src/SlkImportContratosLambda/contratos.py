import pandas as pd
from pymysql import Error
from time import sleep
import utils.valida_doc as valida_doc
import utils.tool_db as tool_db
import datetime

SEP = "=" * 70
SEP_MENOR = "-" * 50


def _int(v):
    """Converte para int de forma segura. Retorna None para None/NaN."""
    try:
        return None if pd.isna(v) else int(float(v))
    except (ValueError, TypeError):
        return None


def _flt(v):
    """Converte para float de forma segura. Aceita formato BR (vírgula como separador decimal). Retorna None para None/NaN."""
    try:
        if pd.isna(v):
            return None
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().rstrip('%')
        if ',' in s:
            s = s.replace('.', '').replace(',', '.')
        return float(s)
    except (ValueError, TypeError):
        return None


def _date_br(v):
    """Converte data de DD/MM/YYYY para YYYY-MM-DD. Aceita também YYYY-MM-DD diretamente. Retorna None para None/NaN."""
    try:
        if pd.isna(v):
            return None
        s = str(v).strip()
        if not s:
            return None
        if '/' in s:
            return datetime.datetime.strptime(s, "%d/%m/%Y").strftime("%Y-%m-%d")
        return s
    except (ValueError, TypeError, AttributeError):
        return None


def _str(v):
    """Retorna None para None/NaN, str para outros valores."""
    try:
        return None if pd.isna(v) else (None if str(v).strip() == '' else str(v))
    except (ValueError, TypeError):
        return str(v) if v is not None else None


def read_data(path_csv):
    df = pd.read_csv(path_csv)
    df = df.drop(df.columns[0], axis=1)
    print(df)
    return df.iloc[3:]


def get_id_imovel(df, codigo_contrato):
    result = df[df['codigo_contrato'] == codigo_contrato]
    if not result.empty:
        return result.iloc[0]['id_imovel']
    return None


def get_id_parceiro(df, codigo_contrato):
    result = df[df['codigo_contrato'] == codigo_contrato]
    if not result.empty:
        return result.iloc[0]['id_parceiro']
    return None


def converter_para_float(valor):
    valor = str(valor).replace('.', '').replace(',', '.')
    return float(valor)


def valida_dados(row):
    result = {
        "doc": row['documento_parceiro'],
        "codigo": row['codigo_contrato'],
        "_vals": {col: row[col] for col in row.index},
    }

    # Válidando CPF/CNPJ do parceiro
    result['documento_parceiro'] = True if valida_doc.is_cpf(
        row['documento_parceiro']) or valida_doc.is_cnpj(row['documento_parceiro']) else False

    colunas_vazias = []
    for col_name in ['codigo_contrato', 'fk_id_parceiro_parceiros', 'documento_parceiro', 'data_ocupacao_contrato',
                     'primeiro_aluguel_prop_contrato', 'debito_taxa_boleto ', 'debito_taxa_ted_doc_pix ',
                     'credito_taxa_boleto', 'credito_taxa_ted_doc_pix ',
                     'meses_duracao_contrato', 'dia_vencimento_contrato', 'taxa_contrato',
                     'taxa_admin_contrato', 'taxa_admin_minima_contrato', 'multa_atraso_contato',
                     'credito_multa_atraso_contrato', 'split_multa_atraso_contrato',
                     'desconto_pontualidade_pagamento',
                     'juros_atraso_ao_dia_contrato', 'taxa_boleto_contrato', 'taxa_ted_contrato',
                     'taxa_garantia_contrato', 'fk_tipo_garantia_taxa', 'taxa_admin_parc_up_contrato',
                     'data_ocupacao_contrato', 'valor_aluguel_contrato', 'fk_garantia_locaticia',
                     'data_ultimo_reajuste_contrato', 'data_proximo_reajuste',
                     'cobrar_ted_repasse_contrato', 'fk_id_seguradora_seguradoras',
                     'fk_id_indice_indices_reajuste', 'transferir_repasse_contrato',
                     'pontualizado', 'fk_id_produtos_up', 'fk_cobertura_contrato', 'codigo_legado', 'cobrar_despesa_bancaria', 'taxa_contrato_parc_up']:
        value = row[col_name]
        if pd.isna(value):
            colunas_vazias.append(col_name)
    result['col_vazias'] = colunas_vazias

     # Validando formato de data (cada campo individualmente)
    result['data_ocupacao_contrato'] = True if valida_doc.validar_data(
        row['data_ocupacao_contrato']) else False
    result['data_ultimo_reajuste_contrato'] = True if valida_doc.validar_data(
        row['data_ultimo_reajuste_contrato']) else False
    result['data_proximo_reajuste'] = True if valida_doc.validar_data(
        row['data_proximo_reajuste']) else False
    result['date_inicio_contrato'] = True if valida_doc.validar_data(
        row['date_inicio_contrato']) else False
    result['date_finalizacao_contrato'] = True if valida_doc.validar_data(
        row['date_finalizacao_contrato']) else False
    result['vencimento_seguro_fianca_contrato'] = True if valida_doc.validar_data(
        row['vencimento_seguro_fianca_contrato']) else False

    # Validando formato br (valores monetários/percentuais)
    result['taxa_contrato'] = True if valida_doc.valida_formato_br(
        str(row['taxa_contrato'])) else False
    result['taxa_admin_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_admin_contrato']) else False
    result['taxa_admin_minima_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_admin_minima_contrato']) else False
    result['taxa_admin_parc_up_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_admin_parc_up_contrato']) else False
    result['parcela_imob_multa_rescisoria'] = True if valida_doc.valida_formato_br(
        row['parcela_imob_multa_rescisoria']) else False
    result['juros_atraso_ao_dia_contrato'] = True if valida_doc.valida_formato_br(
        row['juros_atraso_ao_dia_contrato']) else False
    result['taxa_boleto_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_boleto_contrato']) else False
    result['taxa_ted_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_ted_contrato']) else False
    result['taxa_garantia_contrato'] = True if valida_doc.valida_formato_br(
        row['taxa_garantia_contrato']) else False
    result['valor_aluguel_contrato'] = True if valida_doc.valida_formato_br(
        row['valor_aluguel_contrato']) else False
    result['multa_atraso_contato'] = True if valida_doc.valida_formato_br(
        row['multa_atraso_contato']) else False
    result['taxa_garantia_contrato_vl'] = True if valida_doc.valida_formato_br(
        row['taxa_garantia_contrato_vl']) else False
    result['split_multa_atraso_contrato'] = True if valida_doc.valida_formato_br(
        row['split_multa_atraso_contrato']) else False
    result['desconto_pontualidade_pagamento'] = True if valida_doc.valida_formato_br(
        row['desconto_pontualidade_pagamento']) else False
    result['despesa_bancaria'] = True if valida_doc.valida_formato_br(
        row['despesa_bancaria']) else False
    result['taxa_contrato_parc_up'] = True if valida_doc.valida_formato_br(
        row['taxa_contrato_parc_up']) else False

    # Validando se está como int
    result['meses_duracao_contrato'] = True if valida_doc.validar_int(
        row['meses_duracao_contrato']) else False
    result['periodo_liberacao_sem_multa'] = True if valida_doc.validar_int(
        row['periodo_liberacao_sem_multa']) else False
    result['dia_vencimento_contrato'] = (True if (valida_doc.validar_int(
        row['dia_vencimento_contrato']) and 1 <= int(row['dia_vencimento_contrato']) <= 31) else False)
    result['dia_repasse_contrato'] = (True if (valida_doc.validar_int(
        row['dia_repasse_contrato']) and 1 <= int(row['dia_repasse_contrato']) <= 31) else False)

    # Validando se está de acordo com descrição TI
    result['finalidade_contrato'] = False if str(
        row['finalidade_contrato']) not in ['', '1', '2'] else True
    result['fk_tipo_garantia_taxa'] = False if str(
        row['fk_tipo_garantia_taxa']) not in ['1', '2', '3', '4'] else True
    result['finalidade_locacao_contrato'] = False if str(
        row['finalidade_locacao_contrato']) not in ['', '0', '1', '2', '3'] else True
    result['primeiro_aluguel_prop_contrato'] = False if str(
        row['primeiro_aluguel_prop_contrato']) not in ['V', 'F', 'AD', 'AL'] else True
    result['fk_garantia_locaticia'] = False if int(row['fk_garantia_locaticia']) not in [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10] else True
    result['cobrar_ted_repasse_contrato'] = False if str(
        row['cobrar_ted_repasse_contrato']) not in ['V', 'F'] else True
    result['fk_id_seguradora_seguradoras'] = False if int(row['fk_id_seguradora_seguradoras']) not in [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20] else True
    result['fk_id_indice_indices_reajuste'] = False if int(
        row['fk_id_indice_indices_reajuste']) not in [1, 2, 3, 4, 5, 6, 7] else True
    result['transferir_repasse_contrato'] = False if str(
        row['transferir_repasse_contrato']) not in ['V', 'F'] else True
    result['pontualizado'] = False if int(
        row['pontualizado']) not in [0, 1, 2] else True
    result['fk_id_produtos_up'] = False if int(
        row['fk_id_produtos_up']) not in [1, 2, 3, 4] else True
    result['fk_cobertura_contrato'] = False if int(
        row['fk_cobertura_contrato']) not in [1, 2, 3] else True
    # result['modelo_pagamento_iptu'] = False if str(
    #     row['modelo_pagamento_iptu']) not in ['', '1', '2', '3', '4'] else True  # coluna ainda nao existe no banco
    result['gerar_notas_fiscais'] = False if str(row['gerar_notas_fiscais']) not in [
        1, 0] else True
    result['credito_taxa_boleto'] = False if str(row['credito_taxa_boleto']) not in [
        3, 5] else True
    result['debito_taxa_boleto'] = False if str(row['debito_taxa_boleto']) not in [
        2, 3] else True
    result['credito_taxa_ted_doc_pix '] = False if str(row['credito_taxa_ted_doc_pix ']) not in [
        3, 5] else True
    result['debito_taxa_ted_doc_pix'] = False if str(row['debito_taxa_ted_doc_pix']) not in [
        1, 3] else True
    result['credito_multa_atraso_contrato'] = False if int(
        row['credito_multa_atraso_contrato']) not in [1, 3, 5] else True
    result['credito_split_multa_atraso_contrato'] = False if int(
        row['credito_split_multa_atraso_contrato']) not in [1, 3, 5] else True
    result['fk_tb_descricao_referencia_aluguel'] = False if int(
        row['fk_tb_descricao_referencia_aluguel']) not in [1, 2] else True
    result['cobrar_despesa_bancaria'] = False if str(row['cobrar_despesa_bancaria']) not in [
        0, 1] else True

    connection = tool_db.get_connection()
    result['parceiro'] = False
    if not pd.isna(row['documento_parceiro']):
        id_parceiro = tool_db.obter_id_parceiro(
            connection, str(row['documento_parceiro']))
        result['parceiro'] = False if id_parceiro is None else id_parceiro
    connection.close()

    return result


def insert_contrato(codigo_contrato,
                    date_inicio_contrato,
                    meses_duracao_contrato,
                    date_finalizacao_contrato,
                    dia_vencimento_contrato,
                    finalidade_contrato,
                    finalidade_locacao_contrato,
                    atividade_contrato,
                    taxa_contrato,
                    taxa_admin_contrato,
                    taxa_admin_minima_contrato,
                    multa_atraso_contato,
                    credito_multa_atraso_contrato,
                    split_multa_atraso_contrato,
                    credito_split_multa_atraso_contrato,
                    desconto_pontualidade_pagamento,
                    parcela_imob_multa_rescisoria,
                    periodo_liberacao_sem_multa,
                    juros_atraso_ao_dia_contrato,
                    taxa_boleto_contrato,
                    debito_taxa_boleto,
                    taxa_ted_contrato,
                    debito_taxa_ted_doc_pix,
                    taxa_admin_parc_up_contrato,
                    dia_repasse_contrato,
                    data_ocupacao_contrato,
                    valor_aluguel_contrato,
                    primeiro_aluguel_prop_contrato,
                    fk_garantia_locaticia,
                    apolice_contrato,
                    data_ultimo_reajuste_contrato,
                    data_proximo_reajuste,
                    vencimento_seguro_fianca_contrato,
                    cobrar_ted_repasse_contrato,
                    observacoes_contrato,
                    fk_id_imovel_imoveis,
                    fk_id_parceiro_parceiros,
                    fk_id_seguradora_seguradoras,
                    fk_id_indice_indices_reajuste,
                    transferir_repasse_contrato,
                    pontualizado,
                    fk_id_produtos_up,
                    fk_cobertura_contrato,
                    codigo_legado,
                    taxa_garantia_contrato,
                    taxa_garantia_contrato_vl,
                    fk_tipo_garantia_taxa,
                    gerar_notas_fiscais,
                    credito_taxa_boleto,
                    credito_taxa_ted_doc_pix,
                    despesa_bancaria,
                    cobrar_despesa_bancaria,
                    fk_tb_descricao_referencia_aluguel,         
                    taxa_contrato_parc_up,
                    # modelo_pagamento_iptu=None,  # coluna ainda não existe no banco
                    connection=None,
                    commit=True,
                    log_file=None
                    ):
    _own_connection = connection is None
    _log_file = log_file or globals().get('log_file', 'logs/contratos.txt')
    cursor = None
    try:
        if _own_connection:
            connection = tool_db.get_connection()

        fk_id_status_status_contrato = 13  # assinado
        exc_contrato = 'F'
        enviado_porto_contrato = 'F'
        migracao = 1  # Sim
        fk_id_lmi = 6  # 0

        cursor = connection.cursor()

        insert_query = """
        INSERT INTO contratos (
            codigo_contrato,
            date_inicio_contrato,
            meses_duracao_contrato,
            date_finalizacao_contrato,
            dia_vencimento_contrato,
            finalidade_contrato,
            finalidade_locacao_contrato,
            atividade_contrato,
            taxa_contrato,
            taxa_admin_contrato,
            taxa_admin_minima_contrato,
            multa_atraso_contato,
            credito_multa_atraso_contrato,
            split_multa_atraso_contrato,
            credito_split_multa_atraso_contrato,
            desconto_pontualidade_pagamento,
            parcela_imob_multa_rescisoria,
            periodo_liberacao_sem_multa,
            juros_atraso_ao_dia_contrato,
            taxa_boleto_contrato,
            debito_taxa_boleto,
            taxa_ted_contrato,
            debito_taxa_ted_doc_pix,
            taxa_admin_parc_up_contrato,
            dia_repasse_contrato,
            data_ocupacao_contrato,
            valor_aluguel_contrato,
            primeiro_aluguel_prop_contrato,
            fk_garantia_locaticia,
            apolice_contrato,
            data_ultimo_reajuste_contrato,
            data_proximo_reajuste,
            vencimento_seguro_fianca_contrato,
            cobrar_ted_repasse_contrato,
            observacoes_contrato,
            fk_id_imovel_imoveis,
            fk_id_parceiro_parceiros,
            fk_id_seguradora_seguradoras,
            fk_id_indice_indices_reajuste,
            fk_id_status_status_contrato,
            transferir_repasse_contrato,
            exc_contrato,
            enviado_porto_contrato,
            pontualizado,
            migracao,
            fk_id_lmi,
            fk_id_produtos_up,
            fk_cobertura_contrato,
            codigo_legado,
            taxa_garantia_contrato,
            taxa_garantia_contrato_vl,
            fk_tipo_garantia_taxa,
            gerar_notas_fiscais,
            credito_taxa_boleto,
            credito_taxa_ted_doc_pix,
            despesa_bancaria,
            cobrar_despesa_bancaria,
            fk_tb_descricao_referencia_aluguel,
            taxa_contrato_parc_up
            
            /* modelo_pagamento_iptu: adicionar aqui quando a coluna existir no banco */
        ) VALUES (
          %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        cursor.execute(insert_query, (
            _str(codigo_contrato),
            _date_br(date_inicio_contrato),
            _int(meses_duracao_contrato),
            _date_br(date_finalizacao_contrato),
            _int(dia_vencimento_contrato),
            _str(finalidade_contrato),
            _str(finalidade_locacao_contrato),
            _str(atividade_contrato),
            _flt(taxa_contrato),
            _flt(taxa_admin_contrato),
            _flt(taxa_admin_minima_contrato),
            _flt(multa_atraso_contato),
            _int(credito_multa_atraso_contrato),
            _flt(split_multa_atraso_contrato),
            _int(credito_split_multa_atraso_contrato),
            _flt(desconto_pontualidade_pagamento),
            _flt(parcela_imob_multa_rescisoria),
            _int(periodo_liberacao_sem_multa),
            _flt(juros_atraso_ao_dia_contrato),
            _flt(taxa_boleto_contrato),
            _int(debito_taxa_boleto),
            _flt(taxa_ted_contrato),
            _int(debito_taxa_ted_doc_pix),
            _flt(taxa_admin_parc_up_contrato),
            _int(dia_repasse_contrato),
            _date_br(data_ocupacao_contrato),
            _flt(valor_aluguel_contrato),
            _str(primeiro_aluguel_prop_contrato),
            _int(fk_garantia_locaticia),
            _str(apolice_contrato),
            _date_br(data_ultimo_reajuste_contrato),
            _date_br(data_proximo_reajuste),
            _date_br(vencimento_seguro_fianca_contrato),
            _str(cobrar_ted_repasse_contrato),
            _str(observacoes_contrato),
            _int(fk_id_imovel_imoveis),
            _int(fk_id_parceiro_parceiros),
            _int(fk_id_seguradora_seguradoras),
            _int(fk_id_indice_indices_reajuste),
            _int(fk_id_status_status_contrato),
            _str(transferir_repasse_contrato),
            exc_contrato,
            enviado_porto_contrato,
            _int(pontualizado),
            migracao,
            _int(fk_id_lmi),
            _int(fk_id_produtos_up),
            _int(fk_cobertura_contrato),
            _str(codigo_legado),
            _flt(taxa_garantia_contrato),
            _flt(taxa_garantia_contrato_vl),
            _int(fk_tipo_garantia_taxa),
            _int(gerar_notas_fiscais),
            _int(credito_taxa_boleto),
            _int(credito_taxa_ted_doc_pix),
            _flt(despesa_bancaria),
            _str(cobrar_despesa_bancaria),
            _int(fk_tb_descricao_referencia_aluguel),
            _flt(taxa_contrato_parc_up),
            # _int(modelo_pagamento_iptu),  # coluna ainda nao existe no banco
        ))
        if commit:
            connection.commit()
        id_contrato = cursor.lastrowid
        generete_log(_log_file,
                     f"  CONTRATO INSERIDO COM SUCESSO! "
                     f"ID_CONTRATO: {id_contrato} | CODIGO_CONTRATO: {codigo_contrato} | "
                     f"PONTUALIZADO: {pontualizado}", "OK")
        return id_contrato

    except Error as erro:
        generete_log(_log_file,
                     f"  FALHA AO INSERIR CONTRATO! "
                     f"CODIGO_CONTRATO: {codigo_contrato} | "
                     f"Erro tecnico do banco de dados: {erro}", "ERRO")
        raise

    finally:
        if cursor:
            cursor.close()
        if _own_connection and connection:
            connection.close()


def insert_cont_inquilino(fk_id_contrato_contrato, fk_id_inquilino_inquilinos, principal_ci, connection=None, commit=True):
    _own_connection = connection is None
    cursor = None
    try:
        if _own_connection:
            connection = tool_db.get_connection()

        if connection is not None:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO contratos_inquilinos
            (fk_id_contrato_contrato, fk_id_inquilino_inquilinos, principal_ci)
            VALUES(%s, %s, %s);
            """

            cursor.execute(insert_query, (fk_id_contrato_contrato,
                           fk_id_inquilino_inquilinos, principal_ci))
            if commit:
                connection.commit()
            id_ci = cursor.lastrowid
            generete_log(log_file,
                         f"  Vinculo contrato-inquilino inserido! "
                         f"ID: {id_ci} | FK_CONTRATO: {fk_id_contrato_contrato} | "
                         f"FK_INQUILINO: {fk_id_inquilino_inquilinos} | "
                         f"PRINCIPAL: {principal_ci}", "OK")
            return id_ci

    except Error as erro:
        generete_log(log_file,
                     f"  FALHA ao vincular inquilino ao contrato! "
                     f"FK_CONTRATO: {fk_id_contrato_contrato} | "
                     f"FK_INQUILINO: {fk_id_inquilino_inquilinos} | "
                     f"Erro tecnico: {erro}", "ERRO")
        raise
    finally:
        if cursor:
            cursor.close()
        if _own_connection and connection:
            connection.close()


def insert_cont_prop(fk_id_prop_proprietarios, fk_id_contrato_contratos, repasse_prop_cp, connection=None, commit=True):
    _own_connection = connection is None
    cursor = None
    try:
        if _own_connection:
            connection = tool_db.get_connection()
        if connection is not None:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO contratos_proprietarios
            (fk_id_prop_proprietarios, fk_id_contrato_contratos, repasse_prop_cp)
            VALUES(%s, %s, %s);
            """
            cursor.execute(insert_query, (fk_id_prop_proprietarios,
                           fk_id_contrato_contratos, repasse_prop_cp))
            if commit:
                connection.commit()
            id_cp = cursor.lastrowid
            generete_log(log_file,
                         f"  Vinculo contrato-proprietario inserido! "
                         f"ID: {id_cp} | FK_CONTRATO: {fk_id_contrato_contratos} | "
                         f"FK_PROP: {fk_id_prop_proprietarios} | "
                         f"REPASSE: {repasse_prop_cp}", "OK")
            return id_cp

    except Error as erro:
        generete_log(log_file,
                     f"  FALHA ao vincular proprietario ao contrato! "
                     f"FK_CONTRATO: {fk_id_contrato_contratos} | "
                     f"FK_PROP: {fk_id_prop_proprietarios} | "
                     f"Erro tecnico: {erro}", "ERRO")
        raise
    finally:
        if cursor:
            cursor.close()
        if _own_connection and connection:
            connection.close()


def generete_log(log_file, text, level="INFO"):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level:<5}] {text}"
    print(line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write('\n' + line)


def main():
    path_contrato = fr"data\contratos.csv"
    path_imovel = fr"response\imoveis.csv"
    path_inquilno = fr"response\inquilinos.csv"
    path_proprietario = fr"response\proprietarios.csv"
    global log_file
    log_file = fr"logs\contratos.txt"

    start_time = datetime.datetime.now()

    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO ] {SEP}\n")
        f.write(
            f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO ] INICIO DA VALIDACAO DE CONTRATOS\n")
        f.write(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO ] {SEP}")

    df = pd.read_csv(path_contrato)
    df = df.drop(df.columns[0], axis=1)
    df = df.iloc[4:]
    df_imovel = pd.read_csv(path_imovel)
    df_inquilino = pd.read_csv(path_inquilno)
    df_inquilino['dtnascimento_inquilino'] = df_inquilino['dtnascimento_inquilino'].apply(
        _date_br)
    df_proprietario = pd.read_csv(path_proprietario)
    df_proprietario['percentual_repasse'] = df_proprietario['percentual_repasse'].apply(
        converter_para_float)

    df['juros_atraso_ao_dia_contrato'] = df['juros_atraso_ao_dia_contrato'].apply(
        converter_para_float)
    df['taxa_admin_minima_contrato'] = df['taxa_admin_minima_contrato'].apply(
        converter_para_float)
    df['taxa_admin_contrato'] = df['taxa_admin_contrato'].apply(
        converter_para_float)
    df['multa_atraso_contato'] = df['multa_atraso_contato'].apply(
        converter_para_float)
    df['taxa_contrato'] = df['taxa_contrato'].apply(converter_para_float)
    df['taxa_boleto_contrato'] = df['taxa_boleto_contrato'].apply(
        converter_para_float)
    df['taxa_ted_contrato'] = df['taxa_ted_contrato'].apply(
        converter_para_float)
    df['taxa_garantia_contrato'] = df['taxa_garantia_contrato'].apply(
        converter_para_float)
    df['taxa_admin_parc_up_contrato'] = df['taxa_admin_parc_up_contrato'].apply(
        converter_para_float)
    df['valor_aluguel_contrato'] = df['valor_aluguel_contrato'].apply(
        converter_para_float)
    df['split_multa_atraso_contrato'] = df['split_multa_atraso_contrato'].apply(
        converter_para_float)
    df['desconto_pontualidade_pagamento'] = df['desconto_pontualidade_pagamento'].apply(
        converter_para_float)
    df['taxa_garantia_contrato_vl'] = df['taxa_garantia_contrato_vl'].apply(
        converter_para_float)
    df['taxa_contrato_parc_up'] = df['taxa_contrato_parc_up'].apply(
        converter_para_float)

    # Substituir NaN por valores padrão
    df.fillna({
        'codigo_contrato': '',
        'date_inicio_contrato': '0000-00-00',
        'meses_duracao_contrato': 0,
        'date_finalizacao_contrato': '0000-00-00',
        'dia_vencimento_contrato': 0,
        'finalidade_contrato': '',
        'finalidade_locacao_contrato': '',
        'atividade_contrato': '',
        'taxa_contrato': 0.0,
        'taxa_admin_contrato': 0.0,
        'taxa_admin_minima_contrato': 0.0,
        'multa_atraso_contato': 0.0,
        'credito_multa_atraso_contrato': 5,
        'split_multa_atraso_contrato': 0.0,
        'credito_split_multa_atraso_contrato': 3,
        'desconto_pontualidade_pagamento': 0.0,
        'parcela_imob_multa_rescisoria': 0.0,
        'periodo_liberacao_sem_multa': 0.0,
        'juros_atraso_ao_dia_contrato': 0.0,
        'taxa_boleto_contrato': 0.0,
        'debito_taxa_boleto ': 2,
        'taxa_ted_contrato': 0.0,
        'debito_taxa_ted_doc_pix ': 1,
        'credito_taxa_boleto': 5,
        'credito_taxa_ted_doc_pix ': 5,
        'taxa_servico_contrato': 0.0,
        'premio_seguro_contrato': 0.0,
        'taxa_admin_parc_up_contrato': 0.0,
        'data_ocupacao_contrato': '0000-00-00',
        'data_proximo_reajuste': '0000-00-00',
        'valor_aluguel_contrato': 0.0,
        'primeiro_aluguel_prop_contrato': '',
        'fk_garantia_locaticia': '',
        'apolice_contrato': '',
        'data_ultimo_reajuste_contrato': '0000-00-00',
        'vencimento_seguro_fianca_contrato': '0000-00-00',
        'cobrar_ted_repasse_contrato': '',
        'observacoes_contrato': '',
        'fk_id_seguradora_seguradoras': 0,
        'fk_id_indice_indices_reajuste': 0,
        'transferir_repasse_contrato': '',
        'fk_id_produtos_up': 0,
        'fk_cobertura_contrato': 0,
        'taxa_garantia_contrato_vl': 0.0,
        'taxa_contrato_parc_up': 0.0
    }, inplace=True)

    generete_log(log_file, f"Total de registros a validar: {len(df)}")

    response_valida = df.apply(valida_dados, axis=1)

    erros = False
    total_com_erro = 0

    for pos, (_, log) in enumerate(response_valida.items(), 1):
        generete_log(log_file, SEP)
        generete_log(log_file,
                     f"REGISTRO #{pos} | DOC_PARCEIRO: {log['doc']} | CODIGO_CONTRATO: {log['codigo']}")
        generete_log(log_file, SEP_MENOR)

        count = 0

        # --- Verifica campos vazios/nulos ---
        if len(log['col_vazias']) != 0:
            for col in log['col_vazias']:
                generete_log(log_file,
                             f"  CAMPO VAZIO: '{col}' nao pode ser vazio ou nulo", "ERRO")
            count += len(log['col_vazias'])

        # --- Verifica CPF/CNPJ do parceiro ---
        if not log['documento_parceiro']:
            generete_log(log_file,
                         f"  CAMPO INVALIDO: 'documento_parceiro' = '{log['doc']}' "
                         f"| Esperado: CPF (xxx.xxx.xxx-xx) ou CNPJ (xx.xxx.xxx/xxxx-xx) valido", "ERRO")
            count += 1

        # --- Verifica parceiro no banco de dados ---
        if not log['parceiro']:
            generete_log(log_file,
                         f"  PARCEIRO NAO ENCONTRADO: o documento '{log['doc']}' nao existe "
                         f"na tabela de parceiros. Cadastre o parceiro antes de importar o contrato.", "ERRO")
            count += 1

        # --- Verifica datas (cada uma individualmente) ---
        campos_data = {
            'date_inicio_contrato': 'Data de inicio do contrato',
            'date_finalizacao_contrato': 'Data de finalizacao do contrato',
            'data_ocupacao_contrato': 'Data de ocupacao',
            'data_ultimo_reajuste_contrato': 'Data do ultimo reajuste',
            'data_proximo_reajuste': 'Data do proximo reajuste',
            'vencimento_seguro_fianca_contrato': 'Vencimento do seguro/fianca',
        }
        for campo, descricao in campos_data.items():
            if not log[campo]:
                valor = log['_vals'].get(campo, '?')
                generete_log(log_file,
                             f"  CAMPO INVALIDO: '{campo}' ({descricao}) = '{valor}' "
                             f"| Esperado: data no formato YYYY-MM-DD ou 0000-00-00", "ERRO")
                count += 1

        # --- Verifica valores monetários/percentuais (formato BR) ---
        campos_br = {
            'taxa_contrato': 'Taxa do contrato',
            'taxa_admin_contrato': 'Taxa de administracao',
            'taxa_admin_minima_contrato': 'Taxa de administracao minima',
            'multa_atraso_contato': 'Multa por atraso',
            'split_multa_atraso_contrato': 'Split da multa por atraso',
            'desconto_pontualidade_pagamento': 'Desconto por pontualidade',
            'parcela_imob_multa_rescisoria': 'Parcela imobiliaria da multa rescisoria',
            'juros_atraso_ao_dia_contrato': 'Juros de atraso ao dia',
            'taxa_boleto_contrato': 'Taxa de boleto',
            'taxa_ted_contrato': 'Taxa TED',
            'taxa_garantia_contrato': 'Taxa de garantia',
            'taxa_admin_parc_up_contrato': 'Taxa admin parceiro UP',
            'valor_aluguel_contrato': 'Valor do aluguel',
            'taxa_garantia_contrato_vl': 'Taxa de garantia VL',
        }
        for campo, descricao in campos_br.items():
            if not log[campo]:
                valor = log['_vals'].get(campo, '?')
                generete_log(log_file,
                             f"  CAMPO INVALIDO: '{campo}' ({descricao}) = '{valor}' "
                             f"| Esperado: numero no formato brasileiro (ex: 1.500,00)", "ERRO")
                count += 1

        # --- Verifica campos inteiros ---
        if not log['meses_duracao_contrato']:
            valor = log['_vals'].get('meses_duracao_contrato', '?')
            generete_log(log_file,
                         f"  CAMPO INVALIDO: 'meses_duracao_contrato' = '{valor}' "
                         f"| Esperado: numero inteiro (ex: 12, 24, 30)", "ERRO")
            count += 1

        if not log['periodo_liberacao_sem_multa']:
            valor = log['_vals'].get('periodo_liberacao_sem_multa', '?')
            generete_log(log_file,
                         f"  CAMPO INVALIDO: 'periodo_liberacao_sem_multa' = '{valor}' "
                         f"| Esperado: numero inteiro", "ERRO")
            count += 1

        if not log['dia_vencimento_contrato']:
            valor = log['_vals'].get('dia_vencimento_contrato', '?')
            generete_log(log_file,
                         f"  CAMPO INVALIDO: 'dia_vencimento_contrato' = '{valor}' "
                         f"| Esperado: numero inteiro entre 1 e 31", "ERRO")
            count += 1

        # --- Verifica campos de domínio (valores permitidos fixos) ---
        campos_dominio = [
            ('finalidade_contrato', log['finalidade_contrato'],
             log['_vals'].get('finalidade_contrato', '?'), "Valores aceitos: '' (vazio), '1' ou '2'"),
            ('finalidade_locacao_contrato', log['finalidade_locacao_contrato'],
             log['_vals'].get('finalidade_locacao_contrato', '?'), "Valores aceitos: '' (vazio), '0', '1', '2' ou '3'"),
            ('primeiro_aluguel_prop_contrato', log['primeiro_aluguel_prop_contrato'],
             log['_vals'].get('primeiro_aluguel_prop_contrato', '?'), "Valores aceitos: 'V', 'F', 'AD' ou 'AL'"),
            ('fk_garantia_locaticia', log['fk_garantia_locaticia'],
             log['_vals'].get('fk_garantia_locaticia', '?'), "Valores aceitos: 1 a 10"),
            ('cobrar_ted_repasse_contrato', log['cobrar_ted_repasse_contrato'],
             log['_vals'].get('cobrar_ted_repasse_contrato', '?'), "Valores aceitos: 'V' ou 'F'"),
            ('fk_id_seguradora_seguradoras', log['fk_id_seguradora_seguradoras'],
             log['_vals'].get('fk_id_seguradora_seguradoras', '?'), "Valores aceitos: 1 a 20"),
            ('fk_id_indice_indices_reajuste', log['fk_id_indice_indices_reajuste'],
             log['_vals'].get('fk_id_indice_indices_reajuste', '?'), "Valores aceitos: 1, 2, 3, 4, 5, 6 ou 7"),
            ('transferir_repasse_contrato', log['transferir_repasse_contrato'],
             log['_vals'].get('transferir_repasse_contrato', '?'), "Valores aceitos: 'V' ou 'F'"),
            ('pontualizado', log['pontualizado'],
             log['_vals'].get('pontualizado', '?'), "Valores aceitos: 0, 1 ou 2"),
            ('fk_id_produtos_up', log['fk_id_produtos_up'],
             log['_vals'].get('fk_id_produtos_up', '?'), "Valores aceitos: 1, 2, 3, 4"),
            ('fk_cobertura_contrato', log['fk_cobertura_contrato'],
             log['_vals'].get('fk_cobertura_contrato', '?'), "Valores aceitos: 1, 2 ou 3"),
            # ('modelo_pagamento_iptu', log['modelo_pagamento_iptu'],
            #  log['_vals'].get('modelo_pagamento_iptu', '?'), "Valores aceitos: '' (vazio), '1', '2', '3' ou '4'"),  # coluna ainda nao existe no banco
            ('fk_tipo_garantia_taxa', log['fk_tipo_garantia_taxa'],
             log['_vals'].get('fk_tipo_garantia_taxa', '?'), "Valores aceitos: '1', '2', '3' ou '4'"),
            ('credito_multa_atraso_contrato', log['credito_multa_atraso_contrato'],
             log['_vals'].get('credito_multa_atraso_contrato', '?'), "Valores aceitos: 1, 3 ou 5"),
            ('credito_split_multa_atraso_contrato', log['credito_split_multa_atraso_contrato'],
             log['_vals'].get('credito_split_multa_atraso_contrato', '?'), "Valores aceitos: 1, 3 ou 5"),
            ('gerar_notas_fiscais', log['gerar_notas_fiscais'],
             log['_vals'].get('gerar_notas_fiscais', '?'), "Valores aceitos: 0 ou 1"),
            ('credito_taxa_boleto', log['credito_taxa_boleto'],
             log['_vals'].get('credito_taxa_boleto', '?'), "Valores aceitos: 3 ou 5"),
            ('credito_taxa_ted_doc_pix ', log['credito_taxa_ted_doc_pix '],
             log['_vals'].get('credito_taxa_ted_doc_pix ', '?'), "Valores aceitos: 3 ou 5"),
            ('fk_tb_descricao_referencia_aluguel', log['fk_tb_descricao_referencia_aluguel'],
             log['_vals'].get('fk_tb_descricao_referencia_aluguel', '?'), "Valores aceitos: 1 ou 2")
        ]

        for campo, valido, valor, dica in campos_dominio:
            if not valido:
                generete_log(log_file,
                             f"  CAMPO INVALIDO: '{campo}' = '{valor}' | {dica}", "ERRO")
                count += 1

        if count != 0:
            generete_log(log_file,
                         f"  >>> TOTAL DE ERROS NESTE REGISTRO: {count} <<<", "ERRO")
            erros = True
            total_com_erro += 1
        else:
            generete_log(
                log_file, "  Registro OK - nenhum erro encontrado", "OK")

    # Resumo da validação
    generete_log(log_file, SEP)
    generete_log(log_file, "RESUMO DA VALIDACAO DE CONTRATOS")
    generete_log(log_file, SEP_MENOR)
    generete_log(log_file, f"  Total de registros analisados : {len(df)}")
    generete_log(
        log_file, f"  Registros sem erros           : {len(df) - total_com_erro}")
    generete_log(
        log_file, f"  Registros COM ERRO            : {total_com_erro}")
    generete_log(log_file, SEP)

    if not erros:
        generete_log(
            log_file, "TODOS OS REGISTROS VALIDADOS! INICIANDO INSERCAO NO BANCO...")
        generete_log(log_file, SEP)

        for pos, (index, row) in enumerate(df.iterrows(), 1):
            fk_id_imovel_imoveis = get_id_imovel(
                df_imovel, row['codigo_contrato'])
            fk_id_parceiro_parceiros = get_id_parceiro(
                df_imovel, row['codigo_contrato'])

            generete_log(log_file, SEP_MENOR)
            generete_log(log_file,
                         f"INSERINDO CONTRATO #{pos} | CODIGO: {row['codigo_contrato']} | "
                         f"ID_IMOVEL: {fk_id_imovel_imoveis} | ID_PARCEIRO: {fk_id_parceiro_parceiros}")

            for col in row.index:
                if pd.isna(row[col]) or row[col] == '' or row[col] == '0000-00-00':
                    row[col] = None

            id_contrato = insert_contrato(
                codigo_contrato=row['codigo_contrato'],
                date_inicio_contrato=row['date_inicio_contrato'],
                meses_duracao_contrato=row['meses_duracao_contrato'],
                date_finalizacao_contrato=row['date_finalizacao_contrato'],
                dia_vencimento_contrato=row['dia_vencimento_contrato'],
                finalidade_contrato=row['finalidade_contrato'],
                finalidade_locacao_contrato=row['finalidade_locacao_contrato'],
                atividade_contrato=row['atividade_contrato'],
                taxa_contrato=row['taxa_contrato'],
                taxa_admin_contrato=row['taxa_admin_contrato'],
                taxa_admin_minima_contrato=row['taxa_admin_minima_contrato'],
                multa_atraso_contato=row['multa_atraso_contato'],
                credito_multa_atraso_contrato=row['credito_multa_atraso_contrato'],
                split_multa_atraso_contrato=row['split_multa_atraso_contrato'],
                credito_split_multa_atraso_contrato=row['credito_split_multa_atraso_contrato'],
                desconto_pontualidade_pagamento=row['desconto_pontualidade_pagamento'],
                parcela_imob_multa_rescisoria=row['parcela_imob_multa_rescisoria'],
                periodo_liberacao_sem_multa=row['periodo_liberacao_sem_multa'],
                juros_atraso_ao_dia_contrato=row['juros_atraso_ao_dia_contrato'],
                taxa_boleto_contrato=row['taxa_boleto_contrato'],
                debito_taxa_boleto=row['debito_taxa_boleto '],
                taxa_ted_contrato=row['taxa_ted_contrato'],
                debito_taxa_ted_doc_pix=row['debito_taxa_ted_doc_pix '],
                taxa_admin_parc_up_contrato=row['taxa_admin_parc_up_contrato'],
                dia_repasse_contrato=row['dia_repasse_contrato'],
                data_ocupacao_contrato=row['data_ocupacao_contrato'],
                valor_aluguel_contrato=row['valor_aluguel_contrato'],
                primeiro_aluguel_prop_contrato=row['primeiro_aluguel_prop_contrato'],
                fk_garantia_locaticia=row['fk_garantia_locaticia'],
                apolice_contrato=row['apolice_contrato'],
                data_ultimo_reajuste_contrato=row['data_ultimo_reajuste_contrato'],
                data_proximo_reajuste=row['data_proximo_reajuste'],
                vencimento_seguro_fianca_contrato=row['vencimento_seguro_fianca_contrato'],
                cobrar_ted_repasse_contrato=row['cobrar_ted_repasse_contrato'],
                observacoes_contrato=row['observacoes_contrato'],
                fk_id_imovel_imoveis=fk_id_imovel_imoveis,
                fk_id_parceiro_parceiros=row['fk_id_parceiro_parceiros'],
                fk_id_seguradora_seguradoras=row['fk_id_seguradora_seguradoras'],
                fk_id_indice_indices_reajuste=row['fk_id_indice_indices_reajuste'],
                transferir_repasse_contrato=row['transferir_repasse_contrato'],
                pontualizado=row['pontualizado'],
                fk_id_produtos_up=row['fk_id_produtos_up'],
                fk_cobertura_contrato=row['fk_cobertura_contrato'],
                codigo_legado=row['codigo_legado'],
                taxa_garantia_contrato=row['taxa_garantia_contrato'],
                taxa_garantia_contrato_vl=row['taxa_garantia_contrato_vl'],
                fk_tipo_garantia_taxa=row['fk_tipo_garantia_taxa'],
                gerar_notas_fiscais=row['gerar_notas_fiscais'],
                credito_taxa_boleto=row['credito_taxa_boleto'],
                credito_taxa_ted_doc_pix=row['credito_taxa_ted_doc_pix '],
                despesa_bancaria=row['despesa_bancaria'],
                cobrar_despesa_bancaria=row['cobrar_despesa_bancaria'],
                fk_tb_descricao_referencia_aluguel=row['fk_tb_descricao_referencia_aluguel'],
                taxa_contrato_parc_up=row['taxa_contrato_parc_up'],
                # modelo_pagamento_iptu=row['modelo_pagamento_iptu'],
            )

            # Vinculando inquilinos ao contrato
            df_inqui_temp = df_inquilino[df_inquilino['codigo_contrato']
                                         == row['codigo_contrato']]
            if df_inqui_temp.empty:
                generete_log(log_file,
                             f"  AVISO: Nenhum inquilino encontrado para o contrato '{row['codigo_contrato']}'",
                             "AVISO")
            else:
                generete_log(log_file,
                             f"  Vinculando {len(df_inqui_temp)} inquilino(s) ao contrato ID {id_contrato}...")
                for _, row_inqui in df_inqui_temp.iterrows():
                    insert_cont_inquilino(
                        id_contrato, row_inqui['id_inquilino'], row_inqui['inquilino_principal'])

            # Vinculando proprietários ao contrato
            df_prop_temp = df_proprietario[df_proprietario['codigo_contrato']
                                           == row['codigo_contrato']]
            if df_prop_temp.empty:
                generete_log(log_file,
                             f"  AVISO: Nenhum proprietario encontrado para o contrato '{row['codigo_contrato']}'",
                             "AVISO")
            else:
                generete_log(log_file,
                             f"  Vinculando {len(df_prop_temp)} proprietario(s) ao contrato ID {id_contrato}...")
                for _, row_prop in df_prop_temp.iterrows():
                    insert_cont_prop(
                        row_prop['id_proprietario'], id_contrato, row_prop['percentual_repasse'])

            sleep(5)

        end_time = datetime.datetime.now()
        generete_log(log_file, SEP)
        generete_log(
            log_file, "IMPORTACAO CONCLUIDA COM SUCESSO - CONTRATOS", "OK")
        generete_log(
            log_file, f"  Data/Hora termino  : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        generete_log(
            log_file, f"  Tempo total        : {end_time - start_time}")
        generete_log(log_file, SEP)
    else:
        generete_log(log_file,
                     "IMPORTACAO CANCELADA! CONTRATOS TEM ERROS DE VALIDACAO.", "ERRO")
        generete_log(log_file,
                     "Corrija TODOS os erros listados acima e execute novamente.", "ERRO")
        generete_log(log_file, SEP)


if __name__ == '__main__':
    main()