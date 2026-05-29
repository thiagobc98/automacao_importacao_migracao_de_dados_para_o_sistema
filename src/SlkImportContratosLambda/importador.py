import os
import pandas as pd
from typing import Any, Callable
from logs import Logger
from downloader_planilha import DownloaderPlanilha
from validacoes import Validacoes
from repositorio import Repositorio
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread

FOLDER_ID_SUCESSO = '16Sa_edymi_6U3YezbT4fSmwC7t4MghQb'
FOLDER_ID_ERRO    = '1ChngdRcWK0UOnGtprJtL6jthmekjaNr2'



def _upload_arquivo_drive(service: Any, caminho: str, folder_id: str) -> str:
    """Faz upload de um arquivo local para uma pasta do Google Drive. Retorna o file ID."""
    nome = os.path.basename(caminho)
    media = MediaFileUpload(caminho, resumable=False)

    file = service.files().create(
        body={
            'name': nome,
            'parents': [folder_id]
        },
        media_body=media,
        fields='id',
        supportsAllDrives=True  # 🔥 ESSENCIAL
    ).execute()

    print(f"-> Upload concluído: {nome} → pasta {folder_id} (ID: {file['id']})")
    return file['id']


def _enviar_logs_para_drive(credentials: Any, logger: Logger, tem_erros: bool) -> None:
    """Envia os arquivos de log para as pastas corretas no Google Drive."""
    print("-> Enviando arquivos para o Google Drive...")
    service = build('drive', 'v3', credentials=credentials)

    # Arquivos de sucesso → pasta de sucesso
    for caminho in [logger.geral_file, logger.sucesso_file]:
        if os.path.exists(caminho):
            _upload_arquivo_drive(service, caminho, FOLDER_ID_SUCESSO)

    # Arquivos de erro → pasta de erro
    if tem_erros:
        if os.path.exists(logger.erros_file):
            _upload_arquivo_drive(service, logger.erros_file, FOLDER_ID_ERRO)
        for csv_nome in ['contrato.csv', 'proprietario.csv', 'inquilino.csv', 'imovel.csv']:
            caminho_csv = f'/tmp/erros/{csv_nome}'
            if os.path.exists(caminho_csv):
                _upload_arquivo_drive(service, caminho_csv, FOLDER_ID_ERRO)


def executar_importacao(code_sheets: str, gc: gspread.Client, credentials: Any, logger: Logger, notify_slack: Callable[[str], None] | None = None) -> None:

    def _notify(msg: str) -> None:
        if notify_slack:
            notify_slack(msg)

    # ------------------------------------------------------------------
    # ETAPA 1 - Download
    # ------------------------------------------------------------------
    downloader = DownloaderPlanilha(code_sheets, logger, gc)
    downloader.executar()

    # ------------------------------------------------------------------
    # 🔍 VALIDAÇÃO: Verificando se os arquivos foram baixados
    # ------------------------------------------------------------------
    import glob
    arquivos = glob.glob('/tmp/data/*')
    print("=" * 60)
    print("📂 ARQUIVOS BAIXADOS EM /tmp/data/:")
    for arq in arquivos:
        tamanho = os.path.getsize(arq)
        print(f"   ✅ {arq} ({tamanho} bytes)")
    if not arquivos:
        print("   ❌ NENHUM ARQUIVO ENCONTRADO!")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 📤 Upload dos CSVs baixados para o Google Drive
    # ------------------------------------------------------------------
    FOLDER_ID_VALIDACAO = '1dcwUz_rrxQAzZ5Z0udQRaJFxG4ILROuM'
    print(f"-> Enviando arquivos para o Google Drive (pasta {FOLDER_ID_VALIDACAO})...")
    service = build('drive', 'v3', credentials=credentials)
    for arq in arquivos:
        _upload_arquivo_drive(service, arq, FOLDER_ID_VALIDACAO)

    # ------------------------------------------------------------------
    # ETAPA 2 - Leitura e pre-processamento
    # ------------------------------------------------------------------
    df_contratos, df_proprietarios, df_inquilinos, df_imoveis = downloader.carregar_dados()
    _notify(" -> *Etapa 1/3 concluída:* Planilha baixada e lida com sucesso")
    print("->ETAPA 2: Leitura e pre-processamento concluida com sucesso!")

    # ------------------------------------------------------------------
    # ETAPA 3 - Agrupamento por codigo_contrato
    # ------------------------------------------------------------------
    logger.geral(logger.SEP)
    logger.geral("-> ETAPA 3: AGRUPANDO DADOS POR CODIGO_CONTRATO")
    logger.geral(logger.SEP)

    contratos_group     = df_contratos.groupby('codigo_contrato')
    proprietarios_group = df_proprietarios.groupby('codigo_contrato')
    inquilinos_group    = df_inquilinos.groupby('codigo_contrato')
    imoveis_group       = df_imoveis.groupby('codigo_contrato')

    contratos_processados = []
    for codigo in contratos_group.groups.keys():
        contratos_processados.append({
            "codigo_contrato": codigo,
            "contrato":        contratos_group.get_group(codigo).iloc[0].to_dict(),
            "proprietarios":   proprietarios_group.get_group(codigo).to_dict('records') if codigo in proprietarios_group.groups else [],
            "inquilinos":      inquilinos_group.get_group(codigo).to_dict('records')    if codigo in inquilinos_group.groups    else [],
            "imoveis":         imoveis_group.get_group(codigo).to_dict('records')       if codigo in imoveis_group.groups       else [],
        })

    df_final = pd.DataFrame(contratos_processados)
    logger.geral(f"Total de contratos agrupados: {len(df_final)}")

    repositorio = Repositorio(logger)
    codigos_existentes = repositorio.obter_contratos_existentes()
    logger.geral(f"Contratos ja existentes no banco: {len(codigos_existentes)}")
    _notify(f"-> *Etapa 2/3 concluída:* {len(df_final)} contrato(s) agrupado(s) — iniciando validação e inserção no banco...")
    print("->ETAPA 3: Agrupamento por codigo_contrato concluida com sucesso!")

    # ------------------------------------------------------------------
    # ETAPA 4 - Validacao e insercao contrato por contrato
    # ------------------------------------------------------------------
    logger.geral(logger.SEP)
    logger.geral("-> ETAPA 4: VALIDANDO E INSERINDO CONTRATO POR CONTRATO")
    logger.geral(logger.SEP)

    contratos_ok       = []
    contratos_com_erro = []
    contratos_pulados  = []

    rows_erro_contrato     = []
    rows_erro_proprietario = []
    rows_erro_inquilino    = []
    rows_erro_imovel       = []

    for pos, (_, linha) in enumerate(df_final.iterrows(), 1):
        codigo = linha["codigo_contrato"]

        logger.geral(logger.SEP)
        logger.geral(f"[{pos}/{len(df_final)}] PROCESSANDO CONTRATO: {codigo}")

        if str(codigo) in codigos_existentes:
            logger.geral(f"  AVISO: Contrato '{codigo}' ja existe no banco. Pulando.", "AVISO")
            contratos_pulados.append(codigo)
            continue

        erros = Validacoes.checar_erros_contrato(linha)

        if erros:
            logger.escrever_erros_contrato(codigo, erros)
            logger.geral(f"  RESULTADO: REJEITADO ({len(erros)} erro(s))", "ERRO")
            contratos_com_erro.append(codigo)

            rows_erro_contrato.append(contratos_group.get_group(codigo))
            if codigo in proprietarios_group.groups:
                rows_erro_proprietario.append(proprietarios_group.get_group(codigo))
            if codigo in inquilinos_group.groups:
                rows_erro_inquilino.append(inquilinos_group.get_group(codigo))
            if codigo in imoveis_group.groups:
                rows_erro_imovel.append(imoveis_group.get_group(codigo))

        else:
            logger.direto_sucesso(logger.SEP)
            logger.sucesso(f"CONTRATO OK: {codigo}", "OK")
            logger.direto_sucesso(logger.SEP_MENOR)

            logger.geral("  VALIDACAO: OK! Iniciando insercao no banco de dados...")

            sucesso = repositorio.inserir_contrato_completo(linha)

            if sucesso:
                logger.sucesso(f"  CONTRATO {codigo}: INSERIDO COM SUCESSO!", "OK")
                logger.direto_sucesso(logger.SEP)
                logger.geral("  RESULTADO: INSERIDO COM SUCESSO!", "OK")
                contratos_ok.append(codigo)
            else:
                logger.sucesso(f"  CONTRATO {codigo}: FALHOU NA INSERCAO NO BANCO!", "ERRO")
                logger.direto_sucesso(logger.SEP)
                logger.geral("  RESULTADO: FALHA NA INSERCAO NO BANCO!", "ERRO")
                contratos_com_erro.append(codigo)

    # ------------------------------------------------------------------
    # RESUMO FINAL (log)
    # ------------------------------------------------------------------
    import datetime
    end_time = datetime.datetime.now()
    tempo_total = end_time - logger.start_time

    logger.geral(logger.SEP)
    logger.geral("RESUMO FINAL")
    logger.geral(logger.SEP_MENOR)
    logger.geral(f"  Total de contratos na planilha   : {len(df_final)}")
    logger.geral(f"  Contratos ja existentes (pulados): {len(contratos_pulados)}")
    logger.geral(f"  Contratos INSERIDOS com sucesso  : {len(contratos_ok)}")
    logger.geral(f"  Contratos REJEITADOS (com erro)  : {len(contratos_com_erro)}")
    logger.geral(logger.SEP_MENOR)

    if contratos_ok:
        logger.geral("  INSERIDOS:")
        for cod in contratos_ok:
            logger.geral(f"    [OK]   {cod}", "OK")

    if contratos_com_erro:
        logger.geral("  REJEITADOS (corrija e reimporte):")
        for cod in contratos_com_erro:
            logger.geral(f"    [ERRO] {cod}", "ERRO")

    logger.geral(logger.SEP_MENOR)
    logger.geral(f"  Tempo total de execucao: {tempo_total}")
    logger.geral(logger.SEP)

    # ------------------------------------------------------------------
    # 📤 Upload dos logs para o Google Drive — coleta links
    # ------------------------------------------------------------------
    FOLDER_LOG_GERAL   = '1uUcZgVNRegsfsOJReQgbwysD4-4deY-O'
    FOLDER_LOG_ERROS   = '1Rzo_IPH0mZY2NdkrA4ufqBhLdar2Iy6F'
    FOLDER_LOG_SUCESSO = '1ZolONmhxRhDWXZcyL73nE9yQUH1MHwl0'

    logger.escrever_resumo_final(
        total=len(df_final),
        inseridos=len(contratos_ok),
        pulados=len(contratos_pulados),
        erros=len(contratos_com_erro),
        tempo_total=tempo_total
    )

    _notify("-> *Etapa 3/3:* Enviando logs para o Google Drive...")
    print("-> Enviando logs para o Google Drive...")
    service = build('drive', 'v3', credentials=credentials)
    links_drive = {}

    if os.path.exists(logger.geral_file):
        fid = _upload_arquivo_drive(service, logger.geral_file, FOLDER_LOG_GERAL)
        links_drive['geral'] = f"https://drive.google.com/file/d/{fid}/view"
    if os.path.exists(logger.erros_file):
        fid = _upload_arquivo_drive(service, logger.erros_file, FOLDER_LOG_ERROS)
        links_drive['erros'] = f"https://drive.google.com/file/d/{fid}/view"
    if os.path.exists(logger.sucesso_file):
        fid = _upload_arquivo_drive(service, logger.sucesso_file, FOLDER_LOG_SUCESSO)
        links_drive['sucesso'] = f"https://drive.google.com/file/d/{fid}/view"

    print("✅ Logs enviados com sucesso!")

    # ------------------------------------------------------------------
    # 📢 Mensagem final no Slack
    # ------------------------------------------------------------------
    tem_erros   = len(contratos_com_erro) > 0
    tudo_ok     = not tem_erros and len(contratos_ok) > 0
    tudo_pulado = not tem_erros and len(contratos_ok) == 0

    if tudo_ok:
        cabecalho = "✅ *Importação concluída com sucesso!* ✅"
    elif tudo_pulado:
        cabecalho = "ℹ️ *Importação concluída — todos os contratos já existiam no banco.* ℹ️"
    elif tem_erros and len(contratos_ok) > 0:
        cabecalho = (
            f"⚠️ *Importação concluída com exceções*\n"
            f"> {len(contratos_com_erro)} contrato(s) foram rejeitados. "
            f"Verifique o log de erros e corrija antes de reimportar."
        )
    else:
        cabecalho = (
            f"❌ *Importação concluída — nenhum contrato foi inserido* ❌\n"
            f"> Todos os {len(contratos_com_erro)} contrato(s) foram rejeitados por erro. "
            f"Verifique o log de erros."
        )

    linhas_slack = [cabecalho, ""]
    linhas_slack.append("-> *Resumo:*")
    linhas_slack.append(f"• Total na planilha: {len(df_final)}")
    if len(contratos_ok) > 0:
        linhas_slack.append(f"•  Inseridos com sucesso: {len(contratos_ok)}")
    if len(contratos_pulados) > 0:
        linhas_slack.append(f"• Já existentes (pulados): {len(contratos_pulados)}")
    if len(contratos_com_erro) > 0:
        linhas_slack.append(f"•  Rejeitados (com erro): {len(contratos_com_erro)}")
        linhas_slack.append(f">  _Contratos: {', '.join(str(c) for c in contratos_com_erro)}_")

    if links_drive:
        linhas_slack.append("")
        linhas_slack.append("📎 *Logs no Google Drive:*")
        if 'geral' in links_drive:
            linhas_slack.append(f"• <{links_drive['geral']}|🔒 Log Geral (Exclusivo para o time de TI)>")
        if 'sucesso' in links_drive:
            linhas_slack.append(f"• <{links_drive['sucesso']}|✅ Log de Sucesso>")
        if 'erros' in links_drive:
            linhas_slack.append(f"• <{links_drive['erros']}|❌ Log de Erros>")

    linhas_slack.append("")
    linhas_slack.append(f"⏱️ Tempo total: {str(tempo_total).split('.')[0]}")

    _notify("\n".join(linhas_slack))