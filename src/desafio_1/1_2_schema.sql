-- =================================================================
-- ESQUEMA DE BANCO DE DADOS PARA OPERAÇÕES DE RESTAURANTE COCO BAMBU
-- Desafio 1.2
--
-- Autor: Gustavo Canedo Gusmão
-- Data: 29/07/2025
--
-- Abordagem:
-- O esquema utiliza um modelo relacional normalizado para garantir
-- a integridade e a escalabilidade dos dados.
--
-- O principal desafio, a natureza polimórfica do array 'detailLines',
-- foi resolvido com um padrão de "Associação Polimórfica". A tabela
-- 'detail_lines' atua como uma tabela central, e a coluna 'line_type'
-- indica qual tabela específica contém os detalhes daquela linha.
-- =================================================================

-- ----------------------------
-- Tabelas de Referência (Dados Mestres)
-- ----------------------------

CREATE TABLE stores (
    store_ref_id VARCHAR(255) PRIMARY KEY, -- Mapeado de locRef
    store_name VARCHAR(255) NOT NULL,
    address TEXT,
    -- Outros dados relevantes que podem ser retirados de outras fontes de dados.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    employee_number INT PRIMARY KEY, -- Mapeado de empNum and chkEmpNum
    employee_id BIGINT UNIQUE, -- Mapeado de chkEmpId (internal DB id)
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    hire_date DATE,
    -- Outros dados relevantes que podem ser retirados de outras fontes de dados.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE menu_items (
    menu_item_number INT PRIMARY KEY, -- Mapeado de menuItem.miNum
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    -- Outros dados relevantes que podem ser retirados de outras fontes de dados.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
-- Tabelas Transacionais
-- ----------------------------

CREATE TABLE guest_checks (
    guest_check_id BIGINT PRIMARY KEY, -- Mapeado de guestCheckId
    store_ref_id VARCHAR(255) REFERENCES stores(store_ref_id) ON DELETE SET NULL, -- Mapeado de locRef
    employee_number INT REFERENCES employees(employee_number) ON DELETE SET NULL, -- Mapeado de empNum
    check_number INT, -- Mapeado de chkNum
    is_closed BOOLEAN DEFAULT FALSE, -- Mapeado de clsdFlag
    open_business_date DATE, -- Mapeado de opnBusDt
    open_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de opnUTC
    closed_business_date DATE, -- Mapeado de clsdBusDt
    closed_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de clsdUTC
    guest_count INT, -- Mapeado de gstCnt
    sub_total DECIMAL(10, 2), -- Mapeado de subTtl
    check_total DECIMAL(10, 2), -- Mapeado de chkTtl
    discount_total DECIMAL(10, 2), -- Mapeado de dscTtl
    payment_total DECIMAL(10, 2), -- Mapeado de payTtl
    balance_due DECIMAL(10, 2), -- Mapeado de balDueTtl
    non_taxable_sales_total DECIMAL(10, 2), -- Mapeado de nonTxblSlsTtl
    revenue_center_number INT, -- Mapeado de rvcNum
    order_type_number INT, -- Mapeado de otNum
    order_channel_number INT, -- Mapeado de ocNum
    table_number INT, -- Mapeado de tblNum
    table_name VARCHAR(255), -- Mapeado de tblName
    total_service_rounds INT, -- Mapeado de numSrvcRd
    prints_count INT, -- Mapeado de numChkPrntd
    api_response_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de curUTC
    last_updated_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de lastUpdatedUTC
    business_date TIMESTAMP WITH TIME ZONE, -- Mapeado de busDt
    last_transaction_utc TIMESTAMP WITH TIME ZONE -- Mapeado de lastTransUTC
);

CREATE TABLE taxes (
    tax_id SERIAL PRIMARY KEY,
    guest_check_id BIGINT NOT NULL REFERENCES guest_checks(guest_check_id) ON DELETE CASCADE,
    tax_number INT NOT NULL, -- Mapeado de taxes.taxNum
    taxable_sales_total DECIMAL(10, 2), -- Mapeado de taxes.txblSlsTtl
    tax_collected_total DECIMAL(10, 2), -- Mapeado de taxes.taxCollTtl
    tax_rate DECIMAL(10, 2), -- Mapeado de taxes.taxRate
    tax_type INT, -- Mapeado de taxes.type
    UNIQUE(guest_check_id, tax_number)
);

-- Tabela Central para a Associação Polimórfica.
CREATE TABLE detail_lines (
    detail_line_id BIGINT PRIMARY KEY, -- Mapeado de guestCheckLineItemId
    guest_check_id BIGINT NOT NULL REFERENCES guest_checks(guest_check_id) ON DELETE CASCADE,
    employee_number INT REFERENCES employees(employee_number) ON DELETE SET NULL, -- Mapeado de chkEmpNum
    revenue_center_number INT, -- Mapeado de detailLines.rvcNum
    detail_order_type_number INT, -- Mapeado de dtlOtNum
    detail_order_channel_number INT, -- Mapeado de dtlOcNum
    detail_id INT, -- Mapeado de dtlId
    line_number INT, -- Mapeado de lineNum
    seat_number INT, -- Mapeado de seatNum
    service_round_number INT, -- Mapeado de svcRndNum
    workstation_number INT, -- Mapeado de wsNum
    detail_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de detailUTC
    detail_last_updated_utc TIMESTAMP WITH TIME ZONE, -- Mapeado de lastUpdateUTC
    -- Coluna chave para o Polimorfismo
    line_type VARCHAR(50) NOT NULL CHECK (line_type IN ('MENU_ITEM', 'DISCOUNT', 'SERVICE_CHARGE', 'TENDER_MEDIA', 'ERROR_CODE')),
    entity_id BIGINT NOT NULL -- Esse ID aponta para a primary key na especificada tabela de detalhes.
);

-- -------------------------------------------------
-- Tabelas de Detalhe Específicas (Filhas Polimórficas)
-- -------------------------------------------------

-- Observação: A restrição de chave estrangeira (foreign key) de detail_lines(entity_id) para estas tabelas é gerenciada na camada de aplicação.

-- MENU_ITEM deverá apontar para order_item_details
CREATE TABLE order_item_details (
    order_item_detail_id SERIAL PRIMARY KEY,
    menu_item_number INT NOT NULL REFERENCES menu_items(menu_item_number) ON DELETE RESTRICT, -- Mapeado de menuItem.miNum
    display_quantity INT NOT NULL, -- Mapeado de dspQty
    aggregate_quantity INT NOT NULL, -- Mapeado de aggQty
    display_total DECIMAL(10, 2) NOT NULL, -- Mapeado de dspTtl
    aggregate_total DECIMAL(10, 2) NOT NULL, -- Mapeado de aggTtl
    included_tax DECIMAL(10, 5), -- Mapeado de menuItem.inclTax
    is_modifier BOOLEAN DEFAULT FALSE, -- Mapeado de menuItem.modFlag
    active_taxes VARCHAR(255) -- Mapeado de menuItem.activeTaxes
);

-- DISCOUNT deverá apontar para discounts
CREATE TABLE discounts (
    discount_id SERIAL PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    reason VARCHAR(255),
    authorization_employee_number INT REFERENCES employees(employee_number) ON DELETE SET NULL
);

-- SERVICE_CHARGE deverá apontar para service_charges
CREATE TABLE service_charges (
    service_charge_id SERIAL PRIMARY KEY,
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255)
);

-- TENDER_MEDIA deverá apontar para tender_media
CREATE TABLE tender_media (
    tender_media_id SERIAL PRIMARY KEY,
    payment_type VARCHAR(50) NOT NULL, -- e.g., 'CASH', 'CREDIT_CARD', 'PIX'
    amount_paid DECIMAL(10, 2) NOT NULL,
    card_last_digits VARCHAR(4),
    authorization_code VARCHAR(255)
);

-- ERROR_CODE deverá apontar para error_codes
CREATE TABLE error_codes (
    error_code_id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    message TEXT
);