# Especificação Técnica — Nível 1: Structural Comprehension

> **Nível Hierárquico:** 1 (Camada Fundacional — Sem dependências superiores; pré-requisito obrigatório para os Níveis 2, 3 e 4)
> **Padrão de Execução:** `[Incremental Build Model]`
> **Escopo Alvo:** Monolito C# (.NET) composto por ~700 módulos/projetos e Banco de Dados Relacional.

---

## 1. Objetivo e Regra de Unicidade Estrita

O **Nível 1 (Structural Comprehension)** estabelece a fundação determinística de metadados do sistema. Nenhuma análise de fluxo (Nível 2), domínio/heurística (Nível 3) ou visualização (Nível 4) pode existir sem que cada elemento estrutural possua uma **Identidade Única Global (UID)** imutável e sem colisões.

> **Regra de Invariância do Nível 1:**
> `[Neste nível todo o mapeamento deve conter apenas informações únicas para todas as informações que forem somadas]`
> Todo artefato mapeado nos 700 módulos é registrado em uma **Tabela de Símbolos Global Deduplicada (Content-Addressable Identity Registry)**. Se duas referências em projetos diferentes apontam para a mesma tabela física, arquivo ou método, elas resolvem para **exatamente o mesmo UID**, garantindo cardinalidade única na soma global de metadados.

---

## 2. Gates de Interação Obrigatória (`{ ... }`) do Nível 1

Seguindo o padrão **`[Incremental Build Model]`**, o motor de mapeamento deve **interromper a execução** nos pontos demarcados por `{ ... }` e aguardar o insumo do usuário antes de avançar.

### Gate 1.1 — Identificação da Aplicação
```text
{ INTERAÇÃO OBRIGATÓRIA: Perguntar e registrar o nome oficial da Aplicação (ou Ecossistema/Produto) da qual o código mapeado faz parte }
```
* **Comportamento da IA:** Antes de iniciar a varredura da árvore de diretórios, o agente solicita ao usuário o nome canônico da aplicação (`APP_CANONICAL_NAME`) e o diretório raiz (`ROOT_PATH`).
* **Saída gerada:** Criação do namespace raiz `id://app/<APP_CANONICAL_NAME>` que servirá de prefixo ou contexto para os artefatos de código.

### Gate 1.2 — Mapeamento Relacional do Banco de Dados
```text
{ forneça o mapeamento relacional do banco de dados }
```
* **Comportamento da IA:** Solicita ao usuário o esquema relacional do banco de dados (DDL, script de schema, `INFORMATION_SCHEMA`, ou dump estrutural de Tabelas, Colunas, Primary Keys, Foreign Keys, Unique Constraints e Indexes). Caso o usuário ainda não possua o arquivo extraído, a IA fornece imediatamente a query SQL de extração do catálogo relacional.
* **Semântica Estrutural:**
  * **Persistência e Reutilização:** Dados armazenados no banco relacional são classificados como `PERSISTENT_SHARED_STATE` (dados persistidos, transacionais, reutilizados ao longo do tempo e acessíveis por múltiplas fontes/aplicações simultaneamente).
  * **Grafo Relacional:** Mapeia explicitamente as arestas de integridade referencial (`PK <-> FK` explícitas no catálogo e chaves lógicas candidatas).

### Gate 1.3 — Extração de Stored Procedures ao Final do Nível 1
```text
{ fornecer o código-fonte das procedures listadas no arquivo de texto com o SELECT montado pela IA ao fim do mapeamento estrutural }
```
* **Comportamento da IA:** Ao concluir a varredura estrutural dos 700 módulos C#, a IA consolida todas as chamadas a *Stored Procedures*, *Functions* e *Triggers* detectadas nas strings de comando / ORMs / ADO.NET, grava o arquivo `01_procedures_pendentes_extracao.txt` contendo a lista deduplicada e o comando `SELECT` pronto para execução no SGBD, e **PAUSA A EXECUÇÃO** até que o usuário forneça o resultado dessa consulta (pré-requisito bloqueante para o Nível 2).

---

## 3. Taxonomia de Formas de Armazenamento de Dados

O Nível 1 classifica exaustivamente todas as formas de retenção de informação em duas grandes categorias físicas: **Armazenamento Persistente (Não-Volátil)** e **Armazenamento Temporário (Memória RAM / Volátil)**.

### 3.1. Armazenamento Persistente (Disco e Mídias Físicas/Externas)
Qualquer meio onde o dado sobrevive ao término do processo ou ciclo de energia da máquina:

| Categoria de Mídia / Meio | Código de Tipo (`MEDIA_CLASS`) | Descrição e Exemplos Mapeáveis no Código |
| :--- | :--- | :--- |
| **Banco de Dados Relacional** | `PERSIST_DB_RELATIONAL` | Tabelas, Views Materializadas, Índices em SGBDs (SQL Server, Oracle, PostgreSQL, MySQL, DB2). |
| **Disco Local / Sistema de Arquivos** | `PERSIST_DISK_LOCAL` | Arquivos locais (`.txt`, `.xml`, `.json`, `.csv`, `.dat`, `.bin`, logs, SQLite local, Memory-Mapped Files persistidos em disco). |
| **Rede / Compartilhamento (NAS/SAN)** | `PERSIST_DISK_NETWORK` | Caminhos UNC (`\\servidor\pasta\arquivo`), volumes montados via SMB/NFS. |
| **Mídias Ópticas / Removíveis / Legadas** | `PERSIST_MEDIA_REMOVABLE` | CDs, DVDs, Fitas Magnéticas (LTO/Tape Backup), Pendrives, Cartões, ou registros físicos históricos/imutáveis ("pedras" / mídia fria WORM - *Write Once Read Many*). |
| **Armazenamento de Objetos / Nuvem** | `PERSIST_CLOUD_BLOB` | Buckets S3, Azure Blob Storage, FTP/SFTP remoto. |
| **Filas e Eventos Persistentes** | `PERSIST_QUEUE_LOG` | MSMQ, RabbitMQ (durable), Kafka topics, Event Store em disco. |
| **Configuração / Registro do SO** | `PERSIST_OS_CONFIG` | Windows Registry (`HKLM`/`HKCU`), `appsettings.json`, `web.config`, `app.config`, variáveis de ambiente persistidas. |

### 3.2. Armazenamento Temporário (Memória RAM / Volátil)
Dados que existem apenas durante o ciclo de vida da execução do processo ou sessão em memória principal.

---

## 4. Contrato de Filtragem de Memória RAM (Resolução do Problema de Escala de Metadados)

> **Problema Arquitetural Endereçado:**
> `/*?? aqui é necessário filtrar e definir o que realmente deve ser mapeado, um mapeamento completo de tudo que está armazenado em memória deve ficar maior que o próprio código, o que não será possível ser utilizado como metadados simplificados */`

Para evitar a explosão combinatória em um monolito de **700 módulos** (onde mapear cada variável local geraria metadados maiores que o próprio código-fonte), estabelece-se o **Contrato de Abstração de Memória Independente de Linguagem (*Language-Agnostic Memory Boundary Contract*)**:

### 4.1. Regra de Corte (O que DESCARTAR)
1. **Variáveis Locais de Método:** Contadores de loop (`i`, `j`), variáveis temporárias de cálculo intermediário, flags booleanas locais, strings auxiliares de formatação.
2. **Variáveis/Campos Privados de Classe (*Fields*):** Estado interno encapsulado que não atravessa fronteiras públicas nem representa cache compartilhado.
3. **Alocações Efêmeras de Escopo Fechado:** Objetos instanciados e destruídos dentro do mesmo método sem interação com I/O ou retorno.

### 4.2. Regra de Retenção (O que MAPEAR como Identidade de Memória RAM)
Apenas **4 classes de estruturas em memória** recebem Identidade Única (`id://mem/...`), pois são as únicas necessárias para reconstruir 100% do Call Flow no Nível 2:

1. **Envelopes de Fronteira de Chamada (`MEM_BOUNDARY_CONTRACT`):**
   * O vetor de **Parâmetros de Entrada** e o **Tipo de Retorno** na assinatura de cada método mapeado (DTOs, Entities, Value Objects ou tuplas que cruzam a fronteira entre `Método A -> Método B`).
2. **Contêineres de Trânsito de I/O (`MEM_IO_BUFFER`):**
   * Estruturas em RAM que recebem ou enviam dados diretamente para Banco ou Disco (ex: `DataTable`, `DataSet`, `IDataReader`, `MemoryStream`, `DbSet<T>`, listas desserializadas de arquivos).
3. **Estado Compartilhado / Cache de Processo (`MEM_SHARED_CACHE`):**
   * `MemoryCache`, variáveis `static` mutáveis que retêm dados entre requisições, Singletons de estado, `HttpContext.Session`, `HttpContext.Items`.
4. **Cache Distribuído em Memória (`MEM_DISTRIBUTED_RAM`):**
   * Estruturas mantidas em Redis, Memcached ou In-Memory Grids.

> **Resultado Prático:** O volume de metadados de memória cai para **< 3% do tamanho do código-fonte**, mantendo 100% da linhagem de dados entre entradas, transformações e persistência.

---

## 5. Modelo Formal de Identidade Única da Informação (UID Schema)

Toda informação mapeada no Nível 1 recebe um **URI Canônico Determinístico** que garante desambiguação absoluta entre tipos de origem:

```text
Formato Geral:
id://<DOMINIO_ORIGEM>/<SUBTIPO>/<NAMESPACE_HIERARQUICO>#<HASH_ASSINATURA>
```

### 5.1. Tabela de Prefixos e Regras de Construção de Identidade

| Origem da Informação | Prefixo Canônico | Estrutura da Identidade Única | Garantia de Isolamento |
| :--- | :--- | :--- | :--- |
| **1. Banco de Dados Relacional** | `id://db-rel/` | `id://db-rel/<catalog>/<schema>/<table>` e `id://db-rel/<catalog>/<schema>/<table>/<column>` | Nunca pode ser confundida com classes C#, arquivos ou memória. Classifica explicitamente o dado como parte de estrutura relacional persistida. |
| **2. Objetos Executáveis de Banco (Procedures/Functions/Triggers)** | `id://db-proc/` | `id://db-proc/<catalog>/<schema>/<object_type>/<proc_name>` | Entidades externas de banco interpretadas como objetos de primeira classe com identidade própria. |
| **3. Arquivos Locais / Disco / Mídias** | `id://storage/` | `id://storage/<MEDIA_CLASS>/<root_volume_or_share>/<normalized_relative_path>` | Distingue explicitamente arquivos locais (`PERSIST_DISK_LOCAL`), rede (`PERSIST_DISK_NETWORK`) e mídias físicas (`PERSIST_MEDIA_REMOVABLE`). |
| **4. Memória RAM (Contratos Filtrados)** | `id://mem-ram/` | `id://mem-ram/<MEM_CLASS>/<owner_code_uid>/<data_type_canonical>` | Identidade estritamente distinta de banco, disco e de outros tipos de armazenamento em memória (`BOUNDARY` vs `IO_BUFFER` vs `CACHE`). |
| **5. Código-Fonte (Raiz, Módulo, Classe, Método)** | `id://code/` | `id://code/<app_name>/<root_folder_hash>/<module_name>/<namespace>/<class_name>/<method_signature_id>` | Baseada na pasta raiz + aplicação + módulo + classe + assinatura tipada do método. Descarta variáveis de classe e de método. |
| **6. Bibliotecas e Dependências** | `id://lib/` | `id://lib/<internal_or_external>/<assembly_or_nuget_name>/<version>` | Identifica a origem de cada dependência antes da resolução do Call Flow. |

---

## 6. Mapeamento Específico para Código C# (.NET)

Para suportar a evolução contínua e leitura incremental de **700 módulos C#**, o mapeamento de código obedece à seguinte ordem estrita de execução:

### 6.1. Fase 1A — Mapeamento Prévio de Bibliotecas e Grafo de Dependências
Antes de analisar qualquer arquivo `.cs`, o motor analisa a camada de projeto (`.sln`, `.csproj`, `packages.config`, `Directory.Build.props`):
1. **Inventário de Dependências Internas (`ProjectReference`):** Constrói o DAG (Grafo Acíclico Direcionado) entre os 700 módulos do monolito.
2. **Inventário de Bibliotecas Externas (`PackageReference` / `Reference` / DLLs):** Registra cada biblioteca com seu `id://lib/external/...` e classifica seu papel (ORM/Acesso a Dados como Dapper/EF/ADO.NET, UI como WinForms/WPF/ASP.NET, I/O de Disco, Serialização, etc.).
3. **Ordem Topológica de Build/Leitura:** Ordena os 700 módulos das folhas (projetos base/Core sem dependências internas) até o topo (projetos de UI/API/Orquestração), garantindo que ao mapear um módulo $M_k$, todas as suas dependências $M_{1..k-1}$ já possuam identidades resolvidas.

### 6.2. Fase 1B — Mapeamento de Assinaturas de Código (Classes e Métodos)
* **Unidades Principais de Identidade:** Apenas **`Namespaces` -> `Classes / Interfaces / Structs` -> `Métodos / Propriedades com lógica`**.
* **Descarte Explícito:** Variáveis de classe (fields privados) e variáveis internas de métodos são descartadas como identidades estruturais.
* **Assinatura Canônica e Reutilização Incremental:**
  Cada método é mapeado pela sua assinatura normalizada e um hash SHA-256 do seu corpo AST (`BodyAstHash`):
  ```json
  {
    "uid": "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento/Faturamento.Services/NotaFiscalService/EmitirNota(Int64,NotaFiscalDto):ResultadoEmissaoDto",
    "app_name": "ERP_Monolito",
    "module_id": "Mod042_Faturamento",
    "relative_file_path": "src/Mod042_Faturamento/Services/NotaFiscalService.cs",
    "file_content_hash": "sha256:4a8b9c...",
    "symbol_type": "METHOD",
    "parent_class_uid": "id://code/ERP_Monolito/root_8f3a/Mod042_Faturamento/Faturamento.Services/NotaFiscalService",
    "access_modifier": "public",
    "signature": {
      "name": "EmitirNota",
      "parameters": [
        { "position": 0, "type": "System.Int64", "mem_uid": "id://mem-ram/MEM_BOUNDARY_CONTRACT/.../param0_Int64" },
        { "position": 1, "type": "Faturamento.Contracts.NotaFiscalDto", "mem_uid": "id://mem-ram/MEM_BOUNDARY_CONTRACT/.../param1_NotaFiscalDto" }
      ],
      "return_type": { "type": "Faturamento.Contracts.ResultadoEmissaoDto", "mem_uid": "id://mem-ram/MEM_BOUNDARY_CONTRACT/.../ret_ResultadoEmissaoDto" }
    },
    "body_ast_hash": "sha256:e91d2f...",
    "referenced_libraries": ["id://lib/external/System.Data.SqlClient/4.8.5"],
    "detected_storage_touchpoints": [
      "id://db-proc/ERP_DB/dbo/PROC/sp_Faturamento_EmitirNota",
      "id://db-rel/ERP_DB/dbo/TB_NOTA_FISCAL",
      "id://storage/PERSIST_DISK_NETWORK/share_nfe/xml_saida"
    ]
  }
  ```
* **Reutilização Incremental em Modificações (`Delta Update`):**
  Quando o código sofre alteração, o motor compara o `file_content_hash` e o `body_ast_hash`:
  * Se `body_ast_hash` não mudou: **0% de reprocessamento**.
  * Se o corpo do método mudou, mas a assinatura permaneceu igual: o `uid` do método **não muda** (preservando os vínculos nos outros 699 módulos), atualizando apenas suas referências internas.

---

## 7. Artefato de Saída Obrigatório: Extração de Procedures para o Usuário

Ao término do mapeamento estrutural dos 700 módulos, o motor gera automaticamente o arquivo:
`01_procedures_pendentes_extracao.txt`

### Formato Padrão do Arquivo Gerado (`01_procedures_pendentes_extracao.txt`)
```sql
-- ============================================================================
-- ARQUIVO GERADO AUTOMATICAMENTE PELO NÍVEL 1 (STRUCTURAL COMPREHENSION)
-- APLICAÇÃO: <APP_CANONICAL_NAME>
-- TOTAL DE PROCEDURES ÚNICAS IDENTIFICADAS NOS 700 MÓDULOS: <N>
-- INSTRUÇÃO AO USUÁRIO: Execute o SELECT abaixo no seu banco de dados e
-- forneça o resultado exportado (CSV/JSON/TXT) para liberar o Nível 2.
-- ============================================================================

-- [OPÇÃO 1: SQL SERVER (T-SQL)]
SELECT 
    DB_NAME() AS [Catalog],
    SCHEMA_NAME(o.schema_id) AS [Schema],
    o.name AS [ProcedureName],
    o.type_desc AS [ObjectType],
    m.definition AS [SourceCode]
FROM sys.sql_modules m
INNER JOIN sys.objects o ON m.object_id = o.object_id
WHERE o.name IN (
    'sp_Faturamento_EmitirNota',
    'sp_Estoque_BaixarSaldo',
    'sp_Financeiro_GerarTitulo'
    -- [... lista deduplicada completa extraída do código C# ...]
)
ORDER BY SCHEMA_NAME(o.schema_id), o.name;

-- [OPÇÃO 2: ORACLE (PL/SQL)]
SELECT 
    OWNER AS Catalog,
    OBJECT_NAME AS ProcedureName,
    OBJECT_TYPE AS ObjectType,
    LISTAGG(TEXT, '') WITHIN GROUP (ORDER BY LINE) AS SourceCode
FROM ALL_SOURCE
WHERE NAME IN (
    'SP_FATURAMENTO_EMITIRNOTA',
    'SP_ESTOQUE_BAIXARSALDO',
    'SP_FINANCEIRO_GERARTITULO'
)
GROUP BY OWNER, OBJECT_NAME, OBJECT_TYPE;

-- [OPÇÃO 3: POSTGRESQL]
SELECT 
    current_database() AS catalog,
    n.nspname AS schema,
    p.proname AS procedure_name,
    pg_get_functiondef(p.oid) AS source_code
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname IN (
    'sp_faturamento_emitirnota',
    'sp_estoque_baixarsaldo',
    'sp_financeiro_gerartitulo'
);
```
