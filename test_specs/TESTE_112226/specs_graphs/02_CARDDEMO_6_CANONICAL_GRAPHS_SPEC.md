# 02 — Especificação Técnica e Visual dos 6 Gráficos Canônicos do AWS CardDemo

**Repositório de Referência:** [`https://github.com/aws-samples/aws-mainframe-modernization-carddemo`](https://github.com/aws-samples/aws-mainframe-modernization-carddemo)  
**Padrões Gráficos Cobertos:**
1. Diagramas nativos do repositório (`diagrams/CARDDEMO-DataModel.drawio` e arquitetura Online/Batch).
2. Gráficos de Decomposição de Domínio e Dependências do **AWS Transform for Mainframe / AWS Blu Age**.
3. **Knowledge Graph Enriquecido** e **Capability Map Radial** do estudo *Legacy Modernization Meets GenAI* (Martin Fowler / Thoughtworks sobre o CardDemo).

---

## 1. Gráfico 1: Modelo de Dados e Topologia de Persistência VSAM + AIX + Copybooks (`CARDDEMO-DataModel`)

### 1.1. Objetivo e Fonte Estrutural
Reproduz o diagrama `diagrams/CARDDEMO-DataModel.drawio` do repositório oficial, conectando cada **Dataset Físico VSAM (`KSDS`/`PS`)**, seus **Índices Alternativos (`AIX Path`)**, o **Copybook COBOL (`.cpy`)** que define seu schema em memória e as **Chaves Primárias/Estrangeiras Lógicas (`1:1`, `1:N`, `N:1`)**.

### 1.2. Representação Gráfica Canônica (Gráfico 1)

```mermaid
erDiagram
    CUSTDATA_VSAM_KSDS {
        string CUST_ID PK "PIC 9(09) - CVCUS01Y.cpy (500B)"
        string CUST_FIRST_NAME "PIC X(25)"
        string CUST_LAST_NAME "PIC X(25)"
        string CUST_SSN "PIC 9(09)"
        string CUST_FICO_CREDIT_SCORE "PIC 9(03)"
    }

    CARDXREF_VSAM_KSDS {
        string XREF_CARD_NUM PK "PIC X(16) - CVACT03Y.cpy (50B)"
        string XREF_CUST_ID FK "PIC 9(09) -> CUSTDATA.CUST_ID"
        string XREF_ACCT_ID FK "PIC 9(11) [AIX: CXACAIX] -> ACCTDATA.ACCT_ID"
    }

    ACCTDATA_VSAM_KSDS {
        string ACCT_ID PK "PIC 9(11) - CVACT01Y.cpy (300B)"
        string ACCT_ACTIVE_STATUS "PIC X(01)"
        decimal ACCT_CURR_BAL "PIC S9(10)V99"
        decimal ACCT_CREDIT_LIMIT "PIC S9(10)V99"
        decimal ACCT_CASH_CREDIT_LIMIT "PIC S9(10)V99"
        string ACCT_EXPIRAION_DATE "PIC X(10)"
        string ACCT_GROUP_ID FK "PIC X(10) -> DISCGRP.DIS_ACCT_GROUP_ID"
    }

    CARDDATA_VSAM_KSDS {
        string CARD_NUM PK "PIC X(16) - CVACT02Y.cpy (150B)"
        string CARD_ACCT_ID FK "PIC 9(11) [AIX: CARDAIX] -> ACCTDATA.ACCT_ID"
        string CARD_CVV_CD "PIC 9(03)"
        string CARD_EMBOSSED_NAME "PIC X(50)"
        string CARD_EXPIRAION_DATE "PIC X(10)"
        string CARD_ACTIVE_STATUS "PIC X(01)"
    }

    TRANSACT_VSAM_KSDS {
        string TRAN_ID PK "PIC X(16) - CVTRA05Y.cpy (350B)"
        string TRAN_TYPE_CD FK "PIC X(02) -> TRANTYPE.TRAN_TYPE"
        string TRAN_CAT_CD FK "PIC 9(04) -> TRANCATG.TRAN_CAT_CD"
        string TRAN_SOURCE "PIC X(10)"
        decimal TRAN_AMT "PIC S9(09)V99"
        string TRAN_CARD_NUM FK "PIC X(16) [AIX: TRANAIX] -> CARDDATA.CARD_NUM"
        string TRAN_ORIG_TS "PIC X(26)"
        string TRAN_PROC_TS "PIC X(26)"
    }

    TCATBALF_VSAM_KSDS {
        string TRANCAT_ACCT_ID PK,FK "PIC 9(11) - CVTRA01Y.cpy (50B)"
        string TRANCAT_TYPE_CD PK,FK "PIC X(02)"
        string TRANCAT_CD PK,FK "PIC 9(04)"
        decimal TRAN_CAT_BAL "PIC S9(09)V99"
    }

    DISCGRP_VSAM_KSDS {
        string DIS_ACCT_GROUP_ID PK "PIC X(10) - CVTRA02Y.cpy (50B)"
        string DIS_TRAN_TYPE_CD PK,FK "PIC X(02)"
        string DIS_TRAN_CAT_CD PK,FK "PIC 9(04)"
        decimal DIS_INT_RATE "PIC S9(04)V99"
    }

    TRANTYPE_VSAM_KSDS {
        string TRAN_TYPE PK "PIC X(02) - CVTRA03Y.cpy (60B)"
        string TRAN_TYPE_DESC "PIC X(50)"
    }

    TRANCATG_VSAM_KSDS {
        string TRAN_TYPE_CD PK,FK "PIC X(02) - CVTRA04Y.cpy (60B)"
        string TRAN_CAT_CD PK "PIC 9(04)"
        string TRAN_CAT_TYPE_DESC "PIC X(50)"
    }

    USRSEC_VSAM_KSDS {
        string SEC_USR_ID PK "PIC X(08) - CSUSR01Y.cpy (80B)"
        string SEC_USR_FNAME "PIC X(20)"
        string SEC_USR_LNAME "PIC X(20)"
        string SEC_USR_PWD "PIC X(08)"
        string SEC_USR_TYPE "PIC X(01) ['A'=Admin, 'U'=User]"
    }

    CUSTDATA_VSAM_KSDS ||--o{ CARDXREF_VSAM_KSDS : "1:N (XREF-CUST-ID)"
    ACCTDATA_VSAM_KSDS ||--o{ CARDXREF_VSAM_KSDS : "1:N (XREF-ACCT-ID / CXACAIX)"
    ACCTDATA_VSAM_KSDS ||--o{ CARDDATA_VSAM_KSDS : "1:N (CARD-ACCT-ID / CARDAIX)"
    CARDDATA_VSAM_KSDS ||--|| CARDXREF_VSAM_KSDS : "1:1 (CARD-NUM = XREF-CARD-NUM)"
    CARDDATA_VSAM_KSDS ||--o{ TRANSACT_VSAM_KSDS : "1:N (TRAN-CARD-NUM / TRANAIX)"
    ACCTDATA_VSAM_KSDS ||--o{ TCATBALF_VSAM_KSDS : "1:N (TRANCAT-ACCT-ID)"
    DISCGRP_VSAM_KSDS }o--|| ACCTDATA_VSAM_KSDS : "N:1 (ACCT-GROUP-ID)"
    TRANTYPE_VSAM_KSDS ||--o{ TRANCATG_VSAM_KSDS : "1:N (TRAN-TYPE-CD)"
    TRANCATG_VSAM_KSDS ||--o{ TRANSACT_VSAM_KSDS : "1:N (TRAN-TYPE-CD + TRAN-CAT-CD)"
    TRANCATG_VSAM_KSDS ||--o{ TCATBALF_VSAM_KSDS : "1:N (TRANCAT-TYPE-CD + TRANCAT-CD)"
    TRANCATG_VSAM_KSDS ||--o{ DISCGRP_VSAM_KSDS : "1:N (DIS-TRAN-TYPE-CD + DIS-TRAN-CAT-CD)"
```

---

## 2. Gráfico 2: Fluxo de Chamadas Online CICS, Transações, Mapas BMS e `DFHCOMMAREA` (`Online CICS Screen & Call Flow Graph`)

### 2.1. Objetivo e Fonte Estrutural
Mapeia o **Nível 2 (Call Flow Comprehension)** para o subsistema Online CICS (`carddemo-cics-online`), rastreando:
- O ponto de entrada (`FLOW_START`): Transação `CC00` $\rightarrow$ Mapa `COSGN00` $\rightarrow$ Programa `COSGN00C`.
- As **Pré-Condições** (`urn:ia1:precond:*`): Validação de credenciais em `USRSEC` e bifurcação por `SEC-USR-TYPE` (`'A'` vs. `'U'`).
- O transporte de estado em memória RAM via `DFHCOMMAREA` (`COCOM01Y.cpy`).
- Os pontos terminais de persistência (`FLOW_END`): leituras e escritas em `USRSEC`, `ACCTDAT`, `CUSTDAT`, `CARDDAT`, `CCXREF`, `TRANSACT` e a fila `INTRDR`.

### 2.2. Representação Gráfica Canônica (Gráfico 2)

```mermaid
flowchart TD
    subgraph ENTRY["Porta de Entrada CICS 3270 (Sign-On)"]
        TX_CC00(["Tx: CC00 | Mapa BMS: COSGN00\nPrograma: COSGN00C.cbl\n[Precond P1: UserId & Pwd != Spaces]\n[Precond P2: Registro existe em USRSEC]"])
    end

    subgraph MENUS["Roteadores de Menu (Bifurcação por SEC-USR-TYPE em COCOM01Y)"]
        TX_CA00["Tx: CA00 | Mapa: COADM01\nPrograma: COADM01C.cbl (Admin Menu)\n[Precond: SEC-USR-TYPE == 'A']"]
        TX_CM00["Tx: CM00 | Mapa: COMEN01\nPrograma: COMEN01C.cbl (Main Menu)\n[Precond: SEC-USR-TYPE == 'U']"]
    end

    subgraph ADMIN_FLOWS["Fluxos de Administração de Usuários (CICS)"]
        CU00["Tx: CU00 | COUSR00C (User List)\nBMS: COUSR00"]
        CU01["Tx: CU01 | COUSR01C (User Add)\nBMS: COUSR01"]
        CU02["Tx: CU02 | COUSR02C (User Update)\nBMS: COUSR02"]
        CU03["Tx: CU03 | COUSR03C (User Delete)\nBMS: COUSR03"]
    end

    subgraph USER_FLOWS["Fluxos Transacionais de Cartão de Crédito (CICS)"]
        CAVW["Tx: CAVW | COACTVWC (Account View)\nBMS: COACTVW"]
        CAUP["Tx: CAUP | COACTUPC (Account Update)\nBMS: COACTUP\n[Preconds: Validação FICO, Limite, Datas, CPF/SSN]"]
        CCLI["Tx: CCLI | COCRDLIC (Card List)\nBMS: COCRDLI"]
        CCDL["Tx: CCDL | COCRDSLC (Card Detail)\nBMS: COCRDSL"]
        CCUP["Tx: CCUP | COCRDUPC (Card Update)\nBMS: COCRDUP\n[Preconds: Luhn/16 dígitos, CVV, Status, Expiração]"]
        CT00["Tx: CT00 | COTRN00C (Transaction List)\nBMS: COTRN00"]
        CT01["Tx: CT01 | COTRN01C (Transaction View)\nBMS: COTRN01"]
        CT02["Tx: CT02 | COTRN02C (Transaction Add)\nBMS: COTRN02\n[CALL 'CSUTLDTC' | Precond: Cartão válido em CCXREF]"]
        CB00["Tx: CB00 | COBIL00C (Bill Payment)\nBMS: COBIL00\n[Precond: ACCT-CURR-BAL > 0 & Confirm == 'Y']"]
        CR00["Tx: CR00 | CORPT00C (Transaction Reports)\nBMS: CORPT00\n[CALL 'CSUTLDTC' | Submete JCL via INTRDR]"]
    end

    subgraph VSAM_SINKS["Sinks de Persistência VSAM e Filas (Nível 1)"]
        DB_USRSEC[("VSAM KSDS: USRSEC\n(CSUSR01Y)")]
        DB_ACCT[("VSAM KSDS: ACCTDAT\n(CVACT01Y)")]
        DB_CUST[("VSAM KSDS: CUSTDAT\n(CVCUS01Y)")]
        DB_CARD[("VSAM KSDS: CARDDAT\n(CVACT02Y)")]
        DB_XREF[("VSAM KSDS/AIX: CCXREF\n(CVACT03Y)")]
        DB_TRAN[("VSAM KSDS: TRANSACT\n(CVTRA05Y)")]
        Q_INTRDR[["Fila CICS TD: INTRDR\n(Dispara Job Batch TRANREPT.jcl)"]]
    end

    TX_CC00 -->|"READ"| DB_USRSEC
    TX_CC00 -->|"XCTL (COMMAREA: USR-TYPE='A')"| TX_CA00
    TX_CC00 -->|"XCTL (COMMAREA: USR-TYPE='U')"| TX_CM00

    TX_CA00 -->|"XCTL Opt 1"| CU00
    TX_CA00 -->|"XCTL Opt 2"| CU01
    TX_CA00 -->|"XCTL Opt 3"| CU02
    TX_CA00 -->|"XCTL Opt 4"| CU03
    CU00 -->|"XCTL Sel 'U'"| CU02
    CU00 -->|"XCTL Sel 'D'"| CU03
    CU00 & CU01 & CU02 & CU03 -->|"BROWSE / WRITE / REWRITE / DELETE"| DB_USRSEC

    TX_CM00 -->|"XCTL Opt 01"| CAVW
    TX_CM00 -->|"XCTL Opt 02"| CAUP
    TX_CM00 -->|"XCTL Opt 03"| CCLI
    TX_CM00 -->|"XCTL Opt 04"| CCDL
    TX_CM00 -->|"XCTL Opt 05"| CCUP
    TX_CM00 -->|"XCTL Opt 06"| CT00
    TX_CM00 -->|"XCTL Opt 07"| CT01
    TX_CM00 -->|"XCTL Opt 08"| CT02
    TX_CM00 -->|"XCTL Opt 09"| CR00
    TX_CM00 -->|"XCTL Opt 10"| CB00

    CCLI -->|"XCTL Sel 'S'"| CCDL
    CCLI -->|"XCTL Sel 'U'"| CCUP
    CT00 -->|"XCTL Sel 'S'"| CT01

    CAVW -->|"READ"| DB_XREF & DB_ACCT & DB_CUST
    CAUP -->|"READ / REWRITE"| DB_XREF & DB_ACCT & DB_CUST
    CCLI & CCDL -->|"BROWSE / READ"| DB_CARD
    CCUP -->|"READ / REWRITE"| DB_CARD
    CT00 & CT01 -->|"BROWSE / READ"| DB_TRAN
    CT02 -->|"READ CCXREF / WRITE TRANSACT"| DB_XREF & DB_TRAN
    CB00 -->|"REWRITE Saldo=0 / WRITE Pagto"| DB_ACCT & DB_XREF & DB_TRAN
    CR00 -->|"WRITEQ TD"| Q_INTRDR
```

---

## 3. Gráfico 3: Pipeline de Execução Batch JCL, Utilitários e Linhagem de Datasets/GDGs (`Batch JCL & Dataset Lineage Graph`)

### 3.1. Objetivo e Fonte Estrutural
Representa o fluxo operacional noturno (Batch Processing Path) coordenado pelos scripts `app/jcl/*.jcl` (`POSTTRAN.jcl`, `INTCALC.jcl`, `COMBTRAN.jcl`, `TRANBKP.jcl`, `CREASTMT.jcl`, `TRANREPT.jcl`), detalhando como os dados saem dos arquivos sequenciais de movimento diário (`DALYTRAN.PS`), passam por validações e cálculos de juros, atualizam os arquivos mestres VSAM (`ACCTDATA`, `TCATBALF`, `TRANSACT`) e geram relatórios e faturas (`TRANREPT`, `STATEMNT.PS`, `STATEMNT.HTML`).

### 3.2. Representação Gráfica Canônica (Gráfico 3)

```mermaid
flowchart LR
    subgraph INPUT_DAILY["Entrada Diária & Ponte Online"]
        DS_DALY[("Dataset Sequencial: DALYTRAN.PS\n(CVTRA06Y - Movimento Diário)")]
        ONLINE_RPT(["Online CICS: CORPT00C (Tx CR00)\nSubmete JCL via INTRDR"])
    end

    subgraph JCL_POST["1. Job: POSTTRAN.jcl (Posting Diário)"]
        PGM_CBTRN02C["STEP15: EXEC PGM=CBTRN02C\n[CALL 'CSUTLDTC']\n[Preconds: Cartão existe em CARDXREF;\nConta existe em ACCTDATA;\nSaldo + Tran <= ACCT-CREDIT-LIMIT;\nACCT-EXPIRAION-DATE >= TranDate]"]
    end

    subgraph VSAM_MASTERS["Datasets Mestres VSAM KSDS (Compartilhados com CICS)"]
        VSAM_XREF[("CARDXREF.VSAM.KSDS\n+ AIX CXACAIX")]
        VSAM_ACCT[("ACCTDATA.VSAM.KSDS\n(Saldos Atualizados)")]
        VSAM_TCAT[("TCATBALF.VSAM.KSDS\n(Saldo por Categoria)")]
        VSAM_DISC[("DISCGRP.VSAM.KSDS\n(Taxas de Juros)")]
        VSAM_TRAN[("TRANSACT.VSAM.KSDS\n(Transações Efetivadas)")]
        VSAM_CUST[("CUSTDATA.VSAM.KSDS\n(Dados do Cliente)")]
        VSAM_TTYP[("TRANTYPE & TRANCATG\n(Tabelas de Domínio)")]
    end

    subgraph REJECTS["Saída de Rejeitados"]
        DS_REJS[("GDG: DALYREJS.GnnnnV00\n(Transações Rejeitadas + Motivo)")]
    end

    subgraph JCL_INT["2. Job: INTCALC.jcl (Cálculo de Juros)"]
        PGM_CBACT04C["STEP05: EXEC PGM=CBACT04C\n[TX_CALC: Juros = (TRAN-CAT-BAL * DIS-INT-RATE) / 1200]\n[Atualiza ACCT-CURR-BAL e emite transação de juros]"]
        DS_SYSTRAN[("GDG: SYSTRAN.GnnnnV00\n(Transações de Juros Geradas)")]
    end

    subgraph JCL_RPT["3. Job: TRANREPT.jcl (Relatório de Transações)"]
        STEP_SORT["STEP05: EXEC PGM=SORT\n(Filtra e ordena TRANSACT por data)"]
        PGM_CBTRN03C["STEP10: EXEC PGM=CBTRN03C\n[CALL 'CSUTLDTC']\n(Join TRANSACT + CARDXREF + TRANTYPE + TRANCATG)"]
        DS_RPT[("GDG: TRANREPT.GnnnnV00\n(Relatório Formatado 133 col)")]
    end

    subgraph JCL_STMT["4. Job: CREASTMT.jcl (Emissão de Faturas)"]
        PGM_CBSTM03A["STEP040: EXEC PGM=CBSTM03A\n--[CALL]--> PGM=CBSTM03B\n(Monta extrato mensal por Conta/Cliente)"]
        DS_STMT_TXT[("Dataset: STATEMNT.PS\n(Fatura Texto)")]
        DS_STMT_HTML[("Dataset: STATEMNT.HTML\n(Fatura HTML)")]
    end

    DS_DALY -->|"DD DALYTRAN (INPUT)"| PGM_CBTRN02C
    VSAM_XREF -->|"DD XREFFILE (INPUT)"| PGM_CBTRN02C
    PGM_CBTRN02C -->|"DD ACCTFILE (I-O REWRITE)"| VSAM_ACCT
    PGM_CBTRN02C -->|"DD TCATBALF (I-O WRITE/REWRITE)"| VSAM_TCAT
    PGM_CBTRN02C -->|"DD TRANFILE (OUTPUT WRITE)"| VSAM_TRAN
    PGM_CBTRN02C -->|"DD DALYREJS (OUTPUT Rejeitados)"| DS_REJS

    VSAM_TCAT -->|"DD TCATBALF (INPUT)"| PGM_CBACT04C
    VSAM_XREF -->|"DD XREFFILE (AIX PATH)"| PGM_CBACT04C
    VSAM_DISC -->|"DD DISCGRP (INPUT)"| PGM_CBACT04C
    PGM_CBACT04C -->|"DD ACCTFILE (I-O REWRITE)"| VSAM_ACCT
    PGM_CBACT04C -->|"DD TRANSACT (OUTPUT)"| DS_SYSTRAN

    ONLINE_RPT -.->|"WRITEQ TD INTRDR"| STEP_SORT
    VSAM_TRAN -->|"DD SORTIN"| STEP_SORT
    STEP_SORT -->|"DD TRANFILE"| PGM_CBTRN03C
    VSAM_XREF & VSAM_TTYP -->|"INPUT Lookup"| PGM_CBTRN03C
    PGM_CBTRN03C -->|"DD TRANREPT"| DS_RPT

    VSAM_TRAN & VSAM_XREF & VSAM_CUST & VSAM_ACCT -->|"Via CBSTM03B"| PGM_CBSTM03A
    PGM_CBSTM03A -->|"DD STMTFILE"| DS_STMT_TXT
    PGM_CBSTM03A -->|"DD HTMLFILE"| DS_STMT_HTML
```

---

## 4. Gráfico 4: Grafo de Dependências Estruturais Estáticas (`Programs × Copybooks × Subroutines × BMS`)

### 4.1. Objetivo e Fonte Estrutural
Exibe a árvore de acoplamento em tempo de compilação e linkedição (*Dependency View* do AWS Transform / Blu Age), mostrando quais Copybooks de dados (`CV*Y.cpy`, `CSUSR01Y.cpy`), Copybooks de sessão (`COCOM01Y.cpy`) e Sub-rotinas (`CSUTLDTC`, `CBSTM03B`) são compartilhados entre múltiplos programas COBOL.

### 4.2. Representação Gráfica Canônica (Gráfico 4)

```mermaid
flowchart TD
    subgraph SHARED_CPY["Copybooks de Dados & Sessão Compartilhados (app/cpy/)"]
        CPY_COMM["COCOM01Y.cpy\n(CARDDEMO-COMMAREA)\n[17 Programas Online]"]
        CPY_USR["CSUSR01Y.cpy\n(SEC-USER-DATA)\n[7 Programas Online]"]
        CPY_ACT1["CVACT01Y.cpy\n(ACCOUNT-RECORD)\n[7 Online + 6 Batch = 13 Pgms]"]
        CPY_ACT2["CVACT02Y.cpy\n(CARD-RECORD)\n[4 Online + 2 Batch = 6 Pgms]"]
        CPY_ACT3["CVACT03Y.cpy\n(CARD-XREF-RECORD)\n[5 Online + 6 Batch = 11 Pgms]"]
        CPY_CUS1["CVCUS01Y.cpy\n(CUSTOMER-RECORD)\n[4 Online + 3 Batch = 7 Pgms]"]
        CPY_TRA5["CVTRA05Y.cpy\n(TRAN-RECORD)\n[5 Online + 4 Batch = 9 Pgms]"]
        CPY_TRA12["CVTRA01Y & CVTRA02Y\n(TCATBAL & DISCGRP)\n[CBTRN02C, CBACT04C]"]
        CPY_TRA34["CVTRA03Y & CVTRA04Y\n(TRANTYPE & TRANCATG)\n[CBTRN03C]"]
    end

    subgraph SUBROUTINES["Sub-rotinas COBOL Invocadas via CALL"]
        SUB_DATE[["CSUTLDTC.cbl\n(Validador de Datas CEEDAYS)"]]
        SUB_STMT[["CBSTM03B.cbl\n(Subprograma I/O Faturas)"]]
    end

    subgraph PGMS_AUTH["Cluster 1: Auth & Users"]
        P_AUTH["COSGN00C, COMEN01C, COADM01C,\nCOUSR00C, COUSR01C, COUSR02C, COUSR03C"]
    end

    subgraph PGMS_ACCT_CARD["Cluster 2: Accounts & Cards (Online + Batch)"]
        P_AC["COACTVWC, COACTUPC, COCRDLIC, COCRDSLC, COCRDUPC,\nCBACT01C, CBACT02C, CBACT03C, CBCUS01C"]
    end

    subgraph PGMS_TRAN_BILL["Cluster 3: Transactions, Billing, Interest & Reports"]
        P_TB_ON["COTRN00C, COTRN01C, COTRN02C, COBIL00C, CORPT00C"]
        P_TB_BT["CBTRN01C, CBTRN02C, CBTRN03C, CBACT04C, CBSTM03A"]
    end

    P_AUTH & P_AC & P_TB_ON -->|"COPY"| CPY_COMM
    P_AUTH -->|"COPY"| CPY_USR
    P_AC -->|"COPY"| CPY_ACT1 & CPY_ACT2 & CPY_ACT3 & CPY_CUS1
    P_TB_ON -->|"COPY"| CPY_TRA5 & CPY_ACT1 & CPY_ACT3
    P_TB_BT -->|"COPY"| CPY_ACT1 & CPY_ACT3 & CPY_TRA5 & CPY_TRA12 & CPY_TRA34

    P_TB_ON -->|"CALL 'CSUTLDTC' (COTRN02C, CORPT00C)"| SUB_DATE
    P_TB_BT -->|"CALL 'CSUTLDTC' (CBTRN02C, CBTRN03C)"| SUB_DATE
    P_TB_BT -->|"CALL 'CBSTM03B' (CBSTM03A)"| SUB_STMT
```

---

## 5. Gráfico 5: Decomposição de Domínios e Acoplamento Multi-Aplicação (`Nível 4 de specs_test_ia1` / AWS Transform Domain View)

### 5.1. Aplicação da Fórmula do Nível 4 ($W_D = |S_D| + |P_D|$) sobre o CardDemo
Aplicando as regras do **Nível 3 (Glossário Semântico e Heurísticas)** e do **Nível 4 (Equação $W_D = |S_D| + |P_D|$ e Contagem de Aplicações Envolvidas)** de `specs_test_ia1` sobre o repositório CardDemo, emergem **6 Domínios de Negócio**:

| Domínio (`domain_uid`) | Termos Âncora do Glossário (`Nível 3`) | Identidade Estrutural Raiz (`Nível 1`) | Identidades Estruturais ($\|S_D\|$) | Pré-Condições Mapeadas ($\|P_D\|$) | Score Total ($W_D = \|S_D\| + \|P_D\|$) | Classificação (`Nível 4`) | Aplicações Envolvidas ($\text{AppCount}$) |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **`D1: SECURITY_AND_USER_ADMIN`** | `User`, `Password`, `UserType`, `SignOn`, `Admin` | `urn:ia1:storage:vsam-ksds:carddemo:USRSEC` (`CSUSR01Y`) | 24 | 28 | **52** | `DOMINIO_TRANSACIONAL_DE_NEGOCIO` (`#F57C00`) | **1** (`carddemo-cics-online`) |
| **`D2: ACCOUNT_AND_CUSTOMER_MGMT`** | `Account`, `Customer`, `CreditLimit`, `Balance`, `FicoScore` | `urn:ia1:storage:vsam-ksds:carddemo:ACCTDATA` (`CVACT01Y`) | 31 | 48 | **79** | `DOMINIO_TRANSACIONAL_DE_NEGOCIO` (`#F57C00`) | **2** (`carddemo-cics-online`, `carddemo-batch-jcl`) |
| **`D3: CREDIT_CARD_LIFECYCLE`** | `CardNumber`, `CvvCode`, `EmbossedName`, `CardStatus`, `ExpirationDate` | `urn:ia1:storage:vsam-ksds:carddemo:CARDDATA` (`CVACT02Y`) | 22 | 36 | **58** | `DOMINIO_TRANSACIONAL_DE_NEGOCIO` (`#F57C00`) | **2** (`carddemo-cics-online`, `carddemo-batch-jcl`) |
| **`D4: TRANSACTION_PROCESSING_AND_POSTING`** | `Transaction`, `DailyTran`, `Amount`, `CardXref`, `RejectCode` | `urn:ia1:storage:vsam-ksds:carddemo:TRANSACT` (`CVTRA05Y`) | 42 | 64 | **106** | `DOMINIO_CORE_CRITICO` (`#D32F2F`) | **2** (`carddemo-cics-online`, `carddemo-batch-jcl`) |
| **`D5: BILLING_PAYMENT_AND_INTEREST_CALC`** | `InterestRate`, `CategoryBalance`, `DisclosureGroup`, `BillPayment` | `urn:ia1:storage:vsam-ksds:carddemo:TCATBALF` (`CVTRA01Y`) | 26 | 29 | **55** | `DOMINIO_TRANSACIONAL_DE_NEGOCIO` (`#F57C00`) | **2** (`carddemo-cics-online`, `carddemo-batch-jcl`) |
| **`D6: STATEMENTS_AND_REPORTING`** | `Statement`, `TransactionReport`, `DateRange`, `HtmlStatement` | `urn:ia1:storage:seq-ps:carddemo:STATEMNT` (`CVTRA07Y`) | 28 | 24 | **52** | `DOMINIO_TRANSACIONAL_DE_NEGOCIO` (`#F57C00`) | **2** (`carddemo-cics-online` via `INTRDR`, `carddemo-batch-jcl`) |

### 5.2. Representação Gráfica Canônica (Gráfico 5 — Mapa de Bolhas e Fronteiras de Aplicação)

```mermaid
flowchart TD
    subgraph APP_ONLINE["Aplicação 1: carddemo-cics-online (CICS / BMS 3270)"]
        D1_NODE["DOMÍNIO 1: SECURITY & USER ADMIN\nScore W_D = 52 (|S|=24 + |P|=28)\nApps Envolvidas: 1 (Single-App)\n[COSGN00C, COMEN01C, COADM01C, COUSR00C..03C]"]
        ON_D2["Módulos Online D2:\nCOACTVWC, COACTUPC"]
        ON_D3["Módulos Online D3:\nCOCRDLIC, COCRDSLC, COCRDUPC"]
        ON_D4["Módulos Online D4:\nCOTRN00C, COTRN01C, COTRN02C"]
        ON_D5["Módulos Online D5:\nCOBIL00C (Bill Payment)"]
        ON_D6["Módulos Online D6:\nCORPT00C (Report Trigger)"]
    end

    subgraph SHARED_PERSISTENCE["Fronteira de Acoplamento Transversal (VSAM KSDS + Copybooks + Sub-rotinas)"]
        D4_NODE["DOMÍNIO 4: TRANSACTION PROCESSING & POSTING [CORE CRÍTICO]\nScore W_D = 106 (|S|=42 + |P|=64) | Transformações |T|=31\nApps Envolvidas: 2 (Online + Batch)\nÂncora: TRANSACT + CARDXREF + CSUTLDTC"]
        D2_NODE["DOMÍNIO 2: ACCOUNT & CUSTOMER MGMT\nScore W_D = 79 (|S|=31 + |P|=48) | Transformações |T|=22\nApps Envolvidas: 2 (Online + Batch)\nÂncora: ACCTDATA + CUSTDATA"]
        D3_NODE["DOMÍNIO 3: CREDIT CARD LIFECYCLE\nScore W_D = 58 (|S|=22 + |P|=36) | Transformações |T|=14\nApps Envolvidas: 2 (Online + Batch)\nÂncora: CARDDATA + CARDAIX"]
        D5_NODE["DOMÍNIO 5: BILLING & INTEREST CALCULATION\nScore W_D = 55 (|S|=26 + |P|=29) | Transformações |T|=19\nApps Envolvidas: 2 (Online + Batch)\nÂncora: TCATBALF + DISCGRP + ACCTDATA"]
        D6_NODE["DOMÍNIO 6: STATEMENTS & REPORTING\nScore W_D = 52 (|S|=28 + |P|=24) | Transformações |T|=17\nApps Envolvidas: 2 (Online -> INTRDR -> Batch)\nÂncora: TRANREPT + STATEMNT.PS/HTML"]
    end

    subgraph APP_BATCH["Aplicação 2: carddemo-batch-jcl (JCL / Batch COBOL)"]
        BT_D2["Módulos Batch D2:\nCBACT01C, CBACT03C, CBCUS01C"]
        BT_D3["Módulos Batch D3:\nCBACT02C"]
        BT_D4["Módulos Batch D4:\nCBTRN01C, CBTRN02C (POSTTRAN.jcl)"]
        BT_D5["Módulos Batch D5:\nCBACT04C (INTCALC.jcl)"]
        BT_D6["Módulos Batch D6:\nCBTRN03C (TRANREPT.jcl),\nCBSTM03A/B (CREASTMT.jcl)"]
    end

    ON_D2 & BT_D2 --> D2_NODE
    ON_D3 & BT_D3 --> D3_NODE
    ON_D4 & BT_D4 --> D4_NODE
    ON_D5 & BT_D5 --> D5_NODE
    ON_D6 & BT_D6 --> D6_NODE
    D4_NODE <-->|"Acoplamento Forte via ACCTDATA & CARDXREF"| D2_NODE
    D5_NODE <-->|"Acoplamento Forte via ACCTDATA & TRANSACT"| D4_NODE
```

---

## 6. Gráfico 6: Knowledge Graph Enriquecido e Capability Map Radial (*Martin Fowler / CodeConcise*)

### 6.1. Objetivo e Fonte Estrutural
Reproduz o **Knowledge Graph Enriquecido (Figura 5)** e o **Capability Map Radial** do artigo *Legacy Modernization Meets GenAI* (Martin Fowler), onde nós estruturais de AST (Programas, Parágrafos COBOL, Copybooks, Telas BMS e Datasets VSAM) são conectados a nós semânticos gerados via Glossário/LLM (Capacidades de Negócio e Explicações em Linguagem Natural).

### 6.2. Representação Gráfica Canônica (Gráfico 6)

```mermaid
flowchart LR
    ROOT(("Centro:\nAWS CardDemo\nCredit Card System"))

    subgraph L1_CAP["Nível 1: Macro-Capacidades"]
        C1(("1. Controle de Acesso\ne Segurança"))
        C2(("2. Gestão de Contas\ne Clientes"))
        C3(("3. Gestão de Cartões\nde Crédito"))
        C4(("4. Processamento e\nLiquidação de Transações"))
        C5(("5. Faturamento, Pagamentos\ne Cálculo de Juros"))
        C6(("6. Extratos Mensais\ne Relatórios"))
    end

    subgraph L2_PROC["Nível 2: Processos e Regras (Tradução Natural Nível 3)"]
        P1_1["Autenticação 3270 e Roteamento por Perfil"]
        P1_2["CRUD de Operadores no Arquivo USRSEC"]
        P2_1["Consulta e Atualização Cadastral Conta/Cliente"]
        P3_1["Listagem, Consulta e Manutenção de Cartões"]
        P4_1["Autorização e Inclusão Online de Transações"]
        P4_2["Batch Posting Diário e Validação de Limite/Expiração"]
        P5_1["Pagamento Online de Fatura (Zera Saldo)"]
        P5_2["Cálculo Batch de Juros por Grupo e Categoria"]
        P6_1["Geração de Relatório por Período (Online->INTRDR->Batch)"]
        P6_2["Emissão de Fatura Mensal em Texto e HTML"]
    end

    subgraph L3_CODE["Nível 3: Artefatos Físicos (COBOL / BMS / JCL / VSAM)"]
        M1_1["COSGN00C.cbl + COSGN00.bms"]
        M1_2["COADM01C + COUSR00C..03C + USRSEC"]
        M2_1["COACTVWC + COACTUPC + CBACT01C + CBCUS01C"]
        M3_1["COCRDLIC + COCRDSLC + COCRDUPC + CBACT02C"]
        M4_1["COTRN00C + COTRN01C + COTRN02C + CSUTLDTC"]
        M4_2["POSTTRAN.jcl + CBTRN01C + CBTRN02C + DALYTRAN"]
        M5_1["COBIL00C.cbl + COBIL00.bms"]
        M5_2["INTCALC.jcl + CBACT04C + DISCGRP + TCATBALF"]
        M6_1["CORPT00C + INTRDR + TRANREPT.jcl + CBTRN03C"]
        M6_2["CREASTMT.jcl + CBSTM03A + CBSTM03B"]
    end

    ROOT --> C1 & C2 & C3 & C4 & C5 & C6
    C1 --> P1_1 --> M1_1
    C1 --> P1_2 --> M1_2
    C2 --> P2_1 --> M2_1
    C3 --> P3_1 --> M3_1
    C4 --> P4_1 --> M4_1
    C4 --> P4_2 --> M4_2
    C5 --> P5_1 --> M5_1
    C5 --> P5_2 --> M5_2
    C6 --> P6_1 --> M6_1
    C6 --> P6_2 --> M6_2
```
