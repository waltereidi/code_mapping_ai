# Especificação Técnica — Nível 3: Tech Stack / Client Heuristics (Partes 1 e 2)

> **Nível Hierárquico:** 3 (Compõe e depende estritamente dos **Níveis 1 e 2**; pré-requisito obrigatório para o **Nível 4: Gráficos**)
> **Padrão de Execução:** `[Incremental Build Model]`
> **Escopo Alvo:** Agrupamento das Identidades (Nível 1) e Call Flows (Nível 2) em Domínios de Negócio, Heurísticas Trans-Aplicação, Glossário Léxico para Leitura Natural, Isolamento de "Telas" e Jornada Humana, Tradução da Programação Imperativa e Mapeamento Sócio-Físico (Grupos de Pessoas e Infraestrutura Física).

---

## 1. Regra de Composição Hierárquica

> **Invariante do Nível 3:**
> `[Neste nível o mapeamento compõe os níveis anteriores, desta forma todo o mapeamento começa a possuir grupos, aqui se identificam os domínios]`
> Enquanto o Nível 1 cataloga átomos estruturais únicos (Identidades) e o Nível 2 constrói moléculas encadeadas (Call Flows), o **Nível 3** agrupa conjuntos de Identidades + Call Flows em **Domínios de Negócio (`id://domain/...`)** e **Heurísticas de Cliente (`id://heuristic/...`)**.

---

## 2. Parte 1 — Tech Stack, Domínios, Glossário e Interface Humana ("Telas")

### 2.1. Mapeamento de Aplicações, Principais Artefatos e Arquivos Físicos
Para cada um dos 700 módulos, o Nível 3 consolida o inventário físico-tecnológico vinculando cada Identidade Única (`UID`) à sua Tech Stack e ao seu artefato compilado/distribuído:

```json
{
  "application_name": "ERP_Monolito_Corporativo",
  "artifact_uid": "id://artifact/ERP_Monolito_Corporativo/Mod042_Faturamento.dll",
  "artifact_type": "CLASS_LIBRARY_DLL",
  "source_files": [
    {
      "file_name": "NotaFiscalService.cs",
      "relative_path": "src/Mod042_Faturamento/Services/NotaFiscalService.cs",
      "tech_stack_classification": {
        "layer": "APPLICATION_SERVICE",
        "framework": ".NET Framework 4.8 / C# 7.3",
        "data_access_tech": ["ADO.NET", "Dapper", "SQL Server Stored Procedures"],
        "ui_tech": "WinForms / DevExpress"
      },
      "contained_identities": [
        "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento/Faturamento.Services/NotaFiscalService",
        "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento/Faturamento.Services/NotaFiscalService/EmitirNota(Int64,NotaFiscalDto):ResultadoEmissaoDto"
      ]
    }
  ]
}
```

### 2.2. Identificação de Domínios e Heurísticas de Negócio Trans-Aplicação
Em monolitos de 700 módulos ou ecossistemas com múltiplas aplicações satélites, a mesma regra de negócio frequentemente aparece fragmentada ou duplicada em módulos distintos.

* **Agrupamento de Conjunto de Identidades + Call Flow (`DomainGroup`):**
  Um **Domínio** ($D_k$) é formalmente definido como a tupla:
  $$D_k = \left( \{I_1, I_2, \dots, I_n\}_{\text{Nível 1}}, \; \{F_1, F_2, \dots, F_m\}_{\text{Nível 2}}, \; \{T_{\text{CRUD}}\}_{\text{Tabelas Dominadas}} \right)$$
  Onde o critério primário de coesão é o compartilhamento de tabelas com classificação `STORAGE_MUTATE_INSERT` / `STORAGE_MUTATE_UPDATE` (do Nível 2) somado à afinidade semântica do Glossário.

* **Heurística de Negócio Trans-Aplicação (`Cross-Application Business Heuristic`):**
  * Abstrações que implementam a **mesma heurística de negócio** — mesmo estando em aplicações ou módulos diferentes (ex: cálculo de comissão no `ERP_Desktop`, no `Portal_Vendas_Web` e no `Servico_Integracao_Batch`) — recebem um identificador de heurística unificado: `id://heuristic/<canonical_business_concept>`.
  * **Agregação de Palavras Comuns à Identidade Única de Origem:**
    Todas as palavras recorrentes de negócio encontradas no código (ex: `Fatura`, `Boleto`, `Desconto`, `Alçada`, `Glosa`, `Romaneio`) são extraídas, normalizadas (stemming/lemmatization) e **agregadas diretamente à Identidade Única (`UID` do Nível 1) de onde foram mapeadas**.

### 2.3. Glossário Integrado e Captura Léxica de Variáveis para Tradução em Leitura Natural
> **Distinção Arquitetural Importante (Nível 1 vs. Nível 3):**
> No **Nível 1**, variáveis locais e de classe são descartadas como *Identidades Estruturais* para não inflar o grafo de chamadas. Já no **Nível 3**, os **nomes** dessas variáveis, parâmetros e colunas que se assemelham a palavras humanas são colhidos como **Metadados Léxicos do Glossário**, vinculados ao `UID` do método/classe pai!

* **Estrutura do Glossário Integrado (`.ia_metadata/level3_tech_stack/glossary.json`):**
  1. **`lexical_token`:** Nome original da variável, parâmetro, método, classe ou coluna (ex: `vlrDescMaxAlcada`, `dtVencimentoProrrogado`, `flgClienteInadimplente`).
  2. **`decomposed_words`:** Decomposição CamelCase/PascalCase/Snake_Case e expansão de abreviações (`["Valor", "Desconto", "Maximo", "Alcada"]`).
  3. **`bound_structural_identities`:** Lista de `UIDs` do Nível 1 onde esse termo aparece.
  4. **`natural_language_template`:** Frase canônica gerada para traduzir chamadas técnicas em leitura natural humana.
     * *Antes (Nível 2 Técnico):* `FrmPed.btnOk_Click -> PedSvc.ValAlcada(idCli, vlrDescMaxAlcada) -> sp_Fin_ChkLim -> TB_CLI_LIM (SELECT)`
     * *Depois (Nível 3 Traduzido pelo Glossário):* `"Ao clicar em Confirmar na Tela de Pedido, o sistema valida se o Valor de Desconto Máximo por Alçada respeita o Limite de Crédito do Cliente consultando a tabela de Limites Financeiros."`

### 2.4. Mapeamento de Interface de Usuário: Isolamento em "Telas" e Fluxo Humano
O mapeamento de UI foca explicitamente na **jornada operacional que um ser humano executa** para acionar um ou mais Call Flows:

1. **Unidade de Isolamento — A `"Tela"` (`id://ui-screen/<app>/<module>/<screen_name>`):**
   Representa qualquer unidade visual autocontida apresentada ao operador humano (Windows Form `Form`, WPF `Window`/`UserControl`, WebForms `.aspx`, MVC/Razor `.cshtml`, Angular/React Component/View).
2. **Inventário de Componentes da Tela:**
   Cada tela lista exaustivamente seus controles interativos (Botões, Campos de Entrada, Combos, Grids, Abas, Menus de Contexto, Atalhos de Teclado).
3. **Vínculo Componente $\to$ Call Flow $\to$ Passo Humano:**
   Para cada componente da tela, registra-se:
   * Qual evento humano o aciona (`Click`, `DoubleClick`, `KeyDown_Enter`, `SelectedIndexChanged`, `FormLoad`).
   * Qual **`aggregate_uid` (Call Flow do Nível 2)** é disparado por esse componente.
   * Qual a **Ordem Sequencial Humana** dentro da tela (baseada nas pré-condições impeditivas do Nível 2: ex. o humano precisa primeiro preencher o CPF e clicar em "Buscar Cliente" [`CallFlow_1`] antes que o botão "Emitir Nota" [`CallFlow_2`] fique habilitado).

---

## 3. Parte 2 — Mapeamento Sócio-Organizacional, Linguagem Ubíqua Não-Regra e Programação Imperativa

### 3.1. Gate 3.1 — Consultas Assistidas para Grupos de Pessoas e Estruturas Físicas
```text
{ identificar consultas na aplicação que sejam capazes de mapear e identificar grupos de pessoas que utilizam cada regra de negócio, quais estruturas físicas podem ser identificadas através das informações existentes e solicitar ao usuário que as forneça; aqui a IA ajuda o usuário fornecendo as consultas que devem ser executadas para que os dados sejam propriamente utilizados }
```

* **Mecanismo de Descoberta Automática pela IA:**
  A IA inspeciona as identidades de banco (`id://db-rel/...`) e os Call Flows de autenticação/autorização/auditoria mapeados nos Níveis 1 e 2, procurando tabelas e colunas com semântica de:
  * **Identidade Humana e Grupos:** Usuários, Perfis, Papéis (`Roles`), Grupos de Acesso, Permissões por Tela/Módulo, Setores, Departamentos, Cargos (`TB_USUARIO`, `TB_PERFIL`, `TB_GRUPO_ACESSO`, `TB_LOG_AUDITORIA`).
  * **Estruturas Físicas Existentes no Banco:** Filiais, Unidades, Prédios, Salas, Almoxarifados, Caixas/PDVs, Estações de Trabalho (`HOSTNAME` / `IP` / `MAC_ADDRESS` em logs), Centros de Custo, Impressoras Fiscais associadas a locais físicos (`TB_FILIAL`, `TB_SETOR_FISICO`, `TB_TERMINAL`, `TB_CENTRO_CUSTO`).
* **Geração do Artefato `03_consultas_grupos_pessoas_e_estruturas_fisicas.sql`:**
  A IA gera o script SQL customizado para o schema real do cliente e **PAUSA A EXECUÇÃO**, solicitando que o usuário execute as consultas e forneça os resultados:

```sql
-- ============================================================================
-- GATE 3.1: MAPEAMENTO DE GRUPOS DE PESSOAS x REGRAS DE NEGÓCIO x ESTRUTURAS FÍSICAS
-- Gerado automaticamente a partir das tabelas identificadas no Nível 1 e Nível 2.
-- ============================================================================

-- 1. Mapeamento de Grupos de Pessoas / Perfis / Setores x Telas e Módulos (Regras de Negócio)
SELECT 
    g.CD_GRUPO_USUARIO      AS GrupoId,
    g.NM_GRUPO_USUARIO      AS NomeGrupoOuPerfil,
    s.NM_SETOR              AS SetorOrganizacional,
    p.CD_TELA_MODULO        AS CodigoTelaOuRegra,
    p.FL_PERMISSAO_ESCRITA  AS PermiteExecutarMutacao,
    COUNT(DISTINCT u.ID_USUARIO) AS QuantidadePessoasAtivasNoGrupo
FROM TB_GRUPO_USUARIO g
INNER JOIN TB_PERMISSAO_GRUPO p ON g.CD_GRUPO_USUARIO = p.CD_GRUPO_USUARIO
LEFT JOIN TB_USUARIO u ON u.CD_GRUPO_USUARIO = g.CD_GRUPO_USUARIO AND u.FL_ATIVO = 1
LEFT JOIN TB_SETOR s ON u.CD_SETOR = s.CD_SETOR
GROUP BY g.CD_GRUPO_USUARIO, g.NM_GRUPO_USUARIO, s.NM_SETOR, p.CD_TELA_MODULO, p.FL_PERMISSAO_ESCRITA;

-- 2. Mapeamento de Estruturas Físicas Identificáveis no Banco (Unidades, Salas, Terminais, Centros de Custo)
SELECT 
    f.CD_FILIAL             AS UnidadeFisicaId,
    f.NM_FILIAL             AS NomeUnidadeFisica,
    l.CD_LOCAL_FISICO       AS SalaOuGalpaoId,
    l.DS_LOCAL_FISICO       AS DescricaoSalaOuEstruturaFisica,
    s.NM_SETOR              AS SetorAlocado,
    t.NM_ESTACAO_TRABALHO   AS TerminalOuHostFisico
FROM TB_FILIAL f
LEFT JOIN TB_LOCAL_FISICO l ON l.CD_FILIAL = f.CD_FILIAL
LEFT JOIN TB_SETOR s ON s.CD_LOCAL_FISICO = l.CD_LOCAL_FISICO
LEFT JOIN TB_TERMINAL_ACESSO t ON t.CD_SETOR = s.CD_SETOR;
```

---

### 3.2. Gate 3.2 — Enriquecimento do Glossário com Linguagem Ubíqua Não-Participante da Regra de Negócio
```text
{ fornecer dados que enriqueçam o glossário mas que não façam parte da regra de negócio; solicite fonte de informações correlacionadas que não fazem parte da regra de negócio mapeada no código, essas informações precisam estar fortemente identificadas como não participantes da regra de negócio mas devem enriquecer a resposta através da identificação da linguagem ubíqua de seus usuários }
```

* **Comportamento da IA:** A IA pausa e solicita ao usuário documentos ou fontes correlacionadas externas ao código-fonte, tais como:
  * Manuais operacionais de treinamento, FAQs internos, chamados de suporte/tickets;
  * Organograma de RH, catálogo de processos (BPMN), apelidos internos de telas ou relatórios usados no dia-a-dia pelos funcionários;
  * Dicionários de jargões do setor (logística, saúde, financeiro, industrial, etc.).
* **Isolamento Semântico Estrito (Blindagem contra Poluição de Regra de Negócio):**
  Todo termo inserido no Glossário a partir deste Gate recebe obrigatoriamente o carimbo:
  ```json
  {
    "term_uid": "id://glossary-ext/termo_romaneio_cego",
    "ubiquitous_term": "Conferência Cega do Box 4",
    "part_of_executable_business_rule": false,
    "classification_tag": "NON_BUSINESS_RULE_UBIQUITOUS_CONTEXT",
    "correlated_domain_uid": "id://domain/RecebimentoMercadoria",
    "correlated_screen_uid": "id://ui-screen/ERP_Monolito/Mod112_WMS/FrmConferenciaEntrada",
    "semantic_enrichment_note": "Os operadores do galpão chamam a tela FrmConferenciaEntrada de 'Conferência Cega do Box 4'. Este termo não altera nem constitui cálculo ou pré-condição no código."
  }
  ```
  > **Garantia de Isolamento:** Nenhum item marcado com `"part_of_executable_business_rule": false` e `"classification_tag": "NON_BUSINESS_RULE_UBIQUITOUS_CONTEXT"` pode ser contabilizado como Identidade Estrutural (Nível 1) nem como Pré-Condição ou Transformação (Nível 2). Seu papel exclusivo é enriquecer a tradução natural e a legibilidade humana dos domínios e gráficos.

---

### 3.3. Mapeamento Descritivo da Programação Imperativa
`-- nesta camada os símbolos e jargões de código devem produzir um mapeamento que descreva a programação imperativa`

Para que a lógica técnica C# e SQL seja compreendida tanto estruturalmente quanto em linguagem natural, o Nível 3 converte os **símbolos e jargões de código imperativo** em uma **Árvore de Semântica Imperativa Padronizada (*Imperative Execution Narrative*)**:

| Símbolo / Jargão Imperativo no Código (C# / SQL) | Classificação Imperativa (`IMPERATIVE_OP`) | Tradução Descritiva Estruturada (Combinada com o Glossário) |
| :--- | :--- | :--- |
| `foreach (var item in lista)` / `for (...)` / `CURSOR` | `ITERATION_LOOP` | *"Para cada [Entidade do Glossário] presente na coleção em memória, executa repetidamente a sequência..."* |
| `if (cond) { ... } else { ... }` / `switch` | `CONDITIONAL_BRANCH` | *"Avalia a pré-condição [PC_ID]: caso verdadeira, segue o caminho A; caso contrário, desvia para o caminho B."* |
| `if (!valido) throw new ...` / `return false;` | `IMPERATIVE_GUARD_ABORT` | *"Impedimento Crítico: interrompe imediatamente o processamento caso [Condição] seja violada."* |
| `obj.Status = NovoStatus;` / `x += y;` | `STATE_MUTATION_IN_MEMORY` | *"Altera o estado em memória de [Termo do Glossário], atribuindo/acumulando o novo valor."* |
| `using (var tx = conn.BeginTransaction())` / `COMMIT` / `ROLLBACK` | `ATOMIC_TRANSACTION_SCOPE` | *"Inicia bloco transacional atômico: todas as gravações subsequentes são confirmadas juntas ou totalmente desfeitas em caso de falha."* |
| `lock (_syncRoot)` / `SemaphoreSlim` / `UPDLOCK` | `CONCURRENCY_SYNCHRONIZATION` | *"Bloqueia acesso concorrente para garantir que apenas um processo altere o recurso por vez."* |
| `try { ... } catch (Exception ex) { ... }` | `FAULT_RECOVERY_HANDLER` | *"Monitora falhas técnicas durante a execução e desvia para rotina de tratamento/compensação."* |
