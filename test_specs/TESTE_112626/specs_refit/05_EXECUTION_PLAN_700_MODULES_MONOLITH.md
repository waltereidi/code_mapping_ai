# Spec 05 (Refit) — Plano de Execução Ordenado de Baixo Custo Computacional para Monolito de ~700 Módulos

**Diretório das Specs Refit:** `./specs_refit/`  
**Diretório Base Autocontido:** `./` (`C:\Users\walte\OneDrive\Documentos\metadados_famema2.11`)  
**Modelo de Execução:** `[Incremental Build Model]` + `Input-First Direct Validation` + **`[Deterministic Engine-0 + Sequential Micro-SLM]`**

---

## 1. Arquitetura de Diretórios e Novos Artefatos de Economia de Tokens

Mantém 100% da estrutura de `./input/`, `./output/` e `./config/` da versão `2.11`, adicionando apenas 2 arquivos leves de controle em `./config/` para habilitar economia extrema de tokens e execução em modelos pequenos:

```text
./ (metadados_famema2.11)
├── specs/                                       # Especificações originais v2.11
├── specs_refit/                                 # Especificações otimizadas v2.11-refit (00 a 06)
├── config/
│   ├── application_manifest.json                # Aplicações, pasta raiz e catálogo de projetos/shards
│   ├── input_folders_manifest.json              # Contratos formais das subpastas de ./input/
│   ├── input_validation_report.json             # Relatório automático de validate_inputs.py
│   ├── incremental_build_state.json             # Hashes SHA-256 (signature_hash, body_hash) e checkpoints
│   ├── urn_symbol_table.json                    # [NOVO] Tabela bijetiva @Xnnnn <-> URN 7 níveis (economia de ~65% tokens)
│   └── semantic_cache.jsonl                     # [NOVO] Cache SHA-256 de radicais léxicos e esqueletos já inferidos
├── scripts/
│   ├── validate_inputs.py                       # Validador direto das pastas ./input/ (0 tokens)
│   └── search_metadata.js                       # Utilitário local de consulta rápida
├── input/                                       # Insumos concentrados e validados diretamente
└── output/                                      # Saídas canônicas idênticas (L1 -> L2 -> L3 -> L4)
```

---

## 2. Pipeline Operacional Passo a Passo (`Máximo Determinismo, Mínimo Token`)

### FASE 0 — Validação Direta Unificada (`0 Tokens`, < 2 segundos)
1. Executar `python ./scripts/validate_inputs.py`.
2. Verificar `./config/input_validation_report.json`: todas as pastas com `VALIDATED_FROM_INPUT` avançam automaticamente sem parada humana.

---

### FASE 1 — Execução 100% Determinística do Nível 1 (`Engine-0`, `0 Tokens`, ~1–3 minutos em CPU)
1. **Passo 1.0 & 1.1 (`Contexto + Banco Relacional`):**
   - Lê `./config/application_manifest.json` e `./input/layer1_application_context/`, reconcilia pastas espelho e gera `application_context.json`.
   - Lê `./input/layer1_relational_schema/` (`ALL_TABLES*`, `*FK*`), gera `helper_extract_relational_schema.sql` por template e grava `identities_db_relational.jsonl`.
2. **Passo 1.2 (`DAG de Bibliotecas e 4 Ondas Topológicas`):**
   - Faz parse XML dos ~700 `.csproj`/`.sln`/`packages.config`, gera `libraries_and_dependencies_graph.json`, `module_dependencies/<modulo>.deps.json` e ordena `topological_build_order_700_modules.json` (`Onda 1: DTO/Infra` $\rightarrow$ `Onda 2: DAO` $\rightarrow$ `Onda 3: BO/Services` $\rightarrow$ `Onda 4: Forms/Web`).
3. **Passo 1.3 (`Assinaturas C#, Memória RAM Filtrada, Persistência Física e Staging Léxico`):**
   - Em lotes de 50 módulos na ordem das Ondas, verifica `signature_hash` e `body_hash` em `./config/incremental_build_state.json` (pulando arquivos inalterados).
   - Extrai via AST `module_signatures/<modulo>.sigs.jsonl` e consolida `identities_memory_ram.jsonl` (**descartando 100% de variáveis locais e fields de classe**), `identities_storage_persistent.jsonl` e `identities_external_objects.jsonl`.
   - Simultaneamente grava `lexical_stems_staging.json` (radicais brutos de variáveis) e popula `./config/urn_symbol_table.json` (`@T0001`, `@M0001`, `@S0001`, `@P0001`).
4. **Passo 1.4 (`Delta de Procedures`):**
   - Cruza `identities_external_objects.jsonl` com `./input/layer2_procedures_source/` e grava `pending_procedures_extraction.txt`.

---

### FASE 2 — Execução Híbrida do Nível 2 (`Engine-0 CFG/SQLGlot` + `SLM-Code 3B–7B Residual`)
1. **Passo 2.1 (`Procedures e Pontos Iniciais DML`):**
   - `Engine-0` faz parse de `./input/layer2_procedures_source/` via `sqlglot`/PLSQL gerando `procedure_internal_flows.jsonl` e `storage_entrypoints_dml_catalog.jsonl` (`INSERT`, `UPDATE`, `DELETE`, `MERGE`, `SELECT`, `DISK_*`).
   - **Fila de Exceção (`dynamic_sql_queue.jsonl`):** Apenas trechos com SQL dinâmico não resolvido estaticamente são enfileirados.
2. **Passo 2.2 (`Despacho em Lote para SLM-Code` — se `dynamic_sql_queue` > 0):**
   - Carrega `SLM-Code` (ex.: `Qwen2.5-Coder-3B/7B`, contexto `4096`, gramática GBNF JSON), resolve toda a fila de uma vez usando aliases `@Xnnnn` e descarrega o modelo (`keep_alive=0` no modo Multi-SLM).
3. **Passo 2.3 (`Micro-Agregados 1 Projeto por Vez + Costura Ponta a Ponta` — `0 Tokens`):**
   - `Engine-0` percorre Onda 1 $\rightarrow$ Onda 4 gerando `project_micro_aggregates/<modulo>.flow.jsonl` (`CallerScopedAggregate` + contagem AST `T01`..`T09` + pré-condições `HARD_ANNULMENT_*`, `BRANCH_EXCLUSION_MUTUAL`, `EMPTY_DATASET_STARVATION`, `CROSS_FLOW_STATE_GATE`).
   - Executa algoritmo de Tarjan + Kahn para gerar `ideal_execution_order_graph.json`, `caller_scoped_aggregates.jsonl`, `preconditions_and_impediments_catalog.jsonl` e `end_to_end_flows.jsonl`, reexpandindo todos os `@Xnnnn` para URNs completos de 7 níveis.

---

### FASE 3 — Execução do Nível 3 (`FullUIExtractor` + `SLM-Embed` + `SLM-Lexicon 3B–8B`)
1. **Passo 3.1 (`Extração Determinística de UI e Imperativo` — `0 Tokens`):**
   - `Engine-0` executa `FullUIExtractor` (multi-encoding `utf-8`..`cp1252` + achatamento recursivo de `UserControl`s) gerando os esqueletos completos das telas, `per_project/<modulo>.l3.json`, `imperative_programming_mapping.jsonl` e `projection_2_application_isolation.jsonl`.
   - Consolida `people_groups_and_physical_structures.jsonl` a partir de `./input/layer3_people_and_physical/` e grava `queries_people_groups_and_physical_structures.sql` e `request_ubiquitous_non_business_sources.json`.
2. **Passo 3.2 (`Alinhamento Vetorial Ubíquo e Cross-App` — `SLM-Embed` ~300–600 MB):**
   - Carrega modelo leve de embeddings (`bge-m3` ou `nomic-embed-text-v1.5`) + BM25 para parear termos externos de `./input/layer3_ubiquitous_external_sources/` com telas e radicais técnicos, e agrupar clusters `CrossAppBusinessHeuristic`. Descarrega `SLM-Embed`.
3. **Passo 3.3 (`Tradução em Lote de Radicais e Síntese de Esqueletos` — `SLM-Lexicon 3B–8B`):**
   - Carrega `SLM-Lexicon` (contexto `4096`–`8192`, gramática GBNF JSON, consultando `./config/semantic_cache.jsonl` antes de cada chamada):
     1. Traduz os ~1.500–3.000 radicais únicos em lotes de 30 itens $\rightarrow$ `Engine-0` monta `lexical_glossary.json` com todos os URNs originais.
     2. Refina descrições curtas de `ubiquitous_non_business_glossary.json` $\rightarrow$ `Engine-0` injeta `"is_business_rule_participant": false` em 100% dos registros.
     3. Sintetiza rótulos de domínio e `HumanInteractionJourney` a partir de esqueletos `< 450 tokens` $\rightarrow$ `Engine-0` reexpande URNs e grava `projection_1_screen_flows.jsonl`, `projection_3_domain_isolation.jsonl` e `projection_4_screen_isolation.jsonl`.
   - Descarrega `SLM-Lexicon`.

---

### FASE 4 — Execução Determinística do Nível 4 e Portão de Verificação Final (`0 Tokens`)
1. **Passo 4.1 (`Auditoria e Gráficos 1, 2 e 3`):**
   - `Engine-0` gera `audit_active_inactive_rules_and_infra.sql` (acionando `SLM-SQL` apenas se houver colunas não-padrão), lê `./input/layer4_audit_and_infra/` e gera `business_rules_activity_registry.json`.
   - Calcula exatamente $\text{domain\_score} = |I_{L1}| + |P_{L2}|$ e renderiza `chart1`, `chart2` e `chart3` (`.json` e `.html`).
2. **Passo 4.2 (`Portão Determinístico de Paridade` — `verify_all.py`):**
   - Executa `verify_all.py`: verifica cobertura de 100% dos projetos, 0 URNs fora do padrão de 7 níveis (`8+ tokens`), 100% de deduplicação, 0 variáveis locais/fields em `mem-ram`, presença de `T01`..`T09`, `"is_business_rule_participant": false` em 100% do glossário ubíquo e exatidão aritmética do Gráfico 1.
   - Qualquer registro que falhe no schema é reparado deterministicamente ou reenviado em micro-prompt pontual (`max_retries = 2` + template determinístico de fallback), garantindo **taxa de sucesso de 100%**.
