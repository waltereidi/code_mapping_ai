# Índice das Especificações `specs_refit` (`v2.11-refit` — Baixo Consumo de Tokens e Execução em SLMs Locais)

Este diretório contém a revisão normativa completa das especificações de mapeamento do monolito (~700 módulos), reprojetada para **reduzir em ~96%–98% o consumo de tokens**, **automatizar deterministicamente o máximo de etapas via AST/CFG/SQLGlot** e permitir execução integral em **LLMs locais gratuitas de baixo custo computacional** (modelo único de 7B–14B ou pipeline cooperativo de múltiplos modelos pequenos de 0.3B–4B), mantendo **100% de paridade nos artefatos de saída** (`output/layer1_structural` a `output/layer4_graphics`) e conformidade total com `validate_inputs.py` e `verify_all.py`.

## Documentos Normativos

1. **[00_MASTER_ARCHITECTURE_AND_HIERARCHY.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/00_MASTER_ARCHITECTURE_AND_HIERARCHY.md)**  
   Arquitetura mestre híbrida (`Engine-0 Determinístico` + `Micro-SLM`), as 7 técnicas obrigatórias de economia de tokens (`T-OPT-01` a `T-OPT-07`), orçamento comparativo de tokens e validação direta `Input-First`.
2. **[01_SPEC_LAYER1_STRUCTURAL_COMPREHENSION.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/01_SPEC_LAYER1_STRUCTURAL_COMPREHENSION.md)**  
   Nível 1 automatizado com **`0 tokens` de IA**: extração determinística de banco relacional, mídias físicas/disco/pedras/CDs, filtro estrito de memória RAM, URNs canônicos de 7 níveis (`8+ segmentos`) e geração da tabela de internação simbólica (`@Xnnnn`).
3. **[02_SPEC_LAYER2_CALL_FLOW_COMPREHENSION.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/02_SPEC_LAYER2_CALL_FLOW_COMPREHENSION.md)**  
   Nível 2 (~92% determinístico via AST/CFG/SQLGlot + ~8% `SLM-Code` residual): pontos iniciais DML (`INSERT`/`UPDATE`/`DELETE`), `CallerScopedAggregate`, regras sintáticas `T01`–`T09`, pré-condições impeditivas e cálculo topológico de Tarjan/Kahn para a ordem ideal de execução.
4. **[03_SPEC_LAYER3_TECH_STACK_AND_HEURISTICS.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/03_SPEC_LAYER3_TECH_STACK_AND_HEURISTICS.md)**  
   Nível 3 com `FullUIExtractor` multi-encoding (`0 tokens`), deduplicação morfológica em lotes de 30 radicais (`Unique-Stem Batching`), embeddings locais (`bge-m3`/`nomic`) para linguagem ubíqua não-regra (`is_business_rule_participant: false`), 4 projeções Socráticas independentes e Motor de Resolução de Prompt de baixo contexto.
5. **[04_SPEC_LAYER4_GRAPHICS_AND_ANALYTICS.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/04_SPEC_LAYER4_GRAPHICS_AND_ANALYTICS.md)**  
   Nível 4 com templates SQL parametrizados, árvore determinística de atividade (`ACTIVE`, `LOW_UTILIZATION`, `INACTIVE_BY_DB_STATE`, `INACTIVE_DEAD_CODE`) e geração matemática/HTML 100% determinística dos Gráficos 1, 2 e 3.
6. **[05_EXECUTION_PLAN_700_MODULES_MONOLITH.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/05_EXECUTION_PLAN_700_MODULES_MONOLITH.md)**  
   Plano operacional passo a passo para ~700 módulos com checkpoints SHA-256, cache semântico, troca sequencial de modelos e portão final `verify_all.py`.
7. **[06_MULTI_SLM_AND_LOW_TOKEN_MODELS_SPEC.md](file:///C:/Users/walte/OneDrive/Documentos/metadados_famema2.11/specs_refit/06_MULTI_SLM_AND_LOW_TOKEN_MODELS_SPEC.md)**  
   Catálogo completo de modelos locais gratuitos compatíveis por faixa de hardware (CPU 8–16 GB RAM, GPU 4–8 GB VRAM, GPU 12–16 GB VRAM) e arquitetura detalhada do **Plano Multi-SLM** (`Engine-0` + `SLM-1` a `SLM-4` com gramáticas GBNF e prova de paridade).
