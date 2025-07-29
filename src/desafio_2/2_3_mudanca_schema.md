### Desafio 2.3: Implicações de uma Mudança no Schema da API

A alteração de um campo na resposta da API, como a renomeação de `taxes` para `taxation`, teria implicações em diferentes estágios do nosso pipeline de dados. Uma arquitetura bem projetada não falha catastroficamente, mas reage a essa mudança de formas específicas em cada camada.

#### 1\. Implicação na Camada Bronze (Ingestão de Dados Brutos)

**Nenhuma implicação direta. O pipeline de ingestão não deve quebrar.**

Esta é a principal vantagem de ter uma camada de dados brutos. A função da camada Bronze é ser um repositório fiel e imutável do que a API de origem nos enviou.

  * **O que acontece:** O processo de ingestão (seja um DAG do Airflow, um script Python, etc.) simplesmente pegaria a nova resposta JSON e a salvaria no S3 como ela é. Os arquivos antigos teriam o campo `taxes`, e os novos teriam o campo `taxation`.
  * **Por que é robusto:** O pipeline de ingestão não tenta interpretar ou validar a estrutura interna do JSON. Ele apenas transporta o dado. Isso garante que nunca percamos dados, mesmo quando a fonte muda inesperadamente.

#### 2\. Implicação na Camada Silver (Transformação e Limpeza)

**Impacto Crítico. Este é o ponto onde o pipeline quebraria ou geraria dados incorretos.**

A camada Silver é onde as grandes mudanças ocorrem: lemos o JSON bruto e o transformamos em um formato estruturado e limpo (como Parquet, seguindo nosso schema do Desafio 1). O código de transformação que realiza essa tarefa espera encontrar o campo `taxes`.

  * **O que acontece:** Quando o job de transformação (ex: um job Spark) tentasse acessar `guestChecks.taxes` em um arquivo novo, ele encontraria um `null` ou, dependendo da linguagem, levantaria uma exceção (`KeyError` em Python).
  * **Consequências:**
      * **Falha do Job:** O pipeline de transformação poderia parar completamente, e nenhum dado novo seria processado e disponibilizado para a equipe de BI.
      * **Dados Incorretos (Falha Silenciosa):** Pior ainda, se o código for escrito de forma a não quebrar com chaves ausentes, ele poderia simplesmente continuar, mas gerando registros sem nenhuma informação de imposto. Isso levaria a relatórios de receita incorretos e a decisões de negócio baseadas em dados falhos.

### Soluções: Como Construir um Pipeline Resiliente

Para mitigar essas implicações, implementamos as seguintes estratégias de engenharia de dados:

1.  **Monitoramento e Alertas sobre o Schema:**
    O pipeline deveria ter uma etapa de **validação de schema**. Antes de processar os dados, uma ferramenta poderia verificar se a estrutura do JSON corresponde ao esperado. Se um novo campo como `taxation` aparecer e um campo esperado como `taxes` desaparecer, o sistema deve gerar um **alerta imediato** (via Slack, e-mail, etc.) para a equipe de engenharia, que pode então investigar e adaptar o código proativamente.

2.  **Código de Transformação Defensivo e Adaptativo:**
    O código que transforma os dados da camada Bronze para a Silver deve ser escrito para ser retrocompatível e resiliente a essas mudanças. Em vez de assumir que o campo `taxes` sempre existirá, ele deve ser capaz de lidar com ambas as versões.

    **Exemplo em Pseudocódigo Python:**

    ```python
    # Para cada registro de guest_check lido do JSON...

    # Verifica a existência do novo campo primeiro, depois do antigo.
    # O 'or' garante que peguemos o primeiro que não for nulo.
    tax_data = guest_check.get('taxation') or guest_check.get('taxes')

    if tax_data:
        # O código de processamento de impostos continua a partir daqui,
        # usando a variável 'tax_data', não importa de qual campo ela veio.
        process_taxes(tax_data)
    else:
        # Loga um aviso de que não foram encontradas informações de imposto.
        log_warning(f"Nenhum dado de imposto encontrado para o guest_check_id: {guest_check.get('guestCheckId')}")
    ```

    Esta abordagem garante que o pipeline continue a funcionar e possa até mesmo reprocessar dados antigos sem problemas.

3.  **Uso de um Schema Registry (Solução Avançada):**
    Em ecossistemas mais maduros, especialmente os que usam streaming com **Apache Kafka**, a melhor prática é usar um **Schema Registry**. Ele funciona como um "cartório" central para os schemas. A API de origem precisaria registrar qualquer nova versão de seu schema antes de enviar os dados. Nosso processo consumidor poderia então buscar o schema correto e se adaptar dinamicamente, prevenindo que dados com formato inesperado sequer entrem no nosso sistema principal.

Em resumo, a mudança de um campo na API **implicaria uma falha ou corrupção de dados na etapa de transformação**, mas um pipeline bem arquitetado é projetado exatamente para detectar e lidar com esses cenários através de monitoramento, código adaptativo e, em casos mais avançados, governança de schemas.