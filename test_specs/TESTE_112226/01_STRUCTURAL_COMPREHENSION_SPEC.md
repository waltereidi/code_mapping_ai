# Nível 1: Especificação de Compreensão Estrutural (`Structural Comprehension`)

## 1. Objetivo e Papel na Hierarquia
O **Nível 1 (Structural Comprehension)** é a camada fundacional de todo o sistema de mapeamento. Sua responsabilidade é inventariar e catalogar todas as estruturas de código, memória e persistência, atribuindo a cada elemento um **Identificador Único Universal e Determinístico (`UID` / `URN`)**.

> **Invariante de Unicidade do Nível 1:**
> Todo o mapeamento gerado neste nível deve conter **apenas informações únicas** para todas as informações que forem somadas ao catálogo global. Nenhuma identidade pode colidir ou ser confundida entre diferentes naturezas de armazenamento (banco relacional vs. arquivo em disco vs. memória RAM vs. código-fonte).

---

## 2. Pré-Requisito de Infraestrutura: Identificação da Aplicação e Pasta Raiz

Antes de iniciar qualquer varredura de código ou persistência, o motor de mapeamento de infraestrutura **deve obrigatoriamente**:

1. **Perguntar / Obter o Nome da Aplicação (`app_id`)**:
   - Caso não esteja declarado no manifesto de inicialização, o mapeador deve solicitar explicitamente ao operador/configuração: *"Qual é o nome canônico da aplicação da qual este código mapeado faz parte?"*
   - O `app_id` é normalizado em formato `slug` imutável (ex.: `erp-corporativo`, `core-billing-monolith`).
2. **Estabelecer a Pasta Raiz como Identidade Única (`root_uid`)**:
   - O diretório raiz do repositório/monolito é convertido em uma âncora de identidade única:
     ```text
     urn:ia1:root:<app_id>:<root_fingerprint>
     ```
   - Todos os caminhos relativos de soluções (`.sln`), projetos/módulos (`.csproj`) e arquivos derivam hierarquicamente dessa raiz, garantindo que dois arquivos com o mesmo nome em módulos diferentes nunca gerem a mesma identidade.

---

## 3. Modelo Universal de Identidade da Informação (UIIM)

Cada fonte de dados e estrutura do sistema recebe uma identidade formalizada sob o esquema `urn:ia1:<categoria>:<subcategoria>:<escopo>:<identificador_canonico>`.

### 3.1. Taxonomia Completa de Identidades por Fonte de Dados

| Categoria | Prefixo de Identidade (`URN`) | Descrição e Regras de Isolamento |
| :--- | :--- | :--- |
| **Banco de Dados Relacional (Tabelas/Views/Relacionamentos)** | `urn:ia1:db:rel:<engine>:<catalog>.<schema>.<table>` | Identifica inequivocamente que a informação provém de uma estrutura de banco relacional (ex.: `sqlserver`, `oracle`, `postgres`). Nunca pode ser confundida com classes C# ou arquivos de mesmo nome. Inclui metadados de PK, FK e cardinalidade. |
| **Colunas / Chaves Relacionais** | `urn:ia1:db:rel:<engine>:<catalog>.<schema>.<table>#<column>` | Sub-identidade opcional para rastreamento fino de chaves primárias e estrangeiras (`PK`, `FK`). |
| **Entidades Externas de Banco (Procedures, Functions, Triggers)** | `urn:ia1:db:ext:<type>:<engine>:<catalog>.<schema>.<object_name>(<param_types>)` | Procedures (`proc`), Functions (`func`) e Triggers (`trig`) são interpretadas como objetos executáveis externos de primeira classe com identidade própria. |
| **Armazenamento Local em Computador / Sistema de Arquivos** | `urn:ia1:storage:local-fs:<app_id>:<normalized_path_or_pattern>` | Identifica arquivos lidos ou gravados no disco local da máquina/servidor (ex.: XML, JSON, CSV, logs, configurações locais). |
| **Mídias Persistentes e Físicas / Arquivamento** | `urn:ia1:storage:medium:<medium_type>:<volume_id>/<resource_id>` | Mapeia todas as formas de persistência física, histórica ou externa: disco magnético/SSD (`disk`), compartilhamento de rede (`nas-smb`), mídias ópticas (`optical-cd`, `dvd`), fita/cold storage (`tape`), ou registros físicos estáticos/imutáveis (`immutable-stone`, `hardware-token`). |
| **Memória RAM — Contrato de Tipo/Estrutura** | `urn:ia1:mem:contract:<app_id>:<module_id>:<canonical_type_name>` | Identifica estruturas de dados em memória (DTOs, Entidades em RAM, Payloads) independentes da linguagem. |
| **Memória RAM — Cache / Sessão / Buffer / Stream** | `urn:ia1:mem:<ram_kind>:<app_id>:<store_name>:<key_pattern>` | Distingue explicitamente os tipos de armazenamento temporário em memória: `cache-inproc`, `cache-dist` (ex.: Redis), `session`, `stream-buffer`, `queue-mem`, `static-state`. |
| **Código-Fonte — Módulo / Projeto** | `urn:ia1:code:module:<app_id>:<module_name>` | Identidade única de cada um dos 700 módulos/projetos do monolito. |
| **Código-Fonte — Dependência / Biblioteca** | `urn:ia1:code:lib:<ecosystem>:<package_or_assembly>@<version>` | Identidade única de bibliotecas externas (NuGet, DLLs de terceiros, SDKs) ou referências internas. |
| **Código-Fonte — Classe / Interface / Struct** | `urn:ia1:code:type:<app_id>:<module_name>:<namespace>.<TypeName>` | Identidade estrutural primária de tipos no código-fonte. |
| **Código-Fonte — Método / Propriedade Executável** | `urn:ia1:code:method:<app_id>:<module_name>:<namespace>.<TypeName>::<MethodName>(<ParamTypes>):<ReturnType>` | Identidade estrutural primária de unidades de execução no código-fonte. |

---

## 4. Especificação Detalhada por Domínio Estrutural

### 4.1. Relacionamento de Tabelas e Persistência em Banco Relacional
- **Premissa**: Dados armazenados no banco garantem que sejam dados persistidos e reutilizados, podendo ser consumidos e alterados por múltiplas fontes (múltiplos módulos, aplicações ou procedures).
- **Requisitos de Mapeamento**:
  1. Toda tabela ou view recebe uma identidade `urn:ia1:db:rel:...` contendo:
     - `db_engine`: Motor relacional (`mssql`, `postgresql`, `oracle`, `mysql`, etc.).
     - `catalog` e `schema`: Exemplo `ERP_PROD.dbo`.
     - `table_name`: Nome canônico em caixa alta/normalizada.
     - `persistence_nature`: Fixo como `"RELATIONAL_PERSISTENT_SHARED"`.
  2. **Grafo de Relacionamentos de Tabelas**:
     - Mapear todas as relações `FOREIGN KEY` explícitas (DDL/migrations/EDMX/DbContext) e implícitas (JOINs recorrentes em SQL/LINQ):
       ```json
       {
         "relationship_uid": "urn:ia1:db:rel-edge:mssql:ERP.dbo.PEDIDO#CLIENTE_ID->ERP.dbo.CLIENTE#ID",
         "source_table_uid": "urn:ia1:db:rel:mssql:ERP.dbo.PEDIDO",
         "target_table_uid": "urn:ia1:db:rel:mssql:ERP.dbo.CLIENTE",
         "cardinality": "N:1"
       }
       ```
  3. **Entidades Externas (Procedures, Functions, Triggers)**:
     - Tratadas como objetos com identidade própria (`urn:ia1:db:ext:proc:...`).
     - O mapeamento registra a assinatura de parâmetros de entrada/saída da procedure e quais tabelas relacionais (`urn:ia1:db:rel:...`) ela lê ou modifica internamente (quando o script SQL estiver disponível).

### 4.2. Mapeamento de Armazenamento Persistente em Disco e Outras Mídias
- Qualquer operação de I/O fora do banco relacional deve classificar o meio físico/lógico exato:
  - `local-fs`: Arquivos no sistema de arquivos do computador local (`File.ReadAllText`, `FileStream`, `DirectoryInfo`).
  - `network-fs`: Caminhos UNC (`\\servidor\pasta\arquivo.ext`), mapeamentos SMB/NFS.
  - `optical-cd` / `removable`: Unidades ópticas/removíveis ou imagens ISO arquivadas.
  - `cold-archive` / `immutable-stone`: Armazenamentos permanentes de leitura única (WORM, fitas LTO, registros físicos imutáveis).
  - `nosql-doc` / `blob-store`: Object storage (S3, Azure Blob) ou bancos baseados em arquivo (SQLite, LiteDB, Access `.mdb`).

### 4.3. Contrato de Memória RAM (Independente de Linguagem) e Regra de Filtragem (`/*?? ... */`)

> **Resolução Arquitetural para o Filtro de Memória RAM:**
> *Problema*: Um mapeamento irrestrito de tudo que está armazenado em memória RAM (cada variável local, contador de loop, alocação temporária na pilha/heap) geraria metadados maiores que o próprio código-fonte, tornando impossível seu uso como metadados simplificados para IA.
>
> *Solução (Contrato de Fronteira de Memória)*:
> O mapeamento de memória RAM **não mapeia estados efêmeros de execução interna**. Ele mapeia exclusivamente **Contratos de Fronteira de Dados** e **Canais Nomeados de Armazenamento em Memória**.

#### O que É Mapeado em Memória RAM (Com Identidade Distinta por Tipo de Memória):
1. **Contratos de Estrutura em Memória (`urn:ia1:mem:contract:...`)**:
   - A forma agnóstica de linguagem de uma Classe/Struct/Record/Interface que transporta dados entre métodos (input/output de métodos).
   - O contrato agnóstico registra apenas:
     - `identity`: UID único do contrato em memória.
     - `shape_category`: `ENTITY | DTO | COMMAND | EVENT | VALUE_OBJECT | COLLECTION | PRIMITIVE_WRAPPER`.
     - `structural_signature_hash`: Hash da estrutura pública exposta.
2. **Armazenamentos Temporários Nomeados em Memória** (cada um com prefixo distinto para nunca se confundirem no Call Flow):
   - `urn:ia1:mem:cache-inproc:...`: Cache em memória do processo (`MemoryCache`, dicionários estáticos de cache).
   - `urn:ia1:mem:cache-dist:...`: Cache distribuído em RAM (`IDistributedCache`, Redis, Memcached).
   - `urn:ia1:mem:session:...`: Sessão de usuário ou contexto de requisição (`HttpContext.Session`, `CallContext`, `AsyncLocal`).
   - `urn:ia1:mem:stream-buffer:...`: Streams em memória (`MemoryStream`, `Pipe`, `Channel<T>`, `BlockingCollection<T>`).
   - `urn:ia1:mem:static-state:...`: Singletons ou estados estáticos compartilhados entre chamadas em RAM.

#### O que é Explicitamente DESCARTADO no Nível 1:
- **Variáveis locais de métodos** (ex.: `var i = 0;`, `string temp = ...;`).
- **Variáveis internas/campos privados de classe** (`private int _counter;`).
- **Alocações efêmeras de pilha (stack frames) e ponteiros de execução**.
*(Nota: Nomes de variáveis com valor semântico de negócio serão lidos apenas pelo coletor léxico do **Nível 3** para compor o Glossário de tradução natural, jamais como identidades estruturais do Nível 1).*

---

## 5. Especificação de Mapeamento de Código C# (`.NET`)

Para garantir determinismo, reuso incremental e suporte a **700 módulos**, o mapeador C# segue 3 regras obrigatórias:

### 5.1. Etapa Prévia Obrigatória: Identificação de Bibliotecas e Dependências
Antes de mapear as classes e métodos de um projeto C# (`.csproj`), o mapeador deve extrair o **Mapa de Dependências do Módulo**:
1. **Referências Internas (`ProjectReference`)**: Quais outros módulos do monolito este projeto consome.
2. **Bibliotecas Externas (`PackageReference`, `packages.config`, `Reference`/DLLs)**: Nome do pacote/assembly, versão e namespace raiz exportado.
3. **Tabela de Resolução de Símbolos**: Permite saber imediatamente, antes de iniciar o Call Flow (Nível 2), se uma chamada em C# aponta para:
   - Um método interno do mesmo módulo;
   - Um método de outro módulo dentro dos 700 módulos do monolito;
   - Uma biblioteca de infraestrutura conhecida (ex.: `System.Data.SqlClient`, `Dapper`, `Microsoft.EntityFrameworkCore`, `System.IO`, `Newtonsoft.Json`);
   - Uma API externa.

### 5.2. Mapeamento Baseado em Assinaturas (Classes e Métodos)
- **Elementos Principais Geradores de Identidade**:
  1. **Classes / Interfaces / Structs / Enums Principais**:
     - Identidade: `urn:ia1:code:type:<app_id>:<module_id>:<namespace>.<TypeName>`
     - Metadados: Modificadores (`public`, `abstract`, `static`), herança (`base_type_uid`), interfaces implementadas (`implemented_interface_uids`) e atributos de classe.
  2. **Métodos (incluindo Construtores e Acessores customizados)**:
     - Identidade: `urn:ia1:code:method:<app_id>:<module_id>:<namespace>.<TypeName>::<MethodName>(<CanonicalParamTypeUIDs>):<CanonicalReturnTypeUID>`
     - Metadados: Assinatura completa tipada, modificadores (`async`, `virtual`, `override`, `static`), atributos/annotations (`[HttpGet]`, `[Authorize]`, `[Transactional]`).
- **Regra de Descarte Estrutural**:
  - **Descartar variáveis de classe (fields)** e **descartar variáveis internas de métodos** na geração de identidades do Nível 1.

### 5.3. Suporte a Reutilização e Atualização Incremental (`Signature & Body Hashing`)
Para que o mapeamento possa ser reutilizado e incrementado quando houver modificações no código sem remapear os 700 módulos do zero:
- Cada Classe e cada Método recebe dois hashes SHA-256 truncados (16 bytes hex):
  1. `sig_hash` (**Hash de Assinatura**): Calculado apenas sobre o nome qualificado, tipos de parâmetros, tipo de retorno e modificadores públicos.
     - *Se `sig_hash` não mudou*: Nenhum módulo externo que chama este método precisa ter suas referências de identidade recriadas.
  2. `body_hash` (**Hash de Implementação Interna**): Calculado sobre a AST normalizada do corpo do método (ignorando comentários e formatação/espaços).
     - *Se `body_hash` não mudou*: O mapeamento de Call Flow (Nível 2) deste método permanece 100% válido em cache e não precisa ser reprocessado.

---

## 6. Regra de Deduplicação e Soma de Informações Únicas

Quando os metadados de todos os módulos são somados no Catálogo Estrutural Global (`L1_Global_Catalog`):
1. **Chave Primária Global**: O `uid` (`urn:ia1:...`) é a chave primária única.
2. **Entidades Compartilhadas** (como uma tabela `urn:ia1:db:rel:mssql:ERP.dbo.CLIENTE`, uma procedure `urn:ia1:db:ext:proc:mssql:ERP.dbo.SP_CALCULA_SALDO` ou uma biblioteca `urn:ia1:code:lib:nuget:Dapper@2.1.0`) são registradas **uma única vez** no catálogo global do Nível 1, mantendo uma lista de `referenced_by_modules` sem jamais duplicar sua identidade.

---

## 7. Exemplo de Saída do Nível 1 (Resumo Estrutural)

```json
{
  "layer": 1,
  "layer_name": "structural_comprehension",
  "application": {
    "app_id": "erp-monolith-core",
    "app_display_name": "ERP Corporativo Monolito",
    "root_uid": "urn:ia1:root:erp-monolith-core:a9f4c2e1"
  },
  "dependencies_manifest": [
    {
      "uid": "urn:ia1:code:lib:nuget:Dapper@2.1.24",
      "category": "ORM_DATA_ACCESS",
      "used_by_modules": ["urn:ia1:code:module:erp-monolith-core:Faturamento.Infra"]
    }
  ],
  "unique_identities": [
    {
      "uid": "urn:ia1:db:rel:mssql:ERP_DB.dbo.TB_PEDIDO",
      "kind": "DB_RELATIONAL_TABLE",
      "persistence": "PERSISTENT_SHARED",
      "relationships": [
        {
          "type": "FOREIGN_KEY",
          "target_uid": "urn:ia1:db:rel:mssql:ERP_DB.dbo.TB_CLIENTE",
          "source_key": "ID_CLIENTE",
          "target_key": "ID_CLIENTE"
        }
      ]
    },
    {
      "uid": "urn:ia1:db:ext:proc:mssql:ERP_DB.dbo.SP_FECHAR_PEDIDO(INT,DECIMAL)",
      "kind": "DB_EXTERNAL_PROCEDURE",
      "persistence": "PERSISTENT_EXECUTABLE"
    },
    {
      "uid": "urn:ia1:storage:local-fs:erp-monolith-core:/var/export/nfe/{ano}/{mes}/*.xml",
      "kind": "LOCAL_DISK_FILE",
      "medium": "disk-local"
    },
    {
      "uid": "urn:ia1:mem:contract:erp-monolith-core:Faturamento.Domain:Faturamento.Domain.DTOs.PedidoFechamentoDto",
      "kind": "RAM_MEMORY_CONTRACT",
      "shape_category": "DTO",
      "sig_hash": "7b81e90a11c34f22"
    },
    {
      "uid": "urn:ia1:code:type:erp-monolith-core:Faturamento.Application:Faturamento.Application.Services.PedidoAppService",
      "kind": "CSHARP_CLASS",
      "sig_hash": "4d92b10c88a12e55"
    },
    {
      "uid": "urn:ia1:code:method:erp-monolith-core:Faturamento.Application:Faturamento.Application.Services.PedidoAppService::FecharPedidoAsync(urn:ia1:mem:contract:erp-monolith-core:Faturamento.Domain:Faturamento.Domain.DTOs.PedidoFechamentoDto):System.Threading.Tasks.Task<System.Boolean>",
      "kind": "CSHARP_METHOD",
      "parent_type_uid": "urn:ia1:code:type:erp-monolith-core:Faturamento.Application:Faturamento.Application.Services.PedidoAppService",
      "sig_hash": "c3019fa451209b8e",
      "body_hash": "99e41bc7281a00f1"
    }
  ]
}
```
