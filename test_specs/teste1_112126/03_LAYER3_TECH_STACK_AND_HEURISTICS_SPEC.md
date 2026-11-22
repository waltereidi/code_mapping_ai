# Especificação do Nível 3: Tech Stack & Client Heuristics (Agrupamento Tecnológico, Domínios e Heurísticas de Negócio)

## 1. Objetivo e Composição sobre os Níveis 1 e 2

O **Nível 3 (Tech Stack & Client Heuristics)** é a camada de síntese arquitetural e semântica.
Enquanto o Nível 1 define **o que existe** (identidades únicas) e o Nível 2 define **como as identidades conversam** (call flows), o Nível 3 agrupa essas estruturas em **Aplicações, Artefatos, Tech Stacks, Domínios, Heurísticas de Negócio Inter-Aplicações e Glossários Vinculados a Fluxos**.

> **Invariante de Composição:**
> Nenhum grupo, domínio, heurística ou termo de glossário no Nível 3 pode existir de forma abstrata ou desconectada. Todo elemento do Nível 3 é definido formalmente como uma tupla composta por:
> $$\text{Cluster}_{L3} = \langle \text{Metadados Semânticos}, \{ \text{IdentityURN}_{L1} \}, \{ \text{CallFlowId}_{L2} \} \rangle$$

---

## 2. Mapeamento de Aplicações, Principais Artefatos e Nomes de Arquivos

Em um monolito de 700 módulos, múltiplos projetos compilam para formar **Artefatos** que são empacotados em **Aplicações Executáveis / Implantáveis**.

### 2.1. Hierarquia Física e de Implantação
1. **Aplicação (`ApplicationIdentity`):** Unidade executável ou implantável percebida pelo cliente ou infraestrutura (ex: `ERP.Desktop.WinForms`, `PortalCliente.Web`, `MotorFaturamento.WindowsService`, `IntegradorFiscal.Worker`).
2. **Artefato Principal (`ArtifactIdentity`):** O binário, pacote ou banco resultante do build de um projeto (ex: `Empresa.Faturamento.Service.dll`, `ErpClient.exe`, `ErpDatabase.dacpac`).
3. **Arquivo Físico (`SourceFileDescriptor`):** O nome do arquivo (`FileName`) e caminho relativo (`RelativePath`) onde as identidades do Nível 1 residem (ex: `FaturamentoAppService.cs`, `NotaFiscalForm.Designer.cs`, `001_CreateTableFatura.sql`).

### 2.2. Vínculo Obrigatório Artefato $\leftrightarrow$ Identidades L1 $\leftrightarrow$ Fluxos L2
Cada Arquivo e Artefato mapeado no Nível 3 mantém a lista reversa de todas as identidades do Nível 1 declaradas nele e de todos os fluxos do Nível 2 que o atravessam:

```json
{
  "application_id": "urn:app:monolito_root:ERP_Faturamento_Suite",
  "application_name": "ERP Suíte de Faturamento e Fiscal",
  "principal_artifacts": [
    {
      "artifact_id": "urn:artifact:monolito_root:Empresa.Faturamento.UI.exe",
      "artifact_name": "Empresa.Faturamento.UI.exe",
      "artifact_type": "DESKTOP_EXECUTABLE",
      "project_identity": "urn:info:mem:code:monolito_root:src/Faturamento.UI",
      "files": [
        {
          "file_name": "EmissaoNotaForm.cs",
          "relative_path": "src/Faturamento.UI/Forms/EmissaoNotaForm.cs",
          "hosted_l1_identities": [
            "urn:info:mem:code:monolito_root:src/Faturamento.UI:Empresa.Faturamento.UI:EmissaoNotaForm",
            "urn:info:mem:code:monolito_root:src/Faturamento.UI:Empresa.Faturamento.UI:EmissaoNotaForm#BtnEmitir_Click(System.Object,System.EventArgs)->System.Void"
          ]
        }
      ]
    }
  ]
}
```

---

## 3. Agrupamento por Tech Stack (Identidades por Camada Tecnológica)

O Nível 3 classifica **quais identidades do Nível 1 fazem parte de qual Tech Stack**, cruzando as bibliotecas identificadas no Nível 1 (`urn:info:dep:pkg:*`) com as assinaturas de código, banco e disco.

### 3.1. Dimensões de Classificação da Tech Stack
Cada identidade do Nível 1 é vinculada a um **Perfil de Tech Stack (`TechStackGroup`)**:

| Camada da Tech Stack | Tecnologias Exemplo Detectadas via L1 | Identidades L1 Agrupadas |
| :--- | :--- | :--- |
| **`UI / Presentation Stack`** | WinForms, WPF, ASP.NET WebForms, Razor/MVC, Blazor | Classes e métodos de Formulários, Controllers, Pages, ViewModels. |
| **`Service & API Stack`** | ASP.NET WebAPI, WCF (`System.ServiceModel`), gRPC, MediatR | Contratos de serviço, handlers de comando/query, endpoints REST/SOAP. |
| **`Business / Domain Logic Stack`** | C# Puro (POCOs, Domain Services, Validators, Engines) | Classes de domínio, calculadoras de regras, validadores em memória RAM (`urn:info:mem:code:*`). |
| **`Data Access / ORM Stack`** | Entity Framework 6 / Core, Dapper, ADO.NET (`SqlCommand`), NHibernate | Repositórios, `DbContext`, DataAdapters, Dapper Extensions. |
| **`Persistence & Storage Stack`** | SQL Server (`mssql`), Oracle, FileSystem XML/CSV, MemoryCache | Tabelas/Procs (`urn:info:db:rel:*`), Arquivos em disco (`urn:info:storage:*`) e Caches (`urn:info:mem:state:*`). |

---

## 4. Heurísticas de Negócio Inter-Aplicações e Agregação Lexical

Em grandes monolitos (700 módulos), **aplicações diferentes frequentemente implementam partes da mesma regra ou heurística de negócio** (por exemplo: o aplicativo Desktop de Balcão, a API de E-commerce e o Serviço Batch Noturno possuem rotinas de *Cálculo de ICMS-ST* ou *Validação de Limite de Crédito*).

### 4.1. Agregação de Palavras Comuns de Negócio à sua Identidade Única de Origem
Para descobrir quais abstrações fazem parte da mesma heurística de negócio mesmo estando em aplicações distintas, o Nível 3 executa o **Pipeline de Tokenização e Ancoragem Lexical**:

1. **Extração de Radicais de Negócio:**
   * Decompõe nomes de classes, métodos, tabelas de banco, colunas e arquivos (via *CamelCase*, *PascalCase* e *SNAKE_CASE* splitting).
   * Exemplo: `FaturamentoAppService#ProcessarFatura`, `TB_FATURA_ITEM`, `CalculoFaturamentoBatch` $\to$ Radical comum: `FATURA` / `FATURAMENTO`.
2. **Filtro de Ruído Técnico (Stopwords de Engenharia):**
   * Remove sufixos/prefixos puramente arquiteturais (`Service`, `Controller`, `Repository`, `Manager`, `Helper`, `Dto`, `TB_`, `SP_`, `Get`, `Set`, `Execute`).
   * Retém exclusivamente os **Substantivos de Domínio** (`Fatura`, `NotaFiscal`, `Imposto`, `Cliente`, `Estoque`, `Pedido`) e **Verbos de Negócio** (`Emitir`, `Cancelar`, `Estornar`, `Liquidar`, `Tributar`).
3. **Ancoragem Estrita na Identidade Única do Nível 1:**
   * Toda palavra comum de negócio é agregada em um índice invertido apontando diretamente para o `IdentityURN` exato de onde ela foi mapeada:
     ```text
     TermoNegocio("FATURA") -> {
       urn:info:db:rel:mssql:default:erp_db:dbo:table:TB_FATURA,
       urn:info:mem:code:monolito_root:src/Faturamento.Service:...:FaturamentoAppService#ProcessarFatura(...),
       urn:info:mem:code:monolito_root:src/Batch.Cobranca:...:FechamentoFaturaJob#Executar(...)
     }
     ```

### 4.2. Cluster de Heurística de Negócio Inter-Aplicações (`CrossAppBusinessHeuristic`)
Duas ou mais abstrações (mesmo de aplicações diferentes) são agrupadas na mesma **Heurística de Negócio** quando satisfazem pelo menos um dos 3 critérios de convergência:
1. **Convergência de Persistência (Forte):** Seus Call Flows (Nível 2) terminam lendo ou gravando no mesmo subconjunto de tabelas de banco relacional (`urn:info:db:rel:*`) ou arquivos em disco (`urn:info:storage:*`).
2. **Convergência de Código Compartilhado (Forte):** Seus Call Flows invocam um mesmo método de domínio ou cálculo centralizado em um módulo core.
3. **Convergência Lexical + Estrutural (Semântica):** Compartilham o mesmo conjunto de termos de negócio normalizados no vocabulário do domínio e operam sobre estruturas equivalentes.

---

## 5. Glossário de Domínio Contido em (Conjunto de Identidades + Call Flow)

> **Requisito Crítico da Especificação:**
> *"aqui é importante que seja possível ter um glossário e este glossário esteja contido no mapeamento de um conjunto de identidades com um call flow"*

O Glossário no Nível 3 **não é um documento de texto separado do código**: ele é uma estrutura de metadados embarcada dentro de cada **Domínio / Cluster de Fluxo**, onde cada termo do glossário amarra:
1. O conceito de negócio e seus sinônimos/abreviações no código (ex: `NF`, `NFe`, `NotaFiscal`, `TB_NOTA`).
2. O **conjunto exato de Identidades do Nível 1** (Classes, Métodos, Tabelas, Arquivos) que materializam esse conceito.
3. O **conjunto exato de Call Flows do Nível 2** onde esse conceito é processado do início (UI) ao fim (Banco/Disco).

### 5.1. Schema JSON Canônico do Nível 3 (Domínio + Tech Stack + Heurística + Glossário Vinculado a Call Flow)

```json
{
  "domain_id": "urn:domain:monolito_root:FATURAMENTO_FISCAL",
  "domain_name": "Domínio de Faturamento e Emissão Fiscal",
  "participating_applications": [
    "urn:app:monolito_root:ERP_Desktop_WinForms",
    "urn:app:monolito_root:API_Portal_Faturamento",
    "urn:app:monolito_root:Worker_Integracao_Sefaz"
  ],
  "tech_stack_breakdown": {
    "presentation": [
      "urn:info:mem:code:monolito_root:src/Faturamento.UI:Empresa.Faturamento.UI:EmissaoNotaForm#BtnEmitir_Click(System.Object,System.EventArgs)->System.Void"
    ],
    "business_services": [
      "urn:info:mem:code:monolito_root:src/Faturamento.Service:Empresa.Faturamento:FaturamentoAppService#ProcessarFatura(System.Int32,System.Boolean)->Empresa.Faturamento.ResultadoFaturaDto"
    ],
    "in_memory_state": [
      "urn:info:mem:state:cache:monolito_root:ParametrosFiscaisCache"
    ],
    "relational_persistence": [
      "urn:info:db:rel:mssql:default:erp_db:dbo:table:TB_FATURA",
      "urn:info:db:rel:mssql:default:erp_db:dbo:table:TB_NOTA_FISCAL"
    ],
    "disk_persistence": [
      "urn:info:storage:fs:local:XML_EXPORT_ROOT:Fatura_{id}.xml:xml"
    ]
  },
  "cross_application_heuristics": [
    {
      "heuristic_id": "urn:heuristic:biz:FATURAMENTO_FISCAL:EMISSAO_E_TRIBUTACAO_FATURA",
      "heuristic_name": "Emissão, Cálculo Tributário e Persistência de Fatura Fiscal",
      "description": "Agrupa fluxos do ERP Desktop e da API Web que calculam impostos, gravam na TB_FATURA e exportam o XML fiscal em disco.",
      "common_business_words_mapped": [
        {
          "canonical_term": "FATURA",
          "raw_tokens_found": ["Fatura", "Faturamento", "TB_FATURA", "ProcessarFatura"],
          "origin_l1_identities": [
            "urn:info:db:rel:mssql:default:erp_db:dbo:table:TB_FATURA",
            "urn:info:mem:code:monolito_root:src/Faturamento.Service:Empresa.Faturamento:FaturamentoAppService#ProcessarFatura(System.Int32,System.Boolean)->Empresa.Faturamento.ResultadoFaturaDto",
            "urn:info:storage:fs:local:XML_EXPORT_ROOT:Fatura_{id}.xml:xml"
          ]
        }
      ],
      "bound_e2e_call_flows": [
        "urn:flow:e2e:monolito_root:UI_EmissaoNotaForm_BtnEmitir_TO_TB_FATURA",
        "urn:flow:e2e:monolito_root:API_FaturamentoController_Post_TO_TB_FATURA"
      ],
      "embedded_glossary": [
        {
          "term": "Fatura Fiscal (Fatura / TB_FATURA)",
          "business_definition": "Documento comercial e fiscal gerado a partir de um pedido aprovado, sujeito a cálculo de ICMS e persistido em banco relacional e arquivo XML local.",
          "code_abbreviations_and_aliases": ["Fatura", "Fat", "TB_FATURA", "ResultadoFaturaDto"],
          "bound_identity_set": [
            "urn:info:db:rel:mssql:default:erp_db:dbo:table:TB_FATURA",
            "urn:info:mem:code:monolito_root:src/Faturamento.Service:Empresa.Faturamento:FaturamentoAppService#ProcessarFatura(System.Int32,System.Boolean)->Empresa.Faturamento.ResultadoFaturaDto",
            "urn:info:storage:fs:local:XML_EXPORT_ROOT:Fatura_{id}.xml:xml"
          ],
          "bound_call_flows": [
            "urn:flow:e2e:monolito_root:UI_EmissaoNotaForm_BtnEmitir_TO_TB_FATURA"
          ]
        },
        {
          "term": "Parâmetros Fiscais em Cache (ParametrosFiscaisCache)",
          "business_definition": "Alíquotas e regras estaduais carregadas temporariamente em memória RAM para evitar leituras repetitivas no banco durante o cálculo da fatura.",
          "code_abbreviations_and_aliases": ["ParametrosFiscaisCache", "CacheAlquota"],
          "bound_identity_set": [
            "urn:info:mem:state:cache:monolito_root:ParametrosFiscaisCache"
          ],
          "bound_call_flows": [
            "urn:flow:e2e:monolito_root:UI_EmissaoNotaForm_BtnEmitir_TO_TB_FATURA"
          ]
        }
      ]
    }
  ]
}
```
