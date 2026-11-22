# Especificação do Nível 1: Structural Comprehension (Compreensão Estrutural)

## 1. Objetivo e Regra de Ouro do Nível 1

O **Nível 1 (Structural Comprehension)** estabelece o catálogo canônico de **Identidades Únicas da Informação**.
Nenhuma análise de fluxo (Nível 2) ou de domínio/arquitetura (Nível 3) pode existir sem que cada recurso de dados ou unidade estrutural de código possua uma identidade única, determinística e livre de colisões.

> **Regra de Ouro (Unicidade sob Soma/União):**
> Neste nível, todo o mapeamento deve funcionar como um **Conjunto Matemático Estrito (`Set<Identity>`)**. Quando os mapeamentos de 700 módulos forem somados, qualquer referência à mesma tabela de banco, ao mesmo arquivo em disco ou ao mesmo método de classe deve produzir **exatamente a mesma chave canônica (`IdentityURN`)**, garantindo zero duplicidade.

---

## 2. Modelo Universal de Identidade da Informação (`IdentityURN`)

Para garantir que uma identidade de banco relacional **nunca seja confundida** com uma identidade de arquivo local ou de processamento em memória RAM, todas as identidades seguem uma gramática formal de **URN Hierárquico Tipado**:

```text
urn:info:<natureza>:<meio_armazenamento>:<origem_raiz>:<caminho_hierarquico_qualificado>[#<sub_elemento>]
```

### 2.1. Taxonomia de Natureza e Meio (`<natureza>:<meio_armazenamento>`)

| Prefixo Canônico | Natureza da Informação | Meio Físico / Lógico | Garantias de Isolamento |
| :--- | :--- | :--- | :--- |
| `urn:info:db:rel:` | Persistência Estruturada Relacional | SGBD Relacional (SQL Server, Oracle, PostgreSQL, MySQL, DB2) | Classifica exclusivamente estruturas de banco relacional (Catalog/Schema/Table/View/Proc/Column). Nunca colide com classes ORM em memória. |
| `urn:info:storage:fs:` | Persistência em Disco Local/Rede | Sistema de Arquivos (NTFS, EXT4, SMB, NFS) | Identifica arquivos residentes no computador local ou volume montado. |
| `urn:info:storage:media:` | Persistência em Mídia Física/Imutável | Mídias Ópticas (CD/DVD/Blu-Ray), Fitas (LTO), Pedras/Cold Archive, WORM, Hardware Tokens | Identifica meios físicos externos, removíveis ou imutáveis de armazenamento persistente. |
| `urn:info:mem:code:` | Estrutura Executável em Memória RAM | Metadados de Código Carregado (Classes, Interfaces, Métodos) | Contrato agnóstico de linguagem para unidades estruturais de execução em RAM. |
| `urn:info:mem:state:` | Armazenamento Temporário em Memória RAM | Cache em RAM (`IMemoryCache`, `Static Dict`, `Redis/In-Memory`), Filas Voláteis, Buffers/Streams | Distingue estado compartilhado temporário em RAM de código estático (`mem:code`) e de disco (`storage:*`). |
| `urn:info:dep:pkg:` | Dependência Externa / Biblioteca | Assemblies Compilados (`.dll`), Pacotes NuGet, SDKs | Identifica bibliotecas externas utilizadas pelo projeto antes do mapeamento de fluxo. |

---

## 3. Especificação por Fonte de Dados

### 3.1. Identidade de Banco de Dados Relacional (`urn:info:db:rel`)

Os dados armazenados em banco relacional possuem duas propriedades estruturais fundamentais:
1. **Persistência e Reutilização:** Sobrevivem ao ciclo de vida da execução em memória.
2. **Acesso Multi-Fonte:** Podem ser lidos e gravados por múltiplos módulos, aplicações ou serviços distintos.

#### Estrutura da Identidade Relacional
```text
urn:info:db:rel:<engine>:<logical_server_or_alias>:<database_catalog>:<schema>:<object_type>:<object_name>[#<column_or_constraint>]
```
* **Exemplos:**
  * Tabela: `urn:info:db:rel:mssql:erp_cluster:db_faturamento:dbo:table:TB_NOTA_FISCAL`
  * Coluna: `urn:info:db:rel:mssql:erp_cluster:db_faturamento:dbo:table:TB_NOTA_FISCAL#ID_CLIENTE`
  * Stored Procedure: `urn:info:db:rel:mssql:erp_cluster:db_faturamento:dbo:proc:SP_CALCULA_IMPOSTO`

#### Mapeamento de Relacionamento entre Tabelas
O Nível 1 mapeia explicitamente a topologia relacional como arestas estruturais permanentes entre identidades `urn:info:db:rel`:
* `REL_FOREIGN_KEY`: Liga `TabelaOrigem#ColunaFK` $\to$ `TabelaDestino#ColunaPK`.
* `REL_IMPLICIT_JOIN`: Liga colunas que participam de cláusulas `JOIN` identificadas em queries SQL/LINQ/Dapper quando a FK física não está declarada no SGBD.
* `REL_VIEW_DEPENDENCY`: Liga uma `View` ou `Procedure` às tabelas base que ela lê ou modifica.

```json
{
  "identity": "urn:info:db:rel:mssql:default:erp_db:dbo:table:PEDIDO",
  "classification": "RELATIONAL_DATABASE_STRUCTURE",
  "persistence_guarantee": "PERSISTED_REUSABLE_MULTI_SOURCE",
  "columns": [
    { "name": "ID_PEDIDO", "identity": "urn:info:db:rel:mssql:default:erp_db:dbo:table:PEDIDO#ID_PEDIDO", "is_pk": true, "type": "INT" },
    { "name": "ID_CLIENTE", "identity": "urn:info:db:rel:mssql:default:erp_db:dbo:table:PEDIDO#ID_CLIENTE", "is_fk": true, "type": "INT" }
  ],
  "relationships": [
    {
      "type": "FOREIGN_KEY",
      "source_column": "urn:info:db:rel:mssql:default:erp_db:dbo:table:PEDIDO#ID_CLIENTE",
      "target_table": "urn:info:db:rel:mssql:default:erp_db:dbo:table:CLIENTE",
      "target_column": "urn:info:db:rel:mssql:default:erp_db:dbo:table:CLIENTE#ID_CLIENTE"
    }
  ]
}
```

---

### 3.2. Identidade de Armazenamento Persistente em Disco e Mídias Físicas (`urn:info:storage`)

Qualquer informação persistida fora de um SGBD relacional (arquivos do computador local, diretórios de rede, mídias ópticas como CDs/DVDs, fitas, armazenamento imutável/frio/"pedras") deve receber uma identidade que classifique seu meio físico, seu ponto de montagem/raiz lógica e seu formato estrutural.

#### Estrutura da Identidade de Armazenamento Físico
```text
urn:info:storage:<medium_class>:<mount_or_root_id>:<normalized_relative_path_or_pattern>:<data_format>
```

#### Classificação de Meios Persistentes (`<medium_class>`)
1. `fs:local` — Disco rígido/SSD do computador local (ex: arquivos de configuração, logs, XMLs fiscais, SQLite local, arquivos `.dat`/`.csv`).
2. `fs:network` — Compartilhamentos de rede (`\\servidor\pasta\...`, NFS, SMB).
3. `media:optical` — Mídias ópticas e graváveis (CD-ROM, DVD, Blu-Ray, imagens ISO montadas).
4. `media:removable` — Pendrives, cartões de memória, tokens criptográficos físicos (HSM/A3).
5. `media:immutable_cold` — Mídias físicas de arquivamento permanente/imutável (fitas magnéticas LTO, gravação física permanente/"pedra"/WORM - *Write Once Read Many*).
6. `blob:object` — Object Storage persistente em disco distribuído (S3, Azure Blob, MinIO).

* **Regra de Normalização de Caminhos Dinâmicos:**
  Se o código acessa `C:\Exportacao\NFe_2026_01.xml` via `Path.Combine(baseDir, $"NFe_{ano}_{mes}.xml")`, a identidade no Nível 1 é parametrizada pelo padrão canônico:
  `urn:info:storage:fs:local:EXPORTACAO_ROOT:NFe_{ano}_{mes}.xml:xml`

---

### 3.3. Identidade em Memória RAM e Resolução do Problema de Explosão de Metadados

> **Resolução Arquitetural para o Ponto Crítico da Especificação:**
> *"/*?? aqui é necessário filtrar e definir o que realmente deve ser mapeado, um mapeamento completo de tudo que está armazenado em memória deve ficar maior que o próprio código, o que não será possível ser utilizado como metadados simplificados */"*

#### Por que o filtro de memória RAM é obrigatório?
Em tempo de execução ou na Árvore Sintática Abstrata (AST), a memória RAM contém variáveis locais, contadores de loop (`int i`), alocações efêmeras na *stack*, expressões intermediárias, *backing fields* privados e objetos temporários na *heap*. Mapear tudo isso gera um grafo **5x a 15x maior que o próprio código-fonte**, inviabilizando o uso por LLMs ou motores de busca.

#### Contrato de Filtragem do que DEVE vs. NÃO DEVE ser mapeado em Memória RAM

Para que o mapeamento em memória seja **compacto, agnóstico de linguagem e suficiente para reconstruir 100% do Call Flow no Nível 2**, definimos a **Lei de Fronteira de Memória**:

| Categoria em Memória RAM | Status | Identidade Gerada | Justificativa Técnica |
| :--- | :--- | :--- | :--- |
| **1. Containers Estruturais de Código** (`Class`, `Interface`, `Struct`, `Record`, `Module`) | **MAPEAR (Obrigatório)** | `urn:info:mem:code:<root>:<module>:<ns>:<type>` | Define os nós estruturais de propriedade de comportamento em memória. |
| **2. Unidades Executáveis / Contratos de Chamada** (`Method`, `Constructor`, `Delegate/Handler`) | **MAPEAR (Obrigatório)** | `urn:info:mem:code:<root>:<module>:<ns>:<type>#<method_sig>` | São os vértices exatos por onde o fluxo de execução (Call Flow) transita. |
| **3. Armazenamento Temporário Compartilhado em RAM** (`IMemoryCache`, `Static Collections`, `Session`, `MemoryStream` de I/O, Filas em memória) | **MAPEAR (Obrigatório)** | `urn:info:mem:state:<subtype>:<scope>:<key_or_holder>` | São pontos onde um dado permanece retido em RAM entre chamadas distintas (essencial para rastrear estado em memória no Call Flow). |
| **4. Tipos de Fronteira (Parâmetros e Retornos de Métodos)** | **MAPEAR (Apenas Referência de Tipo na Assinatura)** | Embutido na assinatura do método (`#Method(ParamType)->ReturnType`) | Permite saber qual estrutura de dados entra e sai do método sem criar identidades para variáveis locais. |
| **5. Variáveis de Classe (Fields/Atributos internos)** | **DESCARTAR** | *Nenhuma* | Ruído estrutural; exceto se for um cache estático compartilhado (`static Dictionary/Cache`). |
| **6. Variáveis Locais de Métodos e Parâmetros Nomeados** | **DESCARTAR** | *Nenhuma* | Escopo puramente efêmero de *stack frame*; não altera a topologia de chamadas entre identidades. |
| **7. Expressões Internas, Literais e Alocações Efêmeras (`new Temp()`)** | **DESCARTAR** | *Nenhuma* | Aumentam o volume exponencialmente sem agregar valor ao grafo de dependências. |

#### Distinção Obrigatória entre Tipos de Armazenamento em Memória RAM
Toda informação processada ou retida em memória recebe um subtipo distinto para nunca misturar código executável com cache volátil:
1. `urn:info:mem:code:...` $\to$ Definição estrutural executável (Classe e Método).
2. `urn:info:mem:state:cache:...` $\to$ Cache em memória RAM (`MemoryCache`, `ConcurrentDictionary` estático).
3. `urn:info:mem:state:session:...` $\to$ Estado de sessão de usuário/contexto HTTP ou Desktop em RAM.
4. `urn:info:mem:state:buffer:...` $\to$ Buffers e Streams em memória (`MemoryStream`, `DataTable` desconectado em RAM) que servem de ponte para Disco ou Banco.

---

## 4. Raiz de Origem e Contrato Agnóstico de Linguagem

Para mapear o código-fonte de 700 módulos sem colisões (mesmo quando dois projetos possuem classes com o mesmo nome), toda identidade de código parte de uma **Pasta Raiz Canônica (`<root_origin>`)** e segue 5 níveis hierárquicos obrigatórios independentes da linguagem:

```text
urn:info:mem:code:<RepoRootId>:<ProjectOrModulePath>:<LogicalNamespace>:<TypeConstructName>#<NormalizedCallableSignature>
```

### Níveis do Contrato Agnóstico de Linguagem
1. **`<RepoRootId>`**: Identificador da pasta raiz do monolito (ex: `monolito_erp`).
2. **`<ProjectOrModulePath>`**: Caminho relativo normalizado do projeto/módulo a partir da pasta raiz (ex: `src/Faturamento/Faturamento.Core`). Garante unicidade mesmo se dois projetos tiverem o mesmo namespace.
3. **`<LogicalNamespace>`**: Namespace, pacote ou módulo lógico (ex: `Empresa.Erp.Faturamento.Services`).
4. **`<TypeConstructName>`**: Nome da `Class`, `Interface`, `Struct` ou `Module`, incluindo aridade genérica (ex: `NotaFiscalService` ou `RepositorioBase`1`).
5. **`<NormalizedCallableSignature>`**: Nome do método + tipos canônicos ordenados dos parâmetros + tipo de retorno (sem nomes de variáveis!).
   * Exemplo: `EmitirNota(urn:info:mem:code:...:PedidoDto)->urn:info:mem:code:...:ResultadoEmissaoDto`

---

## 5. Especificação de Mapeamento para C# (.NET)

### 5.1. Pré-Requisito: Identificação de Bibliotecas e Dependências do Projeto
Antes de mapear as classes e métodos de um projeto C#, o extrator do Nível 1 **deve ler os manifestos do projeto** (`.csproj`, `packages.config`, `Directory.Packages.props`, referências de `.dll`) para construir o mapa de dependências:

1. **Dependências Internas (`ProjectReference`)**:
   * Identifica quais outros módulos (dentre os 700) este projeto referencia.
   * Permite ordenar a leitura do monolito das folhas (projetos base sem dependências) até o topo (UI/APIs).
2. **Bibliotecas Externas e Frameworks (`PackageReference` / `Reference`)**:
   * Registra cada biblioteca como `urn:info:dep:pkg:nuget:<PackageId>:<Version>` ou `urn:info:dep:pkg:assembly:<AssemblyName>`.
   * Classifica o papel da biblioteca para uso imediato na etapa de Call Flow (Nível 2):
     * *Acesso a Dados / ORM*: `EntityFramework`, `Microsoft.EntityFrameworkCore`, `Dapper`, `System.Data.SqlClient`, `NHibernate`.
     * *I/O e Disco*: `System.IO`, `CsvHelper`, `EPPlus`, `iTextSharp`.
     * *Comunicação / UI / Mensageria*: `System.Windows.Forms`, `Microsoft.AspNetCore.Mvc`, `MediatR`, `MassTransit`, `RabbitMQ.Client`, `System.ServiceModel` (WCF).

### 5.2. Extração de Assinaturas C# (Classes e Métodos; Descarte de Variáveis)

O mapeamento de código C# no Nível 1 opera em modo **Signature-First**:

* **Elementos Incluídos (Parte Principal):**
  1. `class`, `interface`, `struct`, `record` (com modificadores, classe base e interfaces implementadas).
  2. `method`, `constructor`, `operator` (com modificadores de visibilidade, nome, parâmetros tipados e tipo de retorno).
* **Elementos Explicitamente Descartados:**
  1. Variáveis de classe (*fields* privados/protegidos/públicos e *auto-properties* puras de armazenamento sem lógica).
  2. Variáveis locais declaradas dentro do corpo dos métodos.

### 5.3. Formato Reutilizável e Atualização Incremental (Hashes de Evolução)

Para que o mapeamento de 700 módulos **não precise ser refeito do zero** quando o código sofrer modificações, cada registro de Classe e Método no Nível 1 contém dois hashes criptográficos curtos (SHA-256 truncado em 16 hex chars):

1. **`signature_hash`**: Calculado exclusivamente sobre a declaração da classe/assinatura do método (nome, visibilidade, tipos de entrada/saída, herança).
   * *Se o `signature_hash` não mudou:* A identidade pública do método e os contratos dos seus chamadores externos permanecem **100% válidos**.
2. **`body_ast_hash`**: Calculado sobre a árvore sintática normalizada do corpo do método (ignorando comentários e espaços em branco).
   * *Se apenas o `body_ast_hash` mudou:* A identidade no Nível 1 é mantida intacta, e apenas o micro-agregado de Call Flow (Nível 2) daquele método específico é recalculado!

#### Schema JSON Canônico de Código C# no Nível 1
```json
{
  "project_identity": "urn:info:mem:code:monolito_root:src/Faturamento.Service",
  "dependencies": {
    "internal_projects": [
      "urn:info:mem:code:monolito_root:src/Core.Domain",
      "urn:info:mem:code:monolito_root:src/Infra.Data"
    ],
    "external_libraries": [
      { "identity": "urn:info:dep:pkg:nuget:Dapper:2.1.28", "category": "DATA_ACCESS_ORM" },
      { "identity": "urn:info:dep:pkg:nuget:Newtonsoft.Json:13.0.3", "category": "SERIALIZATION" }
    ]
  },
  "types": [
    {
      "identity": "urn:info:mem:code:monolito_root:src/Faturamento.Service:Empresa.Faturamento:FaturamentoAppService",
      "kind": "CLASS",
      "file_relative_path": "src/Faturamento.Service/FaturamentoAppService.cs",
      "implements": [
        "urn:info:mem:code:monolito_root:src/Faturamento.Contracts:Empresa.Faturamento:IFaturamentoAppService"
      ],
      "signature_hash": "a94f1c8e02b3d114",
      "methods": [
        {
          "identity": "urn:info:mem:code:monolito_root:src/Faturamento.Service:Empresa.Faturamento:FaturamentoAppService#ProcessarFatura(System.Int32,System.Boolean)->Empresa.Faturamento.ResultadoFaturaDto",
          "name": "ProcessarFatura",
          "visibility": "PUBLIC",
          "parameter_type_identities": [
            "urn:info:dep:pkg:dotnet:System.Int32",
            "urn:info:dep:pkg:dotnet:System.Boolean"
          ],
          "return_type_identity": "urn:info:mem:code:monolito_root:src/Faturamento.Contracts:Empresa.Faturamento:ResultadoFaturaDto",
          "signature_hash": "7c2e90f411a8b532",
          "body_ast_hash": "e3b0c44298fc1c14"
        }
      ]
    }
  ]
}
```
