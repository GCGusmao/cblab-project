# Quadro Kanban - Andamento do Projeto CBLab

Este documento rastreia o progresso do desenvolvimento da solução para o Desafio CBLab. As tarefas são movidas da coluna `A Fazer` para `Em Andamento` e, finalmente, para `Concluído`.

---

### ✅ Concluído (Done)

* [x] Configurar o repositório Git inicial no GitHub/GitLab.
* [x] Fazer a análise inicial do arquivo `ERP.json` e dos requisitos do PDF.
* [x] Criar a estrutura de pastas base do projeto (`/src`, `/data`, `/tests`).
* [x] **Desafio 1.1:** Documentar formalmente o esquema do `ERP.json`.
* [x] **Desafio 1.2:** Desenhar o modelo de dados relacional (SQL) a partir do JSON.
    * [x] Definir a tabela `guest_checks`.
    * [x] Definir a tabela `detail_lines` com abordagem polimórfica.
    * [x] Definir tabelas de suporte (`order_item_details`, `discounts`, etc.).
* [x] Avaliação de criaçao de um ambiente contenerizado para execução dos produtos criados.
* [x] **Desafio 1.3:** Escrever a justificativa detalhada para a abordagem de modelagem de dados escolhida.
* [x] **Desafio 2.1:** Elaborar e escrever a resposta sobre a importância de armazenar as respostas brutas das APIs.

### ⏳ Em Andamento (In Progress)

* [x] **Desafio 2.2:** Projetar e documentar a estrutura de pastas do Data Lake (S3) com particionamento no estilo Hive.
* [x] **Documentação:** Escrever o `README.md` final, explicando o projeto, a solução e como executar o código.

### 📋 A Fazer (To Do)

* [ ] **Desafio 2.3:** Detalhar as implicações e a solução para a mudança de esquema (`taxes` -> `taxation`).
* [ ] **Implementação:** Criar um script em Python (`/src/parser.py`) para validar a modelagem, lendo o `ERP.json` e estruturando os dados.
* [ ] **Testes:** Escrever testes unitários básicos para o script de parsing para garantir a resiliência do código.
* [ ] **Apresentação:** Criar apresentação de slides para apoiar as decisões tomadas junto a camada de negócios.
* [ ] **Revisão Final:** Revisar todo o código, documentos e respostas antes da entrega.
* [ ] **Entrega:** Enviar o e-mail com o link do repositório Git e apresentação de slides.

---
