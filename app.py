import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Configuração visual do tema da página
st.set_page_config(
    page_title="Gestão Avançada DP - Erick", 
    layout="wide", 
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# Configurando o estilo escuro nativo simplificado para evitar quebras no chat
st.markdown("<style>.stApp { background-color: #121620; color: #E2E8F0; }</style>", unsafe_allow_html=True)

# 🔒 1. CONEXÃO COM O FIREBASE ONLINE
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("chave_firebase.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro ao carregar credenciais do Firebase: {e}")

db = firestore.client()

# Receptor Oculto de E-mails do Make
from flask import Flask, request, jsonify
import threading

app_webhook = Flask(__name__)

@app_webhook.route('/webhook', methods=['POST'])
def receber_demanda_email():
    try:
        dados = request.get_json()
        if dados:
            nova_tarefa = {
                "empresa": dados.get("empresa", "Desconhecido"),
                "canal": "E-mail",
                "descricao": dados.get("descricao", "Sem descrição"),
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Aguardando Resposta",
                "prioridade": dados.get("prioridade", "🟢 Média"),
                "timestamp": datetime.now()
            }
            db.collection("chamados").add(nova_tarefa)
            return jsonify({"status": "sucesso"}), 200
    except:
        return jsonify({"status": "erro"}), 500
    return jsonify({"status": "sem dados"}), 400

if 'webhook_iniciado' not in st.session_state:
    def rodar_servidor_rede():
        app_webhook.run(port=5000, debug=False, use_reloader=False)
    t = threading.Thread(target=rodar_servidor_rede)
    t.daemon = True
    t.start()
    st.session_state.webhook_iniciado = True
# Dicionário de dados reais dos clientes de DP extraídos da sua planilha
DICIONARIO_EMPRESAS = {
    "PITANGUI COMERCIO VAREGISTA": {"id": "47", "doc": "07.015.627/0001-65", "sistema": "NUVEM"},
    "POOL RIO SUL": {"id": "70", "doc": "31.445.010/0001-64", "sistema": "ALTERDATA-PACK"},
    "POSTO 09 ACESSORIOS DE COURO": {"id": "73", "doc": "12.582.488/0001-91", "sistema": "NUVEM"},
    "TERMIC SOLUÇÃO": {"id": "82", "doc": "37.757.873/0001-53", "sistema": "ALTERDATA-PACK"},
    "SAUL DOMESTICA": {"id": "147", "doc": "289.946.047-15", "sistema": "E-SOCIAL"},
    "DAISY MIRIAM": {"id": "255", "doc": "768.613.687-68", "sistema": "E-SOCIAL"},
    "LUSO FINANCIAL - MATRIZ": {"id": "256", "doc": "41.846.157/0001-10", "sistema": "NUVEM"},
    "ROUTE 164 APOIO": {"id": "257", "doc": "36.295.032/0001-09", "sistema": "DP"},
    "QUINTAL MINEIRO": {"id": "262", "doc": "51.776.798/0001-07", "sistema": "NUVEM"},
    "PROSPERCLOUD": {"id": "265", "doc": "52.572.163/0001-42", "sistema": "NUVEM"},
    "LUSO FINANCIAL - FILIAL": {"id": "266", "doc": "41.846.157/0002-09", "sistema": "NUVEM"},
    "RIO ROUTE 164": {"id": "275", "doc": "53.534.062/0001-40", "sistema": "DP"},
    "BRENO DIAS": {"id": "276", "doc": "57.689.701/0001-05", "sistema": "NUVEM"},
    "DRG": {"id": "277", "doc": "32.428.537/0001-43", "sistema": "DP"},
    "CECILIA VIANNA  BUFFET": {"id": "278", "doc": "55.743.638/0001-04", "sistema": "NUVEM"},
    "LADEIRA ENGENHARIA": {"id": "281", "doc": "62.633.165/0001-58", "sistema": "NUVEM"},
    "TREFFE SOLUÇÕES": {"id": "289", "doc": "37.258.219/0001-03", "sistema": "NUVEM"},
    "CONTROLADORA CARIOCA": {"id": "290", "doc": "12.136.666/0001-50", "sistema": "NUVEM"},
    "FISIOLAR FISIOTERAPIA": {"id": "291", "doc": "59.240.190/0001-67", "sistema": "NUVEM"},
    "TRUZZI SERVICOS PSIQUIATRICOS": {"id": "293", "doc": "68.048.796/0001-96", "sistema": "NUVEM"},
    "FABIO MARIANO": {"id": "DOM-1", "doc": "081.356.647-96", "sistema": "E-SOCIAL"},
    "JOSE ANTONIO": {"id": "DOM-2", "doc": "700.478.717-68", "sistema": "E-SOCIAL"},
    "ALEXINA": {"id": "DOM-3", "doc": "510.496.607-06", "sistema": "E-SOCIAL"}
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
# CENTRAL PRINCIPAL - DASHBOARD DE PRIVACIDADE E FILAS
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

# BLOCO DE INDICADORES NATIVOS DO STREAMLIT
tot_pendentes = len([d for d in demandas_online if d.get('status') == "Aguardando Resposta"])
tot_urgentes = len([d for d in demandas_online if "Alta" in d.get('prioridade', '') and d.get('status') == "Aguardando Resposta"])
tot_concluidos = len([d for d in demandas_online if "Concluído" in d.get('status', '')])

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(label="⏳ Chamados Pendentes", value=f"{tot_pendentes} ativos")
with m2:
    st.metric(label="🔴 Demandas Críticas", value=f"{tot_urgentes} urgências")
with m3:
    st.metric(label="✅ Finalizados Hoje", value=f"{tot_concluidos} baixas")

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
        
        # Renderização do cartão estruturada puramente através de componentes nativos do Streamlit
        with st.container(border=True):
            col_titulo, col_cod = st.columns([4, 1])
            with col_titulo:
                st.markdown(f"### 🏢 {emp_nome}")
            with col_cod:
                st.markdown(f"**Cód/Ref:** `{info_fixa['id']}`")
                
            st.markdown(f"📋 **Doc:** {info_fixa['doc']} | 💻 **Sistema:** `{info_fixa['sistema']}` | 🌐 **Canal:** {d.get('canal', 'E-mail')}")
            st.markdown("---")
            st.info(f"💡 **Demanda Identificada:** {d.get('descricao', 'Sem descrição')}")
            st.caption(f"📅 Capturado em: {d.get('data', '')} | Prioridade Técnica: {d.get('prioridade', '🟢 Média')}")
            
            # Área de ações operacionais e baixa
            if d.get('status') == "Aguardando Resposta":
                c_exec, c_btn = st.columns([4, 1])
                with c_exec:
                    resposta_dp = st.text_input("Registrar ação executada:", key=f"resp_{d['id_documento']}", label_visibility="collapsed", placeholder="Escreva a resolução técnica aqui...")
                with c_btn:
                    if st.button("Dar Baixa", key=f"btn_{d['id_documento']}", use_container_width=True):
                        if resposta_dp:
                            resultado_baixa = agente_auditor_baixa(resposta_dp)
                            novo_status = "🟢 Concluído" if resultado_baixa.get("fechar_tarefa", False) else "Aguardando Resposta"
                            db.collection("chamados").document(d['id_documento']).update({"status": novo_status})
                            st.rerun()
            else:
                st.success("✅ Atendimento Finalizado")
                if st.button("↩️ Reabrir Chamado", key=f"reabrir_{d['id_documento']}"):
                    db.collection("chamados").document(d['id_documento']).update({"status": "Aguardando Resposta"})
                    st.rerun()
