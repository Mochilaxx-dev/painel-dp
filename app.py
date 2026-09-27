import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

st.set_page_config(page_title="Sistema Multi-Agentes Online - DP", layout="wide", page_icon="🤖")

# 🔒 1. CONEXÃO COM O FIREBASE ONLINE
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("chave_firebase.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo chave_firebase.json: {e}")

db = firestore.client()

st.title("💼 Painel de DP Automatizado via Firebase Cloud")
st.markdown("Suas demandas estão sendo monitoradas e salvas diretamente na nuvem do Google de graça.")

# -----------------------------------------------------------------------------------------
# BARRA LATERAL - ENTRADA MANUAL DE DADOS (CASO PRECISE)
# -----------------------------------------------------------------------------------------
st.sidebar.header("📥 Captura Manual")
lista_empresas = ["Mecânica Silva", "Restaurante Sabor & Cia", "Padaria Central", "Clínica Médica Vida", "Desconhecido"]

with st.sidebar.form(key="mensagem_cliente"):
    empresa = st.selectbox("Empresa Cliente", lista_empresas)
    canal = st.selectbox("Canal", ["WhatsApp", "E-mail"])
    contato = st.text_input("Contato", "(11) 99999-8888")
    mensagem = st.text_area("Texto enviado pelo cliente:")
    botao_enviar = st.form_submit_button("Processar e Salvar")

if botao_enviar and mensagem:
    from agentes import agente_triador, agente_operador
    with st.spinner("🤖 Processando..."):
        resultado_triagem = agente_triador(mensagem)
        if resultado_triagem.get("contem_demanda", False):
            resultado_operacao = agente_operador(resultado_triagem["descricao_resumida"])
            nova_tarefa = {
                "empresa": empresa,
                "canal": canal,
                "contato": contato,
                "descricao": resultado_triagem["descricao_resumida"],
                "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Aguardando Resposta",
                "prioridade": resultado_operacao.get("prioridade", "🟢 Média"),
                "timestamp": datetime.now()
            }
            db.collection("chamados").add(nova_tarefa)
            st.sidebar.success("✨ Salvo manual no Firebase!")

# -----------------------------------------------------------------------------------------
# 🔒 CONTROLE DE PRIVACIDADE E EXIBIÇÃO DOS DADOS ONLINE
# -----------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🛡️ Controle de Privacidade")
filtro_privacidade = st.selectbox(
    "Selecione o Cliente em Atendimento (Oculta os dados dos demais concorrentes):",
    ["Visualizar Todos os Clientes"] + [emp for emp in lista_empresas if emp != "Desconhecido"]
)

# Busca os dados em tempo real direto do Firebase Cloud
try:
    chamados_ref = db.collection("chamados").order_by("timestamp", direction=firestore.Query.DESCENDING)
    docs = chamados_ref.stream()
    
    demandas_online = []
    for doc in docs:
        dados = doc.to_dict()
        dados["id_documento"] = doc.id
        demandas_online.append(dados)
except Exception as e:
    demandas_online = []

if filtro_privacidade != "Visualizar Todos os Clientes":
    demandas_online = [d for d in demandas_online if d['empresa'] == filtro_privacidade]

st.subheader(f"📋 Demandas Atuais - Exibindo: {filtro_privacidade}")

if not demandas_online:
    st.info("Nenhum chamado pendente para esta seleção no momento.")
else:
    from agentes import agente_auditor_baixa
    for d in demandas_online:
        with st.container():
            st.markdown("---")
            c1, c2, c3 = st.columns([1.5, 3.5, 2])
            
            with c1:
                st.markdown(f"### {d.get('empresa', 'Desconhecido')}")
                st.markdown(f"🌐 Canal: `{d.get('canal', 'E-mail')}`")
                st.markdown(f"🚨 Prioridade: {d.get('prioridade', '🟢 Média')}")
                st.caption(f"Data: {d.get('data', '')}")
                
            with c2:
                st.markdown("**Demanda Processada pela IA:**")
                st.info(d.get('descricao', 'Sem descrição'))
                
            with c3:
                st.markdown(f"Status: **{d.get('status', 'Aguardando Resposta')}**")
                if d.get('status') == "Aguardando Resposta":
                    resposta_dp = st.text_input("Escreva sua resposta ao cliente:", key=f"resp_{d['id_documento']}")
                    if st.button("Enviar e Auditar Baixa", key=f"btn_{d['id_documento']}"):
                        if resposta_dp:
                            resultado_baixa = agente_auditor_baixa(resposta_dp)
                            novo_status = "🟢 Concluído" if resultado_baixa.get("fechar_tarefa", False) else "Aguardando Resposta"
                            db.collection("chamados").document(d['id_documento']).update({"status": novo_status})
                            st.rerun()
                else:
                    st.success("✅ Atendimento Finalizado")
                    if st.button("Reabrir Demanda", key=f"reabrir_{d['id_documento']}"):
                        db.collection("chamados").document(d['id_documento']).update({"status": "Aguardando Resposta"})
                        st.rerun()