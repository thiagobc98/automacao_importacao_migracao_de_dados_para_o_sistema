import pandas as pd
import gspread
import download
from logs import Logger


def _converter_para_float(valor) -> float:
    valor = str(valor).replace('.', '').replace(',', '.')
    return float(valor)


class DownloaderPlanilha:

    CAMPOS_FLOAT_CONTRATO = [
        'taxa_contrato', 'taxa_admin_contrato', 'taxa_admin_minima_contrato',
        'multa_atraso_contato', 'split_multa_atraso_contrato', 'desconto_pontualidade_pagamento',
        'parcela_imob_multa_rescisoria', 'juros_atraso_ao_dia_contrato', 'taxa_boleto_contrato',
        'taxa_ted_contrato', 'taxa_garantia_contrato', 'taxa_admin_parc_up_contrato',
        'valor_aluguel_contrato', 'taxa_garantia_contrato_vl', 'despesa_bancaria'
    ]

    FILLNA_CONTRATOS = {
        'codigo_contrato': '', 'meses_duracao_contrato': 0, 'dia_vencimento_contrato': 0,
        'finalidade_contrato': '', 'finalidade_locacao_contrato': '', 'atividade_contrato': '',
        'taxa_contrato': 0.0, 'taxa_admin_contrato': 0.0, 'taxa_admin_minima_contrato': 0.0,
        'multa_atraso_contato': 0.0, 'parcela_imob_multa_rescisoria': 0.0,
        'periodo_liberacao_sem_multa': 0.0, 'juros_atraso_ao_dia_contrato': 0.0,
        'taxa_boleto_contrato': 0.0, 'debito_taxa_boleto ': 2, 'taxa_ted_contrato': 0.0,
        'debito_taxa_ted_doc_pix ': 1, 'credito_taxa_boleto': 5, 'credito_taxa_ted_doc_pix ': 5,
        'taxa_servico_contrato': 0.0, 'premio_seguro_contrato': 0.0,
        'taxa_admin_parc_up_contrato': 0.0,
        'valor_aluguel_contrato': 0.0, 'primeiro_aluguel_prop_contrato': '',
        'fk_garantia_locaticia': '', 'apolice_contrato': '',
        'cobrar_ted_repasse_contrato': '', 'observacoes_contrato': '',
        'fk_id_seguradora_seguradoras': 0, 'fk_id_indice_indices_reajuste': 0,
        'transferir_repasse_contrato': '', 'fk_id_produtos_up': 0,
        'fk_id_parceiro_garantia_parceiro_garantias': 0,
    }

    def __init__(self, code_sheets: str, logger: Logger, gc: gspread.Client) -> None:
        self.code_sheets = code_sheets
        self.logger = logger
        self.gc = gc

    def executar(self) -> None:
        self.logger.geral(self.logger.SEP)
        self.logger.geral("ETAPA 1: BAIXANDO A PLANILHA DO GOOGLE SHEETS")
        self.logger.geral(self.logger.SEP)
        download.executar(self.code_sheets, self.gc)
        self.logger.geral("Download concluido com sucesso!")

    def carregar_dados(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Le os CSVs, faz o pre-processamento e retorna
        (df_contratos, df_proprietarios, df_inquilinos, df_imoveis).
        """
        self.logger.geral(self.logger.SEP)
        self.logger.geral("ETAPA 2: LENDO E PRE-PROCESSANDO OS DADOS")
        self.logger.geral(self.logger.SEP)

        df_contratos     = pd.read_csv('/tmp/data/contratos.csv')
        df_inquilinos    = pd.read_csv('/tmp/data/inquilino.csv')
        df_proprietarios = pd.read_csv('/tmp/data/proprietário.csv')
        df_imoveis       = pd.read_csv('/tmp/data/imoveis.csv')

        df_contratos     = df_contratos.drop(df_contratos.columns[0], axis=1).iloc[4:]
        df_proprietarios = df_proprietarios.drop(df_proprietarios.columns[0], axis=1).iloc[4:]
        df_inquilinos    = df_inquilinos.drop(df_inquilinos.columns[0], axis=1).iloc[4:]
        df_imoveis       = df_imoveis.drop(df_imoveis.columns[0], axis=1).iloc[4:]

        df_proprietarios['emails'] = (
            df_proprietarios['emails'].str.replace(';', ',').str.replace(' ', '')
        )
        df_inquilinos['emails_inquilino'] = (
            df_inquilinos['emails_inquilino'].str.replace(';', ',').str.replace(' ', '')
        )

        df_imoveis = df_imoveis.map(lambda x: x.strip() if isinstance(x, str) else x)
        for campo in ['valor_do_aluguel', 'valor_condominio', 'valor_do_iptu', 'taxa_de_contrato']:
            df_imoveis[campo] = df_imoveis[campo].apply(_converter_para_float)

        for campo in self.CAMPOS_FLOAT_CONTRATO:
            df_contratos[campo] = df_contratos[campo].apply(_converter_para_float)

        df_contratos.fillna(self.FILLNA_CONTRATOS, inplace=True)

        self.logger.geral(f"Contratos carregados    : {len(df_contratos)}")
        self.logger.geral(f"Proprietarios carregados: {len(df_proprietarios)}")
        self.logger.geral(f"Inquilinos carregados   : {len(df_inquilinos)}")
        self.logger.geral(f"Imoveis carregados      : {len(df_imoveis)}")

        return df_contratos, df_proprietarios, df_inquilinos, df_imoveis
