# Spec 01 — Nível 1: Structural Comprehension (Compreensão Estrutural e Modelo de Identidade Única)

**Nível na Hierarquia:** `1 de 4` (Camada Fundacional — Pré-requisito obrigatório para os Níveis 2, 3 e 4)  
**Diretório de Salvamento dos Dados:** `C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural`  
**Regra de Ouro do Nível 1:** *Todo o mapeamento neste nível deve conter apenas informações únicas (100% deduplicadas) para todas as informações que forem somadas. Cada fonte de dados e elemento estrutural deve possuir uma estrutura de Identidade Única (`URN`) que descreva sua origem até que seja inequivocamente única.*

---

## 1. Gates do `[Incremental Build Model]` no Nível 1

### 1.1. Gate Inicial de Infraestrutura e Aplicação (`GATE-L1.0`)
> **`{ o mapeamento de infraestrutura deve saber e perguntar o nome da aplicação em que o código mapeado faz parte }`**

- **Comportamento de Parada:** Ao iniciar a execução sobre a pasta raiz dos 700 módulos, o sistema verifica se o manifesto `C:\Users\walter.matsuda\Documents\metadados_famema2.1\config\application_manifest.json` está preenchido. Caso não esteja, a execução **para** e solicita ao usuário:
  1. O **Nome da Aplicação** (ou lista de aplicações corporativas que compõem o monolito, ex.: `SIHOSP_HCFAMEMA`);
  2. O caminho da **Pasta Raiz do Código-Fonte** (`monolith_root_path`), que será convertido na identidade única de origem do código-fonte.

### 1.2. Gate de Mapeamento Relacional do Banco de Dados (`GATE-L1.1`)
> **`{ forneça o mapeamento relacional do banco de dados }`**

- **Comportamento de Parada:** Antes de fechar o grafo estrutural de persistência do Nível 1, a execução **para** e solicita ao usuário o mapeamento relacional do banco de dados (tabelas, colunas, tipos, chaves primárias `PK` e chaves estrangeiras `FK`).
- **Auxílio da IA ao Usuário:** Para facilitar o fornecimento pelo usuário, a IA disponibiliza imediatamente em `C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural\helper_extract_relational_schema.sql` as consultas prontas de dicionário de dados (`ALL_TABLES`, `ALL_TAB_COLUMNS`, `ALL_CONSTRAINTS`, `ALL_CONS_COLUMNS`) para que o usuário exporte e salve o arquivo em `C:\Users\walter.matsuda\Documents\metadados_famema2.1\input\layer1_relational_schema\`.

### 1.3. Gate Final do Nível 1: Extração de Procedures para o Nível 2 (`GATE-L1.2`)
> **`{ no fim do mapeamento inicial separe as procedures encontradas em um arquivo de texto com o select montado para solicitar a alimentação desses dados pelo usuário que está executando }`**

- **Comportamento de Parada:** Ao concluir a varredura estrutural dos 700 módulos, o motor separa todas as procedures, functions e packages encontradas, grava o arquivo `C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural\pending_procedures_extraction.txt` contendo o comando `SELECT` pronto para execução no SGBD, **interrompe a execução** e solicita ao usuário que forneça o resultado desse `SELECT` em `C:\Users\walter.matsuda\Documents\metadados_famema2.1\input\layer2_procedures_source\` antes de iniciar o Nível 2.

---

## 2. Modelo de Identidade Única para a Informação (`Canonical Information Identity`)

Para garantir que nenhuma identidade seja confundida com outra e que toda informação possua níveis hierárquicos suficientes para mapear sua origem até que seja única, o Nível 1 implementa um **URN Canônico de 7 Níveis**:

```text
urn:<org>:<app_name>:<origin_plane>:<storage_or_runtime_subtype>:<root_or_schema_scope>:<entity_kind>:<canonical_unique_identifier>
```

### 2.1. Regras Obrigatórias de Identidade por Fonte de Dados

| Fonte / Natureza da Informação | Plano (`<origin_plane>`) | Requisitos de Identidade e Distinção Estrita | Formato Canônico da Identidade Única (`URN`) |
| :--- | :--- | :--- | :--- |
| **1. Tabelas e Estrutura de Banco Relacional** | **`db-rel`** | A identidade deve descrever explicitamente que a informação vem de um **banco de dados relacional**, classificando-a como parte de uma estrutura de banco (`schema` + `table` + `column`/`constraint`). **Nunca poderá ser confundida** com uma classe C#, DTO ou arquivo local de mesmo nome. | `urn:famema:<APP>:db-rel:oracle:<SCHEMA>:table:<TABLE_NAME>`<br>`urn:famema:<APP>:db-rel:oracle:<SCHEMA>:column:<TABLE_NAME>.<COLUMN_NAME>`<br>`urn:famema:<APP>:db-rel:oracle:<SCHEMA>:fk:<CONSTRAINT_NAME>` |
| **2. Arquivos do Computador Local e Persistência Física** | **`storage-persist`** | Toda informação proveniente de arquivos do computador local, pastas de rede ou mídias físicas permanentes (`disco`, `pedras`, `cds`, fitas, cartões, impressoras, registry) deve possuir uma identidade exclusiva que discrimine o meio físico e o template do caminho. | `urn:famema:<APP>:storage-persist:local-disk:<ROOT_ALIAS>:file:<NORMALIZED_PATH>`<br>`urn:famema:<APP>:storage-persist:optical-cd-dvd:<MEDIA_ID>:volume:<SPEC>`<br>`urn:famema:<APP>:storage-persist:archival-immutable:<MEDIA_ID>:artifact:<SPEC>` |
| **3. Informação Processada em Memória RAM** | **`mem-ram`** | Toda informação processada em memória deve conter uma identidade **distinta de todos os outros tipos de armazenamento em memória** (separando explicitamente classes, assinaturas de métodos, contratos de transporte DTO, caches estáticos, sessão e buffers em memória). | `urn:famema:<APP>:mem-ram:code-class:<MODULE>:<NAMESPACE>.<CLASS>`<br>`urn:famema:<APP>:mem-ram:code-method-sig:<MODULE>:<CLASS>.<METHOD>(<PARAM_TYPES>):<RETURN_TYPE>`<br>`urn:famema:<APP>:mem-ram:dto-contract:<MODULE>:<NAMESPACE>.<DTO>`<br>`urn:famema:<APP>:mem-ram:static-cache:<MODULE>:<CACHE_HOLDER>.<KEY>`<br>`urn:famema:<APP>:mem-ram:user-session:<MODULE>:session:<KEY>` |
| **4. Estrutura / Pasta Raiz do Código-Fonte** | **`src-root`** | Estabelece a pasta raiz do monolito e a estrutura de diretórios/projetos como uma identidade única que ancora todo arquivo físico de código-fonte. | `urn:famema:<APP>:src-root:monolith-root:<ROOT_FOLDER_NAME>`<br>`urn:famema:<APP>:src-root:module-dir:<MODULE_FOLDER>`<br>`urn:famema:<APP>:src-root:source-file:<MODULE_FOLDER>/<RELATIVE_FILE_PATH>` |
| **5. Entidades Externas (Procedures, Functions, Packages, APIs)** | **`ext-obj`** | Entidades externas como procedures devem ser interpretadas como **objetos de primeira classe** com identidade própria e inconfundível. | `urn:famema:<APP>:ext-obj:db-procedure:<SCHEMA>.<PROC_NAME>`<br>`urn:famema:<APP>:ext-obj:db-function:<SCHEMA>.<FUNC_NAME>`<br>`urn:famema:<APP>:ext-obj:db-package:<SCHEMA>.<PKG_NAME>.<MEMBER>` |

---

## 3. Mapeamento Detalhado das Formas de Armazenamento de Dados

### 3.1. Relacionamento de Tabelas (Persistência Garantida e Reutilização Multi-Fonte)
Dados armazenados em banco relacional possuem duas propriedades estruturais fundamentais que devem ser registradas em cada identidade `db-rel`:
1. **Garantia de Persistência e Reutilização (`persisted_and_reusable: true`):** Diferente da memória RAM volátil, o estado gravado na tabela sobrevive ao ciclo de execução e pode ser reutilizado por fluxos posteriores.
2. **Utilização Multi-Fonte (`multi_source_utilization`):** Uma mesma tabela pode ser lida ou modificada por múltiplos módulos C#, múltiplas aplicações e múltiplas procedures.

O catálogo `identities_db_relational.jsonl` armazena para cada tabela e relacionamento:
- **Identidade Única da Tabela (`table_identity_urn`)** e lista de identidades de suas colunas (`PK`, `FK`, colunas de vigência/status e colunas de negócio);
- **Relacionamentos Relacionais (`relationships`):**
  - *Explícitos (DDL fornecido no `GATE-L1.1`):* Chaves estrangeiras (`FOREIGN KEY`) com tabela origem, coluna origem, tabela destino e coluna destino;
  - *Implícitos (Extraídos das Queries SQL/DAO):* Junções relacionais (`INNER/LEFT JOIN A.COL = B.COL`) recorrentes no código;
- **Fontes Consumidoras e Produtoras (`accessing_sources`):** Lista deduplicada de todas as identidades (`src-root`, `mem-ram:code-class`, `ext-obj:db-procedure`) que utilizam aquela tabela.

### 3.2. Mapeamento Completo de Armazenamento Persistente em Disco e Outras Mídias (`Disco, Pedras, CDs, etc.`)
O mapeador deve identificar **todas as formas de armazenamento persistente fora do SGBD relacional**, desde arquivos locais modernos até mídias físicas, ópticas ou imutáveis/legadas:

| Subtipo de Persistência (`<storage_subtype>`) | Natureza Física / Conceitual | Exemplos Mapeados no Código e Infraestrutura |
| :--- | :--- | :--- |
| **`local-disk`** | Disco rígido/SSD do computador local da estação ou servidor | Arquivos `.ini`, `.config`, `.xml`, `.json`, `.csv`, `.txt`, logs locais, relatórios `.rpt`/`.pdf` salvos em `C:\`, `%APPDATA%`, `%TEMP%`, bancos locais SQLite/Access. |
| **`network-share`** | Sistemas de arquivos distribuídos / pastas compartilhadas em rede | Caminhos UNC (`\\servidor\compartilhamento\...`), drives mapeados (`M:\`, `Z:\`) para laudos, imagens médicas, remessas SUS (AIH/BPA/APAC). |
| **`optical-cd-dvd`** | Mídias ópticas e graváveis (`CDs`, `DVDs`, imagens ISO/DICOM) | Gravação/leitura de exames de imagem (PACS/DICOM em CD/DVD), backups ópticos ou exportações físicas para pacientes/convênios. |
| **`removable-hardware`** | Dispositivos removíveis, tokens criptográficos e periféricos físicos | Pen-drives, cartões SmartCard / Certificados Digitais A3 (assinatura médica), coletores de dados, portas seriais/paralelas (`COM1`, `LPT1`) de impressoras térmicas de pulseiras/etiquetas. |
| **`archival-immutable` (`"pedras"` / arquivo físico / papel / mídia fria)** | Registros físicos permanentes, imutáveis ou fora-de-linha referenciados pelo sistema | Protocolos impressos assinados fisicamente, prontuários em arquivo físico/microfilme (cujo número de envelope/caixa física é rastreado pelo sistema), mídias de retenção legal permanente ("gravado em pedra"/WORM/fita LTO). |
| **`win-registry`** | Registro persistente do Sistema Operacional | Chaves `HKEY_LOCAL_MACHINE` e `HKEY_CURRENT_USER` lidas ou gravadas via `Microsoft.Win32.Registry` para parametrização de estação física. |

---

## 4. Mapeamento de Memória RAM: Contrato Agnóstico de Linguagem e Filtro Anti-Explosão

### 4.1. O Problema da Explosão de Metadados em Memória RAM e a Regra de Filtragem
> **Diretriz da Especificação:** *"aqui é necessário filtrar e definir o que realmente deve ser mapeado; um mapeamento completo de tudo que está armazenado em memória deve ficar maior que o próprio código, o que não será possível ser utilizado como metadados simplificados. Classifique como parte principal para criar as identidades: classes, métodos; descarte variáveis de classe e métodos."*

Para que o mapeamento de memória RAM seja **compacto, único e menor que o código-fonte**, aplica-se o **Filtro Estrutural Estrito de Memória RAM**:

1. **O QUE RECEBE IDENTIDADE ÚNICA EM MEMÓRIA (`MAPEADO`):**
   - **Classes, Interfaces, Structs e Enums (`mem-ram:code-class`):** Unidades estruturais que agrupam comportamento ou estado.
   - **Assinaturas de Métodos / Funções (`mem-ram:code-method-sig`):** Nome do método, tipos e nomes dos parâmetros de entrada e tipo de retorno. Constituem os nós de roteamento do Call Flow.
   - **Classes de Contrato de Dados / DTOs (`mem-ram:dto-contract`):** Identidade da classe de transporte que trafega entre camadas.
   - **Armazenamentos Temporários Compartilhados de Sessão/Cache (`mem-ram:static-cache`, `mem-ram:user-session`, `mem-ram:shared-buffer`):** Caches estáticos globais (`static Dictionary`, `MemoryCache`), variáveis de sessão de usuário (`HttpContext.Session`, contexto global de login) e `DataSets` compartilhados entre telas.
2. **O QUE É ESTRITAMENTE DESCARTADO NO NÍVEL 1 (`DESCARTADO`):**
   - **Variáveis de Classe (Fields / Campos Privados ou Internos):** Descartadas da criação de identidades estruturais.
   - **Variáveis Locais de Métodos:** Variáveis temporárias declaradas dentro do corpo dos métodos (ex.: `int i`, `var aux`, `string sql`, `bool valido`) são **100% descartadas** no Nível 1. *(Nota: apenas os radicais léxicos relevantes ao vocabulário de negócio serão colhidos de forma agregada no Glossário do Nível 3, sem gerar identidades estruturais por variável).*

### 4.2. Contrato de Memória RAM Independente de Linguagem (`LanguageAgnosticMemoryContract`)
Para que o mapeamento de memória RAM entenda a estrutura do código independentemente de sua linguagem (C#, VB.NET, PL/SQL, JavaScript, Delphi), toda identidade `mem-ram` é serializada sob um contrato universal:

```json
{
  "identity_urn": "urn:famema:SIHOSP:mem-ram:code-method-sig:demanda-cirurgia-bo:DemandaCirurgia.BO.BODemandaCirurgica.Salvar(DemandaDTO):Int64",
  "origin_plane": "mem-ram",
  "memory_distinct_subtype": "code-method-sig",
  "language": "csharp",
  "source_root_identity": "urn:famema:SIHOSP:src-root:source-file:demanda-cirurgia-bo/BODemandaCirurgica.cs",
  "enclosing_class_identity": "urn:famema:SIHOSP:mem-ram:code-class:demanda-cirurgia-bo:DemandaCirurgia.BO.BODemandaCirurgica",
  "canonical_name": "Salvar",
  "parameters_contract": [
    {
      "ordinal": 0,
      "type_urn": "urn:famema:SIHOSP:mem-ram:dto-contract:demanda-cirurgia-classes:DemandaCirurgia.Classes.DemandaDTO",
      "parameter_name": "objDemanda"
    }
  ],
  "return_type_urn": "urn:dotnet:system:type:System.Int64",
  "signature_hash": "sha256:4a8b9c0d1e2f...",
  "body_hash": "sha256:9f8e7d6c5b4a..."
}
```

---

## 5. Mapeamento de Código C#: Identificação Prévia de Bibliotecas e Assinaturas Incrementais

### 5.1. Passo 1: Identificação Prévia de Bibliotecas e Dependências do Projeto
Antes de iniciar o mapeamento dos arquivos `.cs` de qualquer projeto C#, o mapeador analisa obrigatoriamente os manifestos de projeto (`.sln`, `.csproj`, `packages.config`, `app.config`, `web.config`) para que **todas as fontes e dependências sejam totalmente identificáveis antes da etapa de Call Flow**:

1. **Mapeamento de Dependências Internas (`ProjectReference` / Assemblies do Monolito):**
   - Constrói o DAG (Grafo Acíclico Dirigido) de dependências entre os 700 módulos, identificando exatamente qual projeto consome qual biblioteca interna.
2. **Mapeamento de Bibliotecas Externas e Frameworks (`ExternalLibraryIdentity`):**
   - Cataloga todas as DLLs e pacotes utilizados (ex.: `Oracle.DataAccess`, `DevExpress.XtraEditors`, `System.Windows.Forms`, `CrystalDecisions`, `Newtonsoft.Json`) sob identidades `urn:famema:<APP>:src-root:lib-dependency:<LIB_NAME>:<VERSION>`.
3. **Tabela de Resolução de `using` por Arquivo:**
   - Associa cada diretiva `using` de um arquivo `.cs` ao projeto interno ou biblioteca externa correspondente, garantindo que no Nível 2 (Call Flow) qualquer tipo ou método invocado tenha sua identidade de origem resolvida sem ambiguidade.

### 5.2. Passo 2: Mapeamento Incremental de Assinaturas de Código C#
1. **Assinaturas Primeiro:** O motor mapeia primeiro **toda a assinatura de código** (Namespaces $\rightarrow$ Classes/Interfaces $\rightarrow$ Assinaturas de Métodos) de todos os 700 módulos.
2. **Formato Reutilizável e Incremental (`Incremental Signature Registry`):**
   - Cada classe e assinatura de método é gravada com dois hashes independentes:
     - `signature_hash`: Hash calculado exclusivamente sobre a assinatura (nome da classe, nome do método, tipos de parâmetros e tipo de retorno).
     - `body_hash`: Hash calculado sobre a implementação interna do método.
   - **Garantia de Reuso e Incremento:** Quando houver modificações futuras no código-fonte:
     - Arquivos cujo hash não mudou são **100% reutilizados sem reprocessamento**.
     - Se apenas o corpo de um método foi alterado (`body_hash` mudou, mas `signature_hash` permaneceu igual), a Identidade Única (`URN`) do método no Nível 1 permanece intacta e nenhum módulo chamador externo precisa ser remapeado.
     - Se uma nova classe ou método for adicionado, apenas o delta incremental é inserido no catálogo de identidades únicas.

---

## 6. Handoff Final do Nível 1: Separação das Procedures e Geração do Arquivo TXT com `SELECT`

Ao finalizar a varredura estrutural dos 700 módulos, todas as identidades externas do tipo procedure, function ou package (`urn:famema:<APP>:ext-obj:db-procedure:<SCHEMA>.<NAME>`) são consolidadas e deduplicadas.

O motor gera automaticamente o arquivo:  
`C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural\pending_procedures_extraction.txt`

### 6.1. Estrutura Obrigatória do Arquivo `pending_procedures_extraction.txt`

```sql
-- ==================================================================================
-- [INCREMENTAL BUILD MODEL] - GATE-L1.2: SOLICITAÇÃO DE DADOS AO USUÁRIO
-- Condição: { forneça o código-fonte das procedures mapeadas no Nível 1 executando
--             o SELECT abaixo no banco de dados para dar continuidade ao Nível 2 }
-- Pasta de Destino da Resposta:
-- C:\Users\walter.matsuda\Documents\metadados_famema2.1\input\layer2_procedures_source\
-- ==================================================================================

-- LISTA DE IDENTIDADES ÚNICAS DE PROCEDURES MAPEADAS NOS 700 MÓDULOS:
-- [0001] urn:famema:SIHOSP:ext-obj:db-procedure:SIHOSP.PRC_GRAVA_DEMANDA_CIRURGICA
-- [0002] urn:famema:SIHOSP:ext-obj:db-function:SIHOSP.GET_NOM_INFRA_DEMANDA
-- [0003] urn:famema:SIHOSP:ext-obj:db-package:SIHOSP.PKG_AGENDAMENTO

SELECT
    OWNER AS SCHEMA_NAME,
    NAME AS PROCEDURE_OR_PACKAGE_NAME,
    TYPE AS OBJECT_TYPE,
    LINE AS LINE_NUMBER,
    TEXT AS SOURCE_LINE
FROM
    ALL_SOURCE
WHERE
    (UPPER(OWNER), UPPER(NAME)) IN (
        ('SIHOSP', 'PRC_GRAVA_DEMANDA_CIRURGICA'),
        ('SIHOSP', 'GET_NOM_INFRA_DEMANDA'),
        ('SIHOSP', 'PKG_AGENDAMENTO')
        -- [Demais procedures deduplicadas injetadas automaticamente]
    )
ORDER BY
    OWNER, NAME, TYPE, LINE;
```

---

## 7. Resumo dos Artefatos Salvos pelo Nível 1

Todos os arquivos abaixo são gravados em `C:\Users\walter.matsuda\Documents\metadados_famema2.1\output\layer1_structural\` contendo **exclusivamente registros únicos deduplicados por URN**:

1. `application_context.json` — Nome da aplicação corporativa e identidade única da pasta raiz.
2. `libraries_and_dependencies_graph.json` — Mapeamento completo das bibliotecas utilizadas em cada projeto C#, referências cruzadas e ordem topológica dos 700 módulos.
3. `identities_db_relational.jsonl` — Identidades únicas de tabelas relacionais, colunas, relacionamentos (`PK`/`FK`/`JOIN`) e lista de consumidores multi-fonte.
4. `identities_storage_persistent.jsonl` — Identidades únicas de todas as formas de armazenamento persistente (`local-disk`, `network-share`, `optical-cd-dvd` [CDs/DVDs], `removable-hardware`, `archival-immutable` [pedras/arquivo físico], `win-registry`).
5. `identities_memory_signatures.jsonl` — Identidades únicas de memória RAM sob contrato agnóstico de linguagem: classes, assinaturas de métodos (com hashes incrementais), contratos DTO e buffers/caches compartilhados (sem variáveis de classe e sem variáveis de métodos).
6. `identities_external_objects.jsonl` — Identidades únicas de procedures, functions, packages e objetos externos.
7. `pending_procedures_extraction.txt` — Arquivo de texto com o `SELECT` montado que aciona a parada do **`GATE-L1.2`** e solicita a alimentação dos códigos-fonte das procedures pelo usuário.
