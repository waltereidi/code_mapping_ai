# Especificação Técnica — Nível 2: Call Flow Comprehension

> **Nível Hierárquico:** 2 (Depende estritamente do **Nível 1: Structural Comprehension**; pré-requisito obrigatório para os Níveis 3 e 4)
> **Padrão de Execução:** `[Incremental Build Model]`
> **Escopo Alvo:** Rastreamento ponta-a-ponta de fluxo de chamadas e linhagem de dados entre as Identidades Únicas do Nível 1 ao longo dos 700 módulos e Stored Procedures.

---

## 1. Regra de Dependência Hierárquica e Gate de Entrada

> **Invariante do Nível 2:**
> `[Neste nível o mapeamento é referente a uma identidade do nível anterior]`
> O Nível 2 **proíbe** a criação de referências anônimas ou textuais soltas. Todo nó em um Call Flow deve apontar obrigatoriamente para um `UID` válido registrado na Tabela de Símbolos Global do Nível 1 (`id://code/...`, `id://db-rel/...`, `id://db-proc/...`, `id://storage/...`, `id://mem-ram/...`).

### Gate 2.1 — Validação do Código-Fonte das Stored Procedures (Pré-Condição Bloqueante)
```text
{ CONDIÇÃO BLOQUEANTE DE ENTRADA: As condições como procedures mapeadas no Nível 1 DEVEM ter o código-fonte fornecido pelo usuário antes de iniciar esta etapa }
```
* **Comportamento da IA:** Antes de iniciar a montagem de qualquer Call Flow, o motor verifica se o arquivo gerado no Gate 1.3 (`01_procedures_pendentes_extracao.txt`) teve seu retorno alimentado pelo usuário.
* **Ingestão AST de Banco:** Assim que o usuário fornece os fontes SQL das procedures, a IA analisa cada procedure para extrair:
  1. Tabelas lidas (`SELECT / JOIN`) e escritas (`INSERT / UPDATE / DELETE / MERGE`).
  2. Chamadas encadeadas a outras procedures/functions (`EXEC / CALL`).
  3. Pré-condições internas do SQL (`IF EXISTS`, `WHERE`, `RAISERROR / THROW`, `RETURN` antecipado) e transformações de colunas.

---

## 2. Identificação de Início e Fim de uma Chamada de Dados

Todo fluxo de execução ponta-a-ponta ($F$) é delimitado formalmente por um **Ponto de Origem (*Entry Point*)** e um ou mais **Pontos Terminais (*Terminal Sinks*)**:

### 2.1. Pontos de Início (*Entry Points* — `FLOW_START`)
1. **UI do Sistema (`UI_EVENT_ORIGIN`):** Eventos iniciados por interação humana em telas (Cliques de botão, Submissão de formulários, Eventos de Grid, Seleção de Menu em WinForms/WPF/WebForms/MVC/Razor/SPA).
2. **Fronteira de Serviço / API (`API_ENDPOINT_ORIGIN`):** Controllers REST/SOAP/WCF/gRPC expostos externamente.
3. **Gatilhos Assíncronos / Background (`DAEMON_JOB_ORIGIN`):** Timers, Windows Services, Hangfire/Quartz Jobs, FileWatchers ou consumidores de filas.
4. **Ponto Inicial de Leitura de Armazenamento (`STORAGE_SOURCE_ORIGIN`):** Dispositivos de armazenamento mapeados no Nível 1 que atuam como fonte primária de alimentação de dados (`READ`/`SELECT`) no início de um pipeline.

### 2.2. Pontos de Fim (*Terminal Sinks* — `FLOW_END`)
1. **Mutação Persistente em Banco (`DB_MUTATION_SINK`):** Comandos finais `INSERT`, `UPDATE`, `DELETE` em tabelas `id://db-rel/...` (diretamente via C# ou dentro de `id://db-proc/...`).
2. **Escrita Persistente em Disco/Mídia (`STORAGE_WRITE_SINK`):** Gravação em arquivos locais, compartilhamentos de rede ou mídias externas `id://storage/...`.
3. **Retorno de Apresentação para UI (`UI_RENDER_SINK`):** Devolução de um contrato em memória (`id://mem-ram/...`) para exibição em componente visual da tela.
4. **Mutação de Cache Compartilhado (`CACHE_SINK`):** Escrita em `id://mem-ram/MEM_SHARED_CACHE/...` ou `MEM_DISTRIBUTED_RAM/...`.

---

## 3. Estrutura Agregadora por Identidade da Fonte Chamadora (Resolução do `/??/`)

> **Problema Arquitetural Endereçado:**
> `deve haver uma estrutura que agregue chamadas onde sua identidade única seja a mesma da fonte que a chamou /??/`

Em um sistema de 700 módulos, um método utilitário ou de domínio (`NotaFiscalRepository.Salvar`) pode ser chamado por 40 fluxos diferentes. Se não vincularmos a árvore de chamadas à identidade da **fonte chamadora**, os fluxos se misturam em um grafo cíclico indecifrável.

### 3.1. O Envelope de Agregação Escopado pela Fonte (*Caller-Scoped Call Aggregate*)
Para resolver isso, define-se a estrutura **`CallFlowAggregate`**, cuja **Identidade Única de Agregação (`aggregate_uid`) é derivada diretamente da Identidade Única (`UID`) da Fonte que iniciou a chamada**:

```text
Regra de Identidade do Agregado:
Se a Fonte Chamadora possui UID = id://code/<app>/<root>/<mod>/<ns>/<class>/<method>
Então o Agregado de Call Flow recebe:
aggregate_uid = id://call-agg/<UID_CANONICO_DA_FONTE_CHAMADORA>
```

* **Herança Hierárquica de Contexto (Call Context Propagation):**
  * **Nível de Módulo (Agregado Local):** Quando o método raiz $M_{root}$ dentro do Projeto $P_i$ inicia chamadas para $M_1 \to M_2 \to M_3$, todas essas arestas são empacotadas dentro do envelope cujo ID é a própria identidade de $M_{root}$.
  * **Nível Ponta-a-Ponta (Agregado Global de UI/Entry Point):** Quando uma ação de UI (`TelaFaturamento.BtnEmitir_Click`) chama $M_{root}$, o agregado de $M_{root}$ é anexado como sub-árvore mantendo a identidade raiz `id://call-agg/code/.../TelaFaturamento/BtnEmitir_Click`.
  * **Vantagem Determinística:** Basta consultar a identidade da fonte chamadora para obter instantaneamente todo o subgrafo de chamadas, tabelas afetadas, transformações e pré-condições subordinadas a ela, sem perda de contexto.

---

## 4. Estratégia Incremental de Leitura: Pequenos Agregados por Projeto (Monolito de 700 Módulos)

Para processar **700 módulos** de forma ordenada e incremental sem exceder limites de memória ou contexto:

### 4.1. Passo 1 — Geração de *Module Call Aggregates (MCA)* (1 Projeto por Vez)
Seguindo a **Ordem Topológica** estabelecida no Nível 1 (das camadas base de infraestrutura/dados até a camada de UI):
1. A IA lê **um único projeto (`Mod_k`) por vez**.
2. Para cada método público/interno ou evento de UI em `Mod_k`, a IA constrói um **Pequeno Agregado Local (`MCA_Mod_k.json`)**.
3. Se um método em `Mod_k` chama um método de outro projeto `Mod_j` (ou uma Stored Procedure `Proc_x`), que já foi mapeado na ordem topológica, o MCA incorpora o resumo de contrato daquele UID dependente.

### 4.2. Passo 2 — Consolidação Ponta-a-Ponta (*Flow Linker*)
Um passo leve de *linking* une os 700 pequenos agregados locais (`MCA_001` a `MCA_700`) resolvendo os ponteiros `callee_uid == caller_uid`, materializando o fluxo completo desde a `---UI do sistema` até o `id://db-rel/...` ou `id://storage/...`.

---

## 5. Contabilização de Transformações de Dados (`T_count`)

Em cada etapa (aresta ou nó) de um fluxo identificado, o motor rastreia as identidades de memória (`id://mem-ram/...`) e contabiliza quantas **Transformações de Dados** ocorrem.

### 5.1. Taxonomia e Métrica de Transformações
Uma transformação é contabilizada sempre que um contrato de memória de entrada $M_{in}$ é modificado para produzir $M_{out}$ ou um comando de persistência:

| Tipo de Transformação | Código | Descrição | Peso na Contagem |
| :--- | :--- | :--- | :---: |
| **Mapeamento Estrutural (Projection/Mapping)** | `TRANS_MAP` | Conversão entre tipos (ex: `ViewModel -> DTO -> Entity -> DataRow`). | +1 por conversão |
| **Cálculo / Regra Matemática** | `TRANS_CALC` | Aplicação de fórmulas, impostos, descontos, agregações (`SUM`, `AVG`). | +1 por expressão de mutação |
| **Enriquecimento / Merge de Fontes** | `TRANS_ENRICH` | Combinação de dados vindos de duas ou mais identidades de armazenamento distintas. | +1 por junção de fontes |
| **Filtragem / Redução de Conjunto** | `TRANS_FILTER` | Aplicação de predicados (`LINQ .Where()`, `SQL WHERE / HAVING`) que reduzem o conjunto de dados. | +1 por filtro aplicado |
| **Serialização / Formatação de I/O** | `TRANS_FORMAT` | Conversão de objetos em memória para XML, JSON, CSV, Posicional ou SQL Parameters. | +1 por serialização |

* **Métrica de Fluxo:** Cada segmento $s_i$ possui $T(s_i)$, e o fluxo completo $F$ possui a soma total de transformações:
  $$T_{\text{total}}(F) = \sum_{i=1}^{n} T(s_i)$$

---

## 6. Contabilização de Pré-Condições (`P_count`) e Previsão de Impedimentos (Short-Circuits)

Este é um requisito crítico do Nível 2: identificar, detalhar, contabilizar todas as pré-condições e prever quais pré-condições **anulam ou impedem** a continuidade das etapas subsequentes.

### 6.1. Identificação e Contabilização de Pré-Condições
Toda estrutura condicional no código C# (`if`, `else if`, `switch`, operador ternário, `Guard Clauses`, validações FluentValidation/DataAnnotations) ou no código SQL das Procedures (`IF`, `WHERE`, `CASE`, `CHECK`) que governa a passagem do dado recebe um **ID Único de Pré-Condição (`precond_uid`)**:

```json
{
  "precond_uid": "id://precond/Mod042_Faturamento/NotaFiscalService/EmitirNota#PC_003",
  "owner_identity_uid": "id://code/ERP_Monolito/.../NotaFiscalService/EmitirNota",
  "sequence_order_in_flow": 3,
  "expression_raw": "if (cliente.StatusCredito == StatusCredito.Bloqueado || pedido.ValorTotal > cliente.LimiteDisponivel)",
  "evaluated_identities": [
    "id://mem-ram/MEM_BOUNDARY_CONTRACT/.../ClienteDto.StatusCredito",
    "id://db-rel/ERP_DB/dbo/TB_CLIENTE/VL_LIMITE_DISPONIVEL"
  ],
  "is_blocking_impediment": true,
  "impediment_effect": "ABORT_FLOW_THROW_EXCEPTION",
  "blocked_downstream_identities": [
    "id://db-proc/ERP_DB/dbo/PROC/sp_Estoque_BaixarSaldo",
    "id://db-proc/ERP_DB/dbo/PROC/sp_Faturamento_EmitirNota",
    "id://db-rel/ERP_DB/dbo/TB_NOTA_FISCAL"
  ]
}
```

### 6.2. Contagem Acumulada de Pré-Condições para Travessia Completa
Para que um dado percorra o fluxo $F$ desde o ponto inicial (ex: UI) até o último ponto de armazenamento ($S_{\text{final}}$), ele deve satisfazer todas as pré-condições no caminho crítico:
$$P_{\text{total}}(F) = \sum_{k \in \text{Caminho}(F)} \text{Pré-Condições}(k)$$

### 6.3. Previsão de Pré-Condições Anuladoras/Impeditivas e Ordem Ideal de Execução
* **Classificação de Impedimento (`BLOCKING_PRECONDITION`):**
  Uma pré-condição é classificada como **Impeditiva/Anuladora** quando sua avaliação negativa (ou positiva, no caso de *Guard Clause*) provoca:
  1. `RETURN_EARLY` (retorno imediato interrompendo o método);
  2. `THROW_EXCEPTION` / `RAISERROR` / `ROLLBACK TRANSACTION`;
  3. `SKIP_BRANCH` (desvio que anula a chamada a um subfluxo ou gravação em banco).
* **Cooperação para Ordem Ideal de Execução das Etapas Seguintes:**
  O motor constrói a **Matriz de Precedência de Impedimentos**:
  * Se o Fluxo $F_B$ depende que a Tabela $T_1$ esteja populada com `STATUS = 'APROVADO'`, e o Fluxo $F_A$ possui a pré-condição impeditiva que governa o `INSERT/UPDATE` de `T_1.STATUS = 'APROVADO'`, então a IA deduz automaticamente que **$F_A$ precede obrigatoriamente $F_B$ na ordem lógica de execução do negócio**.
  * Essa ordem induzida pelos impedimentos alimenta diretamente o Nível 3 (agrupamento de jornadas de tela e domínios) e o Nível 4 (cálculo de complexidade do Gráfico 1).

---

## 7. Classificação CRUD dos Dispositivos de Armazenamento no Call Flow

Para facilitar o isolamento e a identificação de domínio nas etapas seguintes (Nível 3), cada interação entre um fluxo de código e uma identidade de armazenamento do Nível 1 (`id://db-rel/...`, `id://storage/...`, `id://mem-ram/MEM_SHARED_CACHE/...`) é classificada pelo seu papel operacional:

| Papel no Fluxo | Classificação Operacional | Semântica para Isolamento de Domínio (Nível 3) |
| :--- | :--- | :--- |
| **Ponto Inicial / Fonte de Leitura** | `STORAGE_INIT_READ` (`SELECT` / `FILE_READ`) | Indica que a identidade é um **Insumo/Dependência de Consulta** do fluxo (pode pertencer ao próprio domínio ou ser leitura de um domínio externo compartilhado). |
| **Mutação de Criação** | `STORAGE_MUTATE_INSERT` (`INSERT` / `FILE_CREATE`) | Forte indicador de **Propriedade de Domínio (Domain Ownership)**: o fluxo que faz `INSERT` em uma tabela quase sempre pertence ao domínio dono daquela entidade. |
| **Mutação de Alteração** | `STORAGE_MUTATE_UPDATE` (`UPDATE` / `FILE_APPEND_MODIFY`) | Indica **Transição de Estado do Ciclo de Vida** da entidade de negócio. |
| **Mutação de Exclusão** | `STORAGE_MUTATE_DELETE` (`DELETE` / `FILE_DELETE` / `TRUNCATE`) | Indica **Encerramento / Expurgo / Cancelamento** do ciclo de vida da entidade. |

---

## 8. Esquema do Artefato de Saída do Nível 2 (Agregado Incremental por Módulo e Fluxo)

Para cada um dos 700 módulos (`Mod_001` ... `Mod_700`), o Nível 2 persiste um arquivo incremental em `.ia_metadata/level2_call_flows/MCA_<ModuleName>.json` com a seguinte estrutura consolidada:

```json
{
  "module_uid": "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento",
  "call_aggregates": [
    {
      "aggregate_uid": "id://call-agg/code/ERP_Monolito/root_8f3a/Mod042_Faturamento/UI/FrmEmissaoNFe/BtnEmitir_Click",
      "root_caller_identity": "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento/UI/FrmEmissaoNFe/BtnEmitir_Click",
      "flow_start_type": "UI_EVENT_ORIGIN",
      "ordered_execution_chain": [
        {
          "step": 1,
          "caller_uid": "id://code/.../FrmEmissaoNFe/BtnEmitir_Click",
          "callee_uid": "id://code/.../NotaFiscalService/EmitirNota",
          "memory_contract_uid": "id://mem-ram/MEM_BOUNDARY_CONTRACT/.../NotaFiscalDto",
          "transformations_count": 2,
          "preconditions_count": 1,
          "blocking_preconditions": ["id://precond/...#PC_001"]
        },
        {
          "step": 2,
          "caller_uid": "id://code/.../NotaFiscalService/EmitirNota",
          "callee_uid": "id://db-proc/ERP_DB/dbo/PROC/sp_Faturamento_EmitirNota",
          "memory_contract_uid": "id://mem-ram/MEM_IO_BUFFER/.../SqlParameters_EmitirNota",
          "transformations_count": 4,
          "preconditions_count": 5,
          "blocking_preconditions": ["id://precond/...#PC_002", "id://precond/...#PC_003"]
        }
      ],
      "storage_touchpoints_classified": [
        {
          "storage_uid": "id://db-rel/ERP_DB/dbo/TB_CLIENTE",
          "role": "STORAGE_INIT_READ",
          "operation": "SELECT"
        },
        {
          "storage_uid": "id://db-rel/ERP_DB/dbo/TB_NOTA_FISCAL",
          "role": "STORAGE_MUTATE_INSERT",
          "operation": "INSERT"
        },
        {
          "storage_uid": "id://db-rel/ERP_DB/dbo/TB_ESTOQUE_SALDO",
          "role": "STORAGE_MUTATE_UPDATE",
          "operation": "UPDATE"
        },
        {
          "storage_uid": "id://storage/PERSIST_DISK_NETWORK/share_nfe/xml_saida",
          "role": "STORAGE_MUTATE_INSERT",
          "operation": "FILE_CREATE"
        }
      ],
      "metrics_summary": {
        "total_identities_in_flow": 14,
        "total_transformations_count": 6,
        "total_preconditions_count": 6,
        "total_blocking_impediments": 3
      },
      "induced_execution_dependencies": {
        "must_execute_after_flows": [
          "id://call-agg/code/.../Mod010_Comercial/FrmPedidoVenda/BtnAprovarPedido_Click"
        ]
      }
    }
  ]
}
```
