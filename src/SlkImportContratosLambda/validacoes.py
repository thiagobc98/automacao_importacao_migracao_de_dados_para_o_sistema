import pandas as pd
import utils.valida_doc as valida_doc
import utils.tool_db as tool_db


class Validacoes:

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    @staticmethod
    def _validar_opcional_int(valor, lista_permitida: list) -> bool:
        if pd.isna(valor) or str(valor).strip() == "":
            return True
        try:
            return int(valor) in lista_permitida
        except Exception:
            return False

    @staticmethod
    def _validar_campo_opcional(valor, func) -> bool:
        if pd.isna(valor) or str(valor).strip() == "":
            return True
        return func(valor)

    @staticmethod
    def _str_dominio(valor) -> str:
        """Converte valor para string normalizada para comparação de domínio.
        Trata floats sem parte decimal: 1.0 -> '1', 3.0 -> '3', etc.
        """
        s = str(valor).strip()
        try:
            f = float(s)
            if f == int(f):
                return str(int(f))
        except (ValueError, OverflowError):
            pass
        return s

    # ------------------------------------------------------------------
    # Validações individuais
    # ------------------------------------------------------------------

    @classmethod
    def valida_contrato(cls, row) -> dict:
        result = {
            "doc":    row['documento_parceiro'],
            "codigo": row['codigo_contrato'],
        }

        result['documento_parceiro'] = (
            valida_doc.is_cpf(row['documento_parceiro']) or
            valida_doc.is_cnpj(row['documento_parceiro'])
        )

        colunas_obrigatorias = [
            'codigo_contrato', 'fk_id_parceiro_parceiros', 'documento_parceiro',
            'data_ocupacao_contrato', 'primeiro_aluguel_prop_contrato',
            'debito_taxa_boleto ', 'debito_taxa_ted_doc_pix ',
            'credito_taxa_boleto', 'credito_taxa_ted_doc_pix ',
            'meses_duracao_contrato', 'dia_vencimento_contrato',
            'taxa_contrato', 'taxa_admin_contrato', 'taxa_admin_minima_contrato',
            'multa_atraso_contato', 'credito_multa_atraso_contrato',
            'split_multa_atraso_contrato', 'desconto_pontualidade_pagamento',
            'juros_atraso_ao_dia_contrato', 'taxa_boleto_contrato',
            'taxa_ted_contrato', 'taxa_garantia_contrato', 'fk_tipo_garantia_taxa',
            'taxa_admin_parc_up_contrato', 'valor_aluguel_contrato',
            'fk_garantia_locaticia', 'data_ultimo_reajuste_contrato',
            'data_proximo_reajuste', 'cobrar_ted_repasse_contrato',
            'fk_id_seguradora_seguradoras', 'fk_id_indice_indices_reajuste',
            'transferir_repasse_contrato', 'pontualizado', 'fk_id_produtos_up',
            'fk_cobertura_contrato', 'codigo_legado',
            'cobrar_despesa_bancaria'
        ]
        result['col_vazias'] = [
            c for c in colunas_obrigatorias if pd.isna(row[c])]

        # Datas
        result['data_ocupacao_contrato'] = bool(
            valida_doc.validar_data(row['data_ocupacao_contrato']))
        result['data_ultimo_reajuste_contrato'] = bool(
            valida_doc.validar_data(row['data_ultimo_reajuste_contrato']))
        result['data_proximo_reajuste'] = bool(
            valida_doc.validar_data(row['data_proximo_reajuste']))
        result['date_inicio_contrato'] = bool(
            valida_doc.validar_data(row['date_inicio_contrato']))
        result['date_finalizacao_contrato'] = bool(
            valida_doc.validar_data(row['date_finalizacao_contrato']))
        result['vencimento_seguro_fianca_contrato'] = cls._validar_campo_opcional(
            row['vencimento_seguro_fianca_contrato'], valida_doc.validar_data)

        # Caracteres inválidos em campos numéricos
        campos_numericos = [
            'taxa_contrato', 'taxa_admin_contrato', 'taxa_admin_minima_contrato',
            'multa_atraso_contato', 'split_multa_atraso_contrato', 'desconto_pontualidade_pagamento',
            'parcela_imob_multa_rescisoria', 'juros_atraso_ao_dia_contrato', 'taxa_boleto_contrato',
            'taxa_ted_contrato', 'taxa_admin_parc_up_contrato', 'valor_aluguel_contrato',
            'taxa_garantia_contrato', 'taxa_garantia_contrato_vl', 'despesa_bancaria',
        ]
        result['campos_com_percentual'] = [
            campo for campo in campos_numericos
            if '%' in str(row.get(campo, ''))
        ]

        # Numericos BR
        result['taxa_contrato'] = bool(
            valida_doc.valida_formato_br(str(row['taxa_contrato'])))
        result['taxa_admin_contrato'] = bool(
            valida_doc.valida_formato_br(row['taxa_admin_contrato']))
        result['taxa_admin_minima_contrato'] = bool(
            valida_doc.valida_formato_br(row['taxa_admin_minima_contrato']))
        result['taxa_garantia_contrato'] = bool(
            valida_doc.valida_formato_br(row['taxa_garantia_contrato']))
        result['taxa_admin_parc_up_contrato'] = bool(
            valida_doc.valida_formato_br(row['taxa_admin_parc_up_contrato']))
        result['split_multa_atraso_contrato'] = bool(
            valida_doc.valida_formato_br(row['split_multa_atraso_contrato']))
        result['desconto_pontualidade_pagamento'] = bool(
            valida_doc.valida_formato_br(row['desconto_pontualidade_pagamento']))
        result['taxa_garantia_contrato_vl'] = bool(
            valida_doc.valida_formato_br(row['taxa_garantia_contrato_vl']))
        result['parcela_imob_multa_rescisoria'] = valida_doc.valida_numero_br(
            row['parcela_imob_multa_rescisoria'])
        result['juros_atraso_ao_dia_contrato'] = valida_doc.valida_numero_br(
            row['juros_atraso_ao_dia_contrato'])
        result['taxa_boleto_contrato'] = valida_doc.valida_numero_br(
            row['taxa_boleto_contrato'])
        result['taxa_ted_contrato'] = valida_doc.valida_numero_br(
            row['taxa_ted_contrato'])
        result['valor_aluguel_contrato'] = valida_doc.valida_numero_br(
            row['valor_aluguel_contrato'])
        result['multa_atraso_contato'] = valida_doc.valida_numero_br(
            row['multa_atraso_contato'])

        # Inteiros
        result['meses_duracao_contrato'] = bool(
            valida_doc.validar_int(row['meses_duracao_contrato']))
        result['periodo_liberacao_sem_multa'] = bool(
            valida_doc.validar_int(row['periodo_liberacao_sem_multa']))
        result['dia_vencimento_contrato'] = (
            bool(valida_doc.validar_int(row['dia_vencimento_contrato'])) and
            1 <= int(row['dia_vencimento_contrato']) <= 31
        )

        # Domínios
        result['finalidade_contrato'] = str(
            row['finalidade_contrato']) in ['', '1', '2']
        result['fk_tipo_garantia_taxa'] = cls._str_dominio(
            row['fk_tipo_garantia_taxa']) in ['1', '2', '3', '4']
        result['finalidade_locacao_contrato'] = str(
            row['finalidade_locacao_contrato']) in ['', '0', '1', '2', '3']
        result['primeiro_aluguel_prop_contrato'] = str(
            row['primeiro_aluguel_prop_contrato']) in ['V', 'F', 'AD', 'AL']
        result['cobrar_ted_repasse_contrato'] = str(
            row['cobrar_ted_repasse_contrato']) in ['V', 'F']
        result['transferir_repasse_contrato'] = str(
            row['transferir_repasse_contrato']) in ['V', 'F']
        result['gerar_notas_fiscais'] = cls._str_dominio(
            row['gerar_notas_fiscais']) in ['0', '1']
        result['cobrar_despesa_bancaria'] = cls._str_dominio(
            row['cobrar_despesa_bancaria']) in ['0', '1']
        result['credito_taxa_boleto'] = cls._str_dominio(
            row['credito_taxa_boleto']) in ['3', '5']
        result['credito_taxa_ted_doc_pix '] = cls._str_dominio(
            row['credito_taxa_ted_doc_pix ']) in ['3', '5']
        result['fk_garantia_locaticia'] = cls._validar_opcional_int(
            row['fk_garantia_locaticia'],           list(range(1, 11)))
        result['fk_id_seguradora_seguradoras'] = cls._validar_opcional_int(
            row['fk_id_seguradora_seguradoras'],    list(range(1, 21)))
        result['fk_id_indice_indices_reajuste'] = cls._validar_opcional_int(
            row['fk_id_indice_indices_reajuste'],   [1, 2, 3, 4, 5, 6, 7])
        result['pontualizado'] = cls._validar_opcional_int(
            row['pontualizado'],                    [0, 1, 2])
        result['fk_id_produtos_up'] = cls._validar_opcional_int(
            row['fk_id_produtos_up'],              [1, 2, 3, 4])
        result['fk_cobertura_contrato'] = cls._validar_opcional_int(
            row['fk_cobertura_contrato'],          [1, 2, 3])
        result['modelo_pagamento_iptu'] = cls._validar_opcional_int(
            row['modelo_pagamento_iptu'],           [1, 2, 3, 4])
        result['credito_multa_atraso_contrato'] = cls._validar_opcional_int(
            row['credito_multa_atraso_contrato'],  [1, 3, 5])
        result['credito_split_multa_atraso_contrato'] = cls._validar_opcional_int(
            row['credito_split_multa_atraso_contrato'], [1, 3, 5])
        result['fk_tb_descricao_referencia_aluguel'] = cls._validar_opcional_int(
            row['fk_tb_descricao_referencia_aluguel'], [1, 2])
        result['cobrar_despesa_bancaria'] = cls._str_dominio(
            row['cobrar_despesa_bancaria']) in ['0', '1']
        # Parceiro no banco
        result['parceiro'] = False
        if not pd.isna(row['documento_parceiro']):
            conn = tool_db.get_connection()
            id_parceiro = tool_db.obter_id_parceiro(
                conn, str(row['documento_parceiro']))
            conn.close()
            result['parceiro'] = id_parceiro if id_parceiro else False

        return result

    @staticmethod
    def valida_proprietario(row) -> dict:
        resultado = {"cpf": row.get("cpf"), "valores": {}}

        cpf = row.get("cpf")
        resultado["valores"]["cpf"] = cpf
        resultado["CPF"] = valida_doc.is_cpf(cpf) or valida_doc.is_cnpj(cpf)

        emails = row.get("emails")
        resultado["valores"]["emails"] = emails
        resultado["Emails"] = True
        for email in str(emails).split(','):
            if not valida_doc.is_email(email.strip()):
                resultado["Emails"] = False
                break

        rep = row.get("cpf_representante_empresa")
        resultado["valores"]["cpf_representante_empresa"] = rep
        resultado["Representante"] = True
        if not pd.isna(rep):
            resultado["Representante"] = valida_doc.is_cpf(
                rep) or valida_doc.is_cnpj(rep)

        cpf_conta = row.get("cpf_cnpj_da_conta")
        resultado["valores"]["cpf_cnpj_da_conta"] = cpf_conta
        resultado["CPF/CNPJ da conta"] = valida_doc.is_cpf(
            cpf_conta) or valida_doc.is_cnpj(cpf_conta)

        rg = row.get("rg")
        resultado["valores"]["rg"] = rg
        resultado["RG"] = valida_doc.is_rg(rg)

        numero_banco = row.get("numero_banco")
        resultado["valores"]["numero_banco"] = numero_banco
        resultado["Banco"] = False
        if not pd.isna(numero_banco):
            conn = tool_db.get_connection()
            id_banco = tool_db.obter_id_banco_por_numero(
                conn, str(numero_banco))
            conn.close()
            resultado["Banco"] = id_banco if id_banco else False

        colunas_obrigatorias = [
            'codigo_contrato', 'cpf', 'nome', 'telefone', 'emails',
            'percentual_repasse', 'nome_banco', 'numero_banco', 'numero_conta',
            'agencia_conta', 'tipo_conta', 'nome_titular_conta', 'cpf_cnpj_da_conta',
        ]
        resultado["col_vazias"] = [
            {"coluna": c, "valor": row.get(c)}
            for c in colunas_obrigatorias
            if pd.isna(row.get(c))
        ]

        tipo_conta = row.get("tipo_conta")
        resultado["valores"]["tipo_conta"] = tipo_conta
        resultado["tipo_conta"] = str(tipo_conta) in ['1', '2']

        resultado["campos_com_percentual"] = [
            campo for campo in ['percentual_repasse']
            if '%' in str(row.get(campo, ''))
        ]

        return resultado

    
    @staticmethod
    def valida_inquilino(row) -> dict:
        resultado = {"cpf_inquilino": row.get(
            "documento_inquilino"), "valores": {}}

        doc = row.get("documento_inquilino")
        resultado["valores"]["documento_inquilino"] = doc
        resultado["documento_inquilino"] = valida_doc.is_cpf(
            doc) or valida_doc.is_cnpj(doc)

        rg = row.get("rg_inquilino")
        resultado["valores"]["rg_inquilino"] = rg
        resultado["RG"] = True if pd.isna(rg) or str(
            rg).strip() == "" else valida_doc.is_rg(rg)

        email = row.get("emails_inquilino")
        resultado["valores"]["emails_inquilino"] = email
        resultado["emails_inquilino"] = True
        for e in str(email).split(','):
            if not valida_doc.is_email(e.strip()):
                resultado["emails_inquilino"] = False
                break

        cep = row.get("cep_end")
        resultado["valores"]["cep_end"] = cep
        resultado["cep_end"] = valida_doc.valida_cep(cep)

        ec = row.get("estado_civil_inquilino")
        resultado["valores"]["estado_civil_inquilino"] = ec
        resultado["estado_civil_inquilino"] = (
            True if pd.isna(ec) or str(ec).strip() == ""
            else valida_doc.validar_estado_civil(ec)
        )

        genero = row.get("genero_inquilino")
        resultado["valores"]["genero_inquilino"] = genero
        resultado["genero_inquilino"] = (
            True if pd.isna(genero) or str(genero).strip() == ""
            else valida_doc.validar_genero(genero)
        )

        colunas_obrigatorias = [
            'codigo_contrato', 'inquilino_principal', 'documento_inquilino',
            'nome_inquilino', 'telefone_inquilino', 'emails_inquilino',
            'cep_end', 'rua_end', 'numero_end', 'bairro_end', 'cidade_end', 'estado_end',
        ]
        resultado["col_vazias"] = [
            {"coluna": c, "valor": row.get(c)}
            for c in colunas_obrigatorias
            if pd.isna(row.get(c)) or str(row.get(c)).strip() == ""
        ]

        inq_principal = row.get("inquilino_principal")
        resultado["valores"]["inquilino_principal"] = inq_principal
        resultado["inquilino_principal"] = str(
            inq_principal) in ['V', 'F', 'A']

        dtnascimento = row.get("dtnascimento_inquilino")
        resultado["valores"]["dtnascimento_inquilino"] = dtnascimento
        resultado["dtnascimento_inquilino"] = (
            True if pd.isna(dtnascimento) or str(dtnascimento).strip() == ""
            else valida_doc.validar_data(dtnascimento)
        )

        return resultado

    

    @staticmethod
    def valida_imovel(row) -> dict:
        resultado = {
            "doc": row.get("documento_parceiro"),
            "cep": row.get("cep_endereco"),
            "valores": {},
        }

        doc = row.get("documento_parceiro")
        resultado["valores"]["documento_parceiro"] = doc
        resultado["documento_parceiro"] = valida_doc.is_cpf(
            doc) or valida_doc.is_cnpj(doc)

        doc_prop = row.get("documento_proprietario")
        resultado["valores"]["documento_proprietario"] = doc_prop
        resultado["documento_proprietario"] = valida_doc.is_cpf(
            doc_prop) or valida_doc.is_cnpj(doc_prop)

        cep = row.get("cep_endereco")
        resultado["valores"]["cep_endereco"] = cep
        resultado["cep_endereco"] = valida_doc.valida_cep(cep)

        estado = row.get("estado_endereco")
        resultado["valores"]["estado_endereco"] = estado
        resultado["estado_endereco"] = (
            False if pd.isna(estado) or str(estado).strip() == ""
            else len(str(estado).strip()) == 2
        )

        colunas_obrigatorias = [
            'codigo_contrato', 'documento_proprietario', 'fk_id_parceiro_parceiros',
            'documento_parceiro', 'cep_endereco', 'rua_endereco', 'numero_endereco',
            'bairro_endereco', 'cidade_endereco', 'estado_endereco',
            'valor_do_aluguel', 'taxa_de_contrato', 'valor_condominio', 'valor_do_iptu',
        ]
        resultado["col_vazias"] = [
            {"coluna": c, "valor": row.get(c)}
            for c in colunas_obrigatorias
            if pd.isna(row.get(c)) or str(row.get(c)).strip() == ""
        ]

        resultado["campos_com_percentual"] = [
            campo for campo in ['taxa_de_contrato']
            if '%' in str(row.get(campo, ''))
        ]

        resultado["parceiro"] = False
        if not pd.isna(doc) and str(doc).strip() != "":
            conn = tool_db.get_connection()
            id_parceiro = tool_db.obter_id_parceiro(conn, str(doc))
            conn.close()
            resultado["parceiro"] = id_parceiro if id_parceiro else False

        return resultado


    # ------------------------------------------------------------------
    # Checagem completa de erros de um contrato agrupado
    # ------------------------------------------------------------------

    @classmethod
    def checar_erros_contrato(cls, linha) -> list:
        """
        Valida todos os dados de um contrato agrupado.
        Retorna lista de strings descrevendo cada erro encontrado.
        Lista vazia = sem erros.
        """
        codigo = linha["codigo_contrato"]
        erros = []

        # CONTRATO
        contrato = linha["contrato"]
        if contrato:
            # Se o dia de repasse estiver vazio (ou preenchido como 0 pelo fillna), salva como null no banco
            dia_repasse = contrato.get("dia_repasse_contrato")
            if pd.isna(dia_repasse) or str(dia_repasse).strip() in [""]:
                contrato["dia_repasse_contrato"] = None

            row = pd.Series(contrato)
            log = cls.valida_contrato(row)

            for col in log['col_vazias']:
                erros.append(
                    f"  [CONTRATO] CAMPO OBRIGATORIO VAZIO: '{col}'\n"
                    f"             >> O que fazer: Preencha este campo na aba 'contratos' da planilha."
                )

            if not log['documento_parceiro']:
                erros.append(
                    f"  [CONTRATO] CPF/CNPJ DO PARCEIRO INVALIDO: '{log['doc']}'\n"
                    f"             >> O que e isso: O numero informado nao e um CPF nem CNPJ valido.\n"
                    f"             >> O que fazer: Use o formato 000.000.000-00 (CPF) ou 00.000.000/0000-00 (CNPJ)."
                )

            if not log['parceiro']:
                erros.append(
                    f"  [CONTRATO] PARCEIRO NAO ENCONTRADO NO BANCO: '{log['doc']}'\n"
                    f"             >> O que e isso: Nao existe nenhum parceiro cadastrado com esse documento.\n"
                    f"             >> O que fazer: Cadastre o parceiro no sistema antes de importar este contrato."
                )

            campos_data = {
                'date_inicio_contrato':          'Data de inicio do contrato (date_inicio_contrato)',
                'date_finalizacao_contrato':     'Data de finalizacao do contrato (date_finalizacao_contrato)',
                'data_ocupacao_contrato':        'Data de ocupacao (data_ocupacao_contrato)',
                'data_ultimo_reajuste_contrato': 'Data do ultimo reajuste (data_ultimo_reajuste_contrato)',
                'data_proximo_reajuste':         'Data do proximo reajuste (data_proximo_reajuste)',
                'vencimento_seguro_fianca_contrato': 'Vencimento do seguro/fianca (vencimento_seguro_fianca_contrato)',
            }
            for campo, descricao in campos_data.items():
                if not log.get(campo, True):
                    valor = contrato.get(campo, '?')
                    erros.append(
                        f"  [CONTRATO] DATA INVALIDA: {descricao} = '{valor}'\n"
                        f"             >> O que e isso: A data nao esta no formato correto.\n"
                        f"             >> O que fazer: Use o formato AAAA-MM-DD (exemplo: 2024-01-15)."
                    )

            campos_num = {
                'parcela_imob_multa_rescisoria': 'Parcela da multa rescisoria',
                'juros_atraso_ao_dia_contrato':  'Juros de atraso ao dia',
                'taxa_boleto_contrato':          'Taxa de boleto',
                'taxa_ted_contrato':             'Taxa TED',
                'valor_aluguel_contrato':        'Valor do aluguel',
                'multa_atraso_contato':          'Multa por atraso',
            }
            for campo, descricao in campos_num.items():
                if not log.get(campo, True):
                    valor = contrato.get(campo, '?')
                    erros.append(
                        f"  [CONTRATO] NUMERO INVALIDO: {descricao} ({campo}) = '{valor}'\n"
                        f"             >> O que fazer: Use o formato brasileiro, por exemplo: 1.500,00 ou 10,5."
                    )

            for campo in log.get('campos_com_percentual', []):
                valor = contrato.get(campo, '?')
                erros.append(
                    f"  [CONTRATO] CARACTERE INVALIDO NO CAMPO NUMERICO: '{campo}' = '{valor}'\n"
                    f"             >> O que fazer: Remova o '%' do campo. Use apenas numeros no formato brasileiro (ex: 10,5)."
                )

            campos_dominio = {
                'finalidade_contrato':                ('', ['vazio', '1', '2']),
                'finalidade_locacao_contrato':         ('', ['vazio', '0', '1', '2', '3']),
                'primeiro_aluguel_prop_contrato':      ('', ['V', 'F', 'AD', 'AL']),
                'cobrar_ted_repasse_contrato':         ('', ['V', 'F']),
                'transferir_repasse_contrato':         ('', ['V', 'F']),
                'gerar_notas_fiscais':                 ('', ['0', '1']),
                'cobrar_despesa_bancaria':             ('', ['0', '1']),
                'credito_taxa_boleto':                 ('', ['3', '5']),
                'credito_taxa_ted_doc_pix ':           ('', ['3', '5']),
                'fk_tipo_garantia_taxa':               ('', ['1', '2', '3', '4']),
                'fk_id_seguradora_seguradoras':        ('', ['1 a 20']),
                'fk_id_indice_indices_reajuste':       ('', ['1', '2', '3', '4', '5', '6', '7']),
                'pontualizado':                        ('', ['0', '1', '2']),
                'fk_id_produtos_up':                   ('', ['1', '2', '3', '4']),
                'fk_cobertura_contrato':               ('', ['1', '2', '3']),
                'modelo_pagamento_iptu':               ('', ['vazio', '1', '2', '3', '4']),
                'fk_garantia_locaticia':               ('', ['1 a 10']),
                'credito_multa_atraso_contrato':       ('', ['1', '3', '5']),
                'credito_split_multa_atraso_contrato': ('', ['1', '3', '5']),
                'fk_tb_descricao_referencia_aluguel':  ('', ['1', '2'])
            }
            for campo, (_, permitidos) in campos_dominio.items():
                if not log.get(campo, True):
                    valor = contrato.get(campo, '?')
                    erros.append(
                        f"  [CONTRATO] VALOR FORA DO PERMITIDO: '{campo}' = '{valor}'\n"
                        f"             >> O que fazer: Os valores aceitos sao: {', '.join(permitidos)}."
                    )

        # PROPRIETÁRIOS
        for i, prop in enumerate(linha["proprietarios"], 1):
            row = pd.Series(prop)
            log = cls.valida_proprietario(row)
            nome = prop.get('nome', f'Proprietario #{i}')
            cpf = prop.get('cpf', '?')
            prefixo = f"  [PROPRIETARIO #{i} | CPF: {cpf} | Nome: {nome}]"

            for col_info in log['col_vazias']:
                erros.append(
                    f"{prefixo} CAMPO OBRIGATORIO VAZIO: '{col_info['coluna']}'\n"
                    f"             >> O que fazer: Preencha este campo na aba 'proprietario' da planilha."
                )

            if not log['CPF']:
                erros.append(
                    f"{prefixo} CPF/CNPJ INVALIDO: '{log['valores']['cpf']}'\n"
                    f"             >> O que e isso: O numero informado nao e um CPF nem CNPJ valido.\n"
                    f"             >> O que fazer: Corrija para o formato 000.000.000-00 (CPF) ou 00.000.000/0000-00 (CNPJ)."
                )

            if not log['Emails']:
                erros.append(
                    f"{prefixo} EMAIL INVALIDO: '{log['valores']['emails']}'\n"
                    f"             >> O que fazer: Use o formato nome@dominio.com. Para varios emails, separe por virgula."
                )

            if not log['Banco']:
                erros.append(
                    f"{prefixo} BANCO NAO ENCONTRADO: numero_banco = '{log['valores']['numero_banco']}'\n"
                    f"             >> O que e isso: Esse numero de banco nao existe no sistema.\n"
                    f"             >> O que fazer: Verifique o codigo do banco (ex: 001=Banco do Brasil, 033=Santander, 341=Itau)."
                )

            if not log['tipo_conta']:
                erros.append(
                    f"{prefixo} TIPO DE CONTA INVALIDO: '{log['valores']['tipo_conta']}'\n"
                    f"             >> O que fazer: Use '1' para Conta Corrente ou '2' para Conta Poupanca."
                )

            for campo in log.get('campos_com_percentual', []):
                valor = prop.get(campo, '?')
                erros.append(
                    f"{prefixo} CARACTERE INVALIDO NO CAMPO NUMERICO: '{campo}' = '{valor}'\n"
                    f"             >> O que fazer: Remova o '%' do campo. Use apenas numeros no formato brasileiro (ex: 10,5)."
                )

        # INQUILINOS
        for i, inq in enumerate(linha["inquilinos"], 1):
            row = pd.Series(inq)
            log = cls.valida_inquilino(row)
            nome = inq.get('nome_inquilino', f'Inquilino #{i}')
            doc = inq.get('documento_inquilino', '?')
            prefixo = f"  [INQUILINO #{i} | Doc: {doc} | Nome: {nome}]"

            for col_info in log['col_vazias']:
                erros.append(
                    f"{prefixo} CAMPO OBRIGATORIO VAZIO: '{col_info['coluna']}'\n"
                    f"             >> O que fazer: Preencha este campo na aba 'inquilino' da planilha."
                )

            if not log['documento_inquilino']:
                erros.append(
                    f"{prefixo} CPF/CNPJ INVALIDO: '{log['valores']['documento_inquilino']}'\n"
                    f"             >> O que fazer: Corrija para o formato 000.000.000-00 (CPF) ou 00.000.000/0000-00 (CNPJ)."
                )

            if not log['emails_inquilino']:
                erros.append(
                    f"{prefixo} EMAIL INVALIDO: '{log['valores']['emails_inquilino']}'\n"
                    f"             >> O que fazer: Use o formato nome@dominio.com."
                )

            if not log['cep_end']:
                erros.append(
                    f"{prefixo} CEP INVALIDO: '{log['valores']['cep_end']}'\n"
                    f"             >> O que fazer: Use o formato 00000-000 (exemplo: 01310-100)."
                )

            if not log['RG']:
                erros.append(
                    f"{prefixo} RG INVALIDO: '{log['valores']['rg_inquilino']}'\n"
                    f"             >> O que fazer: Verifique o numero do RG informado."
                )

            if not log['dtnascimento_inquilino']:
                erros.append(
                    f"{prefixo} DATA DE NASCIMENTO INVALIDA: '{log['valores']['dtnascimento_inquilino']}'\n"
                    f"             >> O que fazer: Use o formato AAAA-MM-DD ou DD/MM/AAAA (exemplo: 1990-05-20 ou 20/05/1990)."
                )

        # IMOVEIS
        for i, imovel in enumerate(linha["imoveis"], 1):
            row = pd.Series(imovel)
            log = cls.valida_imovel(row)
            cep = imovel.get('cep_endereco', '?')
            doc = imovel.get('documento_parceiro', '?')
            prefixo = f"  [IMOVEL #{i} | CEP: {cep} | Parceiro: {doc}]"

            for col_info in log['col_vazias']:
                erros.append(
                    f"{prefixo} CAMPO OBRIGATORIO VAZIO: '{col_info['coluna']}'\n"
                    f"             >> O que fazer: Preencha este campo na aba 'imoveis' da planilha."
                )

            if not log['documento_parceiro']:
                erros.append(
                    f"{prefixo} DOC PARCEIRO INVALIDO: '{log['valores']['documento_parceiro']}'\n"
                    f"             >> O que fazer: Corrija para CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)."
                )

            if not log['cep_endereco']:
                erros.append(
                    f"{prefixo} CEP INVALIDO: '{log['valores']['cep_endereco']}'\n"
                    f"             >> O que fazer: Use o formato 00000-000 (exemplo: 01310-100)."
                )

            if not log['estado_endereco']:
                erros.append(
                    f"{prefixo} ESTADO INVALIDO: '{log['valores']['estado_endereco']}'\n"
                    f"             >> O que fazer: Use a sigla do estado com 2 letras (ex: SP, RJ, MG, BA)."
                )

            if not log['parceiro']:
                erros.append(
                    f"{prefixo} PARCEIRO NAO ENCONTRADO NO BANCO: '{doc}'\n"
                    f"             >> O que e isso: Esse parceiro nao esta cadastrado no sistema.\n"
                    f"             >> O que fazer: Cadastre o parceiro antes de importar este imovel."
                )

            for campo in log.get('campos_com_percentual', []):
                valor = imovel.get(campo, '?')
                erros.append(
                    f"{prefixo} CARACTERE INVALIDO NO CAMPO NUMERICO: '{campo}' = '{valor}'\n"
                    f"             >> O que fazer: Remova o '%' do campo. Use apenas numeros no formato brasileiro (ex: 10,5)."
                )

        return erros

        