# Spec 05 — Plano de Execução Ordenado (`[Incremental Build Model]`) para Monolito de 700 Módulos

**Diretório Base das Specs:** `C:\Users\walter.matsuda\Documents\metadados_famema2.1\specs`  
**Diretório Base de Salvamento de Todos os Dados:** `C:\Users\walter.matsuda\Documents\metadados_famema2.1`  
**Alvo da Execução:** Pasta raiz contendo todos os **700 projetos/módulos** de um monolito corporativo C#/.NET + Banco de Dados Relacional.  
**Modelo de Execução:** **`[Incremental Build Model]`** — Toda condição delimitada por chaves **`{ condição }`** representa uma **Parada Obrigatória (`HALT GATE`)** onde a execução persiste seu estado incremental, entrega ao usuário as consultas/templates de auxílio gerados pela IA e aguarda o fornecimento dos dados solicitados antes de dar continuidade.

---

## 1. Estrutura Completa de Diretórios em `C:\Users\walter.matsuda\Documents\metadados_famema2.1`

Todos os dados gerados ou recebidos durante a execução dos 700 módulos são salvos exclusivamente dentro de `C:\Users\walter.matsuda\Documents\metadados_famema2.1`:

```text
C:\Users\walter.matsuda\Documents\metadados_famema2.1\
├── specs\                                                        # Especificações Normativas (00 a 05)
├── config\
│   ├── application_manifest.json                                 # Nome da aplicação e pasta raiz dos 700 módulos
│   └── incremental_build_state.json                              # Estado atual do Incremental Build Model, hashes SHA-256 e Gate ativo
├── input\                                                        # Dados fornecidos pelo usuário em cada Gate { ... }
│   ├── layer1_relational_schema\                                 # [Alimentado no GATE-L1.1] Mapeamento relacional do banco
│   ├── layer2_procedures_source\                                 # [Alimentado no GATE-L1.2] Código-fonte das procedures extraídas via SELECT
│   ├── layer3_people_and_physical\                               # [Alimentado no GATE-L3.1] Grupos de pessoas e estruturas físicas
│   ├── layer3_ubiquitous_external_sources\                       # [Alimentado no GATE-L3.2] Fontes externas de linguagem ubíqua (fora da regra)
│   └── layer4_audit_and_infra\                                   # [Alimentado no GATE-L4.1] Auditoria SQL de regras ativas/inativas e salas/setores
└── output\                                                       # Todos os dados mapeados salvos incrementalmente por camada
    ├── layer1_structural\
    │   ├── helper_extract_relational_schema.sql                  # Query auxiliar para extrair tabelas/FKs do banco
    │   ├── topological_build_order_700_modules.json              # Ordem topológica exata dos 700 módulos e suas bibliotecas
    │   ├── module_dependencies\                                  # 700 arquivos (<modulo>.deps.json)
    │   ├── module_signatures\                                    # 700 arquivos (<modulo>.sigs.jsonl) - Classes e Métodos incrementais
    │   ├── identities_db_relational.jsonl                        # Identidades únicas de banco relacional e relacionamentos multi-fonte
    │   ├── identities_storage_persistent.jsonl                   # Identidades únicas de disco local, rede, pedras, CDs, registry
    │   ├── identities_memory_ram.jsonl                           # Identidades únicas de memória RAM (sem variáveis locais/fields)
    │   ├── identities_external_objects.jsonl                     # Identidades únicas de procedures, functions e packages
    │   └── pending_procedures_extraction.txt                     # Arquivo TXT com SELECT montado para o usuário extrair procedures
    ├── layer2_callflow\
    │   ├── procedure_internal_flows.jsonl                        # Fluxos internos das procedures fornecidas no GATE-L1.2
    │   ├── project_micro_aggregates\                             # 700 arquivos (<modulo>.flow.jsonl) - 1 pequeno agregado por projeto
    │   ├── caller_scoped_aggregates.jsonl                        # Chamadas agregadas pela identidade única da fonte chamadora
    │   ├── storage_entrypoints_dml_catalog.jsonl                 # Pontos iniciais de armazenamento classificados (INSERT/UPDATE/DELETE)
    │   ├── preconditions_and_impediments_catalog.jsonl           # Pré-condições detalhadas, contabilizadas e anuladoras/impeditivas
    │   ├── ideal_execution_order_graph.json                      # Ordem de execução ideal calculada via impedimentos e mutações
    │   └── end_to_end_flows.jsonl                                # Fluxos ponta a ponta (UI -> BO -> DAO -> Procedure -> DB/Disco)
    ├── layer3_techstack_heuristics\
    │   ├── lexical_glossary.json                                 # Glossário de variáveis -> leitura natural contido no mapeamento
    │   ├── ubiquitous_non_business_glossary.json                 # Glossário de linguagem ubíqua (is_business_rule_participant: false)
    │   ├── imperative_programming_mapping.jsonl                  # Símbolos e jargões de código descrevendo a programação imperativa
    │   ├── queries_people_groups_and_physical_structures.sql     # Consultas geradas pela IA para o GATE-L3.1
    │   ├── people_groups_and_physical_structures.jsonl           # Grupos de pessoas e estruturas físicas vinculadas às regras
    │   ├── projection_1_screen_flows.jsonl                       # [Teste Socrático 1] Fluxo de Telas
    │   ├── projection_2_application_isolation.jsonl              # [Teste Socrático 2] Isolamento de Aplicações
    │   ├── projection_3_domain_isolation.jsonl                   # [Teste Socrático 3] Isolamento de Domínio
    │   └── projection_4_screen_isolation.jsonl                   # [Teste Socrático 4] Isolamento de Telas (Componentes + Fluxo Humano)
    └── layer4_graphics\
        ├── audit_active_inactive_rules_and_infra.sql             # Consultas geradas pela IA para o GATE-L4.1
        ├── business_rules_activity_registry.json                 # Regras discriminadas: ACTIVE, LOW_UTILIZATION, INACTIVE
        ├── chart1_domain_identities_preconditions_apps.json      # Dados e visualizações do [Gráfico 1]
        ├── chart2_physical_infrastructure_rooms_sectors_people.json # Dados e visualizações do [Gráfico 2]
        └── chart3_sectors_people_groups_system_parts_org_structure.json # Dados e visualizações do [Gráfico 3]
```

---

## 2. Plano de Execução Sequencial no Padrão `[Incremental Build Model]`

### FASE 1 — Execução do Nível 1 (`Structural Comprehension`)

#### Passo 1.0 — Identificação da Aplicação e Pasta Raiz do Monolito
- **Gate do `[Incremental Build Model]` (`GATE-L1.0`):**
  > **`{ perguntar ao usuário o nome da aplicação em que o código mapeado faz parte e confirmar a pasta raiz contendo os 700 módulos }`**
  - **Ação de Parada:** Se `config/application_manifest.json` não existir, a execução **para** e solicita ao usuário o nome da aplicação e o caminho da pasta raiz.
  - **Continuidade:** Uma vez fornecido, cria a identidade única da pasta raiz (`urn:famema:<APP>:src-root:monolith-root:<PASTA_RAIZ>`) e indexa as 700 subpastas de projetos.

#### Passo 1.1 — Solicitação e Mapeamento Relacional do Banco de Dados
- **Gate do `[Incremental Build Model]` (`GATE-L1.1`):**
  > **`{ forneça o mapeamento relacional do banco de dados }`**
  - **Ação Antes da Parada:** A IA gera `output/layer1_structural/helper_extract_relational_schema.sql` com os `SELECTs` de tabelas, colunas e constraints `PK`/`FK`.
  - **Ação de Parada:** A execução **para** e solicita ao usuário que forneça o mapeamento relacional do banco de dados em `input/layer1_relational_schema/`.
  - **Continuidade Incremental:** Com os dados fornecidos, o motor cria as identidades únicas de banco relacional (`urn:...:db-rel:...`), garantindo que nunca sejam confundidas com nenhuma outra identidade e mapeando os relacionamentos de tabelas para reutilização multi-fonte.

#### Passo 1.2 — Identificação Prévia de Bibliotecas C# e Ordenação Topológica dos 700 Módulos
- Antes de ler o código `.cs`, o motor analisa os 700 arquivos `.csproj` / `packages.config`:
  1. Cria as identidades de todas as bibliotecas externas e referências entre projetos (`libraries_and_dependencies_graph.json`).
  2. Calcula a ordem topológica de compilação e dependência dos 700 módulos em 4 Ondas:
     - **Onda 1 (Folhas — Contratos e Infraestrutura):** Projetos `*-classes`, `*-dto`, `*-infra`.
     - **Onda 2 (Persistência):** Projetos `*-dao`.
     - **Onda 3 (Regras de Negócio):** Projetos `*-bo`, `*-services`.
     - **Onda 4 (Interface de Usuário e Fronteira):** Projetos `*-forms`, `*-web`, executáveis `.exe`.

#### Passo 1.3 — Mapeamento Incremental de Assinaturas C# e Dispositivos de Armazenamento (Em Lotes de 50 Módulos)
- Percorre os 700 módulos na ordem topológica (Onda 1 $\rightarrow$ Onda 4):
  1. **Memória RAM (Com Filtro Estrito e Contrato Agnóstico de Linguagem):**
     - Mapeia primeiro toda a assinatura de código C#, gerando identidades únicas e distintas para **Classes (`mem-ram:code-class`)**, **Assinaturas de Métodos (`mem-ram:code-method-sig`)**, **Contratos DTO (`mem-ram:dto-contract`)** e **Caches/Sessões Temporárias (`mem-ram:static-cache` / `user-session`)**.
     - **Descarta imediatamente variáveis de classe e variáveis de métodos**, garantindo que o metadado seja enxuto e nunca fique maior que o código-fonte.
     - Grava `signature_hash` e `body_hash` em `config/incremental_build_state.json` para que execuções futuras processem apenas arquivos modificados.
  2. **Armazenamento Persistente em Disco e Outras Mídias (`storage-persist`):**
     - Mapeia todas as formas de persistência física encontradas no código: arquivos do computador local (`local-disk`), pastas de rede (`network-share`), mídias ópticas (`optical-cd-dvd` — CDs/DVDs), dispositivos removíveis/impressoras (`removable-hardware`), registros físicos imutáveis (`archival-immutable` — pedras/arquivo físico) e `win-registry`.
  3. **Objetos Externos (`ext-obj`) e Consolidação de Unicidade:**
     - Cataloga todas as procedures, functions e packages chamadas pelos 700 módulos.
     - Executa a deduplicação global garantindo que **o Nível 1 contenha apenas informações únicas para todas as informações somadas**.

#### Passo 1.4 — Separação das Procedures em Arquivo TXT com `SELECT` Montado
- Gera o arquivo `C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural\pending_procedures_extraction.txt` com todas as procedures mapeadas e o comando `SELECT` montado sobre `ALL_SOURCE` / `DBMS_METADATA`.
- **Gate do `[Incremental Build Model]` (`GATE-L1.2`):**
  > **`{ as condições como procedures mapeadas devem ter o código-fonte fornecido antes de iniciar a etapa de Call Flow: execute o SELECT do arquivo pending_procedures_extraction.txt e forneça os dados em input/layer2_procedures_source/ }`**
  - **Ação de Parada:** A execução **para** ao final do Nível 1 e aguarda a alimentação do código-fonte das procedures pelo usuário.

---

### FASE 2 — Execução do Nível 2 (`Call Flow Comprehension`)

*(Iniciada somente após o usuário fornecer os dados do `{ GATE-L1.2 }`)*

#### Passo 2.1 — Mapeamento Interno das Procedures e Classificação de Pontos Iniciais de Armazenamento (`INSERT`, `UPDATE`, `DELETE`)
- Analisa o código-fonte das procedures fornecidas no `GATE-L1.2` e as classes `DAO` mapeadas no Nível 1.
- Classifica todos os **pontos iniciais para os dispositivos de armazenamento** mapeados no Nível 1 (`db-rel` e `storage-persist`), rotulando explicitamente cada operação como **`INSERT`**, **`UPDATE`**, **`DELETE`**, **`MERGE`** ou **`SELECT`** (`storage_entrypoints_dml_catalog.jsonl`) para facilitar o isolamento do domínio no Nível 3.

#### Passo 2.2 — Criação Incremental de Pequenos Agregados de Call Flow (Um Único Projeto por Vez)
- Lê **um único projeto por vez** dentre os 700 módulos, seguindo a ordem topológica:
  1. Para cada método do projeto, cria uma estrutura que **agrega as chamadas onde sua identidade única é a mesma da fonte que a chamou (`Caller-Scoped Aggregate`)**.
  2. Identifica e contabiliza **quantas transformações de dados** (`T01` a `T09`) existem em cada parte do fluxo.
  3. Identifica, detalha e contabiliza todas as **pré-condições** presentes naquele método, classificando quais delas **anulam ou impedem as partes subsequentes de dar continuidade**.
  4. Salva o pequeno agregado do projeto em `output/layer2_callflow/project_micro_aggregates/<modulo>.flow.jsonl`.

#### Passo 2.3 — Costura do Fluxo Ponta a Ponta e Cálculo da Ordem de Execução Ideal
- Une os 700 pequenos agregados com os fluxos das procedures desde o **Início na UI do Sistema (`FlowOrigin`)** até o **Fim nos Dispositivos de Armazenamento (`FlowTerminus`)**:
  1. Lista todas as identidades únicas (Nível 1) que fazem parte de cada fluxo ponta a ponta.
  2. Contabiliza o total acumulado de transformações de dados e o total de pré-condições necessárias para que um dado percorra todo o fluxo de execução.
  3. Cruza as **pré-condições impeditivas/anuladoras** com os fluxos que executam `INSERT/UPDATE/DELETE` para gerar o grafo da **Ordem de Execução Ideal das etapas seguintes (`ideal_execution_order_graph.json`)**.

---

### FASE 3 — Execução do Nível 3 (`Tech Stack / Client Heuristics`)

#### Passo 3.1 — Mapeamento da Tech Stack, Glossário de Variáveis, Programação Imperativa e Telas
1. **Aplicações, Artefatos e Tech Stack:** Agrupa os 700 módulos por aplicação, principais artefatos (`.exe`, `.dll`), nomes de arquivos e camada da Tech Stack.
2. **Glossário Contido no Mapeamento (`lexical_glossary.json`):** Extrai e armazena todos os nomes de variáveis e símbolos que se assemelham a palavras humanas para traduzir as chamadas para leitura natural, agregando as palavras comuns à identidade única de onde foram mapeadas.
3. **Mapeamento da Programação Imperativa (`imperative_programming_mapping.jsonl`):** Traduz os símbolos e jargões de código (`if/return`, loops, transações, mutações de DTO, binds SQL) em uma descrição estruturada da programação imperativa.
4. **Isolamento em "Telas" e Fluxo Humano:** Isola cada tela da UI, mapeando todos os seus componentes visuais, quais Call Flows são utilizados por cada componente e o fluxo passo a passo que um **ser humano** precisa realizar na tela para executar um Call Flow.
5. **Heurísticas Cross-Application:** Identifica abstrações que fazem parte da mesma heurística de negócio mesmo em aplicações diferentes.

#### Passo 3.2 — Coleta Assistida de Grupos de Pessoas e Estruturas Físicas
- A IA analisa as tabelas de controle de acesso, profissionais, centros de custo e infraestrutura identificadas no código e gera o arquivo `output/layer3_techstack_heuristics/queries_people_groups_and_physical_structures.sql`.
- **Gate do `[Incremental Build Model]` (`GATE-L3.1`):**
  > **`{ identificar consultas na aplicação que sejam capazes de mapear e identificar grupos de pessoas que utilizam cada regra de negócio, quais estruturas físicas podem ser identificadas através das informações existentes e solicitar ao usuário que as forneça; aqui a IA ajuda o usuário fornecendo as consultas que devem ser executadas para que os dados sejam propriamente utilizados }`**
  - **Ação de Parada:** A execução **para** e aguarda que o usuário execute as consultas geradas pela IA e salve os resultados em `input/layer3_people_and_physical/`.

#### Passo 3.3 — Enriquecimento do Glossário com Linguagem Ubíqua Não-Participante da Regra de Negócio
- **Gate do `[Incremental Build Model]` (`GATE-L3.2`):**
  > **`{ fornecer dados que enriqueçam o glossário mas que não façam parte da regra de negócio; solicite fonte de informações correlacionadas que não fazem parte da regra de negócio mapeado no código; essas informações precisam estar fortemente identificadas como não participantes da regra de negócio mas devem enriquecer a resposta através da identificação da linguagem ubíqua de seus usuários }`**
  - **Ação de Parada:** A execução **para** e solicita ao usuário fontes correlacionadas de vocabulário dos usuários (manuais, POPs, termos hospitalares cotidianos) em `input/layer3_ubiquitous_external_sources/`.
  - **Continuidade:** Os dados fornecidos são indexados em `ubiquitous_non_business_glossary.json` com a marcação estrita `"is_business_rule_participant": false`.

#### Passo 3.4 — Consolidação do Teste Socrático (4 Mapeamentos Independentes de Mesmo Nível) e Motor de Prompt
- Em vez de criar um único nível inflado, o Nível 3 consolida os **4 mapeamentos independentes de mesmo nível** que funcionam juntos via `URN`:
  1. **`Fluxo de Telas`** (`projection_1_screen_flows.jsonl`)
  2. **`Isolamento de Aplicações`** (`projection_2_application_isolation.jsonl`)
  3. **`Isolamento de Domínio`** (`projection_3_domain_isolation.jsonl`)
  4. **`Isolamento de Telas`** (`projection_4_screen_isolation.jsonl`)
- Habilita o **Motor de Resolução de Prompt (Linguagem Ubíqua + Nome de Tela)** para responder a consultas do usuário explicando todas as etapas que compõem o fluxo daquela tela.

---

### FASE 4 — Execução do Nível 4 (`Gráficos`)

#### Passo 4.1 — Geração das Consultas SQL de Inatividade/Baixa Utilização e Infraestrutura Organizacional
- A IA analisa os domínios, tabelas `INSERT/UPDATE/DELETE` e pré-condições de parâmetros e gera o script `output/layer4_graphics/audit_active_inactive_rules_and_infra.sql`.
- **Gate do `[Incremental Build Model]` (`GATE-L4.1`):**
  > **`{ condição para todos os gráficos: executar as consultas identificadas pela IA para solicitar os dados que discriminem quais regras de negócio estão ativas, com baixa utilização ou inativas, e fornecer os dados de infraestrutura física da empresa (salas, setores e estrutura organizacional) em input/layer4_audit_and_infra/ }`**
  - **Ação de Parada:** A execução **para** e aguarda os dados de auditoria de atividade das regras e infraestrutura física.

#### Passo 4.2 — Processamento da Atividade das Regras e Geração dos Gráficos 1, 2 e 3
1. **Discriminação Obrigatória de Atividade:** Classifica cada regra de negócio nos domínios como `ACTIVE`, `LOW_UTILIZATION`, `INACTIVE_BY_DB_STATE` ou `INACTIVE_DEAD_CODE`.
2. **Geração do `[Gráfico 1]` (`chart1_domain_identities_preconditions_apps.json`):**
   - Calcula o peso e classificação de cada domínio pela soma: $|\text{Identidades de Estrutura (Nível 1)}| + |\text{Pré-Condições (Nível 2)}|$;
   - Rotula sobre o **Glossário (Nível 3)**;
   - Identifica onde faz parte de cada aplicação, quantas aplicações estão envolvidas e discrimina regras ativas vs. baixa utilização/inativas.
3. **Geração do `[Gráfico 2]` (`chart2_physical_infrastructure_rooms_sectors_people.json`):**
   - Mapeia cada **Sala ou Parte da Infraestrutura Física** $\rightarrow$ **Quais Setores atuam nela** $\rightarrow$ **Cada Pessoa** $\rightarrow$ **Regra de Negócio e Domínio utilizados por cada pessoa** (com status de atividade).
4. **Geração do `[Gráfico 3]` (`chart3_sectors_people_groups_system_parts_org_structure.json`):**
   - Mapeia **Setores e Grupos de Pessoas** $\rightarrow$ **Partes do Negócio que utilizam** $\rightarrow$ **Partes do Sistema que são acessadas por cada grupo de pessoas (Aplicações, Módulos, Telas)** $\rightarrow$ **Partes Físicas da Estrutura Organizacional em que elas participam**.
