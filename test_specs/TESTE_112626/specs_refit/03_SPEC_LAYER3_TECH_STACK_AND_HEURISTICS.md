# Spec 03 (Refit) — Nível 3: Tech Stack & Client Heuristics com Deduplicação Morfológica, Embeddings Locais e Teste Socrático Econômico

**Nível na Hierarquia:** `3 de 4` (Estritamente dependente dos **Níveis 1 e 2**; pré-requisito obrigatório para o **Nível 4**)  
**Pasta de Saída:** `./output/layer3_techstack_heuristics/`  
**Pastas `./input/` Validadas Diretamente:**
- `./input/layer3_people_and_physical/`
- `./input/layer3_ubiquitous_external_sources/`
- `./input/consolidated_metadata_sources/` *(para enriquecimento determinístico de títulos de telas, menus e busca rápida)*

**Divisão Computacional:** **`~75% Determinístico (FullUIExtractor + Mapa Imperativo + Clusterização Jaccard — 0 Tokens)`** + **`~25% Micro-SLM Léxico/Embeddings (3B–8B + bge-m3/nomic)`** sobre radicais deduplicados e esqueletos comprimidos (`< 500 tokens`).

---

## 1. Como o Nível 3 Reduz 97%+ dos Tokens Mantendo 100% da Qualidade Semântica

O Nível 3 concentra as tarefas mais ricas em linguagem natural (glossário de variáveis, telas, linguagem ubíqua e 4 projeções Socráticas). Para que modelos locais pequenos (3B a 14B) gerem o mesmo resultado de um modelo 70B+ sem estourar contexto:

1. **Extração 100% Determinística de UI (`FullUIExtractor` — `0 Tokens`):** Nunca se envia um arquivo `.Designer.cs` ou `.aspx` para a LLM extrair botões ou inputs. Um parser determinístico multi-encoding extrai 100% dos controles, rótulos, grids, eventos e `UserControl`s aninhados.
2. **Mapeamento Imperativo 100% Determinístico (`0 Tokens`):** As 7 categorias imperativas são geradas diretamente dos nós da AST/CFG do Nível 2 por templates canônicos.
3. **Deduplicação Morfológica em Lote (`Unique-Stem Batching` — `T-OPT-03`):**
   - O `Engine-0` remove prefixos técnicos/húngaros (`txt`, `lue`, `gv`, `btn`, `lbl`, `chk`, `dt`, `flg`, `seq`, `cod`, `nom`, `vlr`, `qtd`, `obj`, `lst`, `p_`, `v_`) e agrupa ~500.000 ocorrências de variáveis nos **~1.500 a 3.000 radicais compostos únicos** do domínio hospitalar (ex.: `prog_sala_prof`, `agenda_restrita`, `nro_faa`).
   - A `SLM-Lexicon` (3B–8B) recebe lotes JSON de **30 radicais únicos por chamada** (`~450 tokens in` $\rightarrow$ `~350 tokens out` sob gramática GBNF) para gerar o termo canônico em português natural.
   - Em seguida, o `Engine-0` re-hidrata deterministicamente todas as `source_identities_urn` de cada radical a partir do índice `lexical_stems_staging.json` colhido no Nível 1!
4. **Alinhamento Ubíquo via Embeddings Locais + BM25 (`T-OPT-07`):**
   - Em vez de colocar centenas de páginas de POPs e chamados GLPI no prompt da LLM, um modelo leve de embeddings (`BAAI/bge-m3` ou `nomic-embed-text-v1.5`, < 600 MB) + BM25 pareia cada expressão ubíqua aos Top-3 itens do `lexical_glossary.json` e `projection_4_screen_isolation.jsonl`, cabendo à SLM apenas confirmar/refinar o rótulo em micro-lotes.
5. **Síntese de Jornadas Humanas por Esqueleto (`Micro-Slice Skeletons` — `T-OPT-04`):**
   - Para descrever o fluxo humano de uma tela (`HumanInteractionJourney`), a SLM recebe apenas um resumo JSON de `< 450 tokens` (título da tela, inputs ordenados por `TabIndex`, botões com aliases de Call Flow `@Fnn` e pré-condições impeditivas), gerando descrições limpas sem risco de truncamento.

---

## 2. PARTE 1 — Tech Stack, Glossário Léxico, Heurísticas Cross-App e `FullUIExtractor`

### 2.1. Aplicações, Artefatos e Tech Stack (`0 Tokens`)
Classificação determinística por tipo de projeto/extensão/herança base:
- `TECH_UI_WINFORMS_DEVEXPRESS` (`Form`, `XtraForm`, `NTIForm`, `UserControl`, `GridView`, `BarManager`)
- `TECH_UI_WEB_ASPNET` (`Page`, `MasterPage`, `Controller`, `ApiController`, `.aspx`, `.cshtml`)
- `TECH_BUSINESS_IMPERATIVE_BO` (projetos `*-bo`, `*-services`, validadores)
- `TECH_DATA_ACCESS_DAO_ORACLE` (projetos `*-dao`, `BDOracle`, `OracleCommand`, `TableAdapter`)
- `TECH_MEMORY_CONTRACTS_DTO` (`*-classes`, `*-dto`, `StaticCache`, `Session`)
- `TECH_RDBMS_ORACLE_PLSQL` (`db-rel`, `ext-obj`)
- `TECH_PERSISTENT_MEDIA_IO` (`storage-persist`).

Grava também os artefatos por projeto `./output/layer3_techstack_heuristics/per_project/<modulo>.l3.json` exigidos pelo verificador de cobertura.

### 2.2. Glossário Léxico (`lexical_glossary.json`)
Gerado pela combinação `Decompositor Morfológico Determinístico` + `Lotes de 30 Radicais na SLM-Lexicon` + `Re-hidratação de URNs no Engine-0`:
- Campos obrigatórios por entrada: `glossary_entry_id`, `canonical_business_term`, `captured_variable_names[]`, `natural_language_reading_template`, `source_identities_urn[]` (URNs de 7 níveis reais), `"is_business_rule_participant": true`.

### 2.3. Heurísticas de Negócio Cross-Application (`CrossAppBusinessHeuristic`)
1. **Clusterização Determinística Inicial (`0 Tokens`):** Constrói um grafo bipartido conectando Call Flows de aplicações diferentes que tocam as mesmas tabelas `db-rel` (especialmente via `INSERT`/`UPDATE`/`DELETE`), chamam as mesmas procedures `ext-obj`, avaliam o mesmo `CA.PARAMETRO` ou possuem similaridade de Jaccard $\ge 0,45$ nos radicais do Glossário.
2. **Rotulagem Concisa (`SLM-Lexicon`):** Cada cluster conectado recebe um micro-prompt (`< 300 tokens`) apenas para sintetizar o título canônico do domínio/heurística compartilhada.

### 2.4. Extrator Completo e Determinístico de Interface (`FullUIExtractor` — `0 Tokens`)
1. **Leitura Multi-Arquivo e Multi-Encoding Obrigatória:**
   - Lê conjuntamente `<Tela>.cs`, `<Tela>.Designer.cs`, `<Tela>.resx` e arquivos Web (`.aspx`, `.ascx`, `.master`, `.cshtml`).
   - Cadeia determinística de encoding: `utf-8-sig` $\rightarrow$ `utf-8` $\rightarrow$ `utf-16` $\rightarrow$ `cp1252` $\rightarrow$ `latin-1` (nunca descarta `.Designer.cs` legado em CP1252/Latin-1).
2. **Resolução dos 4 Nomes da Tela (`ScreenNamingResolution`):**
   - `screen_code`, `designer_display_title`, `functional_screen_name` (cruzado com `./input/layer1_application_context/screens_catalog.csv` e `./input/consolidated_metadata_sources/`) e `hierarchical_menu_path`.
3. **Inventário de 100% dos Componentes (`screen_components`):**
   - Categorias obrigatórias: `BUTTON_ACTION`, `INPUT_FIELD` (com pareamento geométrico/léxico `lbl*` $\rightarrow$ `associated_label_text`), `DATA_GRID_AND_COLUMNS`, `LABEL_AND_STATIC`, `NAVIGATION_AND_CONTAINER` e `EMBEDDED_USER_CONTROL`.
4. **Achatamento Recursivo de `UserControl`s e Guarda Anti-Zero:**
   - Promove recursivamente os controles de `UserControl`s filhos para `effective_components_count` da tela hospedeira e dispara `UI_EXTRACTION_INCOMPLETE` caso exista `InitializeComponent()`/`.aspx` com `0` controles extraídos.

---

## 3. PARTE 2 — Validação Direta `./input/`, Programação Imperativa e Teste Socrático

### 3.1. Grupos de Pessoas e Estruturas Físicas (`VAL-L3.1`)
- O `Engine-0` gera `./output/layer3_techstack_heuristics/queries_people_groups_and_physical_structures.sql` via templates SQL parametrizados sobre as tabelas de acesso/lotação/infraestrutura mapeadas no Nível 1 (`CA.*`, `PESSOA.*`, `INFRA_ESTRUTURA.*`). *(Caso o schema possua tabelas customizadas fora do padrão, aciona `SLM-SQL` com `< 500 tokens` contendo apenas os nomes das tabelas candidatas).*
- Valida diretamente `./input/layer3_people_and_physical/` e consolida `people_groups_and_physical_structures.jsonl` com **0 tokens**.

### 3.2. Linguagem Ubíqua Externa Fora da Regra de Negócio (`VAL-L3.2`)
- Gera deterministicamente o manifesto `./output/layer3_techstack_heuristics/request_ubiquitous_non_business_sources.json`.
- Valida diretamente `./input/layer3_ubiquitous_external_sources/` (chamados GLPI, POPs, manuais, specs correlacionadas).
- Extrai termos recorrentes via TF-IDF/BM25 + embeddings locais (`SLM-Embed`), vincula-os às telas e ao glossário técnico e **força em código Python** (nunca dependendo da obediência do modelo!) as travas imutáveis em 100% dos itens de `ubiquitous_non_business_glossary.json`:
  - `"is_business_rule_participant": false`
  - `"origin_classification": "EXTERNAL_CORRELATED_UBIQUITOUS_LANGUAGE"`
  - `"rule_contamination_guard": "STRICTLY_EXCLUDED_FROM_LOGIC_AND_SCORE"`

### 3.3. Mapeamento da Programação Imperativa (`imperative_programming_mapping.jsonl` — `0 Tokens`)
Gerado por tradução direta AST $\rightarrow$ taxonomia imperativa:
- `IMPERATIVE_BRANCH_GUARD`, `IMPERATIVE_ITERATION_LOOP`, `IMPERATIVE_TRANSACTION_BOUNDARY`, `IMPERATIVE_EXCEPTION_INTERCEPTION`, `IMPERATIVE_STATE_MUTATION`, `IMPERATIVE_IO_DISPATCH`, `IMPERATIVE_EVENT_CALLBACK`.

### 3.4. Teste Socrático: 4 Projeções Independentes de Mesmo Nível
Construídas por projeção relacional sobre os catálogos L1 + L2 + Glossário (com micro-síntese textual de `SLM-Lexicon` apenas nos resumos humanos, usando aliases `@Xnnnn` reexpandidos para URNs canônicos):
1. **`projection_1_screen_flows.jsonl` (`Fluxo de Telas`):** Grafo de navegação `Form.Show`/`ShowDialog`/`Response.Redirect` ordenado por `ideal_execution_order_graph.json` do Nível 2.
2. **`projection_2_application_isolation.jsonl` (`Isolamento de Aplicações` — `100% Determinístico`):** Escopo de módulos, `.exe`/`.dll`, arquivos e fronteiras por aplicação.
3. **`projection_3_domain_isolation.jsonl` (`Isolamento de Domínio`):** Clusters de regras de negócio, `StorageEntrypoints` (`INSERT`/`UPDATE`/`DELETE`), pré-condições e heurísticas cross-app.
4. **`projection_4_screen_isolation.jsonl` (`Isolamento de Telas`):** Ficha completa de cada tela (4 nomes, `buttons[]`, `inputs[]`, `grids[]`, `embedded_user_controls[]`, `HumanInteractionJourney` e URNs dos Call Flows por controle).

---

## 4. Motor de Resolução de Prompt de Baixo Consumo (`Graph-RAG Determinístico + SLM-Lexicon`)

Quando o usuário consulta em **linguagem ubíqua + nome/código de tela** (ex.: *"como funciona a liberação de sala cirúrgica na DECI0009?"*):
1. **Busca Exata + Vetorial (`0 LLM Tokens`, < 50 ms):**
   - Localiza a ficha da tela em `projection_4_screen_isolation.jsonl` (e `./input/consolidated_metadata_sources/spec17_clean/`).
   - Cruza os termos do prompt via BM25 + `SLM-Embed` contra `ubiquitous_non_business_glossary.json` (`is_business_rule_participant: false`) e `lexical_glossary.json` para selecionar apenas o(s) Call Flow(s) pertinente(s) do Nível 2.
2. **Síntese Enriquecida em Contexto Curto (`< 2.000 tokens`):**
   - Entrega à SLM local (`3B–14B`) **somente** a sub-árvore JSON exata daquela tela + Call Flow + pré-condições + DML, permitindo que mesmo um modelo pequeno gere uma narrativa hospitalar rica, fiel à ordem causal e 100% ancorada nos identificadores reais.

---

## 5. Artefatos Salvos pelo Nível 3 (`./output/layer3_techstack_heuristics/`)

1. `per_project/<modulo>.l3.json`
2. `lexical_glossary.json`
3. `request_ubiquitous_non_business_sources.json`
4. `ubiquitous_non_business_glossary.json` *(100% com `"is_business_rule_participant": false`)*
5. `imperative_programming_mapping.jsonl`
6. `queries_people_groups_and_physical_structures.sql`
7. `people_groups_and_physical_structures.jsonl`
8. `projection_1_screen_flows.jsonl`
9. `projection_2_application_isolation.jsonl`
10. `projection_3_domain_isolation.jsonl`
11. `projection_4_screen_isolation.jsonl`
