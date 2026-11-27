# Spec 01 (Refit) — Nível 1: Structural Comprehension com Automação 100% Determinística (`0 LLM Tokens`)

**Nível na Hierarquia:** `1 de 4` (Camada Fundacional — Pré-requisito obrigatório para os Níveis 2, 3 e 4)  
**Pasta de Saída:** `./output/layer1_structural/`  
**Pastas `./input/` Pré-Criadas e Validadas Diretamente:**
- `./input/layer1_application_context/`
- `./input/layer1_relational_schema/`
- `./input/layer1_persistent_storage/`
- `./input/layer2_procedures_source/` *(para cálculo determinístico de cobertura e delta de procedures)*

**Custo de Tokens de IA neste Nível:** **`0 tokens` (100% executado pelo `Engine-0` determinístico em Python/AST/XML/SQL).**  
**Regra de Ouro do Nível 1:** *Todo o mapeamento neste nível deve conter apenas informações únicas (100% deduplicadas) para todas as informações somadas, sob URN Canônico de 7 Níveis (`8+ segmentos separados por ':'`).*

---

## 1. Por Que o Nível 1 Deve Ter Consumo Zero de LLM (`Zero-Token Design`)

No mapeamento tradicional por LLM, pedir a um modelo de linguagem para ler 700 projetos C# apenas para listar classes, métodos, tabelas e dependências consome dezenas de milhões de tokens e introduz erros de formatação em URNs. No `v2.11-refit`, **nenhum token de LLM é gasto no Nível 1**:

| Tarefa do Nível 1 | Ferramenta Determinística (`Engine-0`) | Vantagem Técnica sobre LLM |
| :--- | :--- | :--- |
| Validação de `./input/` (`VAL-L1.0`, `VAL-L1.1`, `VAL-L1.2`) | `./scripts/validate_inputs.py` (Python `csv` / `json`) | Validação instantânea em milissegundos, 100% reprodutível. |
| Dependências `.sln` / `.csproj` / `packages.config` | `xml.etree.ElementTree` + Ordenação Topológica de Kahn | Grafo exato das 4 Ondas de compilação sem risco de omissão. |
| Assinaturas C# / VB.NET (`code-class`, `code-method-sig`, `dto-contract`) | `tree-sitter-c-sharp` (ou Roslyn CLI / parser léxico balanceado com fallback de encoding) | Extrai 100% das assinaturas e descarta 100% de variáveis locais e fields privados por regra sintática exata. |
| Tabelas, PKs, FKs e Joins implícitos (`db-rel`) | Parser CSV sobre `./input/layer1_relational_schema/` + `sqlglot` / regex SQL sobre DAOs | Unicidade matemática por chave `(OWNER, TABLE_NAME)` e grafo multi-fonte completo. |
| Persistência física (`storage-persist`: disco, rede, CDs, pedras, hardware, registry) | Scanner determinístico de APIs I/O guiado por `./input/layer1_persistent_storage/persistent_storage_patterns.json` | Detecta todos os acessos `System.IO`, UNC, `Registry`, portas `COM/LPT` e referências de mídia óptica/física. |
| Extração de Procedures (`ext-obj`) e `pending_procedures_extraction.txt` | Scanner de `CommandType.StoredProcedure` / `CALL` / `EXEC` + `set.difference()` contra `ALL_SOURCE*.csv` | Monta automaticamente o `SELECT` em `ALL_SOURCE` apenas para o delta real ausente. |

---

## 2. Validação Direta das Pastas `./input/` no Nível 1

### 2.1. Contexto da Aplicação e Pasta Raiz (`VAL-L1.0`)
- Valida diretamente `./config/application_manifest.json` e `./input/layer1_application_context/` (`projects_catalog.json`, `screens_catalog.csv`).
- **Reconciliação Determinística de Espelhos:** Pastas sufixadas com backup/cópia (ex.: `pep-forms_`, `*-old`, `*-bkp`) são filtradas por heurística determinística de nome + comparação de árvore de arquivos, impedindo duplicação de identidades `src-root`.
- Somente se `./config/application_manifest.json` estiver ausente e não puder ser derivado de `./input/layer1_application_context/` o motor emite parada formal `{ GATE-L1.0 }`.

### 2.2. Mapeamento Relacional do Banco de Dados (`VAL-L1.1`)
- Valida diretamente `./input/layer1_relational_schema/` (`ALL_TABLES*.csv`, `*FK*.csv`).
- Mantém `./output/layer1_structural/helper_extract_relational_schema.sql` gerado a partir de template SQL estático (zero LLM) contendo `SELECT` sobre `ALL_TABLES`, `ALL_TAB_COLUMNS`, `ALL_CONSTRAINTS` e `ALL_CONS_COLUMNS`.

### 2.3. Cruzamento Direto de Procedures (`VAL-L1.2`)
- Ao concluir a varredura dos módulos, cruza o conjunto deduplicado `ext-obj` contra `./input/layer2_procedures_source/` (`ALL_SOURCE*.csv`, `procedures_source.json`, `*.sql`).
- Gera deterministicamente `./output/layer1_structural/pending_procedures_extraction.txt` contendo:
  1. Estatística de cobertura (`SOURCE_AVAILABLE_IN_INPUT` vs. `MISSING_DELTA`);
  2. Query `SELECT OWNER, NAME, TYPE, LINE, TEXT FROM ALL_SOURCE WHERE (UPPER(OWNER), UPPER(NAME)) IN (...)` populada via template Python.

---

## 3. Contrato Canônico de Identidade Única (`7-Level URN`) + Tabela de Internação Simbólica (`T-OPT-02`)

### 3.1. Estrutura Canônica Obrigatória (`8+ tokens separados por ':'`)
Toda entidade mapeada no Nível 1 recebe um URN estrito validado por regex antes de ser gravado em disco:

```text
urn:famema:<APP>:<origin_plane>:<storage_or_runtime_subtype>:<root_or_schema_scope>:<entity_kind>:<canonical_unique_identifier>
```

| Plano (`<origin_plane>`) | Subtipos Permitidos (`<subtype>`) | Formato Canônico (`8+ segmentos`) |
| :--- | :--- | :--- |
| **`db-rel`** | `oracle`, `sqlserver`, `postgres`, `sqlite` | `urn:famema:<APP>:db-rel:oracle:<SCHEMA>:table:<TABLE_NAME>`<br>`urn:famema:<APP>:db-rel:oracle:<SCHEMA>:column:<TABLE_NAME>.<COL>`<br>`urn:famema:<APP>:db-rel:oracle:<SCHEMA>:fk:<CONSTRAINT_NAME>` |
| **`storage-persist`** | `local-disk`, `network-share`, `optical-cd-dvd`, `removable-hardware`, `archival-immutable`, `win-registry` | `urn:famema:<APP>:storage-persist:local-disk:<ROOT_ALIAS>:file:<NORM_PATH>`<br>`urn:famema:<APP>:storage-persist:optical-cd-dvd:<MEDIA_ID>:volume:<SPEC>`<br>`urn:famema:<APP>:storage-persist:archival-immutable:<MEDIA_ID>:artifact:<SPEC>` |
| **`mem-ram`** | **`code-class`**, **`code-method-sig`**, **`dto-contract`**, **`static-cache`**, **`user-session`**, **`shared-buffer`** | `urn:famema:<APP>:mem-ram:code-class:<MODULE>:<NAMESPACE>.<CLASS>`<br>`urn:famema:<APP>:mem-ram:code-method-sig:<MODULE>:<CLASS>.<METHOD>(<PARAMS>):<RET>`<br>`urn:famema:<APP>:mem-ram:dto-contract:<MODULE>:<NAMESPACE>.<DTO>` |
| **`src-root`** | `monolith-root`, `module-dir`, `source-file`, `lib-dependency` | `urn:famema:<APP>:src-root:monolith-root:<SCOPE>:root:<ROOT_NAME>`<br>`urn:famema:<APP>:src-root:module-dir:<SCOPE>:module:<MODULE>`<br>`urn:famema:<APP>:src-root:source-file:<MODULE>:file:<REL_PATH>` |
| **`ext-obj`** | `db-procedure`, `db-function`, `db-package`, `external-api` | `urn:famema:<APP>:ext-obj:db-procedure:<SCHEMA>:procedure:<PROC_NAME>`<br>`urn:famema:<APP>:ext-obj:db-function:<SCHEMA>:function:<FUNC_NAME>`<br>`urn:famema:<APP>:ext-obj:db-package:<SCHEMA>:package:<PKG>.<MEMBER>` |

### 3.2. Geração Simultânea da Tabela de Internação Simbólica (`./config/urn_symbol_table.json`)
Para economizar ~65% de tokens nos Níveis 2 e 3 e impedir que SLMs pequenos errem a sintaxe de URNs longos, o Nível 1 gera automaticamente um dicionário bijetivo determinístico:
- Prefixo por plano + inteiro sequencial base-36/decimal:
  - `@T0001` $\leftrightarrow$ `urn:famema:SIHOSP:db-rel:oracle:SIHOSP:table:PROG_SALA_PROFISSIONAL`
  - `@M0042` $\leftrightarrow$ `urn:famema:SIHOSP:mem-ram:code-method-sig:demanda-cirurgia-bo:BODemandaCirurgica.Salvar(DemandaDTO):Int64`
  - `@P0007` $\leftrightarrow$ `urn:famema:SIHOSP:ext-obj:db-procedure:SIHOSP:procedure:PRC_GRAVA_DEMANDA_CIRURGICA`
  - `@S0019` $\leftrightarrow$ `urn:famema:SIHOSP:mem-ram:code-class:demanda-cirurgia-forms:DECI0009`
- **Regra Inegociável:** Nos arquivos finais em `./output/`, **100% dos registros são salvos com o URN completo de 7 níveis**; os aliases `@Xnnnn` existem exclusivamente no trânsito interno entre o `Engine-0` e os micro-prompts de SLMs!

---

## 4. Regras Determinísticas de Extração por Domínio Estrutural

### 4.1. Banco Relacional (`db-rel`)
Cada registro em `identities_db_relational.jsonl` é construído por junção exata entre os CSVs de `./input/layer1_relational_schema/` e as referências SQL extraídas dos módulos:
- `persisted_and_reusable: true` (constante estrutural obrigatória);
- `multi_source_utilization`: lista deduplicada de URNs (`mem-ram:code-class`, `mem-ram:code-method-sig`, `ext-obj`) que referenciam a tabela;
- `relationships`: união de FKs explícitas do dicionário de dados + joins SQL (`JOIN <TAB> ON A.COL = B.COL`) extraídos via `sqlglot`/regex.

### 4.2. Armazenamento Persistente em Disco e Outras Mídias (`storage-persist`)
Classificado por tabela determinística de assinaturas de código C#/PLSQL:
- `local-disk`: `System.IO.File`, `StreamWriter`, `StreamReader`, `FileInfo`, extensões `.ini`, `.xml`, `.json`, `.csv`, `.pdf`, `.rpt`, `ConfigurationManager`, `SQLiteConnection`, `OleDbConnection` (`.mdb`/`.accdb`).
- `network-share`: literais UNC `\\<host>\<share>` ou drives mapeados configurados.
- `optical-cd-dvd`: APIs `IMAPI2`, gravadores ópticos, diretórios/volumes DICOM/ISO/CD/DVD.
- `removable-hardware`: `System.IO.Ports.SerialPort` (`COM1`..`COM9`), `LPT1`, `X509Store` / SmartCard / Token A3 (`Crypt32`), impressoras térmicas ZPL/EPL.
- `archival-immutable` (*pedras / arquivo físico / papel / mídia imutável*): referências a envelopes físicos, caixas de prontuário/microfilme, protocolos impressos assinados e retenção WORM.
- `win-registry`: `Microsoft.Win32.Registry`, `RegistryKey`, `HKEY_LOCAL_MACHINE`, `HKEY_CURRENT_USER`.

### 4.3. Filtro Anti-Explosão de Memória RAM (`mem-ram`) e Coleta Lateral de Radicais
1. **Filtro Estrito na AST:**
   - Nós `ClassDeclaration`, `InterfaceDeclaration`, `StructDeclaration`, `EnumDeclaration` $\rightarrow$ `code-class` (ou `dto-contract` quando o projeto for `*-classes`/`*-dto` ou classe contiver apenas propriedades públicas de transporte).
   - Nós `MethodDeclaration`, `ConstructorDeclaration` $\rightarrow$ `code-method-sig` com `signature_hash` (SHA-256 da assinatura normalizada) e `body_hash` (SHA-256 do corpo sem espaços/comentários).
   - Nós `FieldDeclaration` com modificador `static` do tipo coleção/cache ou acessos `HttpContext.Current.Session["..."]` / `MemoryCache` $\rightarrow$ `static-cache` / `user-session`.
   - **Bloqueio Determinístico (`FORBIDDEN_MEM_RAM_SUBTYPES`):** Nós `LocalDeclarationStatement`, `VariableDeclarator` locais e `FieldDeclaration` de instância são **descartados em código** — é estruturalmente impossível gerar URNs de variáveis locais ou fields.
2. **Coleta Lateral Zero-Custo para o Nível 3 (`raw_lexical_tokens_index`):**
   - Durante a mesma passagem única de AST (sem ler o arquivo duas vezes!), os identificadores de variáveis descartadas são decompostos morfologicamente e incrementados em um contador compacto em disco (`./output/layer1_structural/lexical_stems_staging.json`) vinculado ao alias `@Mnnnn` do método, economizando uma nova varredura de 700 módulos no Nível 3.

---

## 5. Artefatos Salvos pelo Nível 1 (`./output/layer1_structural/`)

Todos 100% deduplicados por URN e gerados com **zero tokens de IA**:
1. `application_context.json`
2. `helper_extract_relational_schema.sql`
3. `libraries_and_dependencies_graph.json`
4. `topological_build_order_700_modules.json`
5. `module_dependencies/<modulo>.deps.json`
6. `module_signatures/<modulo>.sigs.jsonl`
7. `identities_db_relational.jsonl`
8. `identities_storage_persistent.jsonl`
9. `identities_memory_ram.jsonl` *(e alias compatível `identities_memory_signatures.jsonl` se requerido)*
10. `identities_external_objects.jsonl`
11. `pending_procedures_extraction.txt`
