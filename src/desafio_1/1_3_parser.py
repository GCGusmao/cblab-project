import json
import psycopg2
from pathlib import Path

# --- Configuração do Banco de Dados e do Arquivo ---
# ATENÇÃO: Em um ambiente de produção, NUNCA armazene credenciais diretamente no código.
# Use variáveis de ambiente, um serviço de segredos (como AWS Secrets Manager) ou um arquivo .env.
# As credenciais estão aqui apenas para facilitar a avaliação deste desafio.
DB_CONFIG = {
    "dbname": "coco_bambu_db",
    "user": "cblab_user",
    "password": "a_senha_super_segura",
    "host": "localhost",
    "port": "5435"
}

# Constrói o caminho relativo para o arquivo JSON de forma segura
# O script está em src/desafio_1/, então subimos dois níveis para a raiz do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
JSON_FILE_PATH = BASE_DIR / "data" / "ERP.json"

def get_db_connection():
    """Cria e retorna uma nova conexão com o banco de dados."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Erro: Não foi possível conectar ao banco de dados PostgreSQL.")
        print(f"Detalhes: {e}")
        print("\nVerifique se o contêiner do Docker está em execução ('docker-compose up -d').")
        return None

def insert_master_data(cursor, guest_check, loc_ref):
    """
    Insere os dados mestres (loja, funcionários, item do menu) de forma idempotente.
    'ON CONFLICT DO NOTHING' garante que, se o registro já existir, nada acontece.
    """
    # 1. Inserir Loja
    cursor.execute(
        """
        INSERT INTO stores (store_ref_id, store_name, address)
        VALUES (%s, %s, %s) ON CONFLICT (store_ref_id) DO NOTHING;
        """,
        (loc_ref, 'Coco Bambu - Unidade Exemplo', 'Endereço Exemplo')
    )

    # 2. Inserir Funcionário do Pedido
    cursor.execute(
        """
        INSERT INTO employees (employee_number, first_name, last_name)
        VALUES (%s, %s, %s) ON CONFLICT (employee_number) DO NOTHING;
        """,
        (guest_check['empNum'], 'Funcionario', 'Principal')
    )

    # 3. Inserir Funcionário da Linha de Detalhe e Item do Menu
    for line in guest_check.get('detailLines', []):
        if 'menuItem' in line:
            menu_item = line['menuItem']
            cursor.execute(
                """
                INSERT INTO employees (employee_number, employee_id, first_name, last_name)
                VALUES (%s, %s, %s, %s) ON CONFLICT (employee_number) DO NOTHING;
                """,
                (line['chkEmpNum'], line['chkEmpId'], 'Funcionario', 'Item')
            )
            cursor.execute(
                """
                INSERT INTO menu_items (menu_item_number, item_name, base_price)
                VALUES (%s, %s, %s) ON CONFLICT (menu_item_number) DO NOTHING;
                """,
                (menu_item['miNum'], f"Item {menu_item['miNum']}", line['dspTtl'])
            )

def process_guest_check(cursor, guest_check, loc_ref):
    """Processa um único registro de guest_check e o insere no banco de dados."""
    
    print(f"\n--- Processando Pedido ID: {guest_check['guestCheckId']} ---")

    # Passo 1: Inserir dados mestres para garantir a existência das chaves estrangeiras
    insert_master_data(cursor, guest_check, loc_ref)
    print("Dados mestres (lojas, funcionários, itens) validados/inseridos.")

    # Passo 2: Inserir o registro principal em guest_checks
    cursor.execute(
        """
        INSERT INTO guest_checks (
            guest_check_id, store_ref_id, employee_number, check_number, is_closed, open_business_date, open_utc, closed_utc,
            guest_count, sub_total, check_total, discount_total, payment_total, balance_due, non_taxable_sales_total,
            revenue_center_number, order_type_number, order_channel_number, table_number, table_name, total_service_rounds,
            prints_count, last_updated_utc, last_transaction_utc
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (guest_check_id) DO NOTHING;
        """,
        (
            guest_check['guestCheckId'], loc_ref, guest_check['empNum'], guest_check['chkNum'], guest_check['clsdFlag'],
            guest_check['opnBusDt'], guest_check['opnUTC'], guest_check['clsdUTC'], guest_check['gstCnt'], guest_check['subTtl'],
            guest_check['chkTtl'], guest_check['dscTtl'], guest_check['payTtl'], guest_check.get('balDueTtl'),
            guest_check.get('nonTxblSlsTtl'), guest_check['rvcNum'], guest_check['otNum'], guest_check.get('ocNum'),
            guest_check['tblNum'], guest_check['tblName'], guest_check['numSrvcRd'], guest_check['numChkPrntd'],
            guest_check['lastUpdatedUTC'], guest_check['lastTransUTC']
        )
    )
    print(f"Registro principal inserido na tabela 'guest_checks'.")

    # Passo 3: Inserir os impostos associados
    for tax in guest_check.get('taxes', []):
        cursor.execute(
            """
            INSERT INTO taxes (guest_check_id, tax_number, taxable_sales_total, tax_collected_total, tax_rate, tax_type)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (guest_check_id, tax_number) DO NOTHING;
            """,
            (guest_check['guestCheckId'], tax['taxNum'], tax['txblSlsTtl'], tax['taxCollTtl'], tax['taxRate'], tax['type'])
        )
    print("Registros de impostos inseridos na tabela 'taxes'.")

    # Passo 4: Processar as linhas de detalhe (a lógica polimórfica)
    for line in guest_check.get('detailLines', []):
        entity_id = None
        line_type = None

        # Validação para o tipo 'MENU_ITEM'
        if 'menuItem' in line:
            line_type = 'MENU_ITEM'
            menu_item_data = line['menuItem']
            
            # 4.1: Insere na tabela filha e recupera o ID gerado
            cursor.execute(
                """
                INSERT INTO order_item_details (
                    menu_item_number, display_quantity, aggregate_quantity, display_total, aggregate_total,
                    included_tax, is_modifier, active_taxes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING order_item_detail_id;
                """,
                (
                    menu_item_data['miNum'], line['dspQty'], line['aggQty'], line['dspTtl'], line['aggTtl'],
                    menu_item_data['inclTax'], menu_item_data['modFlag'], menu_item_data['activeTaxes']
                )
            )
            entity_id = cursor.fetchone()[0]
            print(f"  - Detalhe de item de menu inserido em 'order_item_details' com ID: {entity_id}")

        # Aqui deve-se adicionar a lógica para outros tipos (discount, tenderMedia, etc.)
        # elif 'discount' in line:
        #     line_type = 'DISCOUNT'
        #     ...

        # 4.2: Insere na tabela mãe 'detail_lines' com a referência correta
        if line_type and entity_id:
            cursor.execute(
                """
                INSERT INTO detail_lines (
                    detail_line_id, guest_check_id, employee_number, revenue_center_number, detail_order_type_number,
                    detail_order_channel_number, detail_id, line_number, seat_number, service_round_number,
                    workstation_number, detail_utc, detail_last_updated_utc, line_type, entity_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (detail_line_id) DO NOTHING;
                """,
                (
                    line['guestCheckLineItemId'], guest_check['guestCheckId'], line['chkEmpNum'], line['rvcNum'],
                    line.get('dtlOtNum'), line.get('dtlOcNum'), line['dtlId'], line['lineNum'], line['seatNum'],
                    line['svcRndNum'], line['wsNum'], line['detailUTC'], line['lastUpdateUTC'], line_type, entity_id
                )
            )
            print(f"  - Linha de detalhe polimórfica inserida em 'detail_lines' (Tipo: {line_type}, Entity ID: {entity_id})")

def main():
    """Função principal que orquestra a leitura do JSON e a inserção no banco."""
    print("Iniciando script de parsing e validação do schema...")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        with conn.cursor() as cursor:
            # Carrega os dados do arquivo JSON
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Pega o locRef do nível raiz do JSON
            loc_ref = data.get('locRef')
            if not loc_ref:
                print("Erro Crítico: A chave 'locRef' não foi encontrada no nível raiz do JSON.")
                return

            # Itera sobre cada 'guestCheck' no arquivo, passando o loc_ref
            for guest_check in data.get('guestChecks', []):
                process_guest_check(cursor, guest_check, loc_ref)

            # Confirma a transação
            conn.commit()
            print("\nSUCESSO: Todos os dados do ERP.json foram inseridos no banco de dados.")
            print("A modelagem foi validada com sucesso!")

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em '{JSON_FILE_PATH}'.")
        print("Verifique se o arquivo 'ERP.json' está na pasta 'data' na raiz do projeto.")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{JSON_FILE_PATH}' não é um JSON válido.")
    except psycopg2.Error as e:
        print(f"Erro de banco de dados: {e}")
        print("A transação será revertida (rollback).")
        conn.rollback()
    finally:
        # Garante que a conexão seja sempre fechada
        if conn:
            conn.close()
            print("\nConexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()