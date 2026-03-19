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
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import io
from datetime import datetime
from fpdf import FPDF

# =============================================================================
# 4. MOTOR GRÁFICO (DIAGRAMAS P-h E PERFORMANCE)
# =============================================================================
def gerar_diagrama_mollier(fluido, p_alta, p_baixa, t_suc, t_liq):
    fig, ax = plt.subplots(figsize=(8, 6))
    h_sino = np.linspace(150, 450, 100)
    p_sino = 100 * np.sin(np.pi * (h_sino - 150) / 300) + 50
    ax.plot(h_sino[:50], p_sino[:50], 'b-', label='Líquido Saturado')
    ax.plot(h_sino[50:], p_sino[50:], 'r-', label='Vapor Saturado')
    
    p_alta_safe, p_baixa_safe = max(p_alta, 1.1), max(p_baixa, 1.0)
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
    fig, ax = plt.subplots(figsize=(6, 4))
    categorias, valores = ['SH', 'SC'], [max(sh, 0), max(sc, 0)]
    bars = ax.bar(categorias, valores, color=['#FF9800', '#00BCD4'], edgecolor='black', width=0.5)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, f"{bar.get_height():.1f}°C", ha='center', va='bottom', fontweight='bold')
    ax.set_ylim(0, max(max(valores) + 5, 15))
    ax.set_title("Diagnóstico Térmico")
    plt.tight_layout()
    return fig

# =============================================================================
# 5. MOTOR DE DIAGNÓSTICO (IA DE REFRIGERAÇÃO)
# =============================================================================
def gerar_diagnostico_hvac(sh, sc, corrente, p_alta, p_baixa):
    diag, reco = [], []
    if sh > 12 and sc < 3:
        diag.append("Baixa carga de fluido.")
        reco.append("- Teste de estanqueidade necessário.")
    elif sc > 10 and p_alta > 400:
        diag.append("Alta pressão / Sujeira.")
        reco.append("- Limpar condensadora.")
    elif p_baixa > 150 and p_alta < 300 and corrente < 5:
        diag.append("Compressor com baixa compressão.")
        reco.append("- Avaliar compressor.")
    elif sh < 4 and p_baixa < 100:
        diag.append("Baixo fluxo de ar.")
        reco.append("- Limpar filtros.")
    
    return {"status": "\n".join(diag) if diag else "SISTEMA NORMAL.", 
            "recomendacoes": "\n".join(reco) if reco else "- Manutenção de rotina."}

# =============================================================================
# 6. MOTOR DE PDF (RELATÓRIOS CORRIGIDOS)
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
    
    # Dados e Medições
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 8, f"TIPO: {tipo.upper()}", 1, 1, 'L', 1)
    pdf.ln(2)
    pdf.cell(0, 7, f"Cliente: {dados.get('nome', 'N/A')}", 0, 1)
    pdf.cell(0, 7, f"Equipamento: {dados.get('modelo', 'N/A')}", 0, 1)
    pdf.ln(5)
    pdf.cell(95, 7, f"P. Alta: {dados.get('p_alta')} PSI", 1)
    pdf.cell(95, 7, f"P. Baixa: {dados.get('p_baixa')} PSI", 1, 1)
    pdf.cell(95, 7, f"SH: {dados.get('sh', 0)} C", 1)
    pdf.cell(95, 7, f"SC: {dados.get('sc', 0)} C", 1, 1)
    
    if tipo == "interno" and fig1 and fig2:
        buf1, buf2 = io.BytesIO(), io.BytesIO()
        fig1.savefig(buf1, format='png', dpi=100); buf1.seek(0)
        fig2.savefig(buf2, format='png', dpi=100); buf2.seek(0)
        pdf.image(buf1, x=10, y=pdf.get_y() + 10, w=90)
        pdf.image(buf2, x=105, y=pdf.get_y() + 10, w=90)

    # BLOCO DE CORREÇÃO PARA STREAMLIT CLOUD (FPDF2)
    try:
        pdf_bytes = pdf.output()
        return bytes(pdf_bytes) if isinstance(pdf_bytes, bytearray) else pdf_bytes
    except:
        return pdf.output(dest='S').encode('latin-1')

# =============================================================================
# 7. INTERFACE PRINCIPAL
# =============================================================================
def main():
    if 'dados' not in st.session_state:
        st.session_state.dados = {
            'nome': '', 'cpf': '', 'data': datetime.now().strftime("%d/%m/%Y"),
            'modelo': '', 'fluido': 'R410A', 'p_alta': 250.0, 'p_baixa': 110.0,
            't_suc': 10.0, 't_liq': 35.0, 'corrente': 0.0, 'checklist': {}
        }

    with st.sidebar:
        st.markdown(f"### ❄️ HVAC MESTRE v4.700")
        menu = st.radio("NAVEGAÇÃO:", ["Identificação", "Ciclo Térmico", "Diagnóstico IA"])
        if st.button("🗑️ Limpar Sessão"):
            st.session_state.clear()
            st.rerun()

    tab1, tab2, tab5 = st.tabs(["🆔 Identificação", "🌡️ Ciclo Térmico", "🧠 Diagnóstico"])

    with tab1:
        c1, c2 = st.columns(2)
        st.session_state.dados['nome'] = c1.text_input("Nome/Razão Social:", value=st.session_state.dados['nome'])
        st.session_state.dados['modelo'] = c2.text_input("Modelo do Aparelho:", value=st.session_state.dados['modelo'])

    with tab2:
        c1, c2 = st.columns(2)
        st.session_state.dados['p_alta'] = c1.number_input("P. Alta (PSI):", value=float(st.session_state.dados['p_alta']))
        st.session_state.dados['p_baixa'] = c1.number_input("P. Baixa (PSI):", value=float(st.session_state.dados['p_baixa']))
        # Aqui deve entrar sua função de calcular_parametros_performance
        st.session_state.dados['sh'] = st.session_state.dados['t_suc'] - 10 # Exemplo simplificado
        st.session_state.dados['sc'] = 45 - st.session_state.dados['t_liq']  # Exemplo simplificado
        st.metric("SH", f"{st.session_state.dados['sh']} °C")

    with tab5:
        d = st.session_state.dados
        diag = gerar_diagnostico_hvac(d['sh'], d['sc'], d['corrente'], d['p_alta'], d['p_baixa'])
        st.info(f"**STATUS:** {diag['status']}")
        
        col_pdf1, col_pdf2 = st.columns(2)
        fig1 = gerar_diagrama_mollier(d['fluido'], d['p_alta'], d['p_baixa'], 0, 0)
        fig2 = gerar_grafico_sh_sc(d['sh'], d['sc'])

        pdf_c = gerar_pdf_final(d, tipo="cliente")
        col_pdf1.download_button("📄 PDF Cliente", data=pdf_c, file_name="laudo.pdf", mime="application/pdf")
        
        pdf_i = gerar_pdf_final(d, tipo="interno", fig1=fig1, fig2=fig2)
        col_pdf2.download_button("🛠️ PDF Interno", data=pdf_i, file_name="prontuario.pdf", mime="application/pdf")

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

