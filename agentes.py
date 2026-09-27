from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# =====================================================================
# 🔌 CONFIGURAÇÃO DO MOTOR DE IA (GOOGLE GEMINI GRATUITO)
# =====================================================================
# Substitua pelo código da chave que você pegou no Google AI Studio
MINHA_CHAVE_GEMINI = "COLE_AQUI_SUA_CHAVE_AIza"

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=MINHA_CHAVE_GEMINI,
    temperature=0
)
parser = JsonOutputParser()

def agente_triador(texto_mensagem):
    """Agente 1: Filtra o ruído e extrai a demanda real do DP"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é o Agente Triador de um Departamento Pessoal.
         Analise a mensagem recebida e identifique se há uma demanda operacional de DP (rescisão, férias, ponto, folha, etc).
         Sua resposta deve ser estritamente um JSON no seguinte formato:
         {{
           "contem_demanda": true ou false,
           "descricao_resumida": "Resumo técnico da demanda em português"
         }}"""),
        ("user", "Mensagem recebida: {mensagem}")
    ])
    
    cadeia = prompt | llm | parser
    try:
        return cadeia.invoke({"mensagem": texto_mensagem})
    except:
        return {"contem_demanda": True, "descricao_resumida": texto_mensagem[:50]}

def agente_operador(descricao_demanda):
    """Agente 2: Define prioridades e cria respostas para o site"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é o Agente Operador do sistema de DP.
         Defina o nível de prioridade (🔴 Alta, 🟢 Média ou 🟡 Baixa) e redija uma mensagem curta confirmando o recebimento ao cliente.
         Sua resposta deve ser estritamente um JSON no seguinte formato:
         {{
           "prioridade": "🔴 Alta" ou "🟢 Média" ou "🟡 Baixa",
           "resposta_cliente": "Texto curto confirmando que o DP está trabalhando na demanda."
         }}"""),
        ("user", "Demanda triada: {demanda}")
    ])
    
    cadeia = prompt | llm | parser
    try:
        return cadeia.invoke({"demanda": descricao_demanda})
    except:
        return {"prioridade": "🟢 Média", "resposta_cliente": "Recebemos sua demanda e estamos analisando."}

def agente_auditor_baixa(resposta_dp):
    """Agente 3: Analisa se a resposta do profissional encerra o chamado"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Você é o Agente Auditor de Baixas do DP.
         Se o profissional estiver entregando o documento, guia ou resolução (ex: 'segue anexo', 'concluído', 'feito'), defina fechar_tarefa como true.
         Se ele estiver apenas fazendo uma pergunta ou pedindo documentos, defina fechar_tarefa como false.
         Sua resposta deve ser estritamente um JSON no seguinte formato:
         {{
           "fechar_tarefa": true ou false
         }}"""),
        ("user", "Resposta dada pelo profissional do DP: {resposta}")
    ])
    
    cadeia = prompt | llm | parser
    try:
        return cadeia.invoke({"resposta": resposta_dp})
    except:
        return {"fechar_tarefa": True}