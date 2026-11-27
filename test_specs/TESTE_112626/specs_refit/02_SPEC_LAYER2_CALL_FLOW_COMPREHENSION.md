# Spec 02 (Refit) — Nível 2: Call Flow Comprehension via `AST/CFG Determinístico` + `Micro-SLM Residual`

**Nível na Hierarquia:** `2 de 4` (Estritamente dependente do **Nível 1**; pré-requisito obrigatório para os Níveis 3 e 4)  
**Pasta de Saída:** `./output/layer2_callflow/`  
**Pasta `./input/` Validada Diretamente:** `./input/layer2_procedures_source/`  
**Divisão Computacional:** **`~92%–95% Determinístico (Engine-0 AST/CFG/SQLGlot — 0 Tokens)`** + **`~5%–8% Micro-SLM Code (3B–7B)`** apenas para SQL dinâmico complexo e expressões ambíguas.

---

## 1. Estratégia de Redução Drástica de Tokens no Nível 2

Em vez de pedir a uma LLM para rastrear chamadas método a método em 700 módulos:
1. **Resolução Estática de Chamadas (`0 Tokens`):** Usando a tabela de `using` por arquivo + o catálogo `identities_memory_ram.jsonl` gerados no Nível 1, o `Engine-0` resolve `objeto.Metodo(...)` e `ClasseEstatica.Metodo(...)` diretamente para o URN canônico do método alvo.
2. **Parser SQL/PLSQL Determinístico (`0 Tokens`):** `sqlglot` + analisador de blocos PL/SQL decompõem `ALL_SOURCE*.csv` e strings SQL estáticas do C# para classificar `INSERT`, `UPDATE`, `DELETE`, `MERGE` e `SELECT`.
3. **Quando a SLM Local É Acionada (`Micro-SLM Fallback < 400 tokens`):**
   - **Caso 1 (SQL Dinâmico Concatenado / `EXECUTE IMMEDIATE`):** Quando o C# monta SQL via `StringBuilder` condicional complexo ou PL/SQL usa `EXECUTE IMMEDIATE v_sql` onde o parser estático não identifica a tabela/operação com 100% de certeza.
   - **Caso 2 (Tradução Semântica Curta de Pré-Condições Complexas):** Quando uma expressão booleana encadeada precisa de rótulo funcional legível para enriquecer o catálogo de pré-condições.
   - **Formato do Micro-Prompt (`GBNF JSON` + Aliases `@Xnnnn`):** Entrada máxima de `350 tokens` (apenas o trecho de 10–25 linhas do método) $\rightarrow$ saída JSON estrita de `60 tokens`: `{"dml":"UPDATE","tables":["PACIENTE"],"cond":"FLG_ATIVO=='S'"}`.

---

## 2. Validação Direta de `./input/layer2_procedures_source/` (`VAL-L1.2`)

1. O `Engine-0` valida `./input/layer2_procedures_source/` (`ALL_SOURCE*.csv`, `procedures_source.json`, dumps `.sql`).
2. Reconstrói em memória o código-fonte de cada `OWNER.NAME` ordenando por `LINE` e executa a decomposição AST/PLSQL gerando `procedure_internal_flows.jsonl`.
3. Procedures chamadas no C# mas ausentes em `./input/` recebem marcação determinística `EXTERNAL_PROC_BLACKBOX_PENDING` em `./config/input_validation_report.json`, sem interromper nem perder o mapeamento dos demais fluxos.

---

## 3. Regras Determinísticas para Fronteiras, DML e `Caller-Scoped Aggregate`

### 3.1. Detecção Automática de `FlowOrigin` (UI/Gatilhos) e `FlowTerminus` (Armazenamento)
- **`FlowOrigin`:** Detectado na AST por handlers conectados em `.Designer.cs` / `.aspx` (`+= new EventHandler(...)`, `Click`, `DoubleClick`, `Load`, `Shown`, `EditValueChanged`, `FocusedRowChanged`, `SelectedIndexChanged`, `Validating`, `KeyDown`, `Page_Load`, `[HttpPost]`, `[HttpGet]`, `Timer_Tick`, `DoWork`).
- **`FlowTerminus`:** Qualquer nó folha que atinja `db-rel` (via DAO ou `ext-obj`), `storage-persist` (disco, rede, CD/DVD, hardware, pedras/arquivo físico, registry) ou atualização terminal de `mem-ram` (`static-cache`, `user-session`, `DataSource` de UI).

### 3.2. Classificação Determinística de Pontos Iniciais de Armazenamento (`StorageEntrypoint`)
Grava em `storage_entrypoints_dml_catalog.jsonl` o primeiro método/procedure que abre transação ou executa comando sobre o dispositivo do Nível 1:

| Plano | Operação (`dml_operation_classification`) | Regra de Detecção Estática no `Engine-0` | Papel no Domínio (`domain_ownership_role`) |
| :--- | :--- | :--- | :--- |
| `db-rel` | **`INSERT`** | AST SQL `exp.Insert` ou regex `\bINSERT\s+INTO\s+<TAB>` | `PRIMARY_STATE_CREATOR` |
| `db-rel` | **`UPDATE`** | AST SQL `exp.Update` ou regex `\bUPDATE\s+<TAB>\s+SET\b` | `STATE_LIFECYCLE_MUTATOR` |
| `db-rel` | **`DELETE`** | AST SQL `exp.Delete` ou regex `\bDELETE\s+FROM\s+<TAB>` | `PHYSICAL_STATE_REMOVER` |
| `db-rel` | **`MERGE` / `UPSERT`** | AST SQL `exp.Merge` | `HYBRID_STATE_SYNCHRONIZER` |
| `db-rel` | **`SELECT`** | AST SQL `exp.Select` sem DML envolvente | `STATE_CONSUMER_OR_GUARD` |
| `storage-persist` | **`DISK_INSERT` / `DISK_UPDATE` / `DISK_DELETE` / `DISK_READ`** | Mapeamento direto da API C# (`File.Create`/`WriteAll*` $\rightarrow$ `DISK_INSERT`; `AppendAll*` $\rightarrow$ `DISK_UPDATE`; `File.Delete` $\rightarrow$ `DISK_DELETE`; `ReadAll*`/`OpenRead` $\rightarrow$ `DISK_READ`) | Operação persistente em mídia física/disco |

> **Rastreamento Indireto Obrigatório:** O `Engine-0` propaga transitivamente as operações DML de classes `DAO*`, `TableAdapter`, `DataAdapter` e procedures `ext-obj` até os métodos `BO*` e telas WinForms/Web chamadoras, garantindo que telas como `SMOV5020` reflitam todas as mutações reais (`INSERT`/`UPDATE`/`DELETE`) executadas pelas camadas inferiores.

### 3.3. Agregação Escopada pela Fonte Chamadora (`CallerScopedAggregate`)
- Construída deterministicamente por travessia em árvore a partir de cada método chamador: `aggregate_identity_urn == caller_source_identity_urn`.
- Processada **1 projeto por vez** na ordem topológica das 4 Ondas (`Onda 1 -> Onda 4`), salvando `./output/layer2_callflow/project_micro_aggregates/<modulo>.flow.jsonl` com consumo de RAM constante (`O(1)` em relação ao tamanho do monolito).

---

## 4. Tabela de Regras AST para Contabilização de Transformações (`T01` a `T09` — `0 Tokens`)

O `Engine-0` contabiliza deterministicamente as transformações de dados em cada método/procedure sem depender de LLM:

| Código | Padrão Sintático Detectado na AST (C# / VB.NET / PL-SQL) |
| :--- | :--- |
| **`T01_UI_EXTRACT_PARSE`** | Leitura de `.Text`, `.EditValue`, `.SelectedValue`, `.Checked`, `.Value` combinada com `Convert.To*`, `*.Parse`, `TryParse` ou atribuição a DTO. |
| **`T02_OBJECT_MAPPING`** | Instanciação `new OutroDTO { ... }` ou cópia de >= 2 propriedades entre tipos DTO/Model distintos. |
| **`T03_IN_MEMORY_COMPUTATION`** | Expressões aritméticas/agregações, cadeias LINQ (`.Where`, `.Select`, `.Sum`, `.GroupBy`), `String.Format` / interpolação de negócio. |
| **`T04_DB_PARAMETER_BINDING`** | `cmd.Parameters.Add*`, `OracleParameter`, `:param` / `@param` alimentado a partir de variável/DTO. |
| **`T05_DB_DML_TRANSFORMATION`** | Funções SQL em colunas de `INSERT`/`UPDATE`/`SELECT` (`NVL`, `COALESCE`, `DECODE`, `CASE`, `TO_DATE`, `TO_CHAR`, `SYSDATE`, `.NEXTVAL`). |
| **`T06_RESULTSET_MATERIALIZATION`** | `ExecuteReader()`, `DataAdapter.Fill(ds)`, `ExecuteDataTable()`, `OPEN cursor FOR SELECT`. |
| **`T07_HYDRATION_TO_DTO`** | Laço `while (dr.Read())` ou `foreach (DataRow row in ...)` instanciando e populando objetos/listas DTO. |
| **`T08_UI_RENDER_BINDING`** | Atribuição a `.DataSource = ...`, `.DataBind()`, preenchimento de controles visuais ou `MessageBox.Show` / `XtraMessageBox`. |
| **`T09_PERSISTENT_MEDIA_SERIALIZATION`** | `XmlSerializer`, `JsonConvert` / `JsonSerializer`, `CsvWriter`, `ExportToPdf`, escrita/leitura de `FileStream` / `Registry` / porta serial. |

---

## 5. Detecção Determinística de Pré-Condições Impeditivas e Ordem Ideal de Execução

### 5.1. Extração via Grafo de Fluxo de Controle (`CFG`)
Cada nó condicional (`if`, `switch`, `guard`, filtro `WHERE` de vigência/status, consulta a `CA.PARAMETRO` ou `RAISE_APPLICATION_ERROR`) recebe ID `<URN_METODO>#PC<NNN>` e é classificado automaticamente pela estrutura do bloco consequente na AST:

1. **`HARD_ANNULMENT_EARLY_RETURN`:** Bloco `if (cond)` contém `return;` (ou `return false/null;`) antes das chamadas `BO`/`DAO` subsequentes $\rightarrow$ anula todos os passos seguintes `[step_i+1 .. step_n]`.
2. **`HARD_ANNULMENT_EXCEPTION_ROLLBACK`:** Bloco contém `throw new ...` ou PL/SQL `RAISE` / `RAISE_APPLICATION_ERROR` ou `Rollback()` $\rightarrow$ aborta o fluxo e desfaz DMLs da transação.
3. **`BRANCH_EXCLUSION_MUTUAL`:** Estrutura `if (cond) { CallA(); } else { CallB(); }` com chamadas disjuntas a métodos/fluxos distintos.
4. **`EMPTY_DATASET_STARVATION`:** Query `SELECT` com predicado restritivo (`FLG_ATIVO = 'S'`, `DAT_HORA_FIM IS NULL`, `STATUS = ...`) cujo resultado alimenta diretamente um `if (lista.Count == 0) return;` ou `foreach` subsequente.
5. **`CROSS_FLOW_STATE_GATE`:** Detectado automaticamente por **cruzamento grafo-relacional**:
   - Se a pré-condição $PC_x$ no Fluxo $F_B$ faz `SELECT` exigindo coluna/estado $(T.\text{col} = v)$ na tabela $T$, e o Fluxo $F_A$ possui `StorageEntrypoint` classificado como `INSERT` ou `UPDATE` sobre a mesma tabela $T$ gravando $T.\text{col}$, o `Engine-0` cria automaticamente a aresta de precedência:
     $$F_A \ (\text{Produtor via INSERT/UPDATE}) \prec_{\text{ideal}} F_B \ (\text{Guardião da Pré-Condição } PC_x)$$

### 5.2. Cálculo Determinístico de `ideal_execution_order_graph.json`
- Executado via ** Condensação de Componentes Fortemente Conexos de Tarjan + Ordenação Topológica de Kahn** (`networkx` / Python puro, **0 tokens**), atribuindo `topological_flow_rank`, `prerequisite_flows` e `unlocks_downstream_flows` para alimentar diretamente o Nível 3.

---

## 6. Artefatos Salvos pelo Nível 2 (`./output/layer2_callflow/`)

Todos gravados com **URNs completos de 7 níveis** (reexpandidos a partir da tabela de aliases antes da escrita em disco):
1. `procedure_internal_flows.jsonl`
2. `project_micro_aggregates/<modulo>.flow.jsonl`
3. `caller_scoped_aggregates.jsonl`
4. `storage_entrypoints_dml_catalog.jsonl`
5. `preconditions_and_impediments_catalog.jsonl`
6. `ideal_execution_order_graph.json`
7. `end_to_end_flows.jsonl`
