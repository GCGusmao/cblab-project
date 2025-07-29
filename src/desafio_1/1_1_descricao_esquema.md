# Desafio 1.1: Descrição do Esquema ERP.json

## Processo de Pensamento

O arquivo `ERP.json` possui uma estrutura aninhada, que tem como cerne o pedido de um cliente (guest), que não é identificado dentro deste conjunto de dados. A partir disto, seguirei com uma análise dos campos, assim como dos arrays de objetos. Durante essa análise, quero também observar os tipos de dados que podem ser núlos (`Null`), visando um futuro tratamento desses campos. Entendo que outros campos podem apresentar valores núlos, mas levanto a hipotese de que, em acordo com uma avaliação das regras de negócio, são somente esses os valores permitidos como `Null`.

Outro ponto de interesse na descrição do esquema é observar que grande parte dos dados relativos a posições temporais (data e hora) estão no formato ISO 8601 (`AAAA-MM-DDThh:mm:ss`) e em relação ao UTC (tempo universal coordenado), o que faz bastante sentido se tratar de uma rede de restaurantes com extensão nacional, tendo assim um referencial universal de tempo, podendo carregar, como é o caso, referenciais locais de tempo.

Em adição, também é importante apontar que, devido ao problema de imprecisão com ponto flutuante (`float`), valores monetários devem ser considerados como `DECIMAL` em modelagens para bancos de dados.

### Descrição do Esquema

A seguir, a descrição do esquema do arquivo `ERP.json`. A estrutura é apresentada em formato de árvore para refletir a hierarquia dos dados, com o tipo de dado e observações relevantes para cada campo.

* `curUTC` (string): Timestamp no formato ISO 8601 UTC que indica o momento da geração da resposta.
* `locRef` (string): Identificador de referência da loja/local.
* `guestChecks` (array de objetos): Uma lista contendo os registros dos pedidos.
    * `guestCheckId` (integer): Identificador numérico único do pedido.
    * `chkNum` (integer): O número da conta desse cliente.
    * `opnBusDt` (string): A data de negócio (`YYYY-MM-DD`) em que o pedido foi aberto. Devido a `Bus=Business`
    * `opnUTC` (string): Timestamp UTC de abertura do pedido.
    * `opnLcl` (string): Timestamp em tempo local de abertura do pedido.
    * `clsdBusDt` (string): A data de negócio (`YYYY-MM-DD`) em que o pedido foi fechado. Devido a `Bus=Business`
    * `clsdUTC` (string): Timestamp UTC de fechamento do pedido.
    * `clsdLcl` (string): Timestamp em tempo local de fechamento do pedido.
    * `lastTransUTC` (string): Timestamp UTC da última transação no pedido.
    * `lastTransLcl` (string): Timestamp em tempo local da última transação no pedido.
    * `lastUpdatedUTC` (string): Timestamp UTC da última atualização do registro do pedido.
    * `lastUpdatedLcl` (string): Timestamp em tempo local da última atualização do registro do pedido.
    * `clsdFlag` (boolean): Flag que indica se o pedido está fechado (`true`) ou aberto (`false`).
    * `gstCnt` (integer): Contagem de clientes (guests) no pedido (geralmente utilizado para dividir a conta e outras análises de negócios).
    * `subTtl` (float): Valor do subtotal do pedido.
    * `nonTxblSlsTtl` (float | null): Total de vendas não taxáveis. **Observação: Pode ser nulo.**
    * `chkTtl` (float): Valor total da conta.
    * `dscTtl` (float): Valor total de descontos aplicados (geralmente negativo), inferido por conta de `txblSlsTtl`.
    * `payTtl` (float): Valor total pago.
    * `balDueTtl` (float | null): Saldo devedor. **Observação: Pode ser nulo.**
    * `rvcNum` (integer): Número do "Revenue Center", ou centro de receita.
    * `otNum` (integer): Número do "Order Type", ou tipo do pedido.
    * `ocNum` (integer | null): Número do "Order Channel", ou canal do pedido. **Observação: Pode ser nulo.**
    * `tblNum` (integer): Número da mesa.
    * `tblName` (string): Nome/identificador da mesa.
    * `empNum` (integer): Número 'amigável' do funcionário/garçom associado ao pedido, como matrícula (sabemos que existe um EmpID).
    * `numSrvcRd` (integer): Número total de rodadas de serviço.
    * `numChkPrntd` (integer): Número total de vezes que o pedido foi impresso.
    * `taxes` (array de objetos): Lista de impostos aplicados ao pedido.
        * `taxNum` (integer): Identificador do tipo de imposto.
        * `txblSlsTtl` (float): Total de vendas taxáveis para este imposto.
        * `taxCollTtl` (float): Total de imposto coletado.
        * `taxRate` (integer): A alíquota do imposto.
        * `type` (integer): O tipo de imposto.
    * `detailLines` (array de objetos): Lista dos itens e eventos do pedido.
        * `guestCheckLineItemId` (integer): ID único do linha de detalhe do item.
        * `rvcNum` (integer): Número do "Revenue Center", ou centro de receita.
        * `dtlOtNum` (integer): Número (detalhe) do "Order Type", ou tipo do pedido.
        * `dtlOcNum` (integer): Número (detalhe) do "Order Channel", ou canal do pedido. **Observação: Pode ser nulo.**
        * `lineNum` (integer): Número sequencial do item no pedido, para apresentação 'cronológica' dos pedidos.
        * `dtlId` (integer): ID de detalhe.
        * `detailUTC` (string): Timestamp UTC de quando o item foi adicionado.
        * `detailLcl` (string): Timestamp em tempo local de quando o item foi adicionado.
        * `lastUpdateUTC` (string): Timestamp UTC de quando o item foi modificado pela última vez.
        * `lastUpdateLcl` (string): Timestamp em tempo local de quando o item foi modificado pela última vez.
        * `busDt` (string): Data de negócio do item.
        * `wsNum` (integer): Número identificador da WorkStation (estação de trabalho, PDV ou outra máquina que gerou o pedido do item).
        * `dspTtl` (float): Valor do item exibido.
        * `dspQty` (integer): Quantidade do item exibida.
        * `aggTtl` (float): Valor total agregado, com modificações ou extras no pedido.
        * `aggQty` (integer): Quantidade agregada para faturamento, em caso de ofertas ou outras estruturas.
        * `chkEmpId` (integer): ID único de identificação do funcionário para sistemas e bancos de dados.
        * `chkEmpNum` (integer): Número 'amigável' do funcionário que lançou o pedido, como matrícula.
        * `svcRndNum` (integer): Número da rodada de serviço.
        * `seatNum` (integer): número de assento/cadeira específica daquele pedido (pode ser usado para organização do serviço)
        * `menuItem` (objeto): Detalhes do item de menu associado.
            * `miNum` (integer): Número/ID do item de menu.
            * `modFlag` (boolean): Flag que indica se é uma modificação de um item.
            * `inclTax` (float): Imposto incluído no preço do item.
            * `activeTaxes` (string): String contendo os IDs dos impostos ativos para este item.
            * `prcLvl` (integer): Nível de preço aplicado.