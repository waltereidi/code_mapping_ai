# Spec 04 (Refit) — Nível 4: Gráficos e Inteligência Analítica com Cálculo 100% Determinístico (`Zero Alucinação Numérica`)

**Nível na Hierarquia:** `4 de 4` (Estritamente dependente dos **Níveis 1, 2 e 3**)  
**Pasta de Saída:** `./output/layer4_graphics/`  
**Pasta `./input/` Validada Diretamente:** `./input/layer4_audit_and_infra/`  
**Divisão Computacional:** **`95%–100% Determinístico (Engine-0 SQL Template Generator + Python Graph/Math Engine + HTML Template Renderer)`**; uso opcional de `SLM-SQL` (`3B–7B`, `< 1.500 tokens` totais) **apenas** se houver tabelas de auditoria fora do padrão nominal.

---

## 1. Regra de Ouro do Refit no Nível 4: `Modelos Pequenos Nunca Fazem Contas`

Em LLMs compactas (3B a 8B), erros de soma ou omissão de itens em listas longas são comuns quando os gráficos são gerados diretamente por texto livre da IA. No `v2.11-refit`:
- **Toda contagem de identidades $\left|I_{\text{Estrutura}}(D)\right|$, toda soma de pré-condições $\left|P_{\text{CallFlow}}(D)\right|$, toda classificação de atividade e toda montagem de grafos JSON e visualizações `.html` são executadas 100% em Python determinístico (`Engine-0`).**
- Isso garante **precisão matemática absoluta (`score == structural_identities_count + preconditions_count` em 100% dos domínios)** independentemente do tamanho do modelo local utilizado nas camadas anteriores.

---

## 2. Validação Direta (`VAL-L4.1`), Geração de SQL de Auditoria e Classificação de Atividade

### 2.1. Geração Baseada em Templates de `audit_active_inactive_rules_and_infra.sql`
O `Engine-0` inspeciona automaticamente:
1. Todos os literais de parâmetros capturados nas pré-condições `PRE_DB_PARAMETER` do Nível 2 $\rightarrow$ injeta na cláusula `WHERE UPPER(NOM_PARAMETRO) IN (...)` sobre `CA.PARAMETRO`;
2. Todas as tabelas alvo de `INSERT`/`UPDATE` em `storage_entrypoints_dml_catalog.jsonl` e suas colunas de data/vigência (`DAT_*`, `FLG_ATIVO`, `STATUS*` vindas do Nível 1) $\rightarrow$ gera os blocos `SELECT COUNT(*), SUM(...), MAX(...)` para auditoria de movimentação recente.
3. *(Opcional — `SLM-SQL` 3B–7B):* Acionada somente se uma tabela de negócio não possuir coluna óbvia de data/status por heurística léxica, recebendo apenas a lista de colunas da tabela (`< 150 tokens`) para apontar a coluna de auditoria temporal.

### 2.2. Validação Direta de `./input/layer4_audit_and_infra/` e Árvore de Decisão Determinística
O motor valida diretamente os arquivos em `./input/layer4_audit_and_infra/` e classifica cada regra de negócio em `business_rules_activity_registry.json` através de árvore de decisão determinística:
1. **`INACTIVE_DEAD_CODE`:** Regra/fluxo sem nenhum `FlowOrigin` alcançável na camada de UI/Serviços ou explicitamente marcada como descontinuada/migrada no catálogo de telas/auditoria.
2. **`INACTIVE_BY_DB_STATE`:** Possui `FlowOrigin` no código, mas uma pré-condição impeditiva `PRE_DB_PARAMETER` está desabilitada no banco (`'N'`, `'0'`, `'FALSE'`) ou a tabela habilitadora possui `0` registros vigentes ativos.
3. **`LOW_UTILIZATION`:** Regra habilitada e alcançável, porém com volume operacional abaixo do limiar configurável (ex.: `< 10` movimentações nos últimos 6 meses ou restrita a uso residual nos CSVs de auditoria).
4. **`ACTIVE`:** Regra habilitada, alcançável na UI e com utilização recorrente comprovada.

---

## 3. Computação Determinística dos 3 Gráficos Obrigatórios (`.json` + `.html`)

Todos os 3 gráficos excluem estritamente qualquer entrada com `"is_business_rule_participant": false` do cálculo de escore/regras e discriminam visualmente `ACTIVE`, `LOW_UTILIZATION`, `INACTIVE_BY_DB_STATE` e `INACTIVE_DEAD_CODE`:

### 3.1. `[Gráfico 1]` — `chart1_domain_identities_preconditions_apps.{json,html}`
- **Fonte:** Join exato em Python entre `projection_3_domain_isolation.jsonl`, `lexical_glossary.json`, `projection_2_application_isolation.jsonl` e `business_rules_activity_registry.json`.
- **Fórmula Computada em Python:**
  $$\text{domain\_score}(D) = \text{structural\_identities\_count}(D) + \text{preconditions\_count}(D)$$
  onde `structural_identities_count` é a cardinalidade do `set()` deduplicado de URNs do Nível 1 participantes do domínio, e `preconditions_count` é a cardinalidade do `set()` deduplicado de `precondition_id`s do Nível 2 no domínio.
- **Atributos de Aplicação:** Registra exatamente os módulos/telas onde o domínio atua por aplicação e `applications_involved_count`.

### 3.2. `[Gráfico 2]` — `chart2_physical_infrastructure_rooms_sectors_people.{json,html}`
- **Fonte:** Join relacional determinístico entre `./input/layer3_people_and_physical/`, `./input/layer4_audit_and_infra/`, `people_groups_and_physical_structures.jsonl`, `projection_3_domain_isolation.jsonl` e `business_rules_activity_registry.json`.
- **Topologia em 4 Níveis:** `Sala / Parte Física da Infraestrutura` $\rightarrow$ `Setores Atuantes na Sala` $\rightarrow$ `Pessoas / Profissionais` $\rightarrow$ `Regras de Negócio e Domínios Utilizados (com status ACTIVE / LOW_UTILIZATION / INACTIVE*)`.

### 3.3. `[Gráfico 3]` — `chart3_sectors_people_groups_system_parts_org_structure.{json,html}`
- **Fonte:** Join determinístico entre grupos/setores (`people_groups_and_physical_structures.jsonl`), `projection_2_application_isolation.jsonl`, `projection_4_screen_isolation.jsonl`, `projection_3_domain_isolation.jsonl` e estrutura física organizacional.
- **Topologia Executiva:** `Setores e Grupos de Pessoas` $\leftrightarrow$ `Partes do Negócio Utilizadas (Domínios/Regras com status de atividade)` $\leftrightarrow$ `Partes do Sistema Acessadas (Aplicações, Módulos e Telas)` $\leftrightarrow$ `Partes Físicas da Estrutura Organizacional`.

### 3.4. Renderização HTML Autocontida (`0 Tokens`)
Os arquivos `.html` correspondentes aos 3 gráficos são gerados por um renderizador Python estático com templates HTML5/SVG/Canvas embutidos (offline, sem CDNs bloqueadas e com filtros interativos de status `ACTIVE` / `LOW_UTILIZATION` / `INACTIVE`), custando **zero tokens de LLM**.

---

## 4. Artefatos Salvos pelo Nível 4 (`./output/layer4_graphics/`)

1. `audit_active_inactive_rules_and_infra.sql`
2. `business_rules_activity_registry.json`
3. `chart1_domain_identities_preconditions_apps.json` e `chart1_domain_identities_preconditions_apps.html`
4. `chart2_physical_infrastructure_rooms_sectors_people.json` e `chart2_physical_infrastructure_rooms_sectors_people.html`
5. `chart3_sectors_people_groups_system_parts_org_structure.json` e `chart3_sectors_people_groups_system_parts_org_structure.html`
