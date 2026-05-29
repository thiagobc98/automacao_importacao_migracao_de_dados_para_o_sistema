# Guia de Uso: Importação de Contratos via Slack

Este guia explica como utilizar o comando `/importar_contratos` no Slack e como preencher corretamente a planilha modelo para garantir que os dados sejam importados sem erros.

### Passo 1: Preparar a Planilha de Importação

> ⚠️ **MUITO IMPORTANTE:** Sempre utilize a nossa Planilha Modelo para montar as listas de importação.
> 🔗 **[Acessar Planilha Modelo de Importação]**


### Como Rodar Localmente (sem deploy)

Para testar a importação sem precisar fazer deploy na AWS:

**Pré-requisitos:**
- Python 3.11 instalado
- MySQL rodando localmente com o banco configurado
- Arquivo JSON de credenciais da service account do Google

**1. Instale as dependências:**
```bash
pip install -r src/SlkImportContratosLambda/requirements.txt
```

**2. Configure as variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp .env.local.exemple .env.local
```

Edite o `.env.local` preenchendo os valores reais:
```
DB_HOST=localhost
DB_NAME=nome_do_seu_banco
DB_USER=root
DB_PASSWORD=sua_senha_aqui

# Caminho para o JSON de credenciais da service account do Google
LOCAL_GOOGLE_CREDENTIALS_PATH=./google_credentials.json

GOOGLE_SECRET_ARN=local-not-used
```

**3. Execute:**
```bash
python run_local.py [ID da planilha]
```

Exemplo:
```bash
python run_local.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms
```

O script carrega o `.env.local`, monta um evento SQS simulado e chama o `lambda_handler` diretamente — sem precisar de AWS, SQS ou Slack.

---

### Passo 2: Rodando a Importação no Slack

1. Após validar, preencher e salvar a planilha gerada através do modelo na `pasta export/projetos`  dentro o `drive compartilhado Tec UP - Dados`;
2. Acesse o **Slack** e vá até o canal `#chame-dados` que é o canal designado para o bot;
3. Digite o seguinte _Slash Command_:
   ```text
   /importar_contratos [ID da planilha da importação de contratos]
   ```
4. Pressione `Enter`. O Bot começará a processar a importação dos contratos e enviará uma mensagem no canal `#chame-dados` com o resultado da importação.   

> ⚠️ **MUITO IMPORTANTE:** Para pegar o ID da planilha, é só copiar o código que aparece na URL da planilha entre `/d/` e `/edit` por exemplo: o link é `https://docs.google.com/spreadsheets/d/1X_6dSNND2ViGxdndN7kSQoirG5UcpQq_aPStwyku67Y/edit?gid=752282860#gid=752282860`, então o ID é `1X_6dSNND2ViGxdndN7kSQoirG5UcpQq_aPStwyku67Y`.

A planilha está dividida em 4 abas, e cada aba possui regras de formatação e colunas de preenchimento obrigatório. Siga a estrutura das tabelas abaixo para preencher os dados:

---

### 1. Aba: Proprietários

| Coluna | RESTRIÇÕES | Orientação de Preenchimento |
| :--- | :--- | :--- |
| **codigo_contrato**| OBRIGATÓRIO | Código do contrato UP *(Atenção: não deixe espaços antes nem depois do código)* |
| **cpf** | OBRIGATÓRIO | CPF com números e pontuação (ex: `123.456.789-00`) |
| **nome** | OBRIGATÓRIO | - |
| **telefone** | OBRIGATÓRIO | Telefone com DDD e pontuação (ex: `(11) 98765-4321`) |
| **emails** | OBRIGATÓRIO | E-mails separados por `;` (ponto e vírgula) (ex: xxxx@gmail.com; yyy@hotmail.com) |
| **cep_endereco** |  | CEP com pontuação (ex: `12345-678`) |
| **rua_endereco** | | - |
| **numero_endereco**| | - |
| **bairro_endereco** | | - |
| **cidade_endereco** |  | - |
| **estado_endereco** | | Apenas 2 letras (ex: `SP`, `RJ`) |
| **complemento_endereco**| | - |
| **percentual_repasse**| OBRIGATÓRIO |O total tem que ser 100% *(Valor em decimal separado por **,**, ex: `50,00`)* |
| **nome_banco** | OBRIGATÓRIO | - |
| **numero_banco** | OBRIGATÓRIO | - |
| **numero_conta** | OBRIGATÓRIO | - |
| **agencia_conta** | OBRIGATÓRIO | - |
| **tipo_conta** | OBRIGATÓRIO | `1` = Corrente <br> `2` = Poupança |
| **nome_titular_conta**| OBRIGATÓRIO | - |
| **cpf_cnpj_da_conta** | OBRIGATÓRIO | CPF ou CNPJ com números e pontuação |
| **rg** |  | RG com números e pontuação |
| **naciolidade** |  | - |
| **estado_civil** |  | - |
| **regime_casamento**|  | - |
| **profissao** |  | - |
| **inscricao_estadual**|  | - |
| **razao_social_empresa**|  | - |
| **nome_representante_empresa** |  | - |
| **cpf_representante_empresa** |  | - |
| **vinculo_empresa** |  | - |

---

### 2. Aba: Inquilinos

| Coluna | RESTRIÇÕES | Orientação de Preenchimento |
| :--- | :--- | :--- |
| **codigo_contrato** | OBRIGATÓRIO | Código do contrato UP *(Atenção: não deixe espaços antes nem depois do código)* |
| **inquilino_principal** | OBRIGATÓRIO | `V` = Inquilino principal <br> `F` = Inquilino solidário <br> `A` = Fiador |
| **documento_inquilino** | OBRIGATÓRIO | CPF ou CNPJ com números e pontuação |
| **nome_inquilino** | OBRIGATÓRIO | - |
| **telefone_inquilino** | OBRIGATÓRIO | Telefone com DDD e pontuação |
| **emails_inquilino** | OBRIGATÓRIO | E-mails separados por `;` (ponto e vírgula) (ex: xxxx@gmail.com; yyy@hotmail.com) |
| **profissao_inquilino** |  | - |
| **dtnascimento_inquilino**|  | Padrão  `DD/MM/YYYY` (ex: `31/12/1990`) |
| **cep_end** | OBRIGATÓRIO | CEP com pontuação |
| **rua_end** | OBRIGATÓRIO | - |
| **numero_end** | OBRIGATÓRIO | - |
| **bairro_end** | OBRIGATÓRIO | - |
| **cidade_end** | OBRIGATÓRIO | - |
| **estado_end** | OBRIGATÓRIO | - |
| **complemento_end** |  | - |
| **genero_inquilino** |  | `M` ou `F` |
| **rg_inquilino** |  | RG com números e pontuação |
| **nacionalidade_inquilino**|  | - |
| **estado_civil_inquilino** |  | `1` = Solteiro <br> `2` = Casado <br> `3` = Divorciado <br> `4` = Viúvo <br> `5` = Separado judicialmente <br> `6` = União estável |
| **regime_cassamento_inquilino**|  | - |

---

### 3. Aba: Imóveis

| Coluna | RESTRIÇÕES | Orientação de Preenchimento |
| :--- | :--- | :--- |
| **codigo_contrato** | OBRIGATÓRIO | Código do contrato UP *(Atenção: não deixe espaços antes nem depois do código)* |
| **documento_proprietario** | OBRIGATÓRIO | CPF com números e pontuação |
| **fk_id_parceiro_parceiros** | OBRIGATÓRIO | Apenas número inteiro |
| **documento_parceiro**| OBRIGATÓRIO | CPF ou CNPJ com números e pontuação *(Captador)* |
| **nome_parceiro** |  | - |
| **cep_endereco** | OBRIGATÓRIO | CEP com pontuação |
| **rua_endereco** | OBRIGATÓRIO | - |
| **numero_endereco** | OBRIGATÓRIO | - |
| **bairro_endereco** | OBRIGATÓRIO | - |
| **cidade_endereco** | OBRIGATÓRIO | - |
| **estado_endereco** | OBRIGATÓRIO | Apenas 2 letras (ex: `SP`) |
| **complemento_endereco** |  | - |
| **valor_do_aluguel**| OBRIGATÓRIO | - |
| **taxa_de_contrato**| OBRIGATÓRIO | Valor em % *(Valor em decimal separado por **,**, ex: `10,00`)* |
| **valor_condominio**| OBRIGATÓRIO | - |
| **valor_do_iptu** | OBRIGATÓRIO | - |
| **dados_do_condominio** |  | Informações separadas por `;` (ponto e vírgula) |
| **local_das_chaves**|  | - |
| **observacoes_contratuais**|  | - |
| **nome_condominio** |  | - |

---

### 4. Aba: Contratos

| Coluna | RESTRIÇÕES | Orientação de Preenchimento |
| :--- | :--- | :--- |
| **codigo_contrato** | OBRIGATÓRIO | Código do contrato UP *(Atenção: não deixe espaços antes nem depois do código)* |
| **fk_id_parceiro_parceiros** | OBRIGATÓRIO | Apenas número inteiro |
| **documento_parceiro** | OBRIGATÓRIO | Documento do parceiro efetivador com todas as PONTUAÇÕES *(Atenção: sem espaços antes nem depois do código)* |
| **data_ocupacao_contrato** | OBRIGATÓRIO | Padrão  `DD/MM/YYYY` |
| **dia_vencimento_contrato** | OBRIGATÓRIO | Apenas o número do dia (De `1` até `31`) |
| **primeiro_aluguel_prop_contrato** | OBRIGATÓRIO | **PRO RATA** <br> `V` = Postecipado - Separado <br> `F` = Postecipado - Junto com 2° vencimento <br> `AD` = Antecipado - Acerto de dias antecipado <br> `AL` = Antecipado - Acerto de dias com aluguel antecipado |
| **finalidade_contrato** |  | `1` = Residencial <br> `2` = Não Residencial |
| **date_inicio_contrato** |  | Padrão  `DD/MM/YYYY` |
| **meses_duracao_contrato** | OBRIGATÓRIO | Número inteiro |
| **date_finalizacao_contrato** |  | Padrão  `DD/MM/YYYY` |
| **data_ultimo_reajuste_contrato** | OBRIGATÓRIO | Padrão  `DD/MM/YYYY` |
| **data_proximo_reajuste** |  | Padrão  `DD/MM/YYYY` |
| **fk_id_indice_indices_reajuste** | OBRIGATÓRIO  | `1` = IGPM <br> `2` = INPC <br> `3` = IPCA <br> `4` = IVAR <br> `5` = MAIOR <br> `6` = IGP-DI (FGV) <br> `7` = MENOR |
| **taxa_admin_contrato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **taxa_admin_minima_contrato** | OBRIGATÓRIO | Valor em R$ *(Valor em decimal separado por `,`)* |
| **taxa_admin_parc_up_contrato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **valor_aluguel_contrato** | OBRIGATÓRIO | Valor em R$ *(Valor em decimal separado por `,`)* |
| **taxa_contrato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **juros_atraso_ao_dia_contrato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **multa_atraso_contato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **credito_multa_atraso_contrato** | OBRIGATÓRIO | `1` = Proprietário <br> `3` = Parceiro Captador <br> `5` = UP Estate (Padrão) |
| **split_multa_atraso_contrato** | OBRIGATÓRIO | Valor em % *(Valor decimal com `,`)* que será enviado para o split. Se `0`, considera-se que não tem divisão da multa. |
| **credito_split_multa_atraso_contrato** |  | `1` = Proprietário <br> `3` = Parceiro Captador (Padrão) <br> `5` = UP Estate |
| **desconto_pontualidade_pagamento** | OBRIGATÓRIO | Valor em % *(Valor decimal com `,`)* a ser concedido de desconto sobre o aluguel. Se `0,00` considera-se sem desconto. |
| **taxa_boleto_contrato** | OBRIGATÓRIO | Valor em R$ *(Valor em decimal separado por `,`)* |
| **debito_taxa_boleto** | OBRIGATÓRIO | `2` = Inquilino (Padrão) <br> `3` = Parceiro Captador |
| **credito_taxa_boleto** |  | `5` = UP Estate (Padrão) <br> `3` = Parceiro Captador |
| **taxa_ted_contrato** | OBRIGATÓRIO | Valor em R$ *(Valor em decimal separado por `,`)* |
| **debito_taxa_ted_doc_pix** | OBRIGATÓRIO | `1` = Proprietário (Padrão) <br> `3` = Parceiro Captador |
| **credito_taxa_ted_doc_pix** | OBRIGATÓRIO | `5` = UP Estate (Padrão) <br> `3` = Parceiro Captador |
| **cobrar_ted_repasse_contrato** | OBRIGATÓRIO | `V` = Sim <br> `F` = Não |
| **taxa_contrato_parc_up** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **fk_garantia_locaticia** | OBRIGATÓRIO | `1` = Seguro Fiança <br> `2` = Seguro Proteção <br> `3` = Título de Capitalização <br> `4` = Fiador <br> `5` = Caução <br> `6` = Fiança Onerosa <br> `7` = A definir <br> `8` = Sem Garantia <br> `9` = Garantia UP <br> `10` = Carta Fiança |
| **fk_id_seguradora_seguradoras** | OBRIGATÓRIO | `1` = Pottencial <br> `2` = Porto Seguro <br> `3` = Tokio Marine <br> `4` = Icatu <br> `5` = CredPago <br> `6` = Avalyst <br> `7` = Sem Seguro <br> `8` = Outros <br> `9` = Too <br> `10` = QuintoCred (Velo) <br> `11` = Sobral Crédito Seguro <br> `12` = Eu Acerto <br> `13` = Mapfre <br> `14` = Garantti <br> `15` = Credaluga <br> `16` = Avaliza <br> `17` = Onda Segura <br> `18` = Ucred <br> `19` = Creditas <br> `20` = Guarda-chuva |
| **observacoes_contrato** |  | Referência dos boletos, outras fianças onerosas e demais observações |
| **apolice_contrato** |  | Caso tenha, colocar o número. Se não, deixar em branco |
| **vencimento_seguro_fianca_contrato** |  | Padrão  `DD/MM/YYYY` |
| **cobrar_despesa_bancaria** | OBRIGATÓRIO | `0` = Não <br> `1` = Sim |
| **despesa_bancaria** |  | Valor em decimal separado por `,` |
| **taxa_garantia_contrato** | OBRIGATÓRIO | Valor em % *(Valor em decimal separado por `,`)* |
| **fk_tipo_garantia_taxa** | OBRIGATÓRIO | `1` = Taxa de Serviço <br> `2` = Prêmio Seguro <br> `3` = Taxa Fiança Digital <br> `4` = Não se aplica |
| **taxa_garantia_contrato_vl** |  | Valor em decimal separado por `,`. *(Se preenchido, irá considerar este valor e ignorar a % de taxa_garantia_contrato)* |
| **transferir_repasse_contrato** | OBRIGATÓRIO | `V` = Sim <br> `F` = Não |
| **pontualizado** | OBRIGATÓRIO | `0` = Não <br> `1` = Sim <br> `2` = Tombamento |
| **fk_id_produtos_up** | OBRIGATÓRIO | `1` = Light <br> `2` = Smart <br> `3` = Full <br> `4` = Bank |
| **fk_cobertura_contrato** | OBRIGATÓRIO | `1` = Growth <br> `2` = Safe <br> `3` = Outros |
| **codigo_legado** | OBRIGATÓRIO |  - |
| **gerar_notas_fiscais** | OBRIGATÓRIO | `0` = Não <br> `1` = Sim |
| **fk_tb_descricao_referencia_aluguel**|  | `1` = Até o vencimento <br> `2` = Mês cheio |
| **modelo_pagamento_iptu** |  | `1` = Anual <br> `2` = Mensal (parcelas prefeitura) <br> `3` = Mensal (anual dividido em 12x) <br> `4` = Isento |
| **finalidade_locacao_contrato** |  | `1` = Moradia de Sócio <br> `2` = Moradia de Funcionário <br> `3` = Atividade Comercial <br> `0` = Outro |
| **atividade_contrato** | | Detalhes para atividade comercial (ex: *Consultório de enfermagem*) |
| **dia_repasse_contrato** | | Apenas o número do dia (De `1` até `31`) |
| **parcela_imob_multa_rescisoria** | | Valor em % da multa recisória para a imobiliária |
| **periodo_liberacao_sem_multa** | | Período em quantidade de meses para o inquilino rescindir o contrato sem multa |

---



