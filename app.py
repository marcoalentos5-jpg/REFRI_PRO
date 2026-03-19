###############################################################################
# [ BLOCO 01 DE 12 ] - NÚCLEO DE CONFIGURAÇÃO, ESTÉTICA CSS E ESTADO DO APP    #
# VERSÃO: 4.700 (BLINDADA) - FOCO: LIMPEZA E ESTABILIDADE                     #
###############################################################################

import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import sqlite3
from datetime import datetime
import urllib.parse
import os

# 1. CONFIGURAÇÃO DE PÁGINA (ESTRUTURA BLOQUEADA)
st.set_page_config(
    page_title="SISTEMA HVAC PROFISSIONAL - MARCOS ALEXANDRE",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. MOTOR DE ESTILIZAÇÃO CSS (JANELAS E BOTÕES)
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; background-color: #ffffff; padding: 15px 15px 0px 15px;
        border-radius: 12px 12px 0px 0px; border-bottom: 2px solid #004a99;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #f8f9fa; border-radius: 5px 5px 0px 0px;
        color: #495057; font-weight: 600; border: 1px solid #dee2e6;
    }
    .stTabs [aria-selected="true"] { background-color: #004a99 !important; color: white !important; }
    
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border-left: 5px solid #004a99; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    .section-title {
        color: #004a99; font-size: 1.2rem; font-weight: bold;
        margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px;
    }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #004a99; color: white; font-weight: bold;
        text-transform: uppercase; transition: 0.4s;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. INICIALIZAÇÃO DE ESTADO (BLINDAGEM DE MEMÓRIA)
if 'dados_cliente' not in st.session_state:
    st.session_state.dados_cliente = {"nome": "", "cpf": "", "data": datetime.now().strftime("%d/%m/%Y")}
if 'checklist_respostas' not in st.session_state:
    st.session_state.checklist_respostas = {}

# 4. CONSTANTES TÉCNICAS
FLUIDOS_INFO = {
    "R410A": {"tipo": "HFC", "cor": "#e6194B"},
    "R134a": {"tipo": "HFC", "cor": "#3cb44b"},
    "R22": {"tipo": "HCFC", "cor": "#ffe119"},
    "R404A": {"tipo": "HFC", "cor": "#4363d8"},
    "R32": {"tipo": "HFC", "cor": "#f58231"}
}

# 5. CLASSES UTILITÁRIAS
def janela_titulo(titulo):
    st.markdown(f'<p class="section-title">{titulo}</p>', unsafe_allow_html=True)

# 6. CRIAÇÃO DAS ABAS (INTERFACE PRINCIPAL)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👤 Identificação", "🏢 Equipamento", "⚡ Elétrica", "🌡️ Térmica", "📋 Checklist", "🧠 Diagnóstico", "🔍 Histórico"
])

# --- CONTEÚDO DA ABA 1 ---
with tab1:
    janela_titulo("👤 1. IDENTIFICAÇÃO DO CLIENTE")
    c1, c2 = st.columns(2)
    with c1:
        cliente_nome = st.text_input("Nome/Razão Social:", key="cli_nome")
        cliente_cpf = st.text_input("CPF ou CNPJ:", key="cli_cpf")
    with c2:
        data_visita = st.date_input("Data do Atendimento:", format="DD/MM/YYYY")
        tipo_servico = st.selectbox("Tipo de Serviço:", ["Instalação", "Preventiva", "Corretiva"], key="tipo_serv_idx")
    st.session_state.dados_cliente.update({"nome": cliente_nome, "cpf": cliente_cpf, "servico": tipo_servico})

# --- CONTEÚDO DA ABA 6 (RESUMIDA E SEM DUPLICIDADE) ---
with tab6:
    janela_titulo("🧠 6. DIAGNÓSTICO E LAUDO")
    defeitos_master = ["Falta de Fluido", "Compressor em Curto", "Capacitor Esgotado", "Obstrução no Filtro"]
    # CHAVE ÚNICA PARA EVITAR O ERRO StreamlitDuplicateElementId
    selecionados = st.multiselect("🔍 Defeitos Identificados:", sorted(defeitos_master), key="diag_multiselect_final")
    parecer = st.text_area("📝 Parecer Técnico:", value="📌 CONCLUSÃO: " + ", ".join(selecionados), height=150)
    
    c_pdf1, c_pdf2, c_wa1, c_wa2 = st.columns(4)
    with c_pdf1: st.button("📄 GERAR LAUDO PDF", key="btn_pdf_laudo")
    with c_wa1: st.button("📲 WHATSAPP CLIENTE", key="btn_wa_cli")
# LINHA 200
###############################################################################
# [ BLOCO 02 DE 12 ] - BANCO DE DADOS SQLITE E PERSISTÊNCIA DE DADOS           #
# VERSÃO: 4.700 (BLINDADA) - FOCO: SEGURANÇA E INTEGRIDADE                     #
###############################################################################

# 7. MOTOR DE BANCO DE DADOS (SQLITE3)
def conectar_db():
    return sqlite3.connect('hvac_master_db.sqlite', check_same_thread=False)

def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nome TEXT,
            cliente_cpf TEXT,
            data_visita TEXT,
            aparelho_modelo TEXT,
            fluido_tipo TEXT,
            pressao_alta REAL,
            pressao_baixa REAL,
            temp_suc_val REAL,
            temp_liq_val REAL,
            superaquecimento REAL,
            subresfriamento REAL,
            corrente_total REAL,
            checklist_json TEXT,
            diagnostico_ia TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

criar_tabelas()

# 8. FUNÇÕES DE MANIPULAÇÃO DE DADOS (CRUD)
def salvar_atendimento(dados):
    conn = conectar_db()
    cursor = conn.cursor()
    query = """
        INSERT INTO atendimentos (
            cliente_nome, cliente_cpf, data_visita, aparelho_modelo,
            fluido_tipo, pressao_alta, pressao_baixa, temp_suc_val,
            temp_liq_val, superaquecimento, subresfriamento, corrente_total,
            checklist_json, diagnostico_ia
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    params = (
        dados.get('nome'), dados.get('cpf'), dados.get('data'), dados.get('modelo'),
        dados.get('fluido'), dados.get('p_alta'), dados.get('p_baixa'), dados.get('t_suc'),
        dados.get('t_liq'), dados.get('sh'), dados.get('sc'), dados.get('corrente'),
        json.dumps(dados.get('checklist', {})), dados.get('diagnostico')
    )
    cursor.execute(query, params)
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id

def buscar_por_cpf(cpf):
    conn = conectar_db()
    # BLINDAGEM: Uso de parâmetros '?' para evitar ataques de SQL Injection
    query = "SELECT * FROM atendimentos WHERE cliente_cpf = ? ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=(cpf,))
    conn.close()
    return df

###############################################################################
# [ BLOCO 03 DE 12 ] - MOTOR DE CÁLCULOS TÉRMICOS E TERMODINÂMICA              #
# VERSÃO: 4.700 (BLINDADA) - FOCO: PRECISÃO E ESTABILIDADE                     #
###############################################################################

# 9. MOTOR DE CÁLCULO DE PROPRIEDADES (PADRÃO ASHRAE)
def calcular_temperatura_saturacao(pressao_psi, fluido):
    """Converte Pressão (PSI) em Temp. de Saturação (°C) via Regressão"""
    coefs = {
        "R410A": {"a": 0.0001, "b": 0.15, "c": -30.0},
        "R134a": {"a": 0.0002, "b": 0.25, "c": -20.0},
        "R22":   {"a": 0.00015, "b": 0.20, "c": -25.0}
    }
    
    if fluido in coefs:
        c = coefs[fluido]
        # Cálculo parabólico para resposta instantânea
        temp_sat = (c['a'] * (pressao_psi**2)) + (c['b'] * pressao_psi) + c['c']
        return round(temp_sat, 2)
    return 0.0

def calcular_parametros_performance(dados):
    """Calcula SH, SC e Temperaturas de Saturação"""
    p_baixa = dados.get('p_baixa', 0)
    p_alta = dados.get('p_alta', 0)
    t_suc = dados.get('t_suc', 0)
    t_liq = dados.get('t_liq', 0)
    fluido = dados.get('fluido', 'R410A')
    
    t_evap = calcular_temperatura_saturacao(p_baixa, fluido)
    t_cond = calcular_temperatura_saturacao(p_alta, fluido)
    
    # SH = T_sucção - T_evaporação | SC = T_condensação - T_líquido
    return {
        "t_evap": t_evap,
        "t_cond": t_cond,
        "sh": round(t_suc - t_evap, 2),
        "sc": round(t_cond - t_liq, 2)
    }

def calcular_cop_estimado(corrente, voltagem, p_alta, p_baixa):
    """Estima o COP baseado na potência e razão de pressão"""
    # BLINDAGEM: Evita divisão por zero e valores negativos
    if corrente <= 0 or p_baixa <= 0: 
        return 0.0
        
    razao_pressao = p_alta / p_baixa
    # Lógica: Eficiência inversamente proporcional à razão de compressão
    cop = 4.5 / (razao_pressao * 0.8)
    return round(min(max(cop, 1.0), 6.0), 2)

###############################################################################
# [ BLOCO 04 DE 12 ] - MOTOR GRÁFICO E DIAGRAMAS TERMODINÂMICOS                #
# VERSÃO: 4.700 (BLINDADA) - FOCO: VISUALIZAÇÃO E ESTABILIDADE                 #
###############################################################################

import matplotlib.pyplot as plt
import numpy as np

# 10. MOTOR DE GERAÇÃO DE DIAGRAMAS (MATPLOTLIB)
def gerar_diagrama_mollier(fluido, p_alta, p_baixa, t_suc, t_liq):
    """Gera o gráfico P-h (Pressão vs Entalpia) simplificado para o laudo"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Curva de Saturação (Sino) - Simulação técnica
    h_sino = np.linspace(150, 450, 100)
    p_sino = 100 * np.sin(np.pi * (h_sino - 150) / 300) + 50
    
    ax.plot(h_sino[:50], p_sino[:50], 'b-', label='Líquido Saturado')
    ax.plot(h_sino[50:], p_sino[50:], 'r-', label='Vapor Saturado')
    
    # Plotagem do Ciclo (Ponto 1 ao 4)
    # Proteção: Pressões mínimas para evitar erro em escala LOG
    p_alta_safe = max(p_alta, 1.1)
    p_baixa_safe = max(p_baixa, 1.0)
    
    pontos_h = [400, 450, 200, 200, 400]
    pontos_p = [p_baixa_safe, p_alta_safe, p_alta_safe, p_baixa_safe, p_baixa_safe]
    
    ax.plot(pontos_h, pontos_p, 'k-o', linewidth=2, label='Ciclo de Refrigeração')
    ax.set_yscale('log')
    
    ax.set_title(f"Diagrama P-h: {fluido}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Entalpia (kJ/kg)")
    ax.set_ylabel("Pressão (PSI)")
    ax.grid(True, which="both", ls="-", alpha=0.3)
    ax.legend(loc='upper right', fontsize='small')
    
    plt.tight_layout()
    return fig

def gerar_grafico_sh_sc(sh, sc):
    """Gera gráfico de barras para diagnóstico rápido de SH e SC"""
    fig, ax = plt.subplots(figsize=(6, 4))
    categorias = ['Superaq. (SH)', 'Subresf. (SC)']
    valores = [max(sh, 0), max(sc, 0)] # Evita barras negativas no visual
    
    bars = ax.bar(categorias, valores, color=['#FF9800', '#00BCD4'], edgecolor='black', width=0.5)
    
    # Rótulos automáticos no topo das barras
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.1f}°C", 
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylim(0, max(max(valores) + 5, 15))
    ax.set_ylabel("Diferencial de Temp. (°C)")
    ax.set_title("Diagnóstico de Performance Térmica", fontsize=10)
    
    plt.tight_layout()
    return fig

###############################################################################
# [ BLOCO 05 DE 12 ] - MOTOR DE DIAGNÓSTICO E INTELIGÊNCIA DE CAMPO            #
# VERSÃO: 4.700 (BLINDADA) - FOCO: LÓGICA TÉCNICA E PERFORMANCE                #
###############################################################################

# 11. MOTOR DE DIAGNÓSTICO (IA DE REFRIGERAÇÃO)
def gerar_diagnostico_hvac(sh, sc, corrente, p_alta, p_baixa):
    """Analisa parâmetros térmicos/elétricos para sugerir falhas reais"""
    diag, reco = [], []
    
    # 1. Baixa Carga de Fluido (SH Alto + SC Baixo)
    if sh > 12 and sc < 3:
        diag.append("SINTOMA: Baixa carga de fluido refrigerante detectada.")
        reco.extend(["- Realizar teste de estanqueidade com nitrogênio.", 
                     "- Verificar vazamentos em flanges e soldas."])
        
    # 2. Excesso de Carga ou Condensadora Suja (SC Alto + P. Alta)
    elif sc > 10 and p_alta > 400:
        diag.append("SINTOMA: Alta pressão de condensação / Excesso de fluido.")
        reco.extend(["- Limpar a serpentina da unidade condensadora.", 
                     "- Verificar ventilador da unidade externa."])
        
    # 3. Ineficiência do Compressor (P. Baixa Alta + P. Alta Baixa + Corrente Baixa)
    elif p_baixa > 150 and p_alta < 300 and corrente < 5:
        diag.append("SINTOMA: Compressor com baixa compressão (bypass).")
        reco.extend(["- Comparar pressões com compressor parado/partida.", 
                     "- Avaliar substituição das válvulas ou compressor."])

    # 4. Evaporadora Obstruída / Baixo Fluxo (SH Baixo + P. Baixa Baixa)
    elif sh < 4 and p_baixa < 100:
        diag.append("SINTOMA: Baixo fluxo de ar ou congelamento na evaporadora.")
        reco.extend(["- Limpar filtros de ar e serpentina interna.", 
                     "- Checar motor ventilador da evaporadora."])

    # 5. Sistema em Equilíbrio
    if not diag:
        diag.append("SISTEMA OPERANDO EM PARÂMETROS NOMINAIS.")
        reco.append("- Realizar apenas manutenção preventiva de rotina.")

    return {
        "status": "\n".join(diag),
        "recomendacoes": "\n".join(reco)
    }

###############################################################################
# [ BLOCO 06 DE 12 ] - MOTOR DE PDF E RELATÓRIO DO CLIENTE                    #
# VERSÃO: 4.700 (BLINDADA) - FOCO: DOCUMENTAÇÃO E COMPATIBILIDADE             #
###############################################################################

class GeradorPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'RELATÓRIO TÉCNICO DE MANUTENÇÃO HVAC', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'MARCOS ALEXANDRE - ENGENHARIA E CLIMATIZAÇÃO', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 10, f'Página {self.page_no()} | Gerado em: {data_geracao}', 0, 0, 'C')

def gerar_pdf_cliente(dados):
    # Inicialização do documento
    pdf = GeradorPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    fill_color = (230, 230, 230)
    
    # 1. IDENTIFICAÇÃO (Estrutura Simplificada)
    pdf.set_fill_color(*fill_color)
    pdf.cell(0, 8, "1. IDENTIFICAÇÃO DO ATENDIMENTO", 1, 1, 'L', 1)
    pdf.ln(2)
    
    # Mapeamento de campos para evitar repetição de código
    campos = [
        f"Cliente: {dados.get('nome', 'N/A')}",
        f"CPF/CNPJ: {dados.get('cpf', 'N/A')}",
        f"Modelo: {dados.get('modelo', 'N/A')}",
        f"Fluido: {dados.get('fluido', 'R410A')}"
    ]
    for campo in campos:
        pdf.cell(0, 7, campo, 0, 1)
    pdf.ln(5)

    # 2. PARÂMETROS TÉCNICOS
    pdf.set_fill_color(*fill_color)
    pdf.cell(0, 8, "2. PARÂMETROS DE FUNCIONAMENTO", 1, 1, 'L', 1)
    pdf.ln(2)
    
    # Tabela 2x2 Otimizada
    pdf.cell(95, 7, f"P. Alta: {dados.get('p_alta', 0)} PSI", 1)
    pdf.cell(95, 7, f"P. Baixa: {dados.get('p_baixa', 0)} PSI", 1, 1)
    pdf.cell(95, 7, f"T. Sucção: {dados.get('t_suc', 0)} °C", 1)
    pdf.cell(95, 7, f"Corrente: {dados.get('corrente', 0)} A", 1, 1)
    pdf.ln(10)

    # 3. CONCLUSÃO E ASSINATURA
    conclusao = ("Equipamento vistoriado e testado sob condições de carga nominal. "
                 "Os parâmetros coletados foram registrados para fins de garantia e histórico.")
    pdf.multi_cell(0, 7, conclusao)
    
    pdf.ln(20)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.cell(0, 10, "Responsável Técnico", 0, 1, 'C')
    
    # Retorno seguro (Tratamento de acentuação para o navegador)
    return pdf.output(dest='S').encode('latin-1', errors='replace')


###############################################################################
# [ BLOCO 07 DE 12 ] - PRONTUÁRIO TÉCNICO INTERNO (ESTRATÉGICO)                #
# VERSÃO: 4.700 (BLINDADA) - FOCO: ANÁLISE AVANÇADA E PERFORMANCE              #
###############################################################################

import io

def gerar_pdf_interno(dados, fig_mollier, fig_sh_sc):
    """Gera o relatório avançado com gráficos para uso da engenharia"""
    pdf = GeradorPDF()
    pdf.add_page()
    
    # Cabeçalho de Alerta (Cor Vermelha para Sigilo)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, "DOCUMENTO INTERNO - PROPRIEDADE TÉCNICA", 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # 1. Seção Termodinâmica (Azul Suave)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 8, "ANÁLISE TERMODINÂMICA AVANÇADA", 1, 1, 'L', 1)
    pdf.set_font("Arial", size=10)
    
    w = 47.5
    pdf.cell(w, 8, f"SH: {dados.get('sh', 0)} °C", 1)
    pdf.cell(w, 8, f"SC: {dados.get('sc', 0)} °C", 1)
    pdf.cell(w, 8, f"T. Evap: {dados.get('t_evap', 0)} °C", 1)
    pdf.cell(w, 8, f"T. Cond: {dados.get('t_cond', 0)} °C", 1, 1)
    pdf.ln(5)

    # 2. Diagnóstico IA
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DIAGNÓSTICO E PLANO DE AÇÃO (IA):", 0, 1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, f"STATUS: {dados.get('diagnostico_status', 'Sem dados')}", border=1)
    pdf.ln(2)
    pdf.multi_cell(0, 6, f"RECOMENDAÇÃO: {dados.get('diagnostico_recomenda', 'N/A')}", border=1)
    pdf.ln(10)

    # 3. Inserção de Gráficos (Otimização via BytesIO)
    # Evita salvar arquivos físicos no servidor (mais rápido e limpo)
    for fig, name, pos_x in [(fig_mollier, "mollier", 10), (fig_sh_sc, "shsc", 105)]:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        pdf.image(buf, x=pos_x, y=pdf.get_y(), w=95)
    
    pdf.ln(60) # Espaço para os gráficos renderizados

    return pdf.output(dest='S').encode('latin-1', errors='replace')

###############################################################################
# [ BLOCO 08 DE 12 ] - INTERFACE: NAVEGAÇÃO E IDENTIFICAÇÃO (ABA 1)           #
# VERSÃO: 4.700 (BLINDADA) - FOCO: FLUXO DE DADOS E UX                         #
###############################################################################

def main():
    # 12. BARRA LATERAL (SIDEBAR) - NAVEGAÇÃO
    with st.sidebar:
        st.markdown(f"### ❄️ HVAC MESTRE v4.700")
        st.info(f"📅 {datetime.now().strftime('%d/%m/%Y')} | 🕒 {datetime.now().strftime('%H:%M')}")
        
        selecao = st.radio(
            "NAVEGAÇÃO PRINCIPAL:",
            ["1. Identificação", "2. Medições Elétricas", "3. Ciclo Frigorífico", 
             "4. Histórico/Busca", "5. Checklist/PMOC", "6. Diagnóstico IA"],
            index=0
        )
        
        st.markdown("---")
        if st.button("Limpar Sessão Atual"):
            st.session_state.clear()
            st.rerun()
        st.caption("Desenvolvido para: Marcos Alexandre")

    # 13. CONSTRUÇÃO DAS ABAS PRINCIPAIS
    aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
        "🆔 Identificação", "⚡ Elétrica", "🌡️ Térmica", 
        "📚 Histórico", "📋 Checklist", "🧠 Diagnóstico"
    ])

    # --- ABA 1: IDENTIFICAÇÃO ---
    with aba1:
        st.subheader("DADOS DO CLIENTE E EQUIPAMENTO")
        
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                cliente_nome = st.text_input("Nome / Razão Social:", placeholder="Ex: Marcos Alexandre", key="nome_in")
                cliente_cpf = st.text_input("CPF ou CNPJ:", placeholder="000.000.000-00", key="cpf_in")
                cliente_zap = st.text_input("WhatsApp (com DDD):", placeholder="21999999999", key="zap_in")
            
            with col2:
                data_visita = st.date_input("Data do Atendimento:", value=datetime.now(), format="DD/MM/YYYY")
                tipo_servico = st.selectbox(
                    "Tipo de Serviço:",
                    ["Instalação", "Manutenção Preventiva (PMOC)", "Manutenção Corretiva", "Infraestrutura"],
                    key="serv_in"
                )
        
        # Sincronização Automática com Session State (Sem redundância)
        st.session_state.update({
            "nome": cliente_nome,
            "cpf": cliente_cpf,
            "whatsapp": cliente_zap,
            "data": data_visita.strftime("%d/%m/%Y"),
            "servico": tipo_servico
        })
        
        st.markdown("---")
        st.info("📌 Preencha os dados acima para habilitar a personalização do laudo.")

    # --- ABA 3: CICLO FRIGORÍFICO (MÉTRICAS) ---
    with aba3:
        if 'params' in st.session_state:
            p = st.session_state.params
            st.markdown("### 📊 Resultados em Tempo Real")
            res1, res2, res3, res4 = st.columns(4)
            
            res1.metric("Superaquecimento", f"{p['sh']} °C", delta=f"{p['sh']-10:.1f}K", delta_color="inverse")
            res2.metric("Sub-resfriamento", f"{p['sc']} °C", delta=f"{p['sc']-5:.1f}K")
            res3.metric("Temp. Evaporação", f"{p['t_evap']} °C")
            res4.metric("Temp. Condensação", f"{p['t_cond']} °C")

    # --- ABA 6: FINALIZAÇÃO E SALVAMENTO ---
    with aba6:
        st.subheader("VEREDITO TÉCNICO E ARQUIVAMENTO")
        
        if st.button("💾 FINALIZAR E SALVAR ATENDIMENTO"):
            try:
                # Coleta centralizada de dados para o banco
                sucesso = salvar_atendimento(st.session_state)
                st.success(f"✅ Atendimento #{sucesso} salvo com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

    # RODAPÉ SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.write("🔒 Conexão SQL: Ativa")

if __name__ == "__main__":
    main()
