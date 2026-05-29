import datetime
import os
import re
from itertools import groupby


class Logger:
    SEP       = "=" * 70
    SEP_MENOR = "-" * 50

    def __init__(self, code_sheets: str) -> None:
        self.start_time: datetime.datetime = datetime.datetime.now()
        ts = self.start_time.strftime('%d-%m-%Y_%Hh%Mm%Ss')

        os.makedirs('/tmp/logs', exist_ok=True)

        self.geral_file:   str = f"/tmp/logs/geral_{ts}.txt"
        self.erros_file:   str = f"/tmp/logs/erros_{ts}.md"
        self.sucesso_file: str = f"/tmp/logs/sucesso_{ts}.md"

        self._inicializar_arquivos(code_sheets)

    def _inicializar_arquivos(self, code_sheets: str) -> None:
        ts       = self.start_time.strftime('%d/%m/%Y %H:%M:%S')
        data_br  = ts
        cabecalho = (
            f"[{ts}] [INFO ] {self.SEP}\n"
            f"[{ts}] [INFO ] IMPORTACAO DE CONTRATOS - v2\n"
            f"[{ts}] [INFO ] Planilha: {code_sheets}\n"
            f"[{ts}] [INFO ] {self.SEP}\n"
        )
        with open(self.geral_file, 'w', encoding='utf-8') as f:
            f.write(cabecalho)
        with open(self.erros_file, 'w', encoding='utf-8') as f:
            f.write(f"# \U0001f4cb RELATÓRIO DE CORREÇÕES DA PLANILHA\n\n")
            f.write(f"**Data:** {data_br}  \n")
            f.write(f"**Planilha lida:** `{code_sheets}`\n\n")
            f.write(f"---\n\n")
        with open(self.sucesso_file, 'w', encoding='utf-8') as f:
            f.write(f"# \u2705 RELATÓRIO DE SUCESSO\n\n")
            f.write(f"**Data:** {data_br}  \n")
            f.write(f"**Planilha lida:** `{code_sheets}`\n\n")
            f.write(f"---\n\n")

    def _escreve_log(self, arquivo: str, texto: str, level: str = "INFO") -> None:
        ts = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        linha = f"[{ts}] [{level:<5}] {texto}"
        print(linha)
        with open(arquivo, 'a', encoding='utf-8') as f:
            f.write(linha + '\n')

    def _escreve_direto(self, arquivo: str, texto: str) -> None:
        with open(arquivo, 'a', encoding='utf-8') as f:
            f.write(texto + '\n')

    def geral(self, texto: str, level: str = "INFO") -> None:
        """Escreve no log geral."""
        self._escreve_log(self.geral_file, texto, level)

    def erro(self, texto: str) -> None:
        """Escreve no log de erros e no geral."""
        self._escreve_log(self.erros_file, texto, "ERRO")
        self._escreve_log(self.geral_file,  texto, "ERRO")

    def ok(self, texto: str) -> None:
        """Escreve no log de sucesso e no geral."""
        self._escreve_log(self.sucesso_file, texto, "OK")
        self._escreve_log(self.geral_file,   texto, "OK")

    def sucesso(self, texto: str, level: str = "OK") -> None:
        """Escreve apenas no log de sucesso (sem duplicar no geral)."""
        self._escreve_log(self.sucesso_file, texto, level)

    def direto_sucesso(self, texto: str) -> None:
        """Escreve texto puro no log de sucesso (sem timestamp/level)."""
        self._escreve_direto(self.sucesso_file, texto)

    # ------------------------------------------------------------------
    # Log de erros em formato Markdown
    # ------------------------------------------------------------------

    def _parse_erro(self, msg: str) -> tuple[str, str, str]:
        """
        Parseia uma mensagem de erro no formato:
          [PREFIX] Descricao do erro\n>> O que fazer: instrucao
        Retorna (prefix_raw, erro_desc, fix_text).
        """
        msg = msg.strip()
        m = re.match(r'^\[(.+?)\]\s*(.*)', msg, re.DOTALL)
        if not m:
            return ('', msg, '')
        prefix_raw = m.group(1).strip()
        linhas: list[str] = [l.strip().lstrip('>').strip() for l in m.group(2).split('\n') if l.strip()]
        erro_desc   = linhas[0] if linhas else ''
        o_que_isso  = ''
        o_que_fazer = ''
        for i, linha in enumerate(linhas):
            if i == 0:
                continue
            if linha.startswith('O que e isso:'):
                o_que_isso = linha[len('O que e isso:'):].strip()
            elif linha.startswith('O que fazer:'):
                o_que_fazer = linha[len('O que fazer:'):].strip()
        return (prefix_raw, erro_desc, o_que_fazer or o_que_isso)

    def _prefix_para_titulo(self, prefix_raw: str) -> str:
        """Converte o prefixo bruto em título Markdown com emoji."""
        if prefix_raw == 'CONTRATO':
            return '\U0001f4c4 Contrato Geral'
        partes = {
            p.split(':', 1)[0].strip(): p.split(':', 1)[1].strip()
            for p in prefix_raw.split('|') if ':' in p
        }
        if 'PROPRIETARIO' in prefix_raw:
            nome = partes.get('Nome', 'Proprietario')
            return f"\U0001f464 Pessoa: {nome} (Proprietário)"
        if 'INQUILINO' in prefix_raw:
            nome = partes.get('Nome', 'Inquilino')
            return f"\U0001f464 Pessoa: {nome} (Inquilino)"
        if 'IMOVEL' in prefix_raw:
            cep = partes.get('CEP', '?')
            return f"\U0001f3e0 Imóvel: CEP {cep}"
        return f"\U0001f4cb {prefix_raw}"

    def escrever_erros_contrato(self, codigo: str, erros: list[str]) -> None:
        """
        Escreve o bloco de erros de um contrato no log de erros (Markdown).
        Agrupa os erros por entidade e formata com emojis e bullet points.
        """
        f = self.erros_file
        self._escreve_direto(f, f"## \U0001f6a8 CONTRATO: `{codigo}`")
        self._escreve_direto(f, "")
        parsed = [self._parse_erro(msg) for msg in erros]
        for prefix_raw, grupo in groupby(parsed, key=lambda x: x[0]):
            titulo = self._prefix_para_titulo(prefix_raw)
            self._escreve_direto(f, f"### {titulo}")
            for _, erro_desc, fix_text in grupo:
                self._escreve_direto(f, f"* \u274c **Erro:** {erro_desc}")
                if fix_text:
                    self._escreve_direto(f, f"* \U0001f449 **Como arrumar:** {fix_text}")
            self._escreve_direto(f, "")
        self._escreve_direto(f, "---")
        self._escreve_direto(f, "")

    def _escrever_bloco_resumo(self, arquivo: str, total: int, pulados: int, inseridos: int, rejeitados: int) -> None:
        """Escreve o bloco de resumo de totais em um arquivo (Markdown)."""
        self._escreve_direto(arquivo, "## \U0001f4ca RESUMO")
        self._escreve_direto(arquivo, "")
        self._escreve_direto(arquivo, "| Métrica | Qtd |")
        self._escreve_direto(arquivo, "|---|---|")
        self._escreve_direto(arquivo, f"| Total de contratos na planilha | {total} |")
        self._escreve_direto(arquivo, f"| Contratos já existentes (pulados) | {pulados} |")
        self._escreve_direto(arquivo, f"| Contratos INSERIDOS com sucesso | {inseridos} |")
        self._escreve_direto(arquivo, f"| Contratos REJEITADOS (com erro) | {rejeitados} |")
        self._escreve_direto(arquivo, "")
        self._escreve_direto(arquivo, "---")
        self._escreve_direto(arquivo, "")

    def escrever_resumo_erros(self, total: int, pulados: int, inseridos: int, rejeitados: int) -> None:
        """Escreve o resumo de totais nos três logs (erros, geral e sucesso)."""
        for arquivo in (self.erros_file, self.geral_file, self.sucesso_file):
            self._escrever_bloco_resumo(arquivo, total, pulados, inseridos, rejeitados)

    def escrever_resumo_final(self, total: int, inseridos: int, pulados: int, erros: int, tempo_total: datetime.timedelta) -> None:
        """Escreve o resumo final da importação no log de erros (Markdown)."""
        self.escrever_resumo_erros(total=total, pulados=pulados, inseridos=inseridos, rejeitados=erros)
        f = self.erros_file
        self._escreve_direto(f, f"**⏱️ Tempo total de execução:** `{str(tempo_total).split('.')[0]}`")
        self._escreve_direto(f, "")

    def escrever_rodape_erros(self) -> None:
        """Escreve o rodapé do log de erros."""
        self._escreve_direto(
            self.erros_file,
            "**Dica de sucesso:** Após corrigir os problemas indicados acima na sua planilha, "
            "rode o importador novamente! \u2728"
        )
