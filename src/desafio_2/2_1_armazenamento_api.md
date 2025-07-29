### Desafio 2.1: Por que armazenar as respostas das APIs?

Armazenar as respostas brutas e imutáveis das APIs é uma prática fundamental na construção de um Data Lake robusto e confiável. Essa estratégia é o pilar da primeira camada da **Arquitetura Medalhão (Medallion Architecture)**, conhecida como camada **Bronze**. Os dados nesta camada são a nossa fonte única da verdade (`Single Source of Truth`).

As razões estratégicas para isso são:

#### 1. Fonte da Verdade e Auditabilidade
A camada Bronze funciona como um registro histórico perfeito do que foi recebido do sistema de origem em um determinado momento. Esses dados brutos e inalterados são a prova definitiva e podem ser usados para:
* **Auditoria:** Confirmar os dados que basearam um relatório financeiro ou uma análise de receita.
* **Conformidade:** Atender a requisitos regulatórios que exigem a manutenção de registros históricos.
* **Resolução de Disputas:** Se houver uma discrepância entre os dados do nosso sistema e o sistema da API de origem, a camada Bronze mostra exatamente o que recebemos.

#### 2. Reprocessamento e Tolerância a Falhas (Replayability)
Esta é uma das vantagens mais críticas do ponto de vista da engenharia. Se um bug for descoberto na lógica de transformação (por exemplo, uma falha no cálculo da receita na camada de negócio), não precisamos sobrecarregar as APIs de origem com novas requisições para corrigir os dados históricos. Em vez disso, nós podemos:
1.  Corrigir o código de transformação.
2.  **Reprocessar** os dados brutos já armazenados na camada Bronze para o período afetado.
3.  Atualizar as camadas subsequentes (Silver e Gold) com os dados corretos.

Isso garante resiliência, economiza custos de API e tempo de desenvolvimento.

#### 3. Desacoplamento de Sistemas (Decoupling)
Ao armazenar os dados brutos primeiro, desacoplamos o processo de **ingestão** (obter os dados) do processo de **transformação** (limpar, modelar e agregar os dados). Isso permite que:
* A equipe de ingestão se concentre em garantir a coleta confiável e pontual dos dados.
* A equipe de Business Intelligence e Analytics trabalhe de forma independente na modelagem e na criação de insights, consumindo os dados já "pousados" no Data Lake, sem depender da disponibilidade das APIs de origem.

#### 4. Flexibilidade para Futuros Casos de Uso e Análise Exploratória
Os requisitos de negócio mudam. Um campo no JSON que parece irrelevante hoje pode ser a chave para um novo modelo de Machine Learning ou uma análise preditiva amanhã. Ao armazenar a resposta completa da API, preservamos 100% da informação original. Isso permite que cientistas de dados e analistas explorem livremente os dados brutos para:
* Descobrir novos padrões e correlações.
* Desenvolver novos produtos de dados que não foram previstos inicialmente.

#### 5. Análise de Causa Raiz (Root Cause Analysis) e Debugging
Quando um número incorreto aparece em um dashboard final (camada Gold), o primeiro passo para depurar é rastrear sua linhagem de dados (`data lineage`). Ter a resposta bruta da API na camada Bronze torna esse processo muito mais simples. Podemos comparar o dado bruto com o dado transformado em cada etapa (Bronze -> Silver -> Gold) para identificar exatamente onde o erro foi introduzido.

Em resumo, armazenar as respostas brutas das APIs não é um ato de "guardar dados por guardar", mas sim uma **decisão de arquitetura estratégica** que garante a governança, a resiliência e a flexibilidade de toda a plataforma de dados, servindo como a base confiável para gerar valor para o negócio.