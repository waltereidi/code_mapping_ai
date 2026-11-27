# Especificação Técnica da Aplicação `FAMEMA Code Reader` (`spec_code_reader`)

Esta pasta contém a especificação completa de engenharia para construção da aplicação **`famema-code-reader`** (`./run_code_reader.sh`), responsável por varrer diretórios de código-fonte (usando um **diretório padrão pré-configurado** ou **pastas indicadas via CLI**) e executar automaticamente toda a sequência de mapeamento das **Camadas 1 a 4** utilizando os **modelos locais gratuitos do Plano 3** (`Engine-0` determinístico + `Multi-SLM` sequencial ou `Single-SLM`).

---

## Como a Aplicação Funciona em 3 Comandos

```sh
# 1. Execução imediata usando o Diretório Padrão configurado em ./config/code_reader.config.json:
./run_code_reader.sh

# 2. Execução varrendo uma ou mais pastas específicas na sequência completa (L1 -> L2 -> L3 -> L4):
./run_code_reader.sh "C:/git" "C:/Sistemas/sihosptray"

# 3. Consulta rápida em linguagem ubíqua + tela sobre o mapeamento gerado:
./run_code_reader.sh --query "Como funciona o cadastro de cirurgia na tela SMOV5020?"
```

---

## Índice dos Documentos da Especificação

1. **[00_SPEC_APPLICATION_OVERVIEW_AND_ARCHITECTURE.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/spec_code_reader/00_SPEC_APPLICATION_OVERVIEW_AND_ARCHITECTURE.md)**  
   Arquitetura modular da aplicação (`code_reader/`), fluxo de componentes e schema completo de `./config/code_reader.config.json` com diretório padrão e perfis de IA.
2. **[01_SPEC_SH_CLI_LAUNCHER_AND_CONFIG.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/spec_code_reader/01_SPEC_SH_CLI_LAUNCHER_AND_CONFIG.md)**  
   Especificação do script `./run_code_reader.sh` (compatível com Git Bash no Windows, WSL, Linux e macOS), flags CLI, regra de precedência entre diretório padrão e pastas informadas, bootstrap de `.venv`/Ollama e códigos de retorno (`0` a `130`).
3. **[02_SPEC_PROJECT_SCANNER_AND_WAVE_DISCOVERY.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/spec_code_reader/02_SPEC_PROJECT_SCANNER_AND_WAVE_DISCOVERY.md)**  
   Especificação do `ProjectScanner`: descoberta recursiva de `.sln`, `.csproj`, `.vbproj` e `WebSites` ASP.NET legados, poda de pastas espelho (`_`), leitura multi-encoding resiliente (`utf-8` a `cp1252`) e ordenação topológica nas **Ondas 1 a 4**.
4. **[03_SPEC_MULTI_SLM_RUNTIME_AND_TOKEN_ENGINE.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/spec_code_reader/03_SPEC_MULTI_SLM_RUNTIME_AND_TOKEN_ENGINE.md)**  
   Integração dos **modelos locais gratuitos do Plano 3** (`qwen2.5-coder:3b`, `bge-m3`, `gemma3:4b`, `phi4-mini` no modo `multi-slm` e `7b`/`14b` nos perfis `single-slm`), descarregamento sequencial `keep_alive=0`, internação de URNs `@Xnnnn`, cache SHA-256 e JSON Schemas estritos.
5. **[04_SPEC_SEQUENTIAL_PIPELINE_L1_TO_L4.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/spec_code_reader/04_SPEC_SEQUENTIAL_PIPELINE_L1_TO_L4.md)**  
   Máquina de estados e sequência estrita dos **Estágios 0 a 5** (`Validação Input-First` $\rightarrow$ `Nível 1` $\rightarrow$ `Nível 2` $\rightarrow$ `Nível 3` $\rightarrow$ `Nível 4` $\rightarrow$ `Auto-Verificação verify_all.py`).
