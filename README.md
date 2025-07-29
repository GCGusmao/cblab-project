# Desafio de Engenharia de Dados - Coco Bambu

Este repositório contém a solução completa para o desafio técnico do processo seletivo de Engenharia de Dados, proposto pelo CBLab.

O projeto aborda os dois principais desafios propostos:

1.  **Modelagem de Dados:** A transcrição de uma estrutura JSON (de um ERP) para um schema de banco de dados relacional robusto, incluindo a justificativa da abordagem.
2.  **Arquitetura de Dados:** O design de uma arquitetura para ingestão e armazenamento de dados de múltiplas APIs em um Data Lake, considerando performance, escalabilidade e a evolução do schema.

## 📜 Índice

  * [📂 Estrutura do Projeto](#estrutura-do-projeto)
  * [🚀 Quickstart: Executando o Projeto](#quickstart-executando-o-projeto)
  * [🛠️ Conectando ao Banco de Dados](#conectando-ao-banco-de-dados)
  * [📄 Solução Detalhada do Desafio](#solução-detalhada-do-desafio)

  * [Solução Detalhada do Desafio](#solução-detalhada-do-desafio)

## 📁 Estrutura do Projeto

O repositório está organizado da seguinte forma para garantir clareza e separação de responsabilidades:

```
.
├── data/
│   └── ERP.json
├── src/
│   ├── desafio_1/
│   │   ├── 1_1_descricao_esquema.md
│   │   ├── 1_2_schema.sql
│   │   ├── 1_3_modelagem_detalhada.md
│   │   └── 1_3_parser.py
│   └── desafio_2/
│       ├── 2_1_armazenamento_api.md
│       ├── 2_2_estrutura_data_lake.md
│       └── 2_3_mudanca_schema.md
├── .gitignore
├── docker-compose.yml
├── KANBAN.md
├── README.md
└── requirements.txt
```

## 🚀 Quickstart: Executando o Projeto

Para validar a solução do Desafio 1 na prática, o projeto inclui um ambiente Docker que provisiona um banco de dados PostgreSQL e um script Python que realiza o parsing do JSON e a inserção dos dados.

**⚠️ Atenção:** a estrutura possui credenciais e variáveis de ambiente escritas diretamente no código. Essa abordagem tem como objetivo facilitar o processo de execução e testes dessas soluções, mas **nunca deve ser utilizada em produção**. Sempre armazene informações sensíveis em arquivos de variáveis de ambiente, como '.env', e nunca publique essas soluções de forma pública.

### Pré-requisitos

  * [Docker](https://www.google.com/search?q=https://www.docker.com/get-started) instalado e em execução.
  * [Docker Compose](https://docs.docker.com/compose/install/) instalado.
  * Python 3.8+ instalado.

### Passo a Passo para Execução

1.  **Inicie o Ambiente Docker**
    Este comando irá iniciar um contêiner PostgreSQL em segundo plano e executar automaticamente o script `1_2_schema.sql` para criar toda a estrutura de tabelas.

    ```bash
    docker-compose up -d
    ```

2.  **Instale as Dependências Python**
    Crie um ambiente virtual (recomendado) e instale a biblioteca necessária.

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Execute o Script de Parser**
    Este script irá ler o arquivo `data/ERP.json`, conectar-se ao banco de dados no Docker e inserir os dados, validando a modelagem.

    ```bash
    python src/desafio_1/1_3_parser.py
    ```

    Se a execução for bem-sucedida, você verá uma mensagem de sucesso no final, confirmando que a modelagem foi validada.

## 🛠️ Conectando ao Banco de Dados

Após iniciar o ambiente Docker, você pode se conectar ao banco de dados para inspecionar as tabelas e os dados inseridos pelo parser.

**1. Conectar via linha de comando (psql):**

```bash
docker exec -it coco-bambu-postgres-db psql -U cblab_user -d coco_bambu_db
```

Dentro do psql, use o comando `\dt` para listar as tabelas.

**2. Conectar via Ferramenta Gráfica (DBeaver, pgAdmin, etc.):**

  * **Host:** `localhost`
  * **Porta:** `5435`
  * **Banco de Dados:** `coco_bambu_db`
  * **Usuário:** `cblab_user`
  * **Senha:** `a_senha_super_segura` (a senha definida no `docker-compose.yml`)

## 📄 Solução Detalhada do Desafio

As respostas detalhadas para cada item do desafio estão organizadas em arquivos Markdown dedicados dentro da pasta `src/`.

### Desafio 1: Modelagem de Dados

  * **1.1. Descrição do Esquema JSON:** A análise detalhada da estrutura, tipos de dados e hierarquia do arquivo `ERP.json` pode ser encontrada em:

      * [`src/desafio_1/1_1_descricao_esquema.md`](src/desafio_1/1_1_descricao_esquema.md)

  * **1.2. Transcrição para Tabelas SQL:** O script SQL completo e comentado para a criação do schema relacional está em:

      * [`src/desafio_1/1_2_schema.sql`](src/desafio_1/1_2_schema.sql)

  * **1.3. Descrição da Abordagem:** A justificativa completa para as decisões de design, incluindo a abordagem polimórfica, tratamento de dados temporais e integridade referencial, está detalhada em:

      * [`src/desafio_1/1_3_modelagem_detalhada.md`](src/desafio_1/1_3_modelagem_detalhada.md)

### Desafio 2: Arquitetura de Pipeline e Data Lake

  * **2.1. Por que armazenar as respostas das APIs?:** A discussão estratégica sobre a importância de criar uma camada de dados brutos (Bronze), no contexto da Arquitetura Medalhão, está em:

      * [`src/desafio_2/2_1_armazenamento_api.md`](src/desafio_2/2_1_armazenamento_api.md)

  * **2.2. Estrutura de Armazenamento:** O design da estrutura de pastas em um Data Lake no AWS S3, com foco em particionamento estratégico para performance com AWS Athena, está detalhado para os 5 endpoints em:

      * [`src/desafio_2/2_2_estrutura_data_lake.md`](src/desafio_2/2_2_estrutura_data_lake.md)

  * **2.3. Implicações de Mudança no Schema:** A análise do cenário de evolução de schema (`Schema Drift`) e as estratégias para construir um pipeline de dados resiliente estão em:

      * [`src/desafio_2/2_3_mudanca_schema.md`](src/desafio_2/2_3_mudanca_schema.md)

