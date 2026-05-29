import os
import csv
import gspread

def executar(code_sheets: str, gc: gspread.Client) -> None:
    """
    Baixa as abas da planilha do Google Sheets e salva em arquivos CSV no diretório /tmp/data/
    """
    print(f"Baixando planilha {code_sheets}...")
    spreadsheet = gc.open_by_key(code_sheets)
    
    abas = [
        ("contratos", "contratos.csv"),
        ("inquilino", "inquilino.csv"),
        ("proprietário", "proprietário.csv"),
        ("imoveis", "imoveis.csv")
    ]
    
    os.makedirs('/tmp/data', exist_ok=True)
    
    for nome_aba, arquivo in abas:
        print(f"Baixando aba {nome_aba}...")
        try:
            ws = spreadsheet.worksheet(nome_aba)
            data = ws.get_all_values()
            
            with open(f"/tmp/data/{arquivo}", "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(data)
            print(f"Aba {nome_aba} salva em /tmp/data/{arquivo}")
        except Exception as e:
            print(f"Erro ao baixar a aba {nome_aba}: {e}")
            raise e
