# Spec 02 — Motor de Varredura de Projetos (`ProjectScanner`) e Ordenação Topológica em 4 Ondas

**Módulos Alvo:** `code_reader/scanner/project_scanner.py` e `code_reader/scanner/wave_sorter.py`  
**Custo de Tokens de IA:** **`0 tokens` (100% determinístico em CPU).**

---

## 1. Responsabilidade do Varredor (`ProjectScanner`)

Ao receber a lista de diretórios resolvida pela CLI (seja o `default_scan_directories` ou as pastas passadas como argumento no `./run_code_reader.sh`), o `ProjectScanner` realiza uma varredura rápida, determinística e tolerante a falhas de codificação para descobrir **todos os projetos, soluções, sites legados e arquivos de código-fonte** antes de iniciar o Nível 1.

---

## 2. Algoritmo de Varredura Recursiva e Identificação de Unidades de Projeto

Para cada diretório raiz $R_k$ informado:

### 2.1. Poda Imediata de Árvores Irrelevantes e Pastas Espelho (`Directory Pruning`)
Durante o `os.walk(R_k, topdown=True)`, o scanner modifica `dirs[:]` *in-place* (evitando descer em milhares de subpastas inúteis):
1. **Pastas Técnicas Ignoradas:** `.git`, `.svn`, `.hg`, `.vs`, `.idea`, `bin`, `obj`, `packages`, `node_modules`, `TestResults`, `Debug`, `Release`, `publish`.
2. **Filtro Anti-Espelho Obrigatório (`Mirror Folder Deduplication`):**
   - Conforme `./config/input_validation_policy.json` (`exclude_mirror_folders_suffixes: ["_"]`), se existir uma pasta irmã `X_` (ou `X-bkp`, `X-old`, `X_backup`) ao lado da pasta canônica `X` (ex.: `pep-forms_` ao lado de `pep-forms`), `X_` é **descartada e registrada no log de reconciliação** (`reconciled_mirror_folders[]` em `application_context.json`), garantindo **zero duplicação de URNs**.

### 2.2. Regras de Detecção dos 4 Tipos de Unidade de Projeto

| Tipo de Unidade | Critério Determinístico de Detecção | Como É Indexada |
| :--- | :--- | :--- |
| **1. Projeto MSBuild Moderno ou Legado (`.csproj` / `.vbproj`)** | Arquivo com extensão `.csproj` ou `.vbproj` (SDK-style .NET ou .NET Framework 2.0–4.8 XML com namespace MSBuild). | Unidade primária (`project_id` = nome da pasta ou stem do `.csproj`). Extrai `AssemblyName`, `RootNamespace`, `OutputType` (`WinExe`, `Exe`, `Library`), `<ProjectReference>`, `<Reference>`/`<HintPath>` e `<PackageReference>`. |
| **2. Solução Visual Studio (`.sln`)** | Arquivo `.sln` contendo blocos `Project("{GUID}") = "Nome", "Caminho\Proj.csproj"`. | Usado como índice agregador de aplicação (`Application Grouping`) para vincular projetos que são compilados juntos sob o mesmo entregável corporativo. |
| **3. WebSite ASP.NET Legado sem `.csproj` (`WebSite Folder`)** | Pasta sem `.csproj`/`.vbproj`, mas que contém `Web.config` (case-insensitive) acompanhado de arquivos `.aspx`, `.ascx`, `.ashx`, `.asmx` ou subpasta `App_Code/`. | Registrada como unidade `LEGACY_ASPNET_WEBSITE` para garantir que portais hospitalares legados nunca fiquem de fora da varredura. |
| **4. Módulo de Scripts / Componentes Soltos (`Orphan Code Module`)** | Subpasta direta da raiz contendo arquivos `.cs`, `.vb` ou `.sql` sem manifesto MSBuild nem projeto pai ancestral. | Registrada como `STANDALONE_SOURCE_MODULE` caso contenha declarações válidas de classes ou procedures. |

---

## 3. Inventário de Arquivos Internos por Projeto e Leitura Multi-Encoding

Para cada projeto descoberto, o `ProjectScanner` indexa e calcula o hash rápido (`SHA-256` de conteúdo bruto + tamanho + `mtime`) de todos os seus artefatos internos:

1. **Código Imperativo:** `*.cs` (separando `*.Designer.cs` para o extrator de UI), `*.vb`.
2. **Interfaces Visuais e Recursos:** `*.Designer.cs`, `*.Designer.vb`, `*.resx`, `*.aspx`, `*.ascx`, `*.master`, `*.cshtml`, `*.vbhtml`.
3. **Configuração e Persistência Local:** `app.config`, `web.config`, `packages.config`, `*.settings`, `*.ini`, `*.xsd` (`DataSet` tipado / `TableAdapter`), `*.rpt` / `*.rdlc`.
4. **Banco de Dados Embutido:** `*.sql`, `*.prc`, `*.fnc`, `*.pks`, `*.pkb`.

> **Garantia Multi-Encoding (`Zero File Drop`):** Todo leitor de texto da aplicação utiliza obrigatoriamente a função `read_text_resilient(path)` tentando em ordem: `utf-8-sig` $\rightarrow$ `utf-8` $\rightarrow$ `utf-16` $\rightarrow$ `cp1252` $\rightarrow$ `latin-1`. Nenhum arquivo `.cs` ou `.Designer.cs` com acentuação em Windows-1252 (padrão clássico do Visual Studio no Brasil) pode falhar com `UnicodeDecodeError` ou ser ignorado como binário.

---

## 4. Construção do Grafo de Dependências (DAG) e Ordenação nas 4 Ondas Topológicas

Antes de iniciar qualquer extração do Nível 1, `wave_sorter.py` constrói o grafo dirigido $G = (V, E)$ onde uma aresta $P_A \rightarrow P_B$ indica que o projeto $P_A$ referencia $P_B$ (via `<ProjectReference>`, `<Reference>` batendo com `AssemblyName` de $P_B$, ou `using <RootNamespace_de_PB>`):

### 4.1. Tratamento de Ciclos Eventuais e Atribuição às 4 Ondas (`Onda 1` $\rightarrow$ `Onda 4`)
1. Caso existam referências circulares legadas via DLL pré-compilada, o algoritmo condensa componentes fortemente conexos (**Tarjan SCC**) para obter um DAG estrito.
2. Cada projeto recebe seu nível topológico e é classificado deterministicamente em uma das **4 Ondas Canônicas** exigidas pelas Specs:

| Onda | Papel Arquitetural | Regra Determinística de Classificação (`wave_sorter.py`) | Ordem de Execução |
| :---: | :--- | :--- | :---: |
| **`Onda 1`** | **Folhas: Contratos, DTOs e Infraestrutura Base** | Grau de dependência interna $= 0$ **ou** sufixo/padrão `*-classes`, `*-dto`, `*-model`, `*-entities`, `*-infra`, `*-util`, `*-dll` sem acesso a SGBD nem `System.Windows.Forms`/`System.Web`. | **1ª a executar** |
| **`Onda 2`** | **Acesso a Dados e Persistência (`DAO`)** | Sufixo `*-dao`, `*-dal`, `*-data`, `*-repository` **ou** projetos biblioteca que importam `Oracle.DataAccess`, `Oracle.ManagedDataAccess`, `System.Data.SqlClient`, `Dapper`, `NHibernate`, `EntityFramework` sem camada de UI. | **2ª a executar** |
| **`Onda 3`** | **Regras de Negócio e Serviços (`BO` / `Services`)** | Sufixo `*-bo`, `*-bll`, `*-business`, `*-service*`, `Listener*`, `WindowsService` **ou** bibliotecas intermediárias que dependem da Onda 2 e não expõem Forms/Pages visuais. | **3ª a executar** |
| **`Onda 4`** | **Fronteira e Interface Humana (`UI` / Executáveis)** | `OutputType` = `WinExe` / `Exe`, projetos `*-forms`, `*-web`, `*-ui`, `LEGACY_ASPNET_WEBSITE` **ou** qualquer módulo contendo classes herdadas de `Form`, `XtraForm`, `NTIForm`, `UserControl`, `System.Web.UI.Page` ou `Controller`. | **4ª a executar** |

### 4.2. Divisão Automática em Lotes/Shards (`batch_size_modules = 50`)
Dentro de cada Onda (`1 -> 2 -> 3 -> 4`), os projetos são ordenados alfabeticamente de forma determinística e agrupados em **lotes de até 50 módulos**. Ao final de cada lote, o `state_manager.py` faz flush atômico de `./config/incremental_build_state.json`.

---

## 5. Sincronização Automática de Manifestos antes do Estágio 1

Concluída a varredura, o `ProjectScanner` grava/atualiza automaticamente:
1. `./config/application_manifest.json` — Lista exata dos projetos descobertos nas pastas indicadas, sua `wave` (`1..4`), `shard` e `canonical_root_identity_urn`.
2. `./output/layer1_structural/libraries_and_dependencies_graph.json` — Grafo completo de referências internas e bibliotecas externas (`urn:famema:<APP>:src-root:lib-dependency:...`).
3. `./output/layer1_structural/topological_build_order_700_modules.json` — Sequência ordenada exata de processamento que governará os Níveis 1, 2 e 3.
