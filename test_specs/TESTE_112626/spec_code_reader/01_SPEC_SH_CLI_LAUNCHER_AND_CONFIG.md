# Spec 01 — Inicializador Shell (`run_code_reader.sh`), Interface CLI e Resolução de Diretório Padrão

**Arquivo Alvo do Inicializador:** `./run_code_reader.sh` (na raiz de `metadados_famema2.11`)  
**Compatibilidade de Shell:** Bash POSIX / Bash 4+ (suporta nativamente **Git Bash / MINGW64 no Windows**, **WSL2**, **Linux** e **macOS**).

---

## 1. Requisitos de Inicialização por Comando `.sh`

A aplicação deve poder ser iniciada com um único comando `.sh`, operando em **dois modos de endereçamento de pastas**:

1. **Modo Diretório Padrão (Zero Argumentos):**
   ```sh
   ./run_code_reader.sh
   ```
   - Nenhuma pasta precisa ser digitada pelo usuário.
   - A aplicação lê `default_scan_directories` de `./config/code_reader.config.json` (ex.: `["c:/git"]`) — ou, caso ausente, faz fallback automático para `monolith_root_path` em `./config/application_manifest.json` — e executa toda a sequência das Camadas 1 a 4 salvando em `./output/`.

2. **Modo Pastas Indicadas na Linha de Comando (1 ou N Pastas):**
   ```sh
   # Passando pastas diretamente como argumentos posicionais (formato Windows ou POSIX):
   ./run_code_reader.sh "C:\Sistemas\sihosptray" "C:\Sistemas\benner"
   ./run_code_reader.sh /c/git /c/Sistemas/sihosptray

   # Ou usando flags explícitas e alvo nomeado:
   ./run_code_reader.sh --scan-dir "D:\Projetos\ModuloCirurgico" --app-name "SIHOSP" --profile multi-slm
   ./run_code_reader.sh --target all_famema --resume
   ```

---

## 2. Regra Estrita de Precedência de Diretórios (`Directory Resolution Order`)

O módulo `config_loader.py` (alimentado por `run_code_reader.sh`) resolve os diretórios de varredura na seguinte ordem estrita de prioridade (do mais específico para o padrão):

1. **Prioridade 1 — Argumentos CLI (`positional paths` ou `--scan-dir` / `-d`):** Se o usuário informar 1 ou mais pastas no comando `.sh`, estas substituem o diretório padrão nesta execução.
2. **Prioridade 2 — Alvo Nomeado (`--target <alias>`):** Carrega a lista de pastas correspondente em `additional_named_targets` dentro de `./config/code_reader.config.json`.
3. **Prioridade 3 — Variável de Ambiente (`CODE_READER_SCAN_DIRS` em `./config/code_reader.env` ou shell):** Lista separada por `;` ou `,`.
4. **Prioridade 4 — Diretório Padrão Configurado (`default_scan_directories` em `./config/code_reader.config.json`):** Padrão persistente da instalação.
5. **Prioridade 5 — Fallback Canônico (`monolith_root_path` em `./config/application_manifest.json`):** Garante compatibilidade retroativa com o manifesto `v2.11`.

### 2.1. Normalização Multi-Plataforma de Caminhos (Windows $\leftrightarrow$ Shell `.sh`)
Como o ambiente principal utiliza Windows com Git Bash ou WSL:
- O script `.sh` e o `config_loader.py` aceitam transparentemente:
  - Caminhos Windows (`C:\git\agendamentos` ou `C:/git/agendamentos`);
  - Caminhos Git Bash / MSYS (`/c/git/agendamentos`);
  - Caminhos WSL (`/mnt/c/git/agendamentos`).
- Internamente, o Python converte o caminho para `pathlib.Path.resolve()` do sistema operacional em que o interpretador Python está rodando, mas **sempre gera URNs normalizados portáteis** (ex.: escopo `c_git` e caminhos relativos ao módulo `agendamentos/Form1.cs`).

---

## 3. Tabela Completa de Flags e Parâmetros do `run_code_reader.sh`

| Flag / Argumento | Exemplo | Descrição | Valor Padrão |
| :--- | :--- | :--- | :--- |
| `[DIR_1 DIR_2 ...]` | `./run_code_reader.sh /c/git` | Uma ou mais pastas raiz onde os projetos serão varridos recursivamente. | `default_scan_directories` |
| `-d`, `--scan-dir <PATH>` | `-d "C:/Sistemas/benner"` | Adiciona diretório à lista de varredura (pode ser repetida múltiplas vezes). | `default_scan_directories` |
| `--set-default-dir <PATH>` | `--set-default-dir "C:/git"` | Atualiza permanentemente o `default_scan_directories` em `./config/code_reader.config.json` antes de iniciar. | *(não altera)* |
| `-t`, `--target <ALIAS>` | `--target benner` | Seleciona um conjunto de diretórios pré-mapeado em `additional_named_targets`. | *(nenhum)* |
| `-a`, `--app-name <NAME>` | `--app-name SIHOSP` | Define o identificador `<APP>` nos URNs `urn:famema:<APP>:...`. | `"SIHOSP"` |
| `-p`, `--profile <PROFILE>` | `--profile multi-slm` | Seleciona o perfil de modelos do Plano 3: `multi-slm`, `single-slm-8gb`, `single-slm-16gb` ou `deterministic-only`. | `"multi-slm"` |
| `-o`, `--output-dir <PATH>` | `-o ./output/run_benner` | Diretório base onde `layer1_structural`..`layer4_graphics` serão gravados. | `./output` |
| `-i`, `--input-dir <PATH>` | `-i ./input` | Diretório base das pastas `input/` validadas diretamente. | `./input` |
| `--from-layer <1..4>` | `--from-layer 2` | Retoma a partir de uma camada específica *(exige camadas anteriores já consolidadas e validadas)*. | `1` |
| `--to-layer <1..4>` | `--to-layer 3` | Executa da camada inicial até a camada limite indicada, respeitando a ordem estrita. | `4` |
| `--resume` / `--no-resume` | `--resume` | Reutiliza checkpoints e hashes SHA-256 (`signature_hash` / `body_hash`) de execuções anteriores. | `--resume` (ativo) |
| `--force-rebuild` | `--force-rebuild` | Ignora hashes incrementais e reprocessa todos os módulos do zero (mantendo `semantic_cache.jsonl` salvo `--no-cache`). | `false` |
| `--no-auto-pull` | `--no-auto-pull` | Impede o download automático de modelos ausentes no Ollama (falha rápido em ambientes offline). | `false` |
| `--query "<PROMPT>"` | `--query "fluxo cirurgia SMOV5020"` | Aciona diretamente o Motor de Resolução de Prompt do Nível 3 sobre o mapeamento já consolidado. | *(modo mapeamento)* |
| `--dry-run` | `--dry-run` | Executa apenas a varredura de pastas, lista os projetos e as 4 Ondas descobertas e encerra sem gravar `output/`. | `false` |

---

## 4. Fluxo Interno Obrigatório do Script `run_code_reader.sh`

O arquivo `./run_code_reader.sh` deve seguir estritamente a estrutura operacional abaixo:

```sh
#!/usr/bin/env bash
set -Eeuo pipefail

# 1. Resolução Portátil do Diretório Base (sempre relativo à localização do próprio script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# 2. Carregamento de Variáveis Padrão Opcionais
if [[ -f "./config/code_reader.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "./config/code_reader.env"
  set +a
fi

# 3. Tratamento Gracioso de Interrupção (Ctrl+C / SIGTERM salva estado incremental)
on_interrupt() {
  echo "[WARN] Interrupção recebida. Aguardando flush atômico de config/incremental_build_state.json..." >&2
  exit 130
}
trap on_interrupt INT TERM

# 4. Descoberta e Preparação do Ambiente Python (.venv local)
PYTHON_BIN=""
if [[ -x "./.venv/Scripts/python.exe" ]]; then
  PYTHON_BIN="./.venv/Scripts/python.exe"
elif [[ -x "./.venv/bin/python" ]]; then
  PYTHON_BIN="./.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "[ERROR] Python 3.11+ não encontrado no PATH." >&2
  exit 3
fi

# Bootstrap automático do .venv caso não exista
if [[ ! -d "./.venv" && -f "./code_reader/requirements.txt" ]]; then
  echo "[INFO] Criando ambiente virtual local em ./.venv ..."
  "${PYTHON_BIN}" -m venv ./.venv
  if [[ -x "./.venv/Scripts/python.exe" ]]; then PYTHON_BIN="./.venv/Scripts/python.exe"; else PYTHON_BIN="./.venv/bin/python"; fi
  "${PYTHON_BIN}" -m pip install --upgrade pip -q
  "${PYTHON_BIN}" -m pip install -r "./code_reader/requirements.txt" -q
fi

# 5. Configuração Econômica de Memória para Ollama Local (1 modelo carregado por vez)
export OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-1}"
export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
export PYTHONUTF8=1

# 6. Verificação do Servidor Local Ollama (inicia em background se instalado e parado)
if command -v ollama >/dev/null 2>&1; then
  if ! curl -fsS "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" >/dev/null 2>&1; then
    echo "[INFO] Iniciando servidor local 'ollama serve' em background..."
    nohup ollama serve > "./output/ollama_daemon.log" 2>&1 &
    for _ in {1..15}; do
      curl -fsS "${OLLAMA_HOST:-http://127.0.0.1:11434}/api/tags" >/dev/null 2>&1 && break
      sleep 1
    done
  fi
fi

# 7. Despacho para o Orquestrador Python repassando todos os argumentos (ou vazio -> usa Diretório Padrão)
exec "${PYTHON_BIN}" -m code_reader.cli "$@"
```

---

## 5. Contrato de Códigos de Saída (`Exit Codes`)

Para permitir automação em CI/CD, agendadores ou scripts encadeados, `run_code_reader.sh` retorna códigos determinísticos:

| Código | Significado | Condição de Disparo |
| :---: | :--- | :--- |
| **`0`** | `SUCCESS_VERIFIED` | Todas as camadas solicitadas concluídas **e** `verify_all.py` aprovado com `0` defeitos. |
| **`1`** | `UNEXPECTED_RUNTIME_ERROR` | Exceção não tratada de I/O ou sistema operacional (checkpoint salvo até o último lote). |
| **`2`** | `INPUT_GATE_DEFICIT_HALT` | Uma pasta obrigatória de `./input/` falhou na validação e a política exige parada bloqueante. |
| **`3`** | `ENVIRONMENT_OR_MODEL_UNAVAILABLE` | Python ausente, pasta de scan inexistente ou servidor/modelos locais indisponíveis sem `--profile deterministic-only`. |
| **`4`** | `VERIFICATION_FAILED` | Execução terminou, mas `verify_all.py` detectou defeito residual após as tentativas de auto-reparo. |
| **`130`** | `INTERRUPTED_CHECKPOINT_SAVED` | Interrompido pelo usuário (`SIGINT`/`SIGTERM`) com estado incremental preservado para `--resume`. |
