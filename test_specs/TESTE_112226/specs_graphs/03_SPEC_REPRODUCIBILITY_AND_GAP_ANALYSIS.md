# 03 — Verificação de Reprodutibilidade das Especificações Atuais e Análise de Lacunas (`Gap Analysis`)

**Objetivo:** Verificar formalmente se as especificações atuais de `C:\Users\walte\OneDrive\Documentos\specs_test_ia1` (`01` a `06`) — e, comparativamente, as especificações do workspace `d:\ia_TESTS\metadados_sihosp\specs` (`01` a `14`) — conseguem reproduzir os **6 Gráficos Canônicos do AWS CardDemo** ([02_CARDDEMO_6_CANONICAL_GRAPHS_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/specs_test_ia1/aws_graphs/02_CARDDEMO_6_CANONICAL_GRAPHS_SPEC.md)), identificando o que já é suportado nativamente e quais contratos precisam ser estendidos.

---

## 1. Matriz de Verificação de Reprodutibilidade por Gráfico

| Gráfico do AWS CardDemo | Cobertura em `specs_test_ia1` (`01..06`) | Cobertura em `metadados_sihosp` (`01..14`) | O que `specs_test_ia1` Já Reproduz Nativamente | O que Falta em `specs_test_ia1` para Reprodução 100% Fiel |
| :--- | :---: | :---: | :--- | :--- |
| **Gráfico 1: `CARDDEMO-DataModel.drawio`** (ER & Topologia VSAM KSDS + AIX + Copybooks) | **75% (Parcial Alta)** | **40% (Baixa)** | - Identidades únicas de armazenamento (`urn:ia1:storage:*`) e contratos de memória (`urn:ia1:mem:contract:*`).<br>- Estrutura de `relationships` (`PK`, `FK`, `cardinality: 1:1 | 1:N | N:1`) já existe para bancos relacionais (`relational_database_identities`). | **[Gap G1] Relacionamentos em Arquivos Indexados (VSAM KSDS + AIX) e Vínculo com Copybook Schema:** No schema `06_DATA_CONTRACTS_AND_SCHEMAS.json`, `persistent_storage_identities` possui apenas `uid`, `medium_category` e `path_or_locator`. Falta permitir `record_schema_contract_uid` (apontando para o Copybook `CV*Y.cpy`), `primary_key`, `alternate_indexes` (`AIX`) e `relationships[]` em arquivos não-relacionais. |
| **Gráfico 2: `Online CICS Screen & COMMAREA Call Flow`** (Transações, BMS, `XCTL`, `DFHCOMMAREA`, Pré-Condições e VSAM) | **85% (Alta)** | **85% (Alta)** | - `FLOW_START` na UI (`COSGN00` / `CC00`) até `FLOW_END` (`STORAGE_SINK`).<br>- `CallerScopedAggregate` mantendo a identidade do método/programa chamador.<br>- Contagem e detalhamento de **Pré-Condições** (`urn:ia1:precond:*`) e **Transformações** (`TX_MAP`, `TX_CALC`).<br>- `DFHCOMMAREA` (`COCOM01Y`) mapeada como `urn:ia1:mem:session:*` / `contract`. | **[Gap G2] Semântica de Transferência CICS (`XCTL` vs `LINK` vs `RETURN TRANSID`):** Em CICS pseudo-conversacional, um programa encerra com `EXEC CICS RETURN TRANSID('CAVW') COMMAREA(...)` e aguarda o input do usuário no terminal 3270 antes de reentrar. Falta um atributo `invocation_semantics` (`XCTL_NO_RETURN`, `PSEUDO_CONVERSATIONAL_RETURN`, `SYNC_CALL`) nos passos de `ordered_calls`. |
| **Gráfico 3: `Batch JCL Pipeline & Dataset/GDG Lineage`** (Jobs JCL, Steps, `SORT`/`IDCAMS`, `FD->DD->DSN` e `INTRDR`) | **45% (Parcial Baixa)** | **15% (Não Reproduz)** | - Mapeia os programas batch (`CB*.cbl`) e seus arquivos de entrada/saída como `STORAGE_SOURCE` e `STORAGE_SINK`.<br>- Contabiliza as pré-condições de `CBTRN02C` e o cálculo de juros (`TX_CALC`) de `CBACT04C`. | **[Gap G3] Orquestração JCL (`Job -> Step -> EXEC PGM`), Utilitários (`SORT`/`IDCAMS`) e Binding Indireto (`FD -> DD -> DSN/GDG`):** O Nível 1 foca em `csharp_code_signature_identities` e não possui entidade para scripts JCL que encadeiam steps e resolvem qual arquivo físico (`DSN` ou geração `GDG +1`) é injetado no nome lógico (`ASSIGN TO <DDNAME>`) do COBOL.<br>**[Gap G4] Ponte Assíncrona Online $\rightarrow$ Batch (`INTRDR`):** `CORPT00C` escreve JCL em `QUEUE('INTRDR')` para disparar `TRANREPT.jcl`. |
| **Gráfico 4: `Static Structural Dependency Matrix`** (`Programs × Copybooks × Subroutines × BMS × JCL`) | **55% (Parcial)** | **50% (Parcial)** | - Mapeia bibliotecas externas/internas (`libraries_manifest`) com `referenced_by_module_uids`.<br>- Mapeia contratos em memória (`ram_memory_contract_identities`). | **[Gap G5] Aresta Explícita de Inclusão Estática de Copybook (`INCLUDES_COPYBOOK`):** No Nível 1 atual, um contrato de memória (`urn:ia1:mem:contract:*`) é referenciado apenas quando aparece na assinatura de parâmetros de um método C#. Em COBOL, Copybooks (`CVACT01Y`, `COCOM01Y`) são incluídos via `COPY` dentro da `WORKING-STORAGE` ou `FILE SECTION` sem aparecerem como argumentos de `CALL`. |
| **Gráfico 5: `Domain Decomposition & Multi-App Coupling`** (AWS Transform Domain View + Hotspots Online/Batch) | **95% (Excelente / Nativo)** | **60% (Parcial)** | - **Reprodução direta e superior pelo Nível 3 e Nível 4:**<br>  1. O Glossário do Nível 3 extrai os termos de negócio das variáveis COBOL;<br>  2. As Heurísticas do Nível 3 unificam programas Online (`CO*`) e Batch (`CB*`) que tocam o mesmo arquivo VSAM raiz (`ACCTDATA`, `TRANSACT`, `CARDXREF`);<br>  3. O Nível 4 calcula $W_D = \|S_D\| + \|P_D\|$ e destaca `involved_applications_count = 2` (`carddemo-cics-online` + `carddemo-batch-jcl`). | **[Gap G6] Ancoragem de Domínio em `persistent_storage_identities`:** A documentação do Nível 3 cita tabelas relacionais (`urn:ia1:db:rel:*`) como âncora primária de persistência compartilhada; basta explicitar que datasets VSAM (`urn:ia1:storage:vsam-ksds:*`) possuem o mesmo peso de âncora primária de persistência compartilhada. |
| **Gráfico 6: `Enriched Knowledge Graph & Radial Capability Map`** (*Martin Fowler / CodeConcise*) | **80% (Alta)** | **95% (Excelente)** | - O Nível 3 gera a tradução automática das chamadas técnicas e pré-condições para **Leitura Natural** usando o Glossário de Variáveis (`NaturalLanguageGlossary`).<br>- O Nível 2 fornece o grafo comportamental enriquecido com contagens de pré-condições e transformações. | **[Gap G7] Topologia Radial Concêntrica em 5 Níveis (`L1..L5`):** O Nível 4 de `specs_test_ia1` especifica 3 gráficos (Mapa de Bolhas com Raias por Aplicação, Matriz Gate Chart de Pré-Condições e Matriz Bipartida Aplicação $\times$ Domínio), mas não inclui o algoritmo de alocação angular radial de 5 anéis presente na `Spec 02` de `metadados_sihosp`. |

---

## 2. Detalhamento das 7 Extensões Estruturais (`G1` a `G7`) para `specs_test_ia1` Reproduzir 100% dos Gráficos

Para que o motor de `specs_test_ia1` reproduza com 100% de precisão todos os 6 gráficos do repositório `aws-mainframe-modernization-carddemo` (sem violar nenhuma regra de dependência estrita `L1 -> L2 -> L3 -> L4`), aplicam-se as seguintes extensões formais:

### 2.1. Extensão `G1` (Nível 1): Suporte a VSAM KSDS, Índices Alternativos (`AIX`), GDGs e Relacionamentos em `persistent_storage_identities`
No Nível 1 ([01_STRUCTURAL_COMPREHENSION_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/specs_test_ia1/01_STRUCTURAL_COMPREHENSION_SPEC.md)), os arquivos de dados estruturados não-relacionais (`VSAM_KSDS`, `VSAM_ESDS`, `VSAM_RRDS`, `GDG_GENERATION_GROUP`, `SEQUENTIAL_DATASET_PS`) passam a suportar:
- `record_schema_contract_uid`: `UID` do Copybook no Nível 1 (`urn:ia1:mem:contract:<app_id>:cpy:<COPYBOOK>`) que descreve o layout físico dos bytes do arquivo.
- `primary_key_field`: Campo chave primária do KSDS (ex.: `ACCT-ID`, `CARD-NUM`, `XREF-CARD-NUM`).
- `alternate_indexes`: Lista de caminhos `AIX` (ex.: `CARDAIX` sobre `CARD-ACCT-ID`, `CXACAIX` sobre `XREF-ACCT-ID`).
- `relationships`: O mesmo contrato de chave estrangeira e cardinalidade (`1:1`, `1:N`, `N:1`) das tabelas relacionais, viabilizando 100% do **Gráfico 1 (`CARDDEMO-DataModel.drawio`)**.

### 2.2. Extensão `G2` (Nível 2): Semântica de Transferência de Controle CICS e Pseudo-Conversação
Em `ordered_calls` do Nível 2 ([02_CALL_FLOW_COMPREHENSION_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/specs_test_ia1/02_CALL_FLOW_COMPREHENSION_SPEC.md)), cada chamada passa a qualificar `invocation_mechanism`:
- `STATIC_OR_DYNAMIC_CALL`: `CALL 'CSUTLDTC' USING ...` (retorna ao chamador).
- `CICS_XCTL_TRANSFER`: `EXEC CICS XCTL PROGRAM(...) COMMAREA(...)` (transfere controle definitivo sem retorno na pilha).
- `CICS_LINK_SUBPROGRAM`: `EXEC CICS LINK PROGRAM(...) COMMAREA(...)` (chama subprograma CICS e retorna).
- `CICS_RETURN_TRANSID`: `EXEC CICS RETURN TRANSID(...) COMMAREA(...)` (encerra a task CICS atual, renderiza o mapa BMS no terminal 3270 e agenda a próxima transação com `DFHCOMMAREA`).

### 2.3. Extensão `G3` (Níveis 1 e 2): Identidades de Orquestração JCL (`Job / Step / DD Binding`) e Utilitários de Sistema
Para reproduzir integralmente o **Gráfico 3 (`Batch JCL Pipeline & Dataset Lineage`)**:
1. **No Nível 1**: Adiciona-se a categoria `batch_orchestration_identities`:
   - `urn:ia1:infra:jcl-job:<app_id>:<job_name>` (ex.: `POSTTRAN`, `INTCALC`, `CREASTMT`, `TRANREPT`).
   - `urn:ia1:infra:jcl-step:<app_id>:<job_name>#<step_name>` apontando para o `executed_program_uid` (programa COBOL `CB*` ou utilitário de sistema `urn:ia1:code:lib:zos-util:SORT | IDCAMS | IEBGENER`).
   - `dd_bindings`: Lista que amarra `dd_name` (ex.: `ACCTFILE`, `TRANFILE`, `DALYREJS`) $\rightarrow$ `dataset_storage_uid` (`urn:ia1:storage:...`) com `access_mode` (`INPUT`, `OUTPUT`, `I-O`, `DISP_NEW_GDG_PLUS_1`).
2. **No Nível 2**: Cada `JCL Job` gera um `CallerScopedAggregate` cuja identidade é `urn:ia1:infra:jcl-job:...` e cujos passos ordenados são os `JCL Steps`, permitindo ao *Linker* costurar automaticamente o JCL ao agregado interno do programa COBOL (`CBTRN02C`, `CBACT04C`, etc.) e resolver os arquivos físicos lidos e gravados.

### 2.4. Extensão `G4` (Nível 2): Ponte Assíncrona Online $\rightarrow$ Batch via Filas (`CICS INTRDR` / MQ)
Quando um programa Online escreve comandos JCL na fila `INTRDR` (`EXEC CICS WRITEQ TD QUEUE('INTRDR')` em `CORPT00C.cbl`):
- O Nível 1 registra a fila como `urn:ia1:mem:stream-buffer:cics:INTRDR`.
- O Nível 2 cria uma aresta `ASYNC_JOB_SUBMISSION` conectando o passo de escrita em `INTRDR` (`CORPT00C`) ao `FLOW_START` do job batch submetido (`urn:ia1:infra:jcl-job:carddemo-batch:TRANREPT`), unindo os grafos Online e Batch em uma única linhagem ponta a ponta.

### 2.5. Extensão `G5` (Nível 1): Vínculo Explícito de Inclusão Estática (`included_copybook_contract_uids`)
Para reproduzir 100% do **Gráfico 4 (`Static Structural Dependency Matrix`)**:
- Em cada identidade de programa/classe (`code_signature_identities`), inclui-se a lista `included_data_contract_uids` contendo os `UIDs` dos Copybooks (`urn:ia1:mem:contract:<app_id>:cpy:<NAME>`) importados via diretiva `COPY`, além do vínculo com o mapa de tela BMS (`bms_screen_contract_uid`).
- O hash de assinatura (`sig_hash`) de um programa COBOL passa a incorporar o `sig_hash` dos Copybooks de interface (`DFHCOMMAREA` / `LINKAGE SECTION`), garantindo que alterações em `COCOM01Y.cpy` invalidem incrementalmente o cache dos programas acoplados.

### 2.6. Extensão `G6` (Nível 3): Persistência VSAM como Âncora Primária de Heurística de Negócio
No Nível 3 ([03_TECH_STACK_AND_HEURISTICS_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/specs_test_ia1/03_TECH_STACK_AND_HEURISTICS_SPEC.md)), a regra de **Convergência por Persistência Compartilhada (Âncora Primária)** passa a aceitar tanto tabelas relacionais (`urn:ia1:db:rel:*`) quanto datasets estruturados compartilhados (`urn:ia1:storage:vsam-ksds:*`), unificando automaticamente os programas Online CICS (`COACTVWC`, `COACTUPC`, `COBIL00C`) e Batch (`CBACT01C`, `CBACT04C`, `CBTRN02C`, `CBSTM03A`) que operam sobre `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS`.

### 2.7. Extensão `G7` (Nível 4): Inclusão da Visão Radial de Capacidades (`Radial Capability Map View`)
No Nível 4 ([04_GRAPHICS_AND_DOMAIN_METRICS_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/specs_test_ia1/04_GRAPHICS_AND_DOMAIN_METRICS_SPEC.md)), além dos 3 gráficos já especificados (Bolhas de Domínio com Raias por Aplicação, Gate Chart de Pré-Condições/Transformações e Matriz Aplicação $\times$ Domínio), adiciona-se opcionalmente o **Gráfico 4.4 (Mapa Radial Hierárquico de Capacidades)** alimentado pelos mesmos `DomainGroups` do Nível 3 e dimensionado pelo score $W_D = |S_D| + |P_D|$.
