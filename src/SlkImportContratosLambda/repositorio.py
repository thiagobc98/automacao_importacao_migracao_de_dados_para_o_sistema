import pandas as pd
import utils.tool_db as tool_db
import contratos as contratos_db
from logs import Logger


class Repositorio:

    def __init__(self, logger: Logger):
        self.logger = logger

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def obter_contratos_existentes(self) -> set:
        conn = tool_db.get_connection()
        if conn is None:
            print(
                "⚠️ Sem conexão com o banco. Retornando lista vazia de contratos existentes.")
            return set()
        codigos = tool_db.obter_contratos_db(conn)
        conn.close()
        return set(codigos)

    # ------------------------------------------------------------------
    # Inserção atômica de um contrato completo
    # ------------------------------------------------------------------

    def inserir_contrato_completo(self, linha) -> bool:
        """
        Insere proprietarios, inquilinos, imoveis e contrato no banco.
        Usa uma unica conexao com transacao atomica: se qualquer insert falhar,
        tudo e revertido (rollback) e nenhum dado parcial fica no banco.
        Retorna True se tudo deu certo, False se houve erro.
        """
        codigo = linha["codigo_contrato"]

        #  def _to_float(val):
        #     if not val:
        #         return 0.0
        #     return float(str(val).replace(',', '.'))

        # Validação: somatório de percentual_repasse dos proprietários deve ser exatamente 100
        def _to_float(val):
            if not val:
                return 0.0
            try:
                return float(str(val).replace(',', '.'))
            except ValueError:
                return 0.0

        total_repasse: float = sum(
            _to_float(p['percentual_repasse']) for p in linha["proprietarios"]
        )
        if abs(total_repasse - 100.0) > 0.01:
            msg_erro = (
                f"[CONTRATO] Percentual de repasse dos proprietários soma {total_repasse:.2f}% "
                f"(esperado 100%).\n"
                f">> O que fazer: Ajuste os valores de percentual_repasse na planilha de "
                f"proprietários para que a soma seja exatamente 100%."
            )
            self.logger.geral(
                f"  ERRO: percentual_repasse soma {total_repasse:.2f}% para contrato {codigo}. "
                f"Importacao cancelada.",
                "ERRO"
            )
            self.logger.escrever_erros_contrato(codigo, [msg_erro])
            return False

        conn = tool_db.get_connection()
        conn.autocommit = False

        try:
            # ---- PROPRIETÁRIOS ----
            ids_props = []
            for prop in linha["proprietarios"]:
                row_prop = pd.Series(prop)
                for col in row_prop.index:
                    if pd.isna(row_prop[col]):
                        row_prop[col] = None

                self.logger.ok(
                    f"  Inserindo proprietario: {row_prop['cpf']} - {row_prop['nome']}")

                id_prop = tool_db.inserir_proprietario(
                    connection=conn,
                    documento_prop=row_prop['cpf'],
                    nome_prop=row_prop['nome'],
                    rg_prop=row_prop['rg'],
                    nacionalidade_prop=row_prop['naciolidade'],
                    telefone_prop=row_prop['telefone'],
                    emails_prop=row_prop['emails'],
                    estado_civil_prop=row_prop['estado_civil'],
                    regime_casamento_prop=row_prop['regime_casamento'],
                    profissao_prop=row_prop['profissao'],
                    inscricao_estadual=row_prop['inscricao_estadual'],
                    razao_social_empresa=row_prop['razao_social_empresa'],
                    nome_representante_empresa=row_prop['nome_representante_empresa'],
                    documento_representante_empresa=row_prop['cpf_representante_empresa'],
                    vinculo_empresa=row_prop['vinculo_empresa'],
                    commit=False,
                )
                self.logger.ok(f"    -> Proprietario: ID = {id_prop}")

                tool_db.inserir_endereco(
                    connection=conn,
                    fk_id_cat_pessoascategorias=1,
                    cep=row_prop['cep_endereco'],
                    rua=row_prop['rua_endereco'],
                    numero=row_prop['numero_endereco'],
                    bairro=row_prop['bairro_endereco'],
                    cidade=row_prop['cidade_endereco'],
                    estado=row_prop['estado_endereco'],
                    complemento=row_prop['complemento_endereco'],
                    ator_id=id_prop,
                    commit=False,
                )

                id_banco = tool_db.obter_id_banco_por_numero(
                    conn, str(row_prop['numero_banco']))
                tool_db.inserir_conta_bancaria(
                    connection=conn,
                    fk_id_cat_pessoascategorias=1,
                    fk_id_banco_bancos=id_banco,
                    numero_conta=row_prop['numero_conta'],
                    agencia=row_prop['agencia_conta'],
                    tipo_conta=row_prop['tipo_conta'],
                    titular=row_prop['nome_titular_conta'],
                    documento=row_prop['cpf_cnpj_da_conta'],
                    ator_id=id_prop,
                    commit=False,
                )
                ids_props.append({
                    'id_proprietario': id_prop,
                    # 'percentual_repasse': row_prop['percentual_repasse'],

                    'percentual_repasse': _to_float(row_prop['percentual_repasse']),
                })

            # ---- INQUILINOS ----
            ids_inqs = []
            for inq in linha["inquilinos"]:
                row_inq = pd.Series(inq)
                for col in row_inq.index:
                    if pd.isna(row_inq[col]):
                        row_inq[col] = None

                self.logger.ok(
                    f"  Inserindo inquilino: {row_inq['documento_inquilino']} - {row_inq['nome_inquilino']}")

                id_inq = tool_db.inserir_inquilino(
                    connection=conn,
                    documento_inquilino=row_inq['documento_inquilino'],
                    nome_inquilino=row_inq['nome_inquilino'],
                    rg_inquilino=row_inq['rg_inquilino'],
                    nacionalidade_inquilino=row_inq['nacionalidade_inquilino'],
                    telefone_inquilino=row_inq['telefone_inquilino'],
                    emails_inquilino=row_inq['emails_inquilino'],
                    estado_civil_inquilino=row_inq['estado_civil_inquilino'],
                    regime_cassamento_inquilino=row_inq['regime_cassamento_inquilino'],
                    profissao_inquilino=row_inq['profissao_inquilino'],
                    # dtnascimento_inquilino=row_inq['dtnascimento_inquilino'],
                    dtnascimento_inquilino=contratos_db._date_br(row_inq['dtnascimento_inquilino']),
                    genero_inquilino=row_inq['genero_inquilino'],
                    nome_representante=None, documento_representante=None,
                    exc_inquilino='F', date_lastupdate_inquilino=None,
                    date_lastupdate_gpay_inquilino=None,
                    fk_id_pretendente_pretendentes=None, user_add_inquilino=None,
                    foto_documento=None, foto_inquilino_documento=None,
                    foto_comprovante_renda=None,
                    commit=False,
                )
                self.logger.ok(f"    -> Inquilino: ID = {id_inq}")

                tool_db.inserir_endereco_inquilino(
                    connection=conn,
                    cep=row_inq['cep_end'],
                    rua=row_inq['rua_end'],
                    numero=row_inq['numero_end'],
                    bairro=row_inq['bairro_end'],
                    cidade=row_inq['cidade_end'],
                    estado=row_inq['estado_end'],
                    complemento=row_inq['complemento_end'],
                    ator_id=id_inq,
                    commit=False,
                )
                ids_inqs.append({
                    'id_inquilino': id_inq,
                    'inquilino_principal': row_inq['inquilino_principal'],
                })

            # ---- IMÓVEIS ----
            ids_imoveis = []
            for imovel in linha["imoveis"]:
                row_imov = pd.Series(imovel)
                for col in row_imov.index:
                    if pd.isna(row_imov[col]):
                        row_imov[col] = ''

                self.logger.ok(
                    f"  Inserindo imovel: parceiro={row_imov['documento_parceiro']} | CEP={row_imov['cep_endereco']}")

                id_prop_imov = tool_db.obter_id_proprietario(
                    conn, str(row_imov['documento_proprietario']))
                id_parc_imov = row_imov['fk_id_parceiro_parceiros']

                id_imov = tool_db.inserir_imovel(
                    connection=conn,
                    fk_id_prop=id_prop_imov,
                    fk_id_parceiro=id_parc_imov,
                    valor_do_aluguel=row_imov['valor_do_aluguel'],
                    taxa_de_contrato=row_imov['taxa_de_contrato'],
                    local_das_chaves=row_imov['local_das_chaves'],
                    observacoes_contratuais=row_imov['observacoes_contratuais'],
                    nome_condominio=row_imov['nome_condominio'],
                    valor_condominio=row_imov['valor_condominio'],
                    valor_do_iptu=row_imov['valor_do_iptu'],
                    dados_do_condominio=row_imov['dados_do_condominio'],
                    commit=False,
                )
                self.logger.ok(f"    -> Imovel: ID = {id_imov}")

                tool_db.inserir_endereco(
                    connection=conn,
                    fk_id_cat_pessoascategorias=5,
                    cep=row_imov['cep_endereco'],
                    rua=row_imov['rua_endereco'],
                    numero=row_imov['numero_endereco'],
                    bairro=row_imov['bairro_endereco'],
                    cidade=row_imov['cidade_endereco'],
                    estado=row_imov['estado_endereco'],
                    complemento=row_imov['complemento_endereco'],
                    ator_id=id_imov,
                    commit=False,
                )
                ########
                ids_imoveis.append({
                    'id_imovel': id_imov,
                    'id_parceiro': id_parc_imov,
                    'valor_iptu': row_imov['valor_do_iptu'],
                })
                ########

            # ---- CONTRATO ----
            row_cont = pd.Series(linha["contrato"])
            id_imovel_cont = ids_imoveis[0]['id_imovel']
            id_parceiro_cont = ids_imoveis[0]['id_parceiro']

            self.logger.ok(
                f"  Inserindo contrato: {codigo} | imovel={id_imovel_cont} | parceiro={id_parceiro_cont}")

            contratos_db.log_file = self.logger.sucesso_file
            id_contrato = contratos_db.insert_contrato(
                codigo_contrato=row_cont['codigo_contrato'],
                date_inicio_contrato=row_cont['date_inicio_contrato'],
                meses_duracao_contrato=row_cont['meses_duracao_contrato'],
                date_finalizacao_contrato=row_cont['date_finalizacao_contrato'],
                dia_vencimento_contrato=row_cont['dia_vencimento_contrato'],
                finalidade_contrato=row_cont['finalidade_contrato'],
                finalidade_locacao_contrato=row_cont['finalidade_locacao_contrato'],
                atividade_contrato=row_cont['atividade_contrato'],
                taxa_contrato=row_cont['taxa_contrato'],
                taxa_admin_contrato=row_cont['taxa_admin_contrato'],
                taxa_admin_minima_contrato=row_cont['taxa_admin_minima_contrato'],
                multa_atraso_contato=row_cont['multa_atraso_contato'],
                credito_multa_atraso_contrato=row_cont['credito_multa_atraso_contrato'],
                split_multa_atraso_contrato=row_cont['split_multa_atraso_contrato'],
                credito_split_multa_atraso_contrato=row_cont['credito_split_multa_atraso_contrato'],
                desconto_pontualidade_pagamento=row_cont['desconto_pontualidade_pagamento'],
                parcela_imob_multa_rescisoria=row_cont['parcela_imob_multa_rescisoria'],
                periodo_liberacao_sem_multa=row_cont['periodo_liberacao_sem_multa'],
                juros_atraso_ao_dia_contrato=row_cont['juros_atraso_ao_dia_contrato'],
                taxa_boleto_contrato=row_cont['taxa_boleto_contrato'],
                debito_taxa_boleto=row_cont['debito_taxa_boleto '],
                taxa_ted_contrato=row_cont['taxa_ted_contrato'],
                debito_taxa_ted_doc_pix=row_cont['debito_taxa_ted_doc_pix '],
                taxa_admin_parc_up_contrato=row_cont['taxa_admin_parc_up_contrato'],
                dia_repasse_contrato=row_cont['dia_repasse_contrato'],
                data_ocupacao_contrato=row_cont['data_ocupacao_contrato'],
                valor_aluguel_contrato=row_cont['valor_aluguel_contrato'],
                primeiro_aluguel_prop_contrato=row_cont['primeiro_aluguel_prop_contrato'],
                fk_garantia_locaticia=row_cont['fk_garantia_locaticia'],
                apolice_contrato=row_cont['apolice_contrato'],
                data_ultimo_reajuste_contrato=row_cont['data_ultimo_reajuste_contrato'],
                data_proximo_reajuste=row_cont['data_proximo_reajuste'],
                vencimento_seguro_fianca_contrato=row_cont['vencimento_seguro_fianca_contrato'],
                cobrar_ted_repasse_contrato=row_cont['cobrar_ted_repasse_contrato'],
                observacoes_contrato=row_cont['observacoes_contrato'],
                fk_id_imovel_imoveis=id_imovel_cont,
                fk_id_parceiro_parceiros=id_parceiro_cont,
                fk_id_seguradora_seguradoras=row_cont['fk_id_seguradora_seguradoras'],
                fk_id_indice_indices_reajuste=row_cont['fk_id_indice_indices_reajuste'],
                transferir_repasse_contrato=row_cont['transferir_repasse_contrato'],
                pontualizado=row_cont['pontualizado'],
                fk_id_produtos_up=row_cont['fk_id_produtos_up'],
                fk_cobertura_contrato=row_cont['fk_cobertura_contrato'],
                codigo_legado=row_cont['codigo_legado'],
                taxa_garantia_contrato=row_cont['taxa_garantia_contrato'],
                taxa_garantia_contrato_vl=row_cont['taxa_garantia_contrato_vl'],
                fk_tipo_garantia_taxa=row_cont['fk_tipo_garantia_taxa'],
                gerar_notas_fiscais=row_cont['gerar_notas_fiscais'],
                credito_taxa_boleto=row_cont['credito_taxa_boleto'],
                credito_taxa_ted_doc_pix=row_cont['credito_taxa_ted_doc_pix '],
                despesa_bancaria=row_cont['despesa_bancaria'],
                cobrar_despesa_bancaria=row_cont['cobrar_despesa_bancaria'],
                fk_tb_descricao_referencia_aluguel=row_cont['fk_tb_descricao_referencia_aluguel'],
                taxa_contrato_parc_up=row_cont['taxa_contrato_parc_up'],
                # modelo_pagamento_iptu=row_cont['modelo_pagamento_iptu'],  # coluna ainda nao existe no banco
                connection=conn,
                commit=False,
            )
            self.logger.ok(f"    -> Contrato: ID = {id_contrato}")

            # Vínculos inquilinos
            for inq in ids_inqs:
                contratos_db.insert_cont_inquilino(
                    id_contrato, inq['id_inquilino'], inq['inquilino_principal'],
                    connection=conn, commit=False,
                )

            # Vínculos proprietários
            for prop in ids_props:
                contratos_db.insert_cont_prop(
                    prop['id_proprietario'], id_contrato, prop['percentual_repasse'],
                    connection=conn, commit=False,
                )
                ########

            # IPTU do contrato
            _modelo_pag = row_cont.get('modelo_pagamento_iptu')
            tool_db.inserir_contrato_iptu(
                connection=conn,
                fk_id_contrato=id_contrato,
                valor_iptu_imovel=ids_imoveis[0]['valor_iptu'],
                modelo_pagamento=None if pd.isna(_modelo_pag) else _modelo_pag,
                commit=False,
            )
            ########

            conn.commit()
            self.logger.ok(
                f"  TRANSACAO COMMITADA COM SUCESSO para contrato {codigo}")
            return True

        except Exception as e:
            conn.rollback()
            self.logger.geral(
                f"  ERRO CRITICO ao inserir contrato {codigo}: {e}", "ERRO")
            self.logger.geral(
                "  ROLLBACK executado: nenhum dado parcial foi salvo no banco.", "ERRO")
            self.logger._escreve_direto(
                self.logger.erros_file, f"## 🚨 CONTRATO: `{codigo}` — Olhar com a TI")
            self.logger._escreve_direto(self.logger.erros_file, "")
            self.logger.erro(
                f"  ERRO CRITICO ao inserir contrato {codigo}: {e}")
            self.logger.erro(
                "  ROLLBACK executado: nenhum dado parcial foi salvo no banco.")
            self.logger._escreve_direto(self.logger.erros_file, "\n---\n")
            return False

        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Exportação de CSVs de erro
    # ------------------------------------------------------------------

    def salvar_csv_erro(self, lista_dfs: list, caminho: str, label: str):
        if lista_dfs:
            df_concat = pd.concat(lista_dfs)
            df_concat.to_csv(caminho, index=False, encoding='utf-8')
            self.logger.geral(
                f"  Gerado: {caminho}  ({len(df_concat)} linha(s) de {label})")
        else:
            self.logger.geral(
                f"  Sem dados de {label} com erro. Arquivo nao gerado.")
