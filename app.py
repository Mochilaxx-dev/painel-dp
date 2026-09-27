import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Configuração visual e tema da página
st.set_page_config(
    page_title="Gestão Avançada DP - Erick", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada para o tema Premium (Dark Mode)
st.markdown("""
<style>
    .stApp { background-color: #121620; color: #E2E8F0; }
    section[data-testid="stSidebar"] { background-color: #1A202C !important; }
    .metric-card {
        background-color: #1E293B; border-radius: 10px; padding: 15px; margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-left: 5px solid #3B82F6;
    }
    .task-card {
        background-color: #1E293B; border-radius: 12px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); border: 1px solid #2D3748;
    }
    .priority-high { border-left: 6px solid #EF4444 !important; }
    .priority-medium { border-left: 6px solid #F59E0B !important; }
    .priority-low { border-left: 6px solid #10B981 !important; }
    .status-done { border-left: 6px solid #4B5563 !important; opacity: 0.6; }
</style>
""", unsafe_allow_html=True)

# 🔒 1. CONEXÃO COM O FIREBASE ONLINE
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("chave_firebase.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais do Firebase: {e}")

db = firestore.client()

# Dicionário de dados reais dos clientes de DP [1]
DICIONARIO_EMPRESAS = {
    "PITANGUI COMERCIO VAREGISTA": {"id": "47", "doc": "07.015.627/0001-65", "sistema": "NUVEM", "emails": ["cecilia@malaamada.com.br", "carmelialeite@terra.com.br"]},
    "POOL RIO SUL": {"id": "70", "doc": "31.445.010/0001-64", "sistema": "ALTERDATA-PACK", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "POSTO 09 ACESSORIOS DE COURO": {"id": "73", "doc": "12.582.488/0001-91", "sistema": "NUVEM", "emails": ["cecilia@malaamada.com.br", "carmelialeite@terra.com.br"]},
    "TERMIC SOLUÇÃO": {"id": "82", "doc": "37.757.873/0001-53", "sistema": "ALTERDATA-PACK", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "SAUL DOMESTICA": {"id": "147", "doc": "289.946.047-15", "sistema": "E-SOCIAL", "emails": ["saul.bteshe@gmail.com", "marilubt@gmail.com"]},
    "DAISY MIRIAM": {"id": "255", "doc": "768.613.687-68", "sistema": "E-SOCIAL", "emails": ["glauallevato@gmail.com", "daisylontra@yahoo.com.br"]},
    "LUSO FINANCIAL - MATRIZ": {"id": "256", "doc": "41.846.157/0001-10", "sistema": "NUVEM", "emails": ["antoniopedro2205@gmail.com", "LUSOFINANCIAL@gmail.com"]},
    "ROUTE 164 APOIO": {"id": "257", "doc": "36.295.032/0001-09", "sistema": "DP", "emails": ["mariana.parada971@gmail.com"]},
    "QUINTAL MINEIRO": {"id": "262", "doc": "51.776.798/0001-07", "sistema": "NUVEM", "emails": ["WHATSAPP"]},
    "PROSPERCLOUD": {"id": "265", "doc": "52.572.163/0001-42", "sistema": "NUVEM", "emails": ["taraujo@iuven.com.br"]},
    "LUSO FINANCIAL - FILIAL": {"id": "266", "doc": "41.846.157/0002-09", "sistema": "NUVEM", "emails": ["antoniopedro2205@gmail.com", "LUSOFINANCIAL@gmail.com"]},
    "RIO ROUTE 164": {"id": "275", "doc": "53.534.062/0001-40", "sistema": "DP", "emails": ["mariana.parada971@gmail.com"]},
    "BRENO DIAS": {"id": "276", "doc": "57.689.701/0001-05", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "DRG": {"id": "277", "doc": "32.428.537/0001-43", "sistema": "DP", "emails": ["contabilidade@drgcontabil.com.br"]},
    "CECILIA VIANNA  BUFFET": {"id": "278", "doc": "55.743.638/0001-04", "sistema": "NUVEM", "emails": ["dinners.rio@gmail.com"]},
    "LADEIRA ENGENHARIA": {"id": "281", "doc": "62.633.165/0001-58", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "TREFFE SOLUÇÕES": {"id": "289", "doc": "37.258.219/0001-03", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "CONTROLADORA CARIOCA": {"id": "290", "doc": "12.136.666/0001-50", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "FISIOLAR FISIOTERAPIA": {"id": "291", "doc": "59.240.190/0001-67", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "TRUZZI SERVICOS PSIQUIATRICOS": {"id": "293", "doc": "68.048.796/0001-96", "sistema": "NUVEM", "emails": ["drfassessoriaempresarial@gmail.com"]},
    "FABIO MARIANO": {"id": "DOM-1", "doc": "081.356.647-96", "sistema": "E-SOCIAL", "emails": ["FABIOHM16@GMAIL.COM"]},
    "JOSE ANTONIO": {"id": "DOM-2", "doc": "700.478.717-68", "sistema": "E-SOCIAL", "emails": ["jafsouto@gmail.com"]},
    "ALEXINA": {"id": "DOM-3", "doc": "510.496.607-06", "sistema": "E-SOCIAL", "emails": ["chicamype@icloud.com"]}
}

lista_empresas_cadastradas = sorted(list(DICIONARIO_EMPRESAS.keys()))

# 📥 CAPTURA MANUAL NA BARRA LATERAL
st.sidebar.markdown("## 📥 Captura Manual")
with st.sidebar.form(key="mensagem_cliente"):
    empresa_sel = st.selectbox("Empresa Cliente", lista_empresas_cadastradas)
    canal_sel = st.selectbox("Canal de Entrada", ["WhatsApp", "E-mail"])
    mensagem_texto = st.text_area("Texto enviado pelo cliente:")
    botao_enviar = st.form_submit_button("Processar e Injetar no Painel")

if botao_enviar and mensagem_texto:
    from agentes import agente_triador, agente_operador
    with st.spinner("🤖 Processando com IA..."):
        resultado_triagem = agente_triador(mensagem_texto)
        if resultado_triagem.get("contem_demanda", False):
            resultado_operacao = agente_operador(resultado_triagem["descricao_resumida"])
            
            nova_tarefa = {
                "empresa": empresa_sel,
                "canal": canal_sel,
                "descricao": resultado_triagem["descricao_resumida"],
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Aguardando Resposta",
                "prioridade": resultado_operacao.get("prioridade", "🟢 Média"),
                "timestamp": datetime.now()
            }
            db.collection("chamados").add(nova_tarefa)
            st.sidebar.success("✨ Sincronizado com o Firebase Cloud!")

# -----------------------------------------------------------------------------------------
# CENTRAL PRINCIPAL - DASHBOARD DE PRIVACIDADE E MÉTRICAS
# -----------------------------------------------------------------------------------------
st.markdown("# 🚀 Hub de Operações - Departamento Pessoal")
st.markdown("Controle unificado de demandas com inteligência artificial e nuvem protegida.")

# Captura de dados do Firebase em Tempo Real
try:
    chamados_ref = db.collection("chamados").order_by("timestamp", direction=firestore.Query.DESCENDING)
    docs = chamados_ref.stream()
    demandas_online = [dict(doc.to_dict(), id_documento=doc.id) for doc in docs]
except:
    demandas_online = []

# BLOCO DE INDICADORES (MÉTRICAS DO DIA)
tot_pendentes = len([d for d in demandas_online if d.get('status') == "Aguardando Resposta"])
tot_urgentes = len([d for d in demandas_online if "Alta" in d.get('prioridade', '') and d.get('status') == "Aguardando Resposta"])
tot_concluidos = len([d for d in demandas_online if "Concluído" in d.get('status', '')])

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card" style="border-left-color: #F59E0B;"><h3>⏳ Pendentes</h3><h2>{tot_pendentes} chamados</h2></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card" style="border-left-color: #EF4444;"><h3>🔴 Críticos</h3><h2>{tot_urgentes} urgências</h2></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card" style="border-left-color: #10B981;"><h3>✅ Finalizados Hoje</h3><h2>{tot_concluidos} baixas</h2></div>', unsafe_allow_html=True)

# 🔒 BARREIRA DE PRIVACIDADE
st.markdown("### 🛡️ Filtro de Visualização por Empresa")
filtro_privacidade = st.selectbox(
    "Escolha o cliente em foco (Dados das outras empresas serão ocultados no monitor):",
    ["Visualizar Todos os Clientes"] + lista_empresas_cadastradas
)

if filtro_privacidade != "Visualizar Todos os Clientes":
    demandas_online = [d for d in demandas_online if d.get('empresa') == filtro_privacidade]

st.markdown(f"### 📋 Fila de Trabalho Ativa — Atendendo: **{filtro_privacidade}**")

if not demandas_online:
    st.info("Nenhuma demanda ativa localizada para este filtro.")
else:
    from agentes import agente_auditor_baixa
    for d in demandas_online:
        emp_nome = d.get('empresa', 'Desconhecido')
        info_fixa = DICIONARIO_EMPRESAS.get(emp_nome, {"id": "-", "doc": "Não cadastrado", "sistema": "Não informado"})
        
        # Define a classe visual com base no status e prioridade
        if d.get('status') != "Aguardando Resposta":
            classe_card = "task-card status-done"
        elif "Alta" in d.get('prioridade', ''):
            classe_card = "task-card priority-high"
        elif "Baixa" in d.get('prioridade', ''):
            classe_card = "task-card priority-low"
        else:
            classe_card = "task-card priority-medium"
            
        st.markdown(f"""
        <div class="{classe_card}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: #F8FAFC;">🏢 {emp_nome}</h3>
                <span style="background: #2D3748; padding: 4px 10px; border-radius: 20px; font-size: 12px; color: #CBD5E1;">🆔 Cód/Ref: {info_fixa['id']}</span>
            </div>
            <p style="margin: 5px 0; font-size: 13px; color: #94A3B8;">
                📋 <b>Doc:</b> {info_fixa['doc']} | 💻 <b>Sistema:</b> <code style="color: #60A5FA;">{info_fixa['sistema']}</code> | 🌐 <b>Canal:</b> {d.get('canal', 'E-mail')}
            </p>
            <hr style="border: 0; border-top: 1px solid #2D3748; margin: 10px 0;">
