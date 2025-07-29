# Desafio Engenharia de Dados - Solução

... (introdução projeto, orientações para execuções de ambiente e etc) ...

## 🚀 Ambiente de Desenvolvimento com Docker

Para facilitar a avaliação e garantir um ambiente consistente, a estrutura do banco de dados do Desafio 1 pode ser criada e executada automaticamente com o Docker.

### Pré-requisitos

  * [Docker](https://www.google.com/search?q=https://www.docker.com/get-started) instalado e em execução.
  * [Docker Compose](https://docs.docker.com/compose/install/) instalado.

### Como Executar

1.  Clone este repositório para a sua máquina local.
2.  Abra um terminal e navegue até a pasta raiz do projeto (onde o arquivo `docker-compose.yml` está localizado).
3.  Execute o seguinte comando para iniciar o contêiner do PostgreSQL em segundo plano:
    ```bash
    docker-compose up -d
    ```
4.  Pronto\! O Docker irá baixar a imagem do PostgreSQL, criar um contêiner e executar automaticamente o script `src/desafio_1/1_2_schema.sql` para criar todas as tabelas e relacionamentos.

### Como Verificar o Resultado

Você pode se conectar ao banco de dados para verificar se o schema foi criado corretamente.

**1. Conectar via linha de comando (psql):**
Execute o seguinte comando no seu terminal para abrir um shell interativo do `psql` dentro do contêiner:

```bash
docker exec -it coco-bambu-postgres-db psql -U cblab_user -d coco_bambu_db
```

Uma vez conectado, execute `\dt` para listar todas as tabelas criadas. Você deverá ver a lista com `stores`, `employees`, `guest_checks`, `detail_lines`, etc.

**2. Conectar via Ferramenta Gráfica (DBeaver, pgAdmin, etc.):**
Use as seguintes credenciais para configurar a conexão na sua ferramenta de preferência:

  * **Host:** `localhost`
  * **Porta:** `5435` **porta alterada para evitar conflitos**
  * **Banco de Dados:** `coco_bambu_db`
  * **Usuário:** `cblab_user`
  * **Senha:** `a_senha_super_segura` (a senha definida no `docker-compose.yml`)

### Para Parar o Ambiente

Para parar e remover o contêiner, execute o seguinte comando na pasta raiz do projeto:

```bash
docker-compose down
```

-----