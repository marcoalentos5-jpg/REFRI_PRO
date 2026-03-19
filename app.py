import streamlit as st
import pandas as pd
import sqlite3
import json
import numpy as np
import matplotlib.pyplot as plt
import io
import os
from datetime import datetime
from fpdf import FPDF

# =============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE E LAYOUT (BLINDAGEM DE INTERFACE)
# =============================================================================
st.set_page_config(
    page_title="HVAC Mestre Pro v4.700",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para manter o padrão visual de engenharia
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e6ed; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e0e6ed; border-radius: 5px 5px 0px 0px; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #004a99 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# 2. MOTOR DE BANCO DE DADOS (SQLITE3 BLINDADO)
# =============================================================================
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
        dados.get('nome', 'N/A'), dados.get('cpf', '000.000.000-00'), 
        dados.get('data', ''), dados.get('modelo', 'Split Inverter'),
        dados.get('fluido', 'R410A'), dados.get('p_alta', 0.0), 
        dados.get('p_baixa', 0.0), dados.get('t_suc', 0.0), 
        dados.get('t_liq', 0.0), dados.get('sh', 0.0), 
        dados.get('sc', 0.0), dados.get('corrente', 0.0),
        json.dumps(dados.get('checklist', {})), 
        dados.get('diagnostico', 'Sem Diagnóstico')
    )
    cursor.execute(query, params)
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id

# =============================================================================
# 3. MOTOR TÉRMICO (FÓRMULAS ASHRAE & REGRESSÃO)
# =============================================================================
def calcular_temperatura_saturacao(pressao_psi, fluido):
    # Coeficientes de regressão parabólica para resposta em tempo real
    coefs = {
        "R410A": {"a": 0.0001, "b": 0.15, "c": -30.0},
        "R134a": {"a": 0.0002, "b": 0.25, "c": -20.0},
        "R22":   {"a": 0.00015, "b": 0.20, "c": -25.0}
    }
    c = coefs.get(fluido, coefs["R410A"])
    temp_sat = (c['a'] * (pressao_psi**2)) + (c['b'] * pressao_psi) + c['c']
    return round(temp_sat, 2)

def calcular_parametros_performance(dados):
    p_baixa = dados.get('p_baixa', 0.0)
    p_alta = dados.get('p_alta', 0.0)
    t_suc = dados.get('t_suc', 0.0)
    t_liq = dados.get('t_liq', 0.0)
    fluido = dados.get('fluido', 'R410A')
    
    t_evap = calcular_temperatura_saturacao(p_baixa, fluido)
    t_cond = calcular_temperatura_saturacao(p_alta, fluido)
    
    sh = round(t_suc - t_evap, 2)
    sc = round(t_cond - t_liq, 2)
    
    return {
        "t_evap": t_evap,
        "t_cond": t_cond,
        "sh": sh,
        "sc": sc
    }
    # =============================================================================
# 4. MOTOR GRÁFICO (DIAGRAMAS P-h E PERFORMANCE)
# =============================================================================
def gerar_diagrama_mollier(fluido, p_alta, p_baixa, t_suc, t_liq):
    """Gera o gráfico de Pressão vs Entalpia (P-h) para análise interna"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Simulação da Curva de Saturação (Sino)
    h_sino = np.linspace(150, 450, 100)
    p_sino = 100 * np.sin(np.pi * (h_sino - 150) / 300) + 50
    
    ax.plot(h_sino[:50], p_sino[:50], 'b-', label='Líquido Saturado')
    ax.plot(h_sino[50:], p_sino[50:], 'r-', label='Vapor Saturado')
    
    # Blindagem para escala Logarítmica (evita crash com valor zero)
    p_alta_safe = max(p_alta, 1.1)
    p_baixa_safe = max(p_baixa, 1.0)
    
    # Pontos do Ciclo Real
    pontos_h = [400, 450, 200, 200, 400]
    pontos_p = [p_baixa_safe, p_alta_safe, p_alta_safe, p_baixa_safe, p_baixa_safe]
    
    ax.plot(pontos_h, pontos_p, 'k-o', linewidth=2, label='Ciclo de Refrigeração')
    ax.set_yscale('log')
    ax.set_title(f"Diagrama P-h: {fluido}", fontsize=12, fontweight='bold')
    ax.set_xlabel("Entalpia (kJ/kg)")
    ax.set_ylabel("Pressão (PSI)")
    ax.grid(True, which="both", ls="-", alpha=0.3)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig

def gerar_grafico_sh_sc(sh, sc):
    """Gera gráfico de barras para diagnóstico rápido"""
    fig, ax = plt.subplots(figsize=(6, 4))
    categorias = ['Superaq. (SH)', 'Subresf. (SC)']
    valores = [max(sh, 0), max(sc, 0)]
    
    bars = ax.bar(categorias, valores, color=['#FF9800', '#00BCD4'], edgecolor='black', width=0.5)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f"{yval:.1f}°C", 
                ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylim(0, max(max(valores) + 5, 15))
    ax.set_ylabel("Temperatura (°C)")
    ax.set_title("Diagnóstico Térmico", fontsize=10)
    plt.tight_layout()
    return fig

# =============================================================================
# 5. MOTOR DE DIAGNÓSTICO (IA DE REFRIGERAÇÃO)
# =============================================================================
def gerar_diagnostico_hvac(sh, sc, corrente, p_alta, p_baixa):
    diag, reco = [], []
    
    if sh > 12 and sc < 3:
        diag.append("SINTOMA: Baixa carga de fluido refrigerante.")
        reco.append("- Realizar teste de estanqueidade; Verificar vazamentos.")
    elif sc > 10 and p_alta > 400:
        diag.append("SINTOMA: Alta pressão / Excesso de fluido ou sujeira.")
        reco.append("- Limpar condensadora; Checar ventiladores externos.")
    elif p_baixa > 150 and p_alta < 300 and corrente < 5:
        diag.append("SINTOMA: Compressor com baixa compressão (Bypass).")
        reco.append("- Avaliar válvulas internas ou substituição do compressor.")
    elif sh < 4 and p_baixa < 100:
        diag.append("SINTOMA: Baixo fluxo de ar ou congelamento.")
        reco.append("- Limpar filtros e serpentina da evaporadora.")
    
    if not diag:
        diag.append("SISTEMA OPERANDO EM PARÂMETROS NOMINAIS.")
        reco.append("- Realizar manutenção preventiva de rotina.")

    return {"status": "\n".join(diag), "recomendacoes": "\n".join(reco)}

# =============================================================================
# 6. MOTOR DE PDF (RELATÓRIOS CLIENTE E INTERNO)
# =============================================================================
class GeradorPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'RELATÓRIO TÉCNICO HVAC PRO', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'MARCOS ALEXANDRE - ENGENHARIA', 0, 1, 'C')
        self.ln(10)

def gerar_pdf_final(dados, tipo="cliente", fig1=None, fig2=None):
    pdf = GeradorPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Seção 1: Dados
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, f"TIPO: {tipo.upper()}", 1, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Cliente: {dados.get('nome')}", 0, 1)
    pdf.cell(0, 7, f"Data: {dados.get('data')}", 0, 1)
    pdf.cell(0, 7, f"Equipamento: {dados.get('modelo')}", 0, 1)
    
    # Seção 2: Medições
    pdf.ln(5)
    pdf.cell(95, 7, f"P. Alta: {dados.get('p_alta')} PSI", 1)
    pdf.cell(95, 7, f"P. Baixa: {dados.get('p_baixa')} PSI", 1, 1)
    pdf.cell(95, 7, f"SH: {dados.get('sh')} C", 1)
    pdf.cell(95, 7, f"SC: {dados.get('sc')} C", 1, 1)
    
    if tipo == "interno" and fig1 and fig2:
        # Uso de Buffer para não criar arquivos lixo no servidor
        buf1, buf2 = io.BytesIO(), io.BytesIO()
        fig1.savefig(buf1, format='png', dpi=100)
        fig2.savefig(buf2, format='png', dpi=100)
        buf1.seek(0); buf2.seek(0)
        
        pdf.image(buf1, x=10, y=pdf.get_y() + 10, w=90)
        pdf.image(buf2, x=105, y=pdf.get_y() + 10, w=90)

    return pdf.output(dest='S').encode('latin-1', errors='replace')

# =============================================================================
# 7. INTERFACE PRINCIPAL (STREAMLIT NAVEGAÇÃO)
# =============================================================================
def main():
    # Inicialização do estado de sessão para evitar erros de variável vazia
    if 'dados' not in st.session_state:
        st.session_state.dados = {
            'nome': '', 'cpf': '', 'data': datetime.now().strftime("%d/%m/%Y"),
            'modelo': '', 'fluido': 'R410A', 'p_alta': 250.0, 'p_baixa': 110.0,
            't_suc': 10.0, 't_liq': 35.0, 'corrente': 0.0, 'checklist': {}
        }

    # --- SIDEBAR: NAVEGAÇÃO E LOGO ---
    with st.sidebar:
        st.markdown(f"### ❄️ HVAC MESTRE v4.700")
        st.info(f"📅 Data: {datetime.now().strftime('%d/%m/%Y')} | 🕒 {datetime.now().strftime('%H:%M')}")
        
        menu = st.radio(
            "NAVEGAÇÃO PRINCIPAL:",
            ["1. Identificação", "2. Ciclo Térmico", "3. Checklist/PMOC", "4. Histórico", "5. Diagnóstico IA"],
            index=0
        )
        
        st.markdown("---")
        if st.button("🗑️ Limpar Atendimento Atual"):
            st.session_state.clear()
            st.rerun()
        st.caption("Desenvolvedor Responsável: Marcos Alexandre")

    # --- CONSTRUÇÃO DAS ABAS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🆔 Identificação", "🌡️ Ciclo Térmico", "📋 Checklist", "📚 Histórico", "🧠 Diagnóstico"
    ])

    # --- ABA 1: IDENTIFICAÇÃO ---
    with tab1:
        st.subheader("Dados do Cliente e Equipamento")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.dados['nome'] = st.text_input("Nome/Razão Social:", value=st.session_state.dados['nome'])
            st.session_state.dados['cpf'] = st.text_input("CPF ou CNPJ:", value=st.session_state.dados['cpf'])
        with col2:
            st.session_state.dados['modelo'] = st.text_input("Modelo do Aparelho:", placeholder="Ex: Split 12k BTU")
            st.session_state.dados['fluido'] = st.selectbox("Fluido Refrigerante:", ["R410A", "R134a", "R22", "R404A"])

    # --- ABA 2: CICLO TÉRMICO (CÁLCULOS REAL-TIME) ---
    with tab2:
        st.subheader("Medições de Pressão e Temperatura")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.dados['p_alta'] = st.number_input("Pressão de Alta (PSI):", value=st.session_state.dados['p_alta'])
            st.session_state.dados['p_baixa'] = st.number_input("Pressão de Baixa (PSI):", value=st.session_state.dados['p_baixa'])
        with col2:
            st.session_state.dados['t_suc'] = st.number_input("Temperatura de Sucção (°C):", value=st.session_state.dados['t_suc'])
            st.session_state.dados['t_liq'] = st.number_input("Temperatura de Líquido (°C):", value=st.session_state.dados['t_liq'])

        # PROCESSAMENTO TÉRMICO
        res = calcular_parametros_performance(st.session_state.dados)
        st.session_state.dados.update(res) # Atualiza SH, SC, T_evap, T_cond

        st.markdown("---")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Superaquecimento", f"{res['sh']} °C", delta="-2K" if res['sh'] > 12 else "OK")
        m2.metric("Sub-resfriamento", f"{res['sc']} °C")
        m3.metric("Temp. Evaporação", f"{res['t_evap']} °C")
        m4.metric("Temp. Condensação", f"{res['t_cond']} °C")

    # --- ABA 5: DIAGNÓSTICO E SALVAMENTO ---
    with tab5:
        st.subheader("Análise de IA e Fechamento")
        diag = gerar_diagnostico_hvac(
            st.session_state.dados['sh'], st.session_state.dados['sc'], 
            st.session_state.dados['corrente'], st.session_state.dados['p_alta'], 
            st.session_state.dados['p_baixa']
        )
        st.session_state.dados['diagnostico'] = diag['status']
        
        st.info(f"**STATUS DO SISTEMA:**\n\n{diag['status']}")
        st.warning(f"**PLANO DE AÇÃO:**\n\n{diag['recomendacoes']}")

        if st.button("💾 FINALIZAR E SALVAR NO BANCO"):
            try:
                novo_id = salvar_atendimento(st.session_state.dados)
                st.success(f"✅ Atendimento #{novo_id} salvo com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")

        # BOTÕES DE PDF
        st.markdown("---")
        col_pdf1, col_pdf2 = st.columns(2)
        
        # Gerar Gráficos para o PDF Interno
        fig1 = gerar_diagrama_mollier(st.session_state.dados['fluido'], st.session_state.dados['p_alta'], st.session_state.dados['p_baixa'], 0, 0)
        fig2 = gerar_grafico_sh_sc(st.session_state.dados['sh'], st.session_state.dados['sc'])

        pdf_c = gerar_pdf_final(st.session_state.dados, tipo="cliente")
        col_pdf1.download_button("📄 Baixar PDF do Cliente", data=pdf_c, file_name="laudo_cliente.pdf", mime="application/pdf")

        pdf_i = gerar_pdf_final(st.session_state.dados, tipo="interno", fig1=fig1, fig2=fig2)
        col_pdf2.download_button("🛠️ Baixar Prontuário Interno", data=pdf_i, file_name="prontuario_interno.pdf", mime="application/pdf")

# EXECUÇÃO DO APP
if __name__ == "__main__":
    main()

# =============================================================================
# 9. MOTOR ELÉTRICO E ANÁLISE DE CONSUMO (BLOCO 09)
# =============================================================================

def calcular_eficiencia_eletrica(tensao, corrente, potencia_nominal, cos_phi=0.9):
    """Calcula a potência real consumida e o desvio da nominal"""
    # P = V * I * cos_phi (Para sistemas monofásicos/Inverter)
    potencia_real = (tensao * corrente * cos_phi) / 1000 # Resultado em kW
    
    # Cálculo de Desvio de Consumo
    if potencia_nominal > 0:
        desvio = ((potencia_real * 1000) / potencia_nominal) - 1
        status_consumo = "Normal" if -0.15 <= desvio <= 0.15 else "Anormal"
    else:
        desvio = 0
        status_consumo = "N/A"
        
    return {
        "p_real_kw": round(potencia_real, 2),
        "desvio_percent": round(desvio * 100, 2),
        "status_eletrico": status_consumo
    }

# --- INTEGRAÇÃO NA ABA 2 (ADIÇÃO AO FLUXO EXISTENTE) ---
with tab2:
    st.markdown("---")
    st.subheader("⚡ Parâmetros Elétricos e Eficiência")
    
    col_el1, col_el2, col_el3 = st.columns(3)
    
    with col_el1:
        tensao = st.selectbox("Tensão de Alimentação (V):", [220, 127, 380, 440], index=0)
        st.session_state.dados['tensao'] = tensao
    
    with col_el2:
        corrente = st.number_input("Corrente Medida (A):", min_value=0.0, step=0.1, value=float(st.session_state.dados.get('corrente', 0.0)))
        st.session_state.dados['corrente'] = corrente
        
    with col_el3:
        pot_nom = st.number_input("Potência Nominal (W):", min_value=0, step=50, help="Ver na etiqueta do fabricante")
        st.session_state.dados['potencia_nominal'] = pot_nom

    # Processamento Elétrico
    eletrico = calcular_eficiencia_eletrica(tensao, corrente, pot_nom)
    st.session_state.dados.update(eletrico)

    # Exibição de Resultados Elétricos
    st.markdown("#### Análise de Consumo Energético")
    c_res1, c_res2, c_res3 = st.columns(3)
    
    c_res1.metric("Potência Real", f"{eletrico['p_real_kw']} kW")
    
    # Delta colorido: Vermelho se estiver consumindo muito acima do nominal
    delta_cor = "normal" if abs(eletrico['desvio_percent']) < 15 else "inverse"
    c_res2.metric("Desvio vs Nominal", f"{eletrico['desvio_percent']}%", delta=f"{eletrico['status_eletrico']}", delta_color=delta_cor)
    
    # Estimativa de Custo Mensal (Baseado em 8h/dia e R$ 0,90/kWh)
    custo_estimado = eletrico['p_real_kw'] * 8 * 30 * 0.90
    c_res3.metric("Custo Mensal Est.", f"R$ {custo_estimado:.2f}", help="Estimativa baseada em 8h diárias")

    # Alerta de Segurança Elétrica
    if corrente > 0 and tensao > 0:
        if eletrico['desvio_percent'] > 25:
            st.error("⚠️ ALERTA: Consumo elétrico muito acima do nominal. Verifique possível travamento mecânico ou fuga de corrente.")
        elif eletrico['desvio_percent'] < -40 and corrente > 0.5:
            st.warning("⚠️ AVISO: Consumo muito abaixo do nominal. Pode indicar baixa carga de fluido ou compressor sem compressão.")

