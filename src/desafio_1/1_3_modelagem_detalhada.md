# Desafio 1.3: Descrição e Justificativa da Abordagem de Modelagem

Este documento detalha as decisões de arquitetura e design tomadas para transcrever a estrutura JSON do `ERP.json` em um esquema de banco de dados relacional, conforme solicitado no Desafio 1 do processo seletivo de Engenharia de Dados. É importante lembrar que as tomadas de devisão foram feitas a partir de uma resposta de API, podendo estar em desacordo com as regras de negócio reais. Deste modo, algumas suposições foram tomadas como verdades.

## 1. Visão Geral da Estratégia

A abordagem principal foi a criação de um **esquema relacional altamente normalizado (3ª Forma Normal - 3NF)**. O objetivo foi construir uma fundação de dados que seja ao mesmo tempo robusta, escalável e otimizada para as consultas analíticas e operacionais típicas de uma cadeia de restaurantes, como o Coco Bambu.

As principais preocupações que guiaram o design foram:

* **Integridade dos Dados:** Garantir que apenas dados válidos e consistentes sejam armazenados (diante da visão de negócio adotada nesse projeto).
* **Eliminação de Redundância:** Evitar o armazenamento da mesma informação em múltiplos locais.
* **Escalabilidade e Manutenibilidade:** Criar um modelo que possa evoluir facilmente para acomodar novas regras de negócio e fontes de dados sem a necessidade de refatorações complexas.
* **Clareza e Legibilidade:** Projetar um esquema que seja intuitivo e fácil de entender por outros desenvolvedores e analistas de dados.

## 2. Decisões de Design Detalhadas

A seguir, as justificativas para as principais decisões de arquitetura do esquema SQL.

### 2.1. A Solução para `detailLines`: Associação Polimórfica

O desafio mais significativo da modelagem era a natureza do array `detailLines`, que pode conter eventos de diferentes tipos (`menuItem`, `discount`, `tenderMedia`, etc.). Uma abordagem de criar uma única tabela "larga" com colunas para todos os tipos possíveis foi descartada por seus graves problemas:

* **Vulnerabilidade na Integridade:** Permitiria a inserção de dados impossíveis (ex: uma linha que é um item de menu e um pagamento ao mesmo tempo).
* **Dificuldade de Manutenção:** A adição de um novo tipo de evento exigiria um `ALTER TABLE` na tabela mais crítica do sistema, uma operação arriscada e lenta em produção.
* **Excesso de Nulos:** Geraria uma tabela com muitas colunas vazias, desperdiçando espaço e tornando as consultas mais complexas.

Em vez disso, foi implementado o padrão de design de **Associação Polimórfica**.

* Uma tabela central (`detail_lines`) armazena os dados comuns a todos os tipos de evento.
* A coluna `line_type` atua como um "discriminador", identificando a natureza de cada registro.
* A coluna `entity_id` aponta para a chave primária de uma das várias tabelas "filhas" (`order_item_details`, `discounts`, `tender_media`, etc.), que armazenam os atributos específicos de cada tipo.

Essa abordagem resolve todos os problemas do modelo largo: a **integridade é garantida por design**, a **escalabilidade é simplificada** (basta adicionar uma nova tabela filha para um novo tipo de evento) e as **consultas são lógicas e flexíveis**, utilizando `LEFT JOIN` para reconstruir uma visão completa dos eventos de um pedido. A nota no script SQL que menciona que a integridade desta chave estrangeira é gerenciada na camada de aplicação reflete o entendimento deste trade-off padrão para ganhar flexibilidade.

### 2.2. Tratamento de Dados Temporais: UTC como Fonte da Verdade

O `ERP.json` fornece timestamps tanto em UTC quanto no fuso horário local (ex: `opnUTC` e `opnLcl`). A decisão de design foi **armazenar exclusivamente os timestamps UTC** utilizando o tipo de dado `TIMESTAMP WITH TIME ZONE`.

**Justificativa:**

1.  **Fonte Única da Verdade:** O UTC é um padrão universal e inequívoco. Armazená-lo garante que cada evento tenha um registro temporal absoluto e comparável, independentemente de onde no mundo ele ocorreu.
2.  **Eliminação de Redundância:** Armazenar o tempo local seria redundante, pois ele é apenas uma representação do UTC em um fuso específico. A partir do valor UTC, qualquer tempo local pode ser calculado no momento da consulta (`SELECT ... AT TIME ZONE '...'`), oferecendo máxima flexibilidade.
3.  **Prevenção de Inconsistências:** Evita o risco de os dados UTC e locais ficarem dessincronizados, eliminando ambiguidades e garantindo a integridade dos dados temporais.

### 2.3. Estrutura e Nomenclatura

Para garantir a clareza e seguir as melhores práticas, foram adotadas as seguintes convenções:

* **Nomenclatura:** Todas as tabelas e colunas foram nomeadas em inglês usando o padrão `snake_case` (ex: `guest_checks`, `menu_item_number`). Isso facilita a interoperabilidade com ferramentas de mercado e mantém a consistência.
* **Dados Mestres vs. Transacionais:** O esquema é claramente dividido entre tabelas de "Dados Mestres" (`stores`, `employees`, `menu_items`), que contêm dados de referência, e "Tabelas Transacionais" (`guest_checks`, `detail_lines`), que registram os eventos do dia a dia.
* **Tipos de Dados:** Foram feitas escolhas de tipos de dados apropriados para garantir a precisão, como `DECIMAL(10, 2)` para valores monetários e `BIGINT` ou `SERIAL` para chaves primárias, antecipando um grande volume de dados.

### 2.4. Integridade Referencial

A integridade entre as tabelas é garantida pelo uso extensivo de `FOREIGN KEY` constraints. O uso de `ON DELETE CASCADE` na relação entre `guest_checks` e suas tabelas dependentes (como `taxes` e `detail_lines`) garante que, se um pedido for removido, todos os seus dados associados sejam limpos automaticamente, prevenindo registros "órfãos" no banco de dados.