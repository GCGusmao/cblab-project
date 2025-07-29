### Desafio 2.2: Como você armazenaria os dados?

Para armazenar as respostas das 5 APIs de forma a permitir manipulação, verificações e buscas rápidas, a solução ideal é criar uma estrutura de pastas lógica e particionada, que é adequada para armazenamento no Amazon S3. Esta estrutura representará a **Camada Bronze** da nossa Arquitetura Medalhão, servindo como o repositório de dados brutos e imutáveis.

A estrutura foi projetada com foco em otimizar o desempenho de ferramentas de consulta como o **AWS Athena**, que se beneficia diretamente de um particionamento inteligente.

#### 1\. Princípios de Design da Estrutura

  * **Separação por Fonte:** Cada um dos 5 endpoints da API terá seu próprio diretório raiz dentro da camada Bronze. Isso isola as fontes de dados, facilitando o gerenciamento, o controle de acesso e o processamento individual de cada fonte.
  * **Particionamento por Data e Loja:** Como todas as APIs são consultadas usando os parâmetros `busDt` (data de negócio) e `storeId` (ID da loja), estes são os candidatos perfeitos para as nossas chaves de partição. Isso permitirá que as consultas sejam filtradas de forma extremamente eficiente.
  * **Padrão Hive-style:** A nomenclatura das pastas seguirá o padrão `chave=valor` (ex: `year=2025`). Este é o formato que o AWS Athena e outras ferramentas do ecossistema Hadoop reconhecem nativamente para aplicar a eliminação de partições (partition pruning).

#### 2\. Estrutura de Pastas Detalhada para os 5 Endpoints

A seguir, a estrutura de pastas completa para a camada Bronze dentro de um bucket S3 chamado `cblab-datalake-production`.

```
s3://cblab-datalake-production/
└── bronze/
    ├── getFiscalInvoice/
    │   └── year={AAAA}/
    │       └── month={MM}/
    │           └── day={DD}/
    │               └── store_id={id_da_loja}/
    │                   └── {timestamp}_{uuid}.json
    │
    ├── getGuestChecks/
    │   └── year={AAAA}/
    │       └── month={MM}/
    │           └── day={DD}/
    │               └── store_id={id_da_loja}/
    │                   └── {timestamp}_{uuid}.json
    │
    ├── getChargeBack/
    │   └── year={AAAA}/
    │       └── month={MM}/
    │           └── day={DD}/
    │               └── store_id={id_da_loja}/
    │                   └── {timestamp}_{uuid}.json
    │
    ├── getTransactions/
    │   └── year={AAAA}/
    │       └── month={MM}/
    │           └── day={DD}/
    │               └── store_id={id_da_loja}/
    │                   └── {timestamp}_{uuid}.json
    │
    └── getCashManagementDetails/
        └── year={AAAA}/
            └── month={MM}/
                └── day={DD}/
                    └── store_id={id_da_loja}/
                        └── {timestamp}_{uuid}.json
```

#### 3\. Exemplos Práticos (Um por Ativo/Endpoint)

Para ilustrar como os arquivos seriam armazenados, considere uma requisição para a loja `99-CB-CB` na data de negócio `29 de Julho de 2025`:

  * **getFiscalInvoice:**
    `s3://cblab-datalake-production/bronze/getFiscalInvoice/year=2025/month=07/day=29/store_id=99-CB-CB/1659124800000_a1b2c3.json`

  * **getGuestChecks:**
    `s3://cblab-datalake-production/bronze/getGuestChecks/year=2025/month=07/day=29/store_id=99-CB-CB/1659124800000_d4e5f6.json`

  * **getChargeBack:**
    `s3://cblab-datalake-production/bronze/getChargeBack/year=2025/month=07/day=29/store_id=99-CB-CB/1659124800000_g7h8i9.json`

  * **getTransactions:**
    `s3://cblab-datalake-production/bronze/getTransactions/year=2025/month=07/day=29/store_id=99-CB-CB/1659124800000_j1k2l3.json`

  * **getCashManagementDetails:**
    `s3://cblab-datalake-production/bronze/getCashManagementDetails/year=2025/month=07/day=29/store_id=99-CB-CB/1659124800000_m4n5o6.json`

Essa estrutura garante que, ao realizar uma consulta no Athena, por exemplo, filtrando por uma data e loja específicas, o serviço irá escanear apenas os arquivos dentro da pasta correspondente, ignorando todo o resto do Data Lake. Isso resulta em uma drástica redução no volume de dados lidos, o que se traduz diretamente em **maior velocidade de consulta e menor custo operacional**.