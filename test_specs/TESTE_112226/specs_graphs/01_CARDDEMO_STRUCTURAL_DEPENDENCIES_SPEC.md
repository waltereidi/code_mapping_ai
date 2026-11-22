# 01 — Especificação de Dependências Estruturais e Inventário Canônico do Repositório `aws-mainframe-modernization-carddemo`

**Repositório Analisado:** [`https://github.com/aws-samples/aws-mainframe-modernization-carddemo`](https://github.com/aws-samples/aws-mainframe-modernization-carddemo)  
**Integração Arquitetural:** Camada Fundacional (**Nível 1 — Structural Comprehension**) de `specs_test_ia1`  
**Objetivo:** Catalogar 100% das identidades estruturais únicas e listar todas as **dependências estruturais diretas e indiretas** entre Programas COBOL (`.cbl`), Mapas de Tela BMS (`.bms`), Copybooks (`.cpy`), Transações CICS (`CSD`), Jobs JCL (`.jcl`), Procedures (`.prc`) e Datasets VSAM/Sequenciais/GDG do CardDemo.

---

## 1. Arquitetura Estrutural do Repositório CardDemo

O repositório **CardDemo** é um monolito mainframe de gestão de cartões de crédito dividido em dois subsistemas operacionais que compartilham a mesma camada de persistência VSAM e os mesmos Copybooks de registro:
1. **Aplicação 1 — Subsistema Online Interativo (`app_id: carddemo-cics-online`)**: 15 programas COBOL CICS (`CO*.cbl`), 15 mapas de tela 3270 BMS (`app/bms/*.bms`) e 15 transações CICS (`CC00`, `CM00`, `CA00`, `CAVW`, `CAUP`, `CCLI`, `CCDL`, `CCUP`, `CT00`, `CT01`, `CT02`, `CR00`, `CB00`, `CU00..CU03`).
2. **Aplicação 2 — Subsistema Batch e Pós-Processamento (`app_id: carddemo-batch-jcl`)**: 12 programas COBOL Batch (`CB*.cbl`), sub-rotinas utilitárias compartilhadas (`CSUTLDTC.cbl`, `COBSWAIT.cbl`) e mais de 25 scripts JCL (`app/jcl/*.jcl`) e procedures (`app/proc/*.prc`).
3. **Módulos de Extensão Opcionais (`app_id: carddemo-extensions-db2-ims-mq`)**: Módulos de integração com DB2 (`COTRTLIC.cbl`, `COTRTUPC.cbl`, `CBACT04C` SQL), IMS DB e IBM MQ (`COPAUA0C.cbl`, `COPAUS0C.cbl`, `COPAUS1C.cbl`, `CBPAUP0C.cbl`).

---

## 2. Taxonomia de Dependências Estruturais Mainframe Mapeadas para o Nível 1 (`urn:ia1:*`)

Ao estudar o repositório CardDemo, identificam-se **8 tipos de dependências estruturais** que conectam os artefatos:

| Código | Tipo de Dependência Estrutural | Origem $\rightarrow$ Destino | Mecanismo Sintático no CardDemo | Identidade Canônica no Nível 1 (`specs_test_ia1`) |
| :--- | :--- | :--- | :--- | :--- |
| **`DEP-01`** | **Mapeamento Transação $\rightarrow$ Programa Inicial** | `CICS Transaction` $\rightarrow$ `COBOL CICS Program` | Definição CSD (`DEFINE TRANSACTION(CC00) PROGRAM(COSGN00C)`) e `WORKING-STORAGE` (`WS-TRANID`) | `urn:ia1:code:entrypoint:carddemo-cics:<TRAN_ID>` $\rightarrow$ `urn:ia1:code:type:carddemo-cics:<PGM_NAME>` |
| **`DEP-02`** | **Renderização e Leitura de Mapa 3270 (BMS)** | `COBOL CICS Program` $\leftrightarrow$ `BMS Mapset / Symbolic Copybook` | `EXEC CICS SEND MAP('...') MAPSET('...')` / `EXEC CICS RECEIVE MAP('...')` + `COPY <MAPSET>.` | `urn:ia1:code:method:...` $\rightarrow$ `urn:ia1:mem:contract:carddemo-cics:bms:<MAP_NAME>` |
| **`DEP-03`** | **Inclusão Léxica de Copybook (`COPY`)** | `COBOL Program` $\rightarrow$ `Copybook (.cpy)` | Diretiva `COPY <COPYBOOK_NAME>.` na `DATA DIVISION` (`FILE SECTION`, `WORKING-STORAGE`, `LINKAGE`) ou `PROCEDURE DIVISION` | `urn:ia1:code:type:...` $\xrightarrow{\text{INCLUDES\_COPYBOOK}}$ `urn:ia1:mem:contract:carddemo:cpy:<CPY_NAME>` |
| **`DEP-04`** | **Transferência de Controle CICS com Contexto (`XCTL` / `RETURN TRANSID`)** | `COBOL CICS Program A` $\rightarrow$ `COBOL CICS Program B` | `EXEC CICS XCTL PROGRAM('...') COMMAREA(CARDDEMO-COMMAREA)` e `EXEC CICS RETURN TRANSID('...') COMMAREA(...)` | `urn:ia1:code:method:...` $\xrightarrow{\text{CICS\_XCTL}}$ `urn:ia1:code:type:...` transportando `urn:ia1:mem:session:carddemo:DFHCOMMAREA:COCOM01Y` |
| **`DEP-05`** | **Chamada de Sub-rotina Sincrona (`CALL`)** | `COBOL Program` $\rightarrow$ `COBOL Subroutine` | `CALL 'CSUTLDTC' USING ...` ou `CALL 'CBSTM03B' USING ...` | `urn:ia1:code:method:...` $\xrightarrow{\text{STATIC\_CALL}}$ `urn:ia1:code:method:carddemo:CSUTLDTC::MAIN(...)` |
| **`DEP-06`** | **Acesso CICS File Control a VSAM (`EXEC CICS READ/WRITE/REWRITE/DELETE/STARTBR`)** | `COBOL CICS Program` $\rightarrow$ `VSAM KSDS / AIX File` | `EXEC CICS READ DATASET('ACCTDAT') INTO(...) RIDFLD(...)` | `urn:ia1:code:method:...` $\rightarrow$ `urn:ia1:storage:vsam-ksds:carddemo:AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS` |
| **`DEP-07`** | **Orquestração Batch e Binding Indireto (`JCL Step -> PGM -> FD -> DD -> DSN/GDG`)** | `JCL Job/Step` $\rightarrow$ `Batch Program` $\rightarrow$ `Logical FD` $\rightarrow$ `JCL DD` $\rightarrow$ `Physical Dataset` | `//STEP01 EXEC PGM=CBTRN02C` + `SELECT DALYTRAN-FILE ASSIGN TO DALYTRAN` + `//DALYTRAN DD DSN=AWS.M2.CARDDEMO.DALYTRAN.PS` | `urn:ia1:infra:jcl-step:...` $\rightarrow$ `urn:ia1:code:type:...` $\rightarrow$ `urn:ia1:storage:vsam-ksds|seq-ps|gdg:...` |
| **`DEP-08`** | **Ponte Híbrida Assíncrona Online $\rightarrow$ Batch (`CICS INTRDR`)** | `COBOL CICS Program` $\rightarrow$ `CICS TD Queue INTRDR` $\rightarrow$ `JCL Job` | `EXEC CICS WRITEQ TD QUEUE('INTRDR') FROM(JOB-LINES)` em `CORPT00C.cbl` submetendo `TRANREPT.jcl` | `urn:ia1:code:method:...:CORPT00C::SUBMIT-JOB` $\rightarrow$ `urn:ia1:mem:stream-buffer:cics:INTRDR` $\rightarrow$ `urn:ia1:infra:jcl-job:carddemo-batch:TRANREPT` |

---

## 3. Lista Completa de Dependências Estruturais por Camada do CardDemo

### 3.1. Persistência VSAM, Arquivos Sequenciais, GDGs e Copybooks de Schema (`Nível 1: Storage & Data Contracts`)

Esta tabela lista todos os arquivos de dados do CardDemo, suas chaves primárias, índices alternativos (`AIX`), relacionamentos estruturais (chaves estrangeiras lógicas) e o Copybook que define seu contrato em memória:

| Nome Lógico CICS / DD | Dataset Físico (`DSN`) | Tipo de Persistência | Copybook de Schema (`.cpy`) | Tamanho (Bytes) | Chave Primária (`PK` / `RIDFLD`) | Chaves Estrangeiras (`FK`) e Índices Alternativos (`AIX`) |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **`USRSEC`** | `AWS.M2.CARDDEMO.USRSEC.VSAM.KSDS` | `VSAM_KSDS` | `CSUSR01Y.cpy` (`SEC-USER-DATA`) | 80 | `SEC-USR-ID` (8 bytes) | Isolado (Segurança/Autenticação; `SEC-USR-TYPE`: `'A'`=Admin, `'U'`=User). |
| **`CUSTDAT`** / `CUSTFILE` | `AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS` | `VSAM_KSDS` | `CVCUS01Y.cpy` (`CUSTOMER-RECORD`) | 500 | `CUST-ID` (9 dígitos) | Referenciado por `CARDXREF.XREF-CUST-ID` ($1:N$). |
| **`ACCTDAT`** / `ACCTFILE` | `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS` | `VSAM_KSDS` | `CVACT01Y.cpy` (`ACCOUNT-RECORD`) | 300 | `ACCT-ID` (11 dígitos) | **FK Lógica:** `ACCT-GROUP-ID` $\rightarrow$ `DISCGRP.DIS-ACCT-GROUP-ID`. Referenciado por `CARDDAT`, `CARDXREF` e `TCATBALF`. |
| **`CARDDAT`** / `CARDFILE` | `AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS` | `VSAM_KSDS` + `AIX` (`CARDAIX`) | `CVACT02Y.cpy` (`CARD-RECORD`) | 150 | `CARD-NUM` (16 dígitos) | **FK / AIX:** `CARD-ACCT-ID` (11 dígitos) $\rightarrow$ `ACCTDAT.ACCT-ID` ($N:1$). |
| **`CCXREF`** / `XREFFILE` | `AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS` | `VSAM_KSDS` + `AIX` (`CXACAIX`) | `CVACT03Y.cpy` (`CARD-XREF-RECORD`) | 50 | `XREF-CARD-NUM` (16 dígitos) | **FK 1:** `XREF-CUST-ID` (9 dígitos) $\rightarrow$ `CUSTDAT.CUST-ID` ($N:1$).<br>**FK 2 / AIX:** `XREF-ACCT-ID` (11 dígitos) $\rightarrow$ `ACCTDAT.ACCT-ID` ($N:1$).<br>**FK 3:** `XREF-CARD-NUM` $\leftrightarrow$ `CARDDAT.CARD-NUM` ($1:1$). |
| **`TRANSACT`** / `TRANFILE` | `AWS.M2.CARDDEMO.TRANSACT.VSAM.KSDS` | `VSAM_KSDS` + `AIX` (`TRANAIX`) | `CVTRA05Y.cpy` (`TRAN-RECORD`) | 350 | `TRAN-ID` (16 caracteres) | **FK 1:** `TRAN-CARD-NUM` $\rightarrow$ `CARDDAT.CARD-NUM` / `CCXREF.XREF-CARD-NUM` ($N:1$).<br>**FK 2:** `TRAN-TYPE-CD` $\rightarrow$ `TRANTYPE.TRAN-TYPE` ($N:1$).<br>**FK 3:** `(TRAN-TYPE-CD, TRAN-CAT-CD)` $\rightarrow$ `TRANCATG` ($N:1$). |
| **`DALYTRAN`** | `AWS.M2.CARDDEMO.DALYTRAN.PS` | `SEQ_PS` / `GDG` | `CVTRA06Y.cpy` (`DALYTRAN-RECORD`) | 350 | Sequencial (`DALYTRAN-ID`) | Movimento diário de transações antes do batch posting (`CBTRN02C`) para `TRANSACT`. |
| **`DALYREJS`** | `AWS.M2.CARDDEMO.DALYREJS.PS` | `SEQ_PS` / `GDG` | `CVTRA06Y.cpy` + Código de Rejeição | 430 | Sequencial | Transações diárias rejeitadas nas pré-condições de `CBTRN02C`. |
| **`TCATBALF`** | `AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS` | `VSAM_KSDS` | `CVTRA01Y.cpy` (`TRAN-CAT-BAL-RECORD`) | 50 | Chave Composta (17 bytes): `TRANCAT-ACCT-ID (11) + TRANCAT-TYPE-CD (2) + TRANCAT-CD (4)` | **FK 1:** `TRANCAT-ACCT-ID` $\rightarrow$ `ACCTDAT.ACCT-ID` ($N:1$).<br>**FK 2:** `(TRANCAT-TYPE-CD, TRANCAT-CD)` $\rightarrow$ `TRANCATG` ($N:1$). |
| **`DISCGRP`** | `AWS.M2.CARDDEMO.DISCGRP.VSAM.KSDS` | `VSAM_KSDS` | `CVTRA02Y.cpy` (`DISCLOSURE-GROUP-RECORD`) | 50 | Chave Composta (16 bytes): `DIS-ACCT-GROUP-ID (10) + DIS-TRAN-TYPE-CD (2) + DIS-TRAN-CAT-CD (4)` | Define a taxa de juros (`DIS-INT-RATE`) por grupo de conta e categoria de transação para `CBACT04C`. |
| **`TRANTYPE`** | `AWS.M2.CARDDEMO.TRANTYPE.VSAM.KSDS` | `VSAM_KSDS` | `CVTRA03Y.cpy` (`TRAN-TYPE-RECORD`) | 60 | `TRAN-TYPE` (2 caracteres) | Tabela de domínio de Tipos de Transação. |
| **`TRANCATG`** | `AWS.M2.CARDDEMO.TRANCATG.VSAM.KSDS` | `VSAM_KSDS` | `CVTRA04Y.cpy` (`TRAN-CAT-RECORD`) | 60 | Chave Composta (6 bytes): `TRAN-TYPE-CD (2) + TRAN-CAT-CD (4)` | **FK:** `TRAN-TYPE-CD` $\rightarrow$ `TRANTYPE.TRAN-TYPE` ($N:1$). |
| **`TRANREPT`** | `AWS.M2.CARDDEMO.TRANREPT.GnnnnV00` | `GDG_REPORT_PS` | `CVTRA07Y.cpy` (`REPORT-LAYOUT`) | 133 | Sequencial (Relatório) | Relatório de transações gerado por `CBTRN03C`. |
| **`STMTFILE` / `HTMLFILE`** | `AWS.M2.CARDDEMO.STATEMNT.PS` / `.HTML` | `SEQ_PS_REPORT` | Layouts internos em `CBSTM03A` | 80 / 100 | Sequencial (Fatura) | Faturas mensais em Texto e HTML geradas por `CBSTM03A`. |

---

### 3.2. Matriz de Dependências Estruturais: Programas Online CICS (`app/cbl/CO*.cbl`)

Cada programa Online CICS abaixo possui dependências estruturais estritas com Transações, Mapas BMS, Copybooks de Dados, Copybooks Utilitários/Comunicação, Sub-rotinas, Programas Alvo (`XCTL`) e Arquivos VSAM:

| Programa COBOL (`.cbl`) | Transação CICS | Mapa BMS (`.bms` / `.cpy`) | Copybooks de Dados e Negócio Incluídos (`COPY`) | Copybooks de Tela/Sessão/Utilitários (`COPY`) | Chamadas de Sub-rotina (`CALL`) / Filas | Transferências CICS (`EXEC CICS XCTL`) | Datasets VSAM Acessados (`READ` / `WRITE` / `REWRITE` / `DELETE` / `BROWSE`) |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| **`COSGN00C.cbl`** (Login / Sign-on) | `CC00` | `COSGN00` | `CSUSR01Y` | `COCOM01Y`, `COSGN00`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` (se `SEC-USR-TYPE = 'U'`)<br>$\rightarrow$ `COADM01C` (se `SEC-USR-TYPE = 'A'`) | `USRSEC` (`READ`) |
| **`COMEN01C.cbl`** (Main Menu Usuário) | `CM00` | `COMEN01` | `COMEN02Y`, `CSUSR01Y` | `COCOM01Y`, `COMEN01`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COSGN00C` (F3 Exit)<br>$\rightarrow$ `COACTVWC`, `COACTUPC`, `COCRDLIC`, `COCRDSLC`, `COCRDUPC`, `COTRN00C`, `COTRN01C`, `COTRN02C`, `CORPT00C`, `COBIL00C` | — |
| **`COADM01C.cbl`** (Admin Menu) | `CA00` | `COADM01` | `COADM02Y`, `CSUSR01Y` | `COCOM01Y`, `COADM01`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COSGN00C` (F3 Exit)<br>$\rightarrow$ `COUSR00C`, `COUSR01C`, `COUSR02C`, `COUSR03C` | — |
| **`COACTVWC.cbl`** (Account View) | `CAVW` | `COACTVW` | `CVACT01Y`, `CVACT02Y`, `CVACT03Y`, `CVCUS01Y` | `COCOM01Y`, `COACTVW`, `CSDAT01Y`, `CSMSG01Y`, `CSMSG02Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` | `CCXREF` (`READ` via AIX `CXACAIX`), `ACCTDAT` (`READ`), `CUSTDAT` (`READ`) |
| **`COACTUPC.cbl`** (Account Update) | `CAUP` | `COACTUP` | `CVACT01Y`, `CVACT03Y`, `CVCUS01Y` | `COCOM01Y`, `COACTUP`, `CSDAT01Y`, `CSMSG01Y`, `CSMSG02Y`, `CSSETATY`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` | `CCXREF` (`READ` via `CXACAIX`), `ACCTDAT` (`READ`, `READ UPDATE`, `REWRITE`), `CUSTDAT` (`READ`, `READ UPDATE`, `REWRITE`) |
| **`COCRDLIC.cbl`** (Credit Card List) | `CCLI` | `COCRDLI` | `CVACT01Y`, `CVACT02Y` | `COCOM01Y`, `COCRDLI`, `CSDAT01Y`, `CSMSG01Y`, `CSSETATY`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` (F3)<br>$\rightarrow$ `COCRDSLC` (Select `'S'` View)<br>$\rightarrow$ `COCRDUPC` (Select `'U'` Update) | `CARDDAT` (`STARTBR`, `READNEXT`, `READPREV`, `ENDBR` / via `CARDAIX`) |
| **`COCRDSLC.cbl`** (Credit Card Detail View) | `CCDL` | `COCRDSL` | `CVACT01Y`, `CVACT02Y`, `CVCUS01Y` | `COCOM01Y`, `COCRDSL`, `CSDAT01Y`, `CSMSG01Y`, `CSSETATY`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` ou `COCRDLIC` (via `CDEMO-FROM-PROGRAM`) | `CARDDAT` (`READ` / via `CARDAIX`) |
| **`COCRDUPC.cbl`** (Credit Card Update) | `CCUP` | `COCRDUP` | `CVACT01Y`, `CVACT02Y`, `CVCUS01Y` | `COCOM01Y`, `COCRDUP`, `CSDAT01Y`, `CSMSG01Y`, `CSMSG02Y`, `CSSETATY`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` ou `COCRDLIC` (via `CDEMO-FROM-PROGRAM`) | `CARDDAT` (`READ`, `READ UPDATE`, `REWRITE`) |
| **`COTRN00C.cbl`** (Transaction List) | `CT00` | `COTRN00` | `CVTRA05Y` | `COCOM01Y`, `COTRN00`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` (F3)<br>$\rightarrow$ `COTRN01C` (Select `'S'` View) | `TRANSACT` (`STARTBR`, `READNEXT`, `READPREV`, `ENDBR`) |
| **`COTRN01C.cbl`** (Transaction View) | `CT01` | `COTRN01` | `CVTRA05Y` | `COCOM01Y`, `COTRN01`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` ou `COTRN00C` (via `CDEMO-FROM-PROGRAM`) | `TRANSACT` (`READ`) |
| **`COTRN02C.cbl`** (Transaction Add) | `CT02` | `COTRN02` | `CVTRA05Y`, `CVACT01Y`, `CVACT03Y` | `COCOM01Y`, `COTRN02`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | `CALL 'CSUTLDTC'` (Validação de datas) | $\rightarrow$ `COMEN01C` | `CCXREF` (`READ` por `XREF-CARD-NUM` ou `CXACAIX`), `TRANSACT` (`STARTBR`, `READPREV` para último ID, `WRITE`) |
| **`CORPT00C.cbl`** (Transaction Reports) | `CR00` | `CORPT00` | `CVTRA05Y` | `COCOM01Y`, `CORPT00`, `CSDAT01Y`, `CSMSG01Y`, `CSSTRPFY`, `DFHBMSCA`, `DFHAID` | `CALL 'CSUTLDTC'` + `EXEC CICS WRITEQ TD QUEUE('INTRDR')` | $\rightarrow$ `COMEN01C`<br>**Disparo Assíncrono:** Submete `TRANREPT.jcl` via `INTRDR` | Fila CICS `INTRDR` (Internal Reader de JCL) |
| **`COBIL00C.cbl`** (Bill Payment Online) | `CB00` | `COBIL00` | `CVACT01Y`, `CVACT03Y`, `CVTRA05Y` | `COCOM01Y`, `COBIL00`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COMEN01C` | `ACCTDAT` (`READ`, `READ UPDATE`, `REWRITE` zerando `ACCT-CURR-BAL`), `CCXREF` (`READ` via `CXACAIX`), `TRANSACT` (`STARTBR`, `READPREV`, `WRITE` transação de pagamento `'02'`) |
| **`COUSR00C.cbl`** (User List Admin) | `CU00` | `COUSR00` | `CSUSR01Y` | `COCOM01Y`, `COUSR00`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COADM01C` (F3)<br>$\rightarrow$ `COUSR02C` (Select `'U'` Update)<br>$\rightarrow$ `COUSR03C` (Select `'D'` Delete) | `USRSEC` (`STARTBR`, `READNEXT`, `READPREV`, `ENDBR`) |
| **`COUSR01C.cbl`** (User Add Admin) | `CU01` | `COUSR01` | `CSUSR01Y` | `COCOM01Y`, `COUSR01`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COADM01C` | `USRSEC` (`WRITE`) |
| **`COUSR02C.cbl`** (User Update Admin) | `CU02` | `COUSR02` | `CSUSR01Y` | `COCOM01Y`, `COUSR02`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COADM01C` ou `COUSR00C` | `USRSEC` (`READ`, `READ UPDATE`, `REWRITE`) |
| **`COUSR03C.cbl`** (User Delete Admin) | `CU03` | `COUSR03` | `CSUSR01Y` | `COCOM01Y`, `COUSR03`, `CSDAT01Y`, `CSMSG01Y`, `DFHBMSCA`, `DFHAID` | — | $\rightarrow$ `COADM01C` ou `COUSR00C` | `USRSEC` (`READ`, `READ UPDATE`, `DELETE`) |

---

### 3.3. Matriz de Dependências Estruturais: Programas Batch COBOL (`app/cbl/CB*.cbl`), Sub-rotinas e Jobs JCL (`app/jcl/*.jcl`)

| Programa Batch (`.cbl`) | Job JCL Invocador (`.jcl`) | Copybooks Incluídos (`COPY`) | Sub-rotinas Chamadas (`CALL`) | Arquivos Lógicos (`SELECT ... ASSIGN TO`) $\rightarrow$ `DD Name` $\rightarrow$ Datasets Físicos (`INPUT` / `I-O` / `OUTPUT`) |
| :--- | :--- | :--- | :--- | :--- |
| **`CBACT01C.cbl`** (Read/Print Accounts) | `READACCT.jcl` | `CVACT01Y` | — | `ACCTFILE-FILE` (`ASSIGN TO ACCTFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS` |
| **`CBACT02C.cbl`** (Read/Print Cards) | `READCARD.jcl` | `CVACT02Y` | — | `CARDFILE-FILE` (`ASSIGN TO CARDFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS` |
| **`CBACT03C.cbl`** (Read/Print Cross-Ref) | `READXREF.jcl` | `CVACT03Y` | — | `XREFFILE-FILE` (`ASSIGN TO XREFFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS` |
| **`CBCUS01C.cbl`** (Read/Print Customers) | `READCUST.jcl` | `CVCUS01Y` | — | `CUSTFILE-FILE` (`ASSIGN TO CUSTFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS` |
| **`CBACT04C.cbl`** (Interest Calculator Engine) | `INTCALC.jcl` | `CVTRA01Y`, `CVACT03Y`, `CVTRA02Y`, `CVACT01Y`, `CVTRA05Y` | — | 1. `TCATBAL-FILE` (`TCATBALF`) $\rightarrow$ **INPUT (Seq):** `AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS`<br>2. `XREF-FILE` (`XREFFILE`) $\rightarrow$ **INPUT (Indexed/AIX):** `AWS.M2.CARDDEMO.CARDXREF.VSAM.AIX.PATH`<br>3. `DISCGRP-FILE` (`DISCGRP`) $\rightarrow$ **INPUT (Indexed):** `AWS.M2.CARDDEMO.DISCGRP.VSAM.KSDS`<br>4. `ACCOUNT-FILE` (`ACCTFILE`) $\rightarrow$ **I-O (READ/REWRITE):** `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS`<br>5. `TRANSACT-FILE` (`TRANSACT`) $\rightarrow$ **OUTPUT (Seq):** `AWS.M2.CARDDEMO.SYSTRAN.GnnnnV00` |
| **`CBTRN01C.cbl`** (Daily Transaction Verification) | `READTRAN.jcl` | `CVTRA06Y`, `CVACT03Y`, `CVACT01Y`, `CVCUS01Y`, `CVACT02Y` | — | 1. `DALYTRAN-FILE` (`DALYTRAN`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.DALYTRAN.PS`<br>2. `XREF-FILE` (`XREFFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS`<br>3. `ACCT-FILE` (`ACCTFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS`<br>4. `CUST-FILE` (`CUSTFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CUSTDATA.VSAM.KSDS`<br>5. `CARD-FILE` (`CARDFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDDATA.VSAM.KSDS` |
| **`CBTRN02C.cbl`** (Daily Transaction Posting Engine) | `POSTTRAN.jcl` | `CVTRA06Y`, `CVTRA05Y`, `CVACT03Y`, `CVACT01Y`, `CVTRA01Y` | `CALL 'CSUTLDTC'` (Valida data de expiração da conta vs. transação) | 1. `DALYTRAN-FILE` (`DALYTRAN`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.DALYTRAN.PS`<br>2. `XREF-FILE` (`XREFFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS`<br>3. `ACCOUNT-FILE` (`ACCTFILE`) $\rightarrow$ **I-O (READ/REWRITE saldos):** `AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS`<br>4. `TCATBAL-FILE` (`TCATBALF`) $\rightarrow$ **I-O (READ/WRITE/REWRITE saldos por categoria):** `AWS.M2.CARDDEMO.TCATBALF.VSAM.KSDS`<br>5. `TRANSACT-FILE` (`TRANFILE`) $\rightarrow$ **OUTPUT (WRITE):** `AWS.M2.CARDDEMO.TRANSACT.VSAM.KSDS`<br>6. `DALYREJS-FILE` (`DALYREJS`) $\rightarrow$ **OUTPUT (WRITE rejeições):** `AWS.M2.CARDDEMO.DALYREJS.GnnnnV00` |
| **`CBTRN03C.cbl`** (Transaction Detail Report) | `TRANREPT.jcl` (ou submetido por `CORPT00C` via `INTRDR`) | `CVTRA05Y`, `CVACT03Y`, `CVTRA03Y`, `CVTRA04Y`, `CVTRA07Y` | `CALL 'CSUTLDTC'` | 1. `TRANSACT-FILE` (`TRANFILE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.TRANSACT.BKUP.GnnnnV00` (filtrado por `SORT` no Step anterior)<br>2. `XREF-FILE` (`CARDXREF`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS`<br>3. `TRANTYPE-FILE` (`TRANTYPE`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.TRANTYPE.VSAM.KSDS`<br>4. `TRANCATG-FILE` (`TRANCATG`) $\rightarrow$ **INPUT:** `AWS.M2.CARDDEMO.TRANCATG.VSAM.KSDS`<br>5. `DATE-PARMS-FILE` (`DATEPARM`) $\rightarrow$ **INPUT:** Intervalo `YYYY-MM-DD`<br>6. `REPORT-FILE` (`TRANREPT`) $\rightarrow$ **OUTPUT:** `AWS.M2.CARDDEMO.TRANREPT.GnnnnV00` |
| **`CBSTM03A.cbl`** (Statement Generation Orchestrator) | `CREASTMT.jcl` | `CVTRA05Y`, `CVACT03Y`, `CVCUS01Y`, `CVACT01Y`, `COSTM01.CPY` | `CALL 'CBSTM03B' USING ...` | 1. **Via `CBSTM03B` (INPUT):** `TRNXFILE` (`TRANSACT` indexado por conta/cartão), `XREFFILE` (`CARDXREF`), `CUSTFILE` (`CUSTDATA`), `ACCTFILE` (`ACCTDATA`)<br>2. `STMT-FILE` (`STMTFILE`) $\rightarrow$ **OUTPUT:** `AWS.M2.CARDDEMO.STATEMNT.PS`<br>3. `HTML-FILE` (`HTMLFILE`) $\rightarrow$ **OUTPUT:** `AWS.M2.CARDDEMO.STATEMNT.HTML` |
| **`CBSTM03B.cbl`** (Statement File I/O Subprogram) | Invocado por `CBSTM03A` em `CREASTMT.jcl` | — (Recebe área de registro via `LINKAGE SECTION`) | — | Gerencia `OPEN`, `READ`, `START`, `CLOSE` de `TRNXFILE`, `XREFFILE`, `CUSTFILE` e `ACCTFILE` para `CBSTM03A`. |
| **`CSUTLDTC.cbl`** (Date Validation Utility) | Invocado via `CALL` por `COTRN02C`, `CORPT00C`, `CBTRN02C`, `CBTRN03C` | — | `CALL 'CEEDAYS'` (LE Callable Service) | Valida datas no formato `YYYY-MM-DD` usando a API Language Environment (`CEEDAYS`). |

---

## 4. Ranking de Acoplamento Estrutural (Hotspots do CardDemo)

A partir da contagem de referências estruturais de entrada (`Fan-In`), os artefatos de maior acoplamento no repositório CardDemo são:

1. **Copybook de Sessão `COCOM01Y.cpy` (`CARDDEMO-COMMAREA`) — `Fan-In = 17 programas (100% do subsistema Online)`**:
   - Transporta `CDEMO-FROM-TRANID`, `CDEMO-FROM-PROGRAM`, `CDEMO-USR-TYPE`, `CDEMO-ACCT-ID`, `CDEMO-CARD-NUM` e `CDEMO-CUST-ID` em todas as chamadas `EXEC CICS XCTL`.
2. **Dataset `ACCTDAT` (`AWS.M2.CARDDEMO.ACCTDATA.VSAM.KSDS`) + Copybook `CVACT01Y.cpy` — `Fan-In = 13 programas (7 Online + 6 Batch)`**:
   - Lido por `COACTVWC`, `COCRDLIC`, `COCRDSLC`, `COCRDUPC`, `COTRN02C`, `CBACT01C`, `CBTRN01C`, `CBSTM03A/B` e **modificado (`REWRITE`) concorrentemente** por 2 programas Online (`COACTUPC`, `COBIL00C`) e 2 motores Batch (`CBTRN02C`, `CBACT04C`).
3. **Dataset `CCXREF` (`AWS.M2.CARDDEMO.CARDXREF.VSAM.KSDS` + AIX `CXACAIX`) + Copybook `CVACT03Y.cpy` — `Fan-In = 11 programas (5 Online + 6 Batch)`**:
   - É a tabela pivô central (`Customer <-> Account <-> Card`) sem a qual nenhum fluxo de conta, transação, fatura ou cálculo de juros consegue navegar entre `CUST-ID`, `ACCT-ID` e `CARD-NUM`.
4. **Dataset `TRANSACT` (`AWS.M2.CARDDEMO.TRANSACT.VSAM.KSDS`) + Copybook `CVTRA05Y.cpy` — `Fan-In = 10 programas (5 Online + 5 Batch)`**:
   - Ponto de convergência financeira entre lançamentos online (`COTRN02C`, `COBIL00C`), batch posting diário (`CBTRN02C`), juros (`CBACT04C`), relatórios (`CBTRN03C`) e faturas (`CBSTM03A/B`).
5. **Sub-rotina Utilitária `CSUTLDTC.cbl` — `Fan-In = 4 programas (2 Online + 2 Batch)`**:
   - Compartilhada transversalmente entre a camada CICS (`COTRN02C`, `CORPT00C`) e a camada Batch (`CBTRN02C`, `CBTRN03C`).
