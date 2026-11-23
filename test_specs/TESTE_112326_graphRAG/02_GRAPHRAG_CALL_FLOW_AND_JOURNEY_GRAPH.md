# Grafo de Fluxos de Chamada e Jornada Cirúrgica (Nível 2) — GraphRAG Centro Cirúrgico FAMEMA

**Especificação Canônica:** `02_GRAPHRAG_CALL_FLOW_AND_JOURNEY_GRAPH.md`  
**Escopo:** Nível 2 — Call Flow Comprehension & Travessia da Jornada Assistencial  
**Domínio:** `urn:domain:centro-cirurgico-procedimentos`  
**Base Documental:** [Guia do Cidadão: Fluxo Centro Cirúrgico](file:///home/walter/repos/metadados_famema/docs_pdf/Guia_do_Cidadao_Fluxo_Centro_Cirurgico.html) & `clusters/centro-cirurgico/screens`

---

## 1. Princípios do Nível 2 (Call Flow) no GraphRAG

O **Nível 2 (Call Flow Comprehension)** estabelece as rotas de travessia do grafo, mapeando como o paciente, as equipes multiprofissionais e as mensagens trafegam entre as entidades canônicas do Nível 1.

O fluxo é estruturado em **duas malhas sincronizadas**:
1. **Malha Clínica Sequencial:** A ordem biológica e assistencial estrita do paciente (Pré-Operatório $\rightarrow$ Trans-Operatório $\rightarrow$ Pós-Operatório Imediato $\rightarrow$ Pós-Operatório Tardio / Alta).
2. **Malha de Execução e Navegação de Software:** A árvore de navegação entre telas WinForms (`canNavigateTo`, `invokedByScreens`), ativação de métodos C# e transações de banco de dados (`PERSISTS_MASTER_TABLE`, `QUERIES_RELATED_TABLE`).

---

## 2. Visão Global da Travessia do Grafo: As 7 Etapas Cronológicas

```mermaid
flowchart TD
    subgraph S1["Etapa 1: Indicação & Fila CROSS"]
        D1["DECI0001MN\n(Inclusão em Lista)"] --> D2["DECG0001 / DECG0002\n(Estratificação de Risco & Idade)"]
        D2 --> D3["DECI0001\n(Manutenção de Demanda)"]
    end

    subgraph S2["Etapa 2: Agendamento & Mapa Operatório"]
        D3 --> M1["DECI0010\n(Agendamento de Data)"]
        M1 --> M2["CCIO0001\n(Painel Mapa Cirúrgico)"]
        M2 --> M3["CCIO0001MapaCirurgia\n(Alocação de Salas HCI/HCII/HCIII)"]
        M2 --> M4["CCIO0001Agendamento\n(Reserva de Vaga & Equipe)"]
    end

    subgraph S3["Etapa 3: Suprimentos, CME & OPME"]
        M2 -.-> K1["DECI0001OrteseProtese\n(Reserva de OPME)"]
        K1 --> K2["KCCI0001\n(Caixa Cirúrgica CME)"]
        K2 --> K3["KCCKitProdutoForms\n(Dispensação de Kit Cirúrgico)"]
    end

    subgraph S4["Etapa 4: Recepção & Preparo Pré-Operatório"]
        M4 --> R1["CCIO0001Confirmacao\n(Confirmação de Chegada)"]
        R1 --> R2["TermoConsentimentoAvaliacaoPreAnestesica\n(TCLE & Parecer Anestésico)"]
        R2 --> R3["Área Pré-Op:\nChecagem de Jejum (8h/2h) & Demarcação de Lateralidade"]
    end

    subgraph S5["Etapa 5: Bloco Operatório & Cirurgia Segura OMS"]
        R3 --> B1["CCIO0002\n(Abertura da Ficha Cirúrgica)"]
        K3 -.-> B1
        B1 --> B2["CCIO0004: Sign-In\n(Antes da Indução Anestésica)"]
        B2 --> B3["CCIO0004: TIME-OUT\n(Pausa Obrigatória em Silêncio Pré-Incisão)"]
        B3 --> B4["CCIO0002Procedimento / UCCirurgia\n(Execução do Ato Operatório)"]
        B4 --> B5["CCIO0004: Sign-Out\n(Contagem de Compressas & Instrumentais)"]
    end

    subgraph S6["Etapa 6: SRPA & Recuperação Pós-Anestésica"]
        B5 --> P1["SMOV5020 / SMOV5020Anestesico\n(Entrada na SRPA & Monitoramento)"]
        P1 --> P2["Avaliação de Despertar:\nAnalgesia, NVPO & Aldrete e Kroulik >= 9"]
    end

    subgraph S7["Etapa 7: Alta & Faturamento SUS / APAC"]
        P2 --> F1["CCIO1000\n(Registro Final da Cirurgia / Laudo PEP)"]
        F1 --> F2["SMOV5053CirurgiaAPAC\n(Emissão de APAC / Faturamento)"]
        F1 --> F3["rptCirurgiaRegistro\n(Relatório Operatório & Censo)"]
    end
```

---

## 3. Detalhamento dos Sub-Fluxos e Travessias de Chamada

### Sub-Fluxo 1: Indicação Cirúrgica, Lista de Espera e Regulação CROSS

```mermaid
flowchart LR
    A1["Ambulatório Especializado\nou Urgência PS"] -->|"Indicação Médica"| B1["DECI0001MN\n(Cadastro de Demanda)"]
    B1 -->|"Estratifica Gravidade"| B2["DECG0001 / DECG0002\n(Score Clínico / Idade)"]
    B2 -->|"Solicita Insumos Iniciais"| B3["DECI0001Insumo\nDECI0001Insumomn"]
    B2 -->|"Solicita Órteses / Próteses"| B4["DECI0001OrteseProtese\nDECI0001OrteseProtesemn"]
    B2 -->|"Exporta para Fila CROSS"| B5["Interface Governamental CROSS\n(Estado de SP)"]
```

- **Ponto de Entrada:** Médico do ambulatório ou da urgência diagnostica a necessidade cirúrgica.
- **Transação:** Gravação em `SIHOSP.DEMANDA_CIRURGICA` e `SIHOSP.DEMANDA_CIRURGICA_PROCEDIMENTO`.
- **Regra de Decisão:** `DECG_ESTRATIFICACAO` calcula a prioridade com base na gravidade da patologia, idade do paciente e presença de comorbidades.
- **Portão de Saída:** Demanda ativa aguardando liberação de cota hospitalar.

---

### Sub-Fluxo 2: Planejamento, Agendamento e Mapa Cirúrgico Diário

```mermaid
flowchart TD
    D1["Demanda em Fila Liberada"] --> D2["DECI0010\n(Agendamento de Data)"]
    D2 -->|"Dispara Agendamento"| D3["CCIO0001\n(Painel Geral do Mapa Cirúrgico)"]
    
    subgraph MODAIS["Telas Modais de Apoio ao Mapa"]
        D3 --> M1["CCIO0001Agendamento\n(Edição de Horário / Porte)"]
        D3 --> M2["CCIO0001MapaCirurgia\n(Distribuição de Salas)"]
        D3 --> M3["CCIO0001EditarPrestador\n(Alocação de Cirurgiões / Anestesistas)"]
        D3 --> M4["CCIO0001Material\n(Alocação de Equipamentos Especiais)"]
        D3 --> M5["CCIO0001Suspensao\n(Cancelamento com Justificativa)"]
    end
    
    M2 -->|"Valida Capacidade da Sala"| S_CHK{"Regra Parametrizada\nSALA_CIRURGICA"}
    S_CHK -->|"Aprovado"| D4["SIHOSP.MAPA_CIRURGICO\n(Mapa Consolidado Emitido)"]
```

- **Ponto de Entrada:** `DECI0010` (Agendamento de Data Cirúrgica).
- **Validações Pré-Agendamento:**
  - Checagem de óbito: `SIHOSP.PACIENTE.DAT_OBITO IS NULL`.
  - Checagem de cadastro: `SIHOSP.CA_CLIENTE.STATUS != 'INATIVO'`.
  - Reserva prévia de sangue no Hemocentro para cirurgias com perda sanguínea prevista $\ge 500\text{ ml}$ (Regra `RN-CC-001`).
- **Orquestração Física:** Alocação entre salas de cirurgia geral em HCI (Salas 1 a 6), pediátricas/obstétricas em HCII (Salas 1 a 3) e oftalmológicas em HCIII (Salas 1 e 2).

---

### Sub-Fluxo 3: Central de Materiais Esterilizados (CME), Kits e OPME

```mermaid
flowchart LR
    K0["Mapa Cirúrgico Publicado"] --> K1["KCCI0001\n(Solicitação de Caixas CME)"]
    K1 --> K2["KCCKitProdutoForms\n(Montagem do Kit por Especialidade)"]
    K2 --> K3["KCCInstrumentalForms\n(Controle Unitário de Pinças / Afastadores)"]
    K3 --> K4["KCCMovimentacaoForms\n(Transferência Física CME -> Bloco)"]
    K4 --> K5["DECI0001OrteseProtese\n(Conferência de OPME & Lote/Série)"]
    K5 --> K6["Sala Cirúrgica Pronta"]
```

- **Módulos C# Envolvidos:** `KitCirurgicoDLL.dll` (regras e movimentação de estoque estéril) e `KitCirurgicoForms.dll` (interfaces WinForms).
- **Controle de Rastreabilidade:** Cada caixa instrumental possui URN própria e registro de ciclo de autoclave (`DAT_ESTERILIZACAO`, `NUM_LOTE_AUTOCLAVE`). Caixas com ciclo vencido geram bloqueio visual impeditivo.

---

### Sub-Fluxo 4: Recepção, Acolhimento e Cuidados Pré-Operatórios (Guia do Cidadão)

```mermaid
flowchart TD
    P1["Chegada do Paciente no Bloco Cirúrgico\n(2º Andar Prédio São Francisco HCI / HCII / HCIII)"]
    P1 --> P2["Recepção: Localização na Escala do Dia\n(CCIO0001Confirmacao)"]
    P2 --> P3["Instalação da Pulseira de Identificação\n(Conferência Verbal Dupla de Nome e Data de Nascimento)"]
    P3 --> P4["Guarda de Pertences com o Acompanhante\n(Retirada de adornos, piercings e próteses móveis)"]
    P4 --> P5["Área de Espera Pré-Operatória:\nTroca por Roupa Privativa do Hospital (Avental e Touca)"]
    P5 --> P6["Enfermagem: Aferição de Sinais Vitais & Punção de Acesso Venoso"]
    P6 --> P7["Conferência de Jejum Rigoroso (8h sólidos / 2h água)\ne Coleta de Alergias (Medicamentos, Látex, Alimentos)"]
    P7 --> P8["Visita do Cirurgião Responsável:\nDEMARCAÇÃO DE LATERALIDADE NA PELE COM CANETA CIRÚRGICA"]
    P8 --> P9["Conferência do TCLE Assinado\n(TermoConsentimentoAvaliacaoPreAnestesica)"]
    P9 --> P10["Transporte em Maca com Grades até a Sala de Operação"]
```

- **Foco do Guia do Cidadão:** O guia impresso distribuído pela FAMEMA educa o paciente sobre a importância da demarcação de lateralidade ("*maior garantia de que a cirurgia será feita no lado exato*") e desmistifica a repetição de perguntas da equipe sobre seu nome e procedimento ("*Protocolo Internacional de Cirurgia Segura OMS: sua confirmação em voz alta é a melhor barreira contra falhas*").

---

### Sub-Fluxo 5: Bloco Operatório, Cirurgia Segura OMS e Ato Cirúrgico

```mermaid
flowchart TD
    B0["Entrada na Sala de Operação\n(Conforto térmico, passagem para mesa e monitores ECG/SpO2/PNI)"]
    
    subgraph SIGN_IN["1. SIGN-IN (Antes da Indução Anestésica)"]
        B0 --> SI1["CCIO0004 / SIHOSP.CHK_PRE_INDUC_ANEST"]
        SI1 --> SI2["Conferência: Paciente, Sítio Demarcado, Consentimento"]
        SI2 --> SI3["Checagem: Monitor Cardíaco & Oxímetro em Funcionamento"]
        SI3 --> SI4["Alerta Anestésico: Alergias Conhecidas?"]
        SI4 --> SI5["Alerta Cirúrgico: Risco de Via Aérea Difícil ou Aspiração?"]
        SI5 --> SI6["Alerta Transfusional: Risco de Perda > 500ml? Reserva de Sangue no Hemocentro?"]
    end
    
    SIGN_IN -->|"Indução Anestésica Concluída\nParamentação Estéril Concluída"| TIME_OUT
    
    subgraph TIME_OUT["2. TIME-OUT (Pausa Obrigatória em Silêncio Pré-Incisão)"]
        TO1["CCIO0004 / SIHOSP.CHK_PRE_INCISAO_CIR\n(TODA A EQUIPE PARA TUDO EM SILÊNCIO)"]
        TO1 --> TO2["Apresentação Verbal de Toda a Equipe por Nome e Função"]
        TO2 --> TO3["Cirurgião, Anestesista e Enfermagem Confirmam em Voz Alta:\nNome do Paciente, Procedimento Exato e Local/Lado da Incisão"]
        TO3 --> TO4["Cirurgião Revisa: Passos Críticos, Duração Prevista e Perda de Sangue Esperada"]
        TO4 --> TO5["Anestesista Revisa: Preocupações Específicas do Paciente e Estabilidade"]
        TO5 --> TO6["Enfermagem Revisa: Esterilidade Confirmada e Equipamentos Testados"]
        TO6 --> TO7["Checagem Antibiótica: Profilaxia Ministrada nos Últimos 60 Minutos?"]
        TO7 --> TO8["Exibição de Imagens / Exames Essenciais na Sala"]
    end
    
    TIME_OUT -->|"Cirurgia Liberada para Incisão"| ATO["CCIO0002 / UCCirurgia\nExecução do Ato Operatório\n(Incisão, Tempo Cirúrgico, Hemostasia)"]
    
    ATO -->|"Cavidade Pronta para Fechamento"| SIGN_OUT
    
    subgraph SIGN_OUT["3. SIGN-OUT (Antes do Fechamento e Saída de Sala)"]
        SO1["CCIO0004 / SIHOSP.CHK_PRE_SAIDA_SALA_CIR"]
        SO1 --> SO2["Enfermeiro Circulante Confirma Verbalmente:\nNome do Procedimento Registrado"]
        SO2 --> SO3["CONTAGEM RIGOROSA DE COMPRESSAS, AGULHAS E INSTRUMENTAIS\n(Contagem Final == Contagem Inicial)"]
        SO3 --> SO4["Identificação e Etiquetagem de Amostras de Biópsia\n(Leitura em voz alta do nome e tecido)"]
        SO4 --> SO5["Revisão Final: Problemas com Equipamentos a Relatar"]
        SO5 --> SO6["Plano de Pós-Operatório Imediato e Destino (SRPA ou UTI)"]
    end
    
    SIGN_OUT --> B_END["Fim da Cirurgia: Transporte com Monitoramento até a SRPA"]
```

---

### Sub-Fluxo 6: Sala de Recuperação Pós-Anestésica (SRPA) e Vitalidade

```mermaid
flowchart TD
    P1["Chegada na SRPA (1º Andar HCI / HCII / HCIII)"]
    P1 --> P2["Passagem de Plantão Sistêmica:\nAnestesiologista de Sala -> Anestesiologista da SRPA (SMOV5020)"]
    P2 --> P3["Vigilância Multiparamétrica Contínua:\nMonitorização Cardíaca, Oximetria, PA não invasiva e Temperatura"]
    P3 --> P4["Protocolo de Controle de Conforto:\nAnalgesia Escalonada para Dor & Antieméticos para Náusea (NVPO)"]
    P4 --> P5["Comunicação com a Família:\nCirurgião vai à Sala de Espera Externa Informar o Sucesso do Procedimento"]
    
    P4 --> ALDRETE{"Aplicação Contínua do\nÍNDICE DE ALDRETE E KROULIK\n(Consciência, Respiração, Circulação,\nSaturação O2 e Atividade Motora)"}
    
    ALDRETE -->|"< 9 Pontos"| WAIT["Manutenção de Suporte de O2, Hidratação e Observação na SRPA"]
    WAIT --> ALDRETE
    
    ALDRETE -->|">= 9 Pontos & Hemodinâmica Estável"| ALTA_SRPA["Alta Médica da SRPA Autorizada pelo Anestesiologista"]
    
    ALTA_SRPA --> DECISAO_DESTINO{"Tipo de Procedimento"}
    DECISAO_DESTINO -->|"Cirurgia Ambulatorial\n(Hospital-Dia)"| DEST_CASA["Sala de Alta: Lanche Leve,\nOrientações por Escrito &\nRetorno ao Domicílio com Acompanhante Adulto"]
    DECISAO_DESTINO -->|"Cirurgia com Internação"| DEST_LEITO["Transporte Confortável na Maca\npara Quarto / Enfermaria ou UTI (NIR)"]
```

---

### Sub-Fluxo 7: Alta / Destino, Laudo Cirúrgico no PEP e Faturamento APAC / AIH

```mermaid
flowchart LR
    A1["Cirurgia Concluída & SRPA Liberada"] --> A2["CCIO1000\n(Registro Final da Cirurgia)"]
    A2 -->|"Assinatura Digital"| A3["SIHOSP.PEP_CIRURGIA\n(Laudo Operatório no Prontuário)"]
    A2 -->|"Apuração de Itens Consumidos"| A4["SIHOSP.CIRURGIA_ORTESE\n(Baixa de OPME com Lote/Série)"]
    A3 --> A5["SMOV5053CirurgiaAPAC\n(Geração de Fatura Ambulatorial)"]
    A3 --> A6["Faturamento AIH\n(Internação Hospitalar SUS)"]
    A5 & A6 --> A7["Auditoria de Contas & Censo de Produtividade\n(rep9000 / rptCirurgias)"]
```

- **Liquidação Administrativa:** O fechamento só é completado se todos os procedimentos realizados possuírem códigos compatíveis na tabela SIGTAP/SUS e se o consumo de materiais estiver 100% justificado pelo laudo operatório assinado.
