import os, glob, yaml, json, csv, re
from collections import defaultdict

output_dir = '/home/walter/repos/code_mapping_ai/test_specs/TESTE_112326_graphRAG'
os.makedirs(output_dir, exist_ok=True)

# 1. Parse screens
screens_dir = '/home/walter/repos/metadados_famema/clusters/centro-cirurgico/screens'
screen_files = sorted(glob.glob(f'{screens_dir}/*.md'))

screens = []
screen_by_code = {}
tables_map = defaultdict(lambda: {'touched_by_screens': [], 'roles': set()})
roles_map = defaultdict(lambda: {'screens': set()})
sectors_map = defaultdict(lambda: {'screens': set(), 'units': set()})
nav_edges_raw = []

for sf in screen_files:
    code = os.path.splitext(os.path.basename(sf))[0]
    with open(sf, 'r', encoding='utf-8') as f:
        parts = f.read().split('---')
    if len(parts) >= 3:
        fm = yaml.safe_load(parts[1])
        body = parts[2].strip()
        fm['screenCode'] = fm.get('screenCode', code)
        fm['body'] = body
        screens.append(fm)
        screen_by_code[fm['screenCode']] = fm
        
        # Tables
        pers = fm.get('persistence', {})
        mt = pers.get('masterTable')
        if mt:
            tables_map[mt]['touched_by_screens'].append(fm['screenCode'])
        for rt in pers.get('relatedTables', []):
            tables_map[rt]['touched_by_screens'].append(fm['screenCode'])
            
        # Roles
        for r in fm.get('accessControl', {}).get('authorizedRoles', []):
            roles_map[r]['screens'].add(fm['screenCode'])
            if mt: tables_map[mt]['roles'].add(r)
            
        # Sectors
        for pl in fm.get('physicalLocations', []):
            unit = pl.get('unit', 'UNKNOWN')
            for sec in pl.get('sectors', []):
                sectors_map[sec]['screens'].add(fm['screenCode'])
                sectors_map[sec]['units'].add(unit)
                
        # Navigation
        for tgt in fm.get('navigation', {}).get('canNavigateTo', []):
            nav_edges_raw.append((fm['screenCode'], tgt))

# 2. Parse C# projects modules
projs = [
    'centro-cirurgico', 'centro-cirurgico-forms',
    'demanda-cirurgia', 'demanda-cirurgia-forms',
    'demanda-cirurgica-gerencial', 'demanda-cirurgica-gerencial-forms',
    'demanda-cirurgica-monitoracao', 'demanda-cirurgica-monitoracao-forms',
    'KitCirurgico', 'kit-cirurgico-forms', 'kit-cirurgico-dll'
]

base_projs = '/home/walter/repos/metadados_famema/projects'
csharp_modules = []
csharp_by_urn = {}

for p in projs:
    meta_path = os.path.join(base_projs, p, 'metadata.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8-sig') as f:
            md = json.load(f)
            for m in md.get('modules', []):
                m['projectSlug'] = p
                csharp_modules.append(m)
                csharp_by_urn[m['moduleUrn']] = m

# 3. Classify into Communities
def assign_communities(code):
    c = code.upper()
    if c.startswith('DECI0001MN') or c.startswith('DECI0001') or c.startswith('DECI0002') or c.startswith('DECI0003') or c.startswith('DECI0005') or c.startswith('DECI0006') or c.startswith('DECI0007') or c.startswith('DECI0008') or c.startswith('DECI0011') or c.startswith('DECI0012') or c.startswith('DECG'):
        return 'C1_DEMANDA_REGULACAO', 'C1.1_FILA_CROSS_ESTRATIFICACAO'
    elif c.startswith('DECI0010') or c.startswith('CCIO0001') or c.startswith('CCIO0003') or c.startswith('CCIO0005') or c.startswith('CCIO0010') or c.startswith('CCIO9000') or c.startswith('DCMO'):
        return 'C2_AGENDAMENTO_MAPA', 'C2.1_MAPA_ESCALA_SALAS'
    elif c.startswith('KCC') or 'ORTESE' in c or 'MATERIAL' in c or 'INSUMO' in c or 'OPME' in c or c.startswith('MATERIAIS'):
        return 'C3_CME_KITS_OPME', 'C3.1_CME_ESTERILIZACAO_DISPENSACAO'
    elif 'RECEP' in c or 'CHECKLIST' in c or 'TERMO' in c or 'AGRADECIMENTO' in c or 'CONFIRMACAO' in c:
        return 'C4_ACOLHIMENTO_PREPARO', 'C4.1_RECEPCAO_CHECA_PRE_OP'
    elif c.startswith('CCIO0002') or c.startswith('CCIO0004') or c.startswith('UC') or 'CIRURGIA' in c and not c.startswith('SMOV') and not c.startswith('DECI'):
        return 'C5_BLOCO_CIRURGIA_SEGURA', 'C5.1_ATO_CIRURGICO_TIME_OUT'
    elif 'SRPA' in c or 'RECUPERA' in c or 'ANEST' in c or c.startswith('SMOV5020'):
        return 'C6_SRPA_RECUPERACAO', 'C6.1_DESPERTAR_ALDRETE'
    elif c.startswith('CCIO1000') or c.startswith('SMOV5053') or c.startswith('RPT') or c.startswith('REP') or 'FICHA' in c:
        return 'C7_FATURAMENTO_APAC_PEP', 'C7.1_LAUDO_APAC_FATURAMENTO'
    else:
        return 'C2_AGENDAMENTO_MAPA', 'C2.2_CONTROLE_GERAL'

# Build Nodes
nodes = []
edges = []

# Clinical Stages (Level 1 Backbone)
stages = [
    {
        'id': 'urn:stage:1:indicacao-regulacao-cross',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 1: Indicação Cirúrgica, Lista de Espera e Regulação CROSS',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C1_DEMANDA_REGULACAO',
        'community_l2': 'C1.1_FILA_CROSS_ESTRATIFICACAO',
        'properties': {
            'order': 1,
            'actor': 'Secretária de Especialidades / Médico Especialista',
            'objective': 'Cadastrar demanda cirúrgica, estratificar prioridade clínica e vincular ao CROSS.',
            'mainScreens': ['DECI0001MN', 'DECG0001', 'DECG0002']
        }
    },
    {
        'id': 'urn:stage:2:agendamento-escala-mapa',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 2: Agendamento da Data Cirúrgica e Montagem do Mapa Operatório',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C2_AGENDAMENTO_MAPA',
        'community_l2': 'C2.1_MAPA_ESCALA_SALAS',
        'properties': {
            'order': 2,
            'actor': 'Enfermeiro Regulador / Gestor do Centro Cirúrgico',
            'objective': 'Alocar data, turno, sala cirúrgica (HCI/HCII/HCIII), anestesista e equipe.',
            'mainScreens': ['DECI0010', 'CCIO0001', 'CCIO0001MapaCirurgia']
        }
    },
    {
        'id': 'urn:stage:3:suprimentos-cme-opme',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 3: Preparação CME, Caixas de Instrumental e Kits de OPME',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C3_CME_KITS_OPME',
        'community_l2': 'C3.1_CME_ESTERILIZACAO_DISPENSACAO',
        'properties': {
            'order': 3,
            'actor': 'Auxiliar Enfermagem CME / Instrumentador / Farmácia',
            'objective': 'Separar caixas cirúrgicas estéreis, insumos, próteses e órteses autorizadas.',
            'mainScreens': ['KCCI0001', 'KCCKitProdutoForms', 'DECI0001OrteseProtese']
        }
    },
    {
        'id': 'urn:stage:4:recepcao-preparo-paciente',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 4: Recepção, Acolhimento e Cuidados Pré-Operatórios Imediatos',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C4_ACOLHIMENTO_PREPARO',
        'community_l2': 'C4.1_RECEPCAO_CHECA_PRE_OP',
        'properties': {
            'order': 4,
            'actor': 'Recepcionista / Téc. Enfermagem / Paciente / Acompanhante',
            'objective': 'Conferir jejum rigoroso, colocar pulseira, verificar TCLE, puncionar acesso e demarcar lateralidade.',
            'mainScreens': ['CCIO0001Confirmacao', 'TermoConsentimentoAvaliacaoPreAnestesica']
        }
    },
    {
        'id': 'urn:stage:5:bloco-cirurgia-segura-ato',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 5: Bloco Operatório, Protocolo de Cirurgia Segura OMS e Ato Cirúrgico',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C5_BLOCO_CIRURGIA_SEGURA',
        'community_l2': 'C5.1_ATO_CIRURGICO_TIME_OUT',
        'properties': {
            'order': 5,
            'actor': 'Cirurgião / Anestesiologista / Instrumentador / Circulante',
            'objective': 'Executar Sign-In, Time-Out verbal obrigatório, procedimento cirúrgico, contagem de compressas e Sign-Out.',
            'mainScreens': ['CCIO0002', 'CCIO0004', 'UCCirurgia', 'CCIO0004DataChegada']
        }
    },
    {
        'id': 'urn:stage:6:srpa-recuperacao-pos-anestesica',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 6: Sala de Recuperação Pós-Anestésica (SRPA) e Avaliação de Alta',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C6_SRPA_RECUPERACAO',
        'community_l2': 'C6.1_DESPERTAR_ALDRETE',
        'properties': {
            'order': 6,
            'actor': 'Enfermeiro Anestesia / Anestesiologista / Téc. Enfermagem',
            'objective': 'Monitorar despertar anestésico, controlar dor/náusea e aplicar escore de Aldrete e Kroulik >= 9.',
            'mainScreens': ['CCIO0002', 'SMOV5020', 'SMOV5020Anestesico']
        }
    },
    {
        'id': 'urn:stage:7:alta-laudo-faturamento-apac',
        'type': 'CLINICAL_STAGE',
        'label': 'Etapa 7: Alta / Destino, Laudo Operatório, PEP e Faturamento APAC / SUS',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C7_FATURAMENTO_APAC_PEP',
        'community_l2': 'C7.1_LAUDO_APAC_FATURAMENTO',
        'properties': {
            'order': 7,
            'actor': 'Cirurgião / Faturamento SUS / SPP / NIR',
            'objective': 'Concluir laudo cirúrgico no PEP, emitir guias APAC/AIH e encaminhar paciente para enfermaria ou domicílio.',
            'mainScreens': ['CCIO1000', 'SMOV5053CirurgiaAPAC', 'rptCirurgiaRegistro']
        }
    }
]

for st in stages:
    nodes.append(st)

# Stage Precedence Edges
for i in range(len(stages) - 1):
    edges.append({
        'id': f'edge_stage_{i+1}_{i+2}',
        'source': stages[i]['id'],
        'target': stages[i+1]['id'],
        'type': 'PRECEDES',
        'weight': 5.0,
        'properties': {
            'description': f'Transição clínica mandatória da {stages[i]["label"]} para {stages[i+1]["label"]}'
        }
    })

# Add Screens as Nodes
for s in screens:
    c1, c2 = assign_communities(s['screenCode'])
    node = {
        'id': s.get('screenUrn', f'urn:screen:centro-cirurgico:{s["screenCode"]}'),
        'type': 'SCREEN_FORM',
        'label': f'{s["screenCode"]} — {s.get("title", s["screenCode"])}',
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': c1,
        'community_l2': c2,
        'properties': {
            'screenCode': s['screenCode'],
            'title': s.get('title'),
            'tier': s.get('tier'),
            'projectSlug': s.get('project', {}).get('slug'),
            'assembly': s.get('project', {}).get('assembly'),
            'layer': s.get('project', {}).get('layer'),
            'masterTable': s.get('persistence', {}).get('masterTable'),
            'relatedTables': s.get('persistence', {}).get('relatedTables', []),
            'flowStitchKeys': s.get('persistence', {}).get('flowStitchKeys', []),
            'authorizedRoles': s.get('accessControl', {}).get('authorizedRoles', []),
            'invokedBy': s.get('navigation', {}).get('invokedBy', []),
            'canNavigateTo': s.get('navigation', {}).get('canNavigateTo', [])
        }
    }
    nodes.append(node)

# Add Database Tables as Nodes
for tbl, info in tables_map.items():
    schema, table = tbl.split('.') if '.' in tbl else ('SIHOSP', tbl)
    node = {
        'id': f'urn:table:{schema.lower()}:{table.lower()}',
        'type': 'DATABASE_TABLE',
        'label': tbl,
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C0_DATA_PERSISTENCE',
        'community_l2': f'C0.DB_{schema.upper()}',
        'properties': {
            'schema': schema,
            'table': table,
            'touched_by_screens_count': len(info['touched_by_screens']),
            'screens': info['touched_by_screens'],
            'roles': list(info['roles'])
        }
    }
    nodes.append(node)

# Add Physical Sectors as Nodes
for sec, sinfo in sectors_map.items():
    node = {
        'id': f'urn:sector:famema:{re.sub(r"[^a-zA-Z0-9]+", "_", sec).lower()}',
        'type': 'PHYSICAL_SECTOR',
        'label': sec,
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C0_INFRASTRUCTURE',
        'community_l2': 'C0.PHYSICAL_SECTORS',
        'properties': {
            'units': list(sinfo['units']),
            'screen_count': len(sinfo['screens']),
            'screens': list(sinfo['screens'])
        }
    }
    nodes.append(node)

# Add Roles as Nodes
for r, rinfo in roles_map.items():
    node = {
        'id': f'urn:role:famema:{re.sub(r"[^a-zA-Z0-9]+", "_", r).lower()}',
        'type': 'ROLE_ACTOR',
        'label': r,
        'community_l0': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'community_l1': 'C0_GOVERNANCE_RBAC',
        'community_l2': 'C0.CLINICAL_ROLES',
        'properties': {
            'screens_authorized_count': len(rinfo['screens']),
            'screens': list(rinfo['screens'])
        }
    }
    nodes.append(node)

# Add Navigation Edges
edge_counter = 1
for src, tgt in nav_edges_raw:
    src_urn = f'urn:screen:centro-cirurgico:{src}'
    tgt_urn = f'urn:screen:centro-cirurgico:{tgt}'
    edges.append({
        'id': f'edge_nav_{edge_counter}',
        'source': src_urn,
        'target': tgt_urn,
        'type': 'NAVIGATES_TO',
        'weight': 2.0,
        'properties': {
            'description': f'{src} abre a tela {tgt}'
        }
    })
    edge_counter += 1

# Add Persistence Edges (Screen -> Table)
for s in screens:
    s_urn = s.get('screenUrn', f'urn:screen:centro-cirurgico:{s["screenCode"]}')
    pers = s.get('persistence', {})
    mt = pers.get('masterTable')
    if mt:
        schema, table = mt.split('.') if '.' in mt else ('SIHOSP', mt)
        tbl_urn = f'urn:table:{schema.lower()}:{table.lower()}'
        edges.append({
            'id': f'edge_db_{edge_counter}',
            'source': s_urn,
            'target': tbl_urn,
            'type': 'PERSISTS_MASTER_TABLE',
            'weight': 3.0,
            'properties': {'stitchKeys': pers.get('flowStitchKeys', [])}
        })
        edge_counter += 1
    for rt in pers.get('relatedTables', []):
        schema, table = rt.split('.') if '.' in rt else ('SIHOSP', rt)
        tbl_urn = f'urn:table:{schema.lower()}:{table.lower()}'
        edges.append({
            'id': f'edge_db_{edge_counter}',
            'source': s_urn,
            'target': tbl_urn,
            'type': 'QUERIES_RELATED_TABLE',
            'weight': 1.0,
            'properties': {}
        })
        edge_counter += 1

# Connect Clinical Stages to Core Screens
stage_screen_map = {
    'urn:stage:1:indicacao-regulacao-cross': ['DECI0001mn', 'DECI0001', 'DECG0001', 'DECG0002', 'DECG0003', 'DECI0002'],
    'urn:stage:2:agendamento-escala-mapa': ['DECI0010', 'CCIO0001', 'CCIO0001Agendamento', 'CCIO0001MapaCirurgia', 'CCIO9000', 'DCMO0001'],
    'urn:stage:3:suprimentos-cme-opme': ['KCCI0001', 'KCCKitProdutoForms', 'KCCInstrumentalForms', 'DECI0001Ortese', 'DECI0001OrteseProtese', 'ReportFichaOPME'],
    'urn:stage:4:recepcao-preparo-paciente': ['CCIO0001Confirmacao', 'CCIO0001IdentificarEquipe', 'TermoConsentimentoAvaliacaoPreAnestesica', 'DCMO0002'],
    'urn:stage:5:bloco-cirurgia-segura-ato': ['CCIO0002', 'CCIO0004', 'CCIO0002Procedimento', 'CCIO0002Participante', 'CCIO0002Ortese', 'UCCirurgia'],
    'urn:stage:6:srpa-recuperacao-pos-anestesica': ['CCIO0002Suspensao', 'SMOV5020', 'SMOV5020Anestesico', 'SMOV5020Cirurgia', 'DCMO0003'],
    'urn:stage:7:alta-laudo-faturamento-apac': ['CCIO1000', 'SMOV5053CirurgiaAPAC', 'rptCirurgiaRegistro', 'rep9000', 'Agradecimento']
}

for stage_urn, sc_list in stage_screen_map.items():
    for sc in sc_list:
        sc_urn = f'urn:screen:centro-cirurgico:{sc}'
        edges.append({
            'id': f'edge_stage_screen_{edge_counter}',
            'source': stage_urn,
            'target': sc_urn,
            'type': 'ORCHESTRATES_SCREEN',
            'weight': 4.0,
            'properties': {'description': f'Etapa clínica orquestra tela de formulário {sc}'}
        })
        edge_counter += 1

print(f'Constructed GraphRAG Graph: {len(nodes)} nodes, {len(edges)} edges.')

# 4. Communities Data (Leiden Hierarchical Structure)
communities = [
    {
        'id': 'C0_CENTRO_CIRURGICO_GLOBAL',
        'level': 0,
        'title': 'Comunidade Global 0: Bloco Cirúrgico Integrado e Ciclo Perioperatório FAMEMA',
        'color': '#E11D48',
        'executive_summary': 'Macro-ecossistema hospitalar responsável pelo ciclo cirúrgico ponta a ponta: regulação de fila (CROSS), agendamento e mapa de salas cirúrgicas (HCI, HCII, HCIII), esterilização e suprimento CME/OPME, acolhimento pré-operatório do cidadão, bloco operatório com protocolo de cirurgia segura OMS, sala de recuperação pós-anestésica (SRPA) e liquidação de faturamento SUS/APAC.',
        'metrics': {
            'total_screens': len(screens),
            'total_csharp_modules': len(csharp_modules),
            'total_database_tables': len(tables_map),
            'total_physical_sectors': len(sectors_map),
            'total_roles': len(roles_map)
        },
        'key_entities': [
            'urn:stage:1:indicacao-regulacao-cross',
            'urn:stage:2:agendamento-escala-mapa',
            'urn:stage:3:suprimentos-cme-opme',
            'urn:stage:4:recepcao-preparo-paciente',
            'urn:stage:5:bloco-cirurgia-segura-ato',
            'urn:stage:6:srpa-recuperacao-pos-anestesica',
            'urn:stage:7:alta-laudo-faturamento-apac'
        ]
    },
    {
        'id': 'C1_DEMANDA_REGULACAO',
        'level': 1,
        'title': 'Comunidade 1: Demanda Cirúrgica, Lista de Espera e Regulação CROSS (DECI & DECG)',
        'color': '#EA580C',
        'executive_summary': 'Orquestra a entrada dos pacientes ambulatoriais e de urgência na fila cirúrgica regulada. Realiza estratificação clínica de risco e prioridade cirúrgica, pontuação por procedimento e idade, interface com a regulação CROSS do Estado de São Paulo e gestão de cancelamentos/suspensões de fila.',
        'key_entities': [
            'urn:screen:centro-cirurgico:DECI0001mn',
            'urn:screen:centro-cirurgico:DECI0001',
            'urn:screen:centro-cirurgico:DECG0001',
            'urn:screen:centro-cirurgico:DECG0002',
            'urn:screen:centro-cirurgico:DECG0003',
            'urn:table:sihosp:demanda_cirurgica',
            'urn:table:sihosp:demanda_cirurgica_procedimento'
        ],
        'findings': [
            'Controle estrito de fila regulada por gravidade e tempo de espera.',
            'Integração com regulação estadual CROSS para validação de cotas cirúrgicas.',
            'Módulos C# de apoio: DemandaCirurgia.dll e DemandaCirurgiaForms.dll.'
        ],
        'risks': 'Risco de duplicidade de indicação caso prontuário unificado não seja validado na entrada.'
    },
    {
        'id': 'C2_AGENDAMENTO_MAPA',
        'level': 1,
        'title': 'Comunidade 2: Planejamento, Agendamento e Mapa Cirúrgico Diário (CCIO0001 & DECI0010)',
        'color': '#3B82F6',
        'executive_summary': 'Transforma demandas da lista de espera em cirurgias agendadas com data, horário, sala e equipe médica. Distribui procedimentos entre as salas de grande porte do HCI, materno-infantis do HCII e oftalmológicas do HCIII. Emite o Mapa Cirúrgico Diário consolidado.',
        'key_entities': [
            'urn:screen:centro-cirurgico:DECI0010',
            'urn:screen:centro-cirurgico:CCIO0001',
            'urn:screen:centro-cirurgico:CCIO0001Agendamento',
            'urn:screen:centro-cirurgico:CCIO0001MapaCirurgia',
            'urn:table:sihosp:mapa_cirurgico',
            'urn:table:sihosp:sala_cirurgica'
        ],
        'findings': [
            'Parametrização dinâmica por sala operatória via regra SALA_CIRURGICA.',
            'Matriz de conflito de salas entre cirurgias eletivas e urgências do PS.',
            'Bloqueio automático de agendamento para pacientes com óbito ou cadastro inativo.'
        ],
        'risks': 'Superalocação de salas operatórias em horários de pico ou atrasos no término de procedimentos anteriores.'
    },
    {
        'id': 'C3_CME_KITS_OPME',
        'level': 1,
        'title': 'Comunidade 3: Central de Materiais Esterilizados (CME), Kits e OPME (KCC & DECI0001Ortese)',
        'color': '#10B981',
        'executive_summary': 'Responsável pelo rastreamento físico e sistêmico dos instrumentais cirúrgicos, autoclave e esterilização na CME, montagem de kits assistenciais padronizados por especialidade e conferência rigorosa de órteses, próteses e materiais especiais (OPME) com autorização prévia.',
        'key_entities': [
            'urn:screen:centro-cirurgico:KCCI0001',
            'urn:screen:centro-cirurgico:KCCKitProdutoForms',
            'urn:screen:centro-cirurgico:KCCInstrumentalForms',
            'urn:screen:centro-cirurgico:DECI0001OrteseProtese',
            'urn:table:sihosp:kcc_kit_assistencial',
            'urn:table:sihosp:ficha_opme'
        ],
        'findings': [
            'Separação entre DLL de regras de negócio (KitCirurgicoDLL) e interface (KitCirurgicoForms).',
            'Validação cruzada de OPME com autorização da Secretaria de Saúde.',
            'Controle de lote, validade de esterilização e movimentação de caixas.'
        ],
        'risks': 'Falta de material consignado ou falha no ciclo de autoclave impedindo a abertura da sala cirúrgica.'
    },
    {
        'id': 'C4_ACOLHIMENTO_PREPARO',
        'level': 1,
        'title': 'Comunidade 4: Recepção, Acolhimento e Cuidados Pré-Operatórios (Guia do Cidadão)',
        'color': '#8B5CF6',
        'executive_summary': 'Conexão direta entre o cidadão/paciente e o bloco cirúrgico. Compreende a conferência de jejum de 8h, acolhimento na recepção do 2º andar do Prédio São Francisco (HCI) ou HCII/HCIII, colocação de pulseira com conferência verbal dupla, verificação de TCLE e exames pré-operatórios, demarcação de lateralidade na pele pelo cirurgião e guarda de pertences com o acompanhante.',
        'key_entities': [
            'urn:screen:centro-cirurgico:CCIO0001Confirmacao',
            'urn:screen:centro-cirurgico:TermoConsentimentoAvaliacaoPreAnestesica',
            'urn:sector:famema:recep_centro_cir_rgico_hci',
            'urn:role:famema:recepcionista',
            'urn:role:famema:enfermeiro'
        ],
        'findings': [
            'Alinhamento integral com as orientações do Guia do Cidadão da FAMEMA.',
            'Barreira de segurança contra lateralidade trocada: demarcação física com caneta cirúrgica.',
            'Instalação de acesso venoso calibroso e monitoramento pré-indução.'
        ],
        'risks': 'Quebra inadvertida de jejum pelo paciente ou extravio de termo de consentimento prévio.'
    },
    {
        'id': 'C5_BLOCO_CIRURGIA_SEGURA',
        'level': 1,
        'title': 'Comunidade 5: Bloco Operatório, Cirurgia Segura OMS e Ato Cirúrgico (CCIO0002 & CCIO0004)',
        'color': '#D97706',
        'executive_summary': 'Coração assistencial invasivo do Centro Cirúrgico. Envolve a entrada na sala de operação, monitorização contínua pelo anestesiologista, cumprimento do Protocolo Internacional de Cirurgia Segura da OMS (Sign-In antes da indução, Time-Out verbal obrigatório em silêncio antes da incisão, e Sign-Out antes da saída de sala com contagem de compressas e instrumentais). Registra a equipe completa (cirurgiões, residentes, anestesistas, circulantes e instrumentadores).',
        'key_entities': [
            'urn:screen:centro-cirurgico:CCIO0002',
            'urn:screen:centro-cirurgico:CCIO0004',
            'urn:screen:centro-cirurgico:CCIO0002Procedimento',
            'urn:screen:centro-cirurgico:CCIO0002Participante',
            'urn:table:sihosp:cirurgia',
            'urn:table:sihosp:checklist_cirurgico'
        ],
        'findings': [
            'Time-Out compulsório antes da primeira incisão conforme regra RN-CC-002.',
            'Registro temporal preciso: entrada em sala, início/fim da anestesia, início/fim da incisão, saída de sala.',
            'Associação atômica de múltiplos procedimentos e uso de antimicrobianos profiláticos.'
        ],
        'risks': 'Omissão de checagem verbal do Time-Out ou discrepância na contagem de compressas.'
    },
    {
        'id': 'C6_SRPA_RECUPERACAO',
        'level': 1,
        'title': 'Comunidade 6: Sala de Recuperação Pós-Anestésica (SRPA) e Vitalidade (SMOV5020 & CCIO)',
        'color': '#06B6D4',
        'executive_summary': 'Acolhe o paciente imediatamente após o término do ato cirúrgico para despertar monitorado. A equipe multiprofissional vigia sinais vitais, ritmo cardíaco, oxigenação e administra analgesia e antieméticos. A alta da SRPA é rigidamente condicionada ao escore de Aldrete e Kroulik >= 9.',
        'key_entities': [
            'urn:screen:centro-cirurgico:SMOV5020',
            'urn:screen:centro-cirurgico:SMOV5020Anestesico',
            'urn:screen:centro-cirurgico:SMOV5020Cirurgia',
            'urn:sector:famema:sala_de_recupera__o_cc_hci',
            'urn:table:sihosp:pep_cirurgia'
        ],
        'findings': [
            'Aplicação contínua do escore de Aldrete e Kroulik (consciência, respiração, circulação, saturação, atividade motora).',
            'Triagem de destino: alta direta para domicílio (Hospital-Dia) vs. transporte para enfermaria / UTI.',
            'Comunicação imediata com o familiar/acompanhante na sala de espera externa.'
        ],
        'risks': 'Depressão respiratória pós-anestésica ou alta precoce da SRPA sem estabilidade hemodinâmica.'
    },
    {
        'id': 'C7_FATURAMENTO_APAC_PEP',
        'level': 1,
        'title': 'Comunidade 7: Documentação Cirúrgica, PEP, APAC e Faturamento SUS (CCIO1000 & SMOV5053)',
        'color': '#4F46E5',
        'executive_summary': 'Fecha o ciclo cirúrgico no âmbito assistencial e administrativo. O cirurgião elabora o laudo operatório detalhado no Prontuário Eletrônico do Paciente (PEP), vinculando códigos de procedimentos SUS (SIGTAP), consumo de OPME e justificativas clínicas. Emite laudos de APAC e AIH para cobrança e faturamento governamental.',
        'key_entities': [
            'urn:screen:centro-cirurgico:CCIO1000',
            'urn:screen:centro-cirurgico:SMOV5053CirurgiaAPAC',
            'urn:screen:centro-cirurgico:rptCirurgiaRegistro',
            'urn:table:sihosp:cirurgia_procedi_realizado',
            'urn:table:sihosp:ficha_opme_material'
        ],
        'findings': [
            'Fechamento de conta com validação cruzada entre insumos consumidos na sala e faturamento.',
            'Auditoria de glosas e conformidade com laudos anestésicos.',
            'Alimentação do Data Warehouse hospitalar para relatórios gerenciais e taxa de suspensão cirúrgica.'
        ],
        'risks': 'Glosa SUS por inconsistência entre o procedimento autorizado na APAC e o laudo operatório final.'
    }
]

# 5. Covariates and Business Rules
covariates = [
    {
        'ruleId': 'RN-CC-001',
        'title': 'Validação de Pedido Cirúrgico, Sangue (Hemocentro) e OPME',
        'category': 'PRE_CONDITION_SURGICAL',
        'enforcedBy': ['CCIO0001Agendamento', 'DECI0010'],
        'expression': 'EXISTS(RESERVA_HEMOTERAPICA) && (HAS_OPME == FALSE || OPME_STATUS == "AUTORIZADO")',
        'description': 'Todo agendamento cirúrgico de médio e grande porte exige prévia reserva transfusional junto ao Hemocentro e autorização formal da secretaria para uso de OPME.'
    },
    {
        'ruleId': 'RN-CC-002',
        'title': 'Protocolo de Cirurgia Segura OMS (Sign-In, Time-Out e Sign-Out)',
        'category': 'CLINICAL_SAFETY_MANDATORY',
        'enforcedBy': ['CCIO0004', 'CCIO0002'],
        'expression': 'SIGN_IN_COMPLETED == TRUE && TIME_OUT_CONFIRMED == TRUE && SIGN_OUT_COUNT_VERIFIED == TRUE',
        'description': 'Obrigatória a execução verbal e o preenchimento digital do checklist cirúrgico em 3 momentos: antes da indução anestésica, antes da incisão da pele (pausa de segurança em silêncio) e antes da saída do paciente da sala.'
    },
    {
        'ruleId': 'RN-CC-003',
        'title': 'Critérios de Alta da SRPA por Índice de Aldrete e Kroulik >= 9',
        'category': 'POST_ANESTHESIA_DISCHARGE',
        'enforcedBy': ['SMOV5020', 'CCIO0002'],
        'expression': 'ALDRETE_KROULIK_SCORE >= 9 && SINAIS_VITAIS_ESTAVEIS == TRUE',
        'description': 'A liberação do paciente da Sala de Recuperação Pós-Anestésica para a enfermaria ou domicílio requer pontuação mínima de 9 no índice de Aldrete e Kroulik.'
    },
    {
        'ruleId': 'RN-CC-004',
        'title': 'Bloqueio Assistencial por Registro de Óbito',
        'category': 'SYSTEM_HARD_BLOCK',
        'enforcedBy': ['CCIO0001', 'CCIO0002', 'DECI0001', 'DECI0010'],
        'expression': 'SIHOSP.PACIENTE.DAT_OBITO IS NOT NULL',
        'description': 'Impede qualquer agendamento, alocação de sala ou registro cirúrgico caso o paciente possua data de óbito registrada na base central SIHOSP.'
    },
    {
        'ruleId': 'RN-CC-005',
        'title': 'Bloqueio Assistencial por Inativação de Cliente/Conveniado',
        'category': 'SYSTEM_HARD_BLOCK',
        'enforcedBy': ['CCIO0001', 'CCIO0002', 'DECI0001'],
        'expression': 'SIHOSP.CA_CLIENTE.STATUS == "INATIVO"',
        'description': 'Impede a inclusão em fila ou agendamento de pacientes com cadastro administrativo marcado como INATIVO no subsistema CA.'
    },
    {
        'ruleId': 'RN-CC-006',
        'title': 'Parametrização Dinâmica de Equipe Cirúrgica (CC_EQUIPE)',
        'category': 'DATA_FILTER_RULE',
        'enforcedBy': ['CCIO0001', 'CCIO0002CentroCusto'],
        'expression': 'LOOKUP(PARAMETRO, "CC_EQUIPE")',
        'description': 'Filtra e restringe a exibição de profissionais e especialidades de acordo com as permissões do Centro de Custo cirúrgico.'
    },
    {
        'ruleId': 'RN-CC-007',
        'title': 'Parametrização e Restrição de Sala Operatória (SALA_CIRURGICA)',
        'category': 'DATA_FILTER_RULE',
        'enforcedBy': ['CCIO0001', 'CCIO0002'],
        'expression': 'LOOKUP(PARAMETRO, "SALA_CIRURGICA")',
        'description': 'Valida se a sala de cirurgia selecionada é compatível com o porte anestésico e a especialidade do procedimento.'
    },
    {
        'ruleId': 'RN-CC-008',
        'title': 'Jejum Pré-Operatório Rigoroso',
        'category': 'CITIZEN_CLINICAL_PROTOCOL',
        'enforcedBy': ['CCIO0001Confirmacao', 'Guia_do_Cidadao'],
        'expression': 'TEMPO_JEJUM_SOLIDOS >= 8 && TEMPO_JEJUM_LIQUIDOS_CLAROS >= 2',
        'description': 'Conferência obrigatória na recepção e pela enfermagem do tempo de jejum para prevenção de broncoaspiração anestésica.'
    },
    {
        'ruleId': 'RN-CC-009',
        'title': 'Demarcação Obrigatória de Lateralidade',
        'category': 'PATIENT_SAFETY_PROTOCOL',
        'enforcedBy': ['CCIO0004', 'Guia_do_Cidadao'],
        'expression': 'DEMARCACAO_LATERALIDADE_CONCLUIDA == TRUE',
        'description': 'O cirurgião responsável deve demarcar pessoalmente o local exato da incisão na pele do paciente consciente antes da entrada na sala de operação.'
    },
    {
        'ruleId': 'RN-CC-010',
        'title': 'Contagem Rigorosa de Instrumentais e Compressas',
        'category': 'INTRA_OPERATIVE_SAFETY',
        'enforcedBy': ['CCIO0004', 'KCCI0001'],
        'expression': 'CONTAGEM_INICIAL == CONTAGEM_FINAL',
        'description': 'Antes do fechamento da cavidade operatória, o circulante e o instrumentador realizam contagem física rigorosa de compressas e gazes.'
    }
]

# 6. Inverted Search Index
search_index = defaultdict(list)
for n in nodes:
    tokens = set(re.findall(r'[a-zA-Z0-9_]{3,}', n['id'].lower() + ' ' + n['label'].lower()))
    for t in tokens:
        search_index[t].append({'id': n['id'], 'type': n['type'], 'label': n['label'], 'comm': n.get('community_l1')})

# Save JSON Datasets
with open(os.path.join(output_dir, 'graphrag_nodes.json'), 'w', encoding='utf-8') as f:
    json.dump({'total_nodes': len(nodes), 'nodes': nodes}, f, indent=2, ensure_ascii=False)

with open(os.path.join(output_dir, 'graphrag_edges.json'), 'w', encoding='utf-8') as f:
    json.dump({'total_edges': len(edges), 'edges': edges}, f, indent=2, ensure_ascii=False)

with open(os.path.join(output_dir, 'graphrag_communities.json'), 'w', encoding='utf-8') as f:
    json.dump({'total_communities': len(communities), 'communities': communities}, f, indent=2, ensure_ascii=False)

with open(os.path.join(output_dir, 'graphrag_covariates_and_rules.json'), 'w', encoding='utf-8') as f:
    json.dump({'total_rules': len(covariates), 'rules': covariates}, f, indent=2, ensure_ascii=False)

with open(os.path.join(output_dir, 'graphrag_search_index.json'), 'w', encoding='utf-8') as f:
    # Save top tokens to avoid gigantic JSON
    clean_index = {k: v[:20] for k, v in search_index.items() if len(k) > 3}
    json.dump({'total_terms': len(clean_index), 'index': clean_index}, f, indent=2, ensure_ascii=False)

print('Successfully generated all GraphRAG JSON artifacts in', output_dir)
