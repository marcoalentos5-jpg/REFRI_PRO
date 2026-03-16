import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata
import io
import urllib.parse

# =========================================================
# 1. CONFIGURAÇÃO, DESIGN E BLINDAGEM VISUAL (20PX)
# =========================================================
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico Pro", 
    layout="wide", 
    page_icon="❄️"
)

# Estilização Profissional Corrigida (Sem erros de sintaxe CSS)
st.markdown("""
<style>
    /* Abas em 20px - Conforme prioridade absoluta */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: bold;
        color: #1E3A8A;
    }
    /* Botões Profissionais */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        background-color: #1E3A8A;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        border: 1px solid white;
    }
    /* Campos de Entrada */
    div[data-baseweb="input"] > div {
        background-color: #F8FAFC;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. MOTOR DE DADOS E UTILITÁRIOS TÉCNICOS
# =========================================================
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def clean(txt):
    """Limpeza rigorosa para evitar erros de codificação no PDF (latin-1)"""
    if not txt: return "N/A"
    mapa = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ã':'a','õ':'o','ç':'c','°':'C','º':'.','ª':'.'}
    res = str(txt)
    for k, v in mapa.items(): res = res.replace(k, v)
    return res.encode('ascii', 'ignore').decode('ascii')

def init_db():
    """Inicialização robusta do banco SQLite com todos os campos da evolução"""
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, celular TEXT, fixo TEXT,
        endereco TEXT, email TEXT, marca TEXT, modelo TEXT, serie_evap TEXT, linha TEXT, 
        capacidade TEXT, serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT, 
        sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, rla REAL, lra REAL,
        p_suc REAL, p_liq REAL, sh REAL, sc REAL, problemas TEXT, medidas TEXT, observacoes TEXT
    )''')
    conn.commit()
    conn.close()

def salvar_dados(dados):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''INSERT INTO atendimentos (
        data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
        marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
        loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, p_suc, p_liq,
        sh, sc, problemas, medidas, observacoes
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados)
    conn.commit()
    conn.close()

init_db()

# =========================================================
# 3. INTERFACE - INÍCIO E ABA IDENTIFICAÇÃO (BLINDADA)
# =========================================================
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# Continuação da Aba Identificação (Finalização da Montagem)
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Estr."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    bairro = e4.text_input("Bairro")
    email_cli = e5.text_input("E-mail")

    # Blindagem de Escopo: Variável definida fora de qualquer condicional
    endereco_completo = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"

    st.markdown("---")
    g1, g2, g3, g4 = st.columns(4)
    fabricante = g1.text_input("Marca/Fabricante")
    modelo_eq = g2.text_input("Modelo/Capacidade")
    tecnologia = g3.selectbox("Tecnologia", ["Inverter", "On-Off"])
    fluido = g4.selectbox("Fluido Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
    
    # Placeholders para campos técnicos do banco (vazios se não preenchidos)
    celular = e4.text_input("Celular/Contato")
    tel_residencial = ""
    serie_evap, linha, cap_digitada, serie_cond, loc_evap, tipo_eq, loc_cond = "", "", "", "", "", "", ""

# =========================================================
# 4. ABA ELÉTRICA - CÁLCULOS DE CARGA E REDE
# =========================================================
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos e Proteção")
    el1, el2, el3 = st.columns(3)
    
    v_rede = el1.number_input("Tensão Nominal Rede (V)", value=220.0)
    v_med = el1.number_input("Tensão Medida no Borne (V)", value=220.0)
    
    rla_comp = el2.number_input("Corrente Nominal (RLA - A)", value=1.0)
    a_med = el2.number_input("Corrente Medida (A)", value=0.0)
    
    lra_comp = el3.number_input("Corrente de Partida (LRA - A)", value=0.0)
    
    # Cálculo em tempo real de variação de tensão e carga
    diff_v = abs(v_rede - v_med)
    percent_carga = (a_med / rla_comp * 100) if rla_comp > 0 else 0
    
    st.markdown("---")
    res1, res2 = st.columns(2)
    if diff_v > (v_rede * 0.1):
        res1.error(f"⚠️ Variação de Tensão Crítica: {diff_v}V")
    else:
        res1.success(f"✅ Tensão Estável: {v_med}V")
        
    if percent_carga > 105:
        res2.warning(f"🚨 Sobreloja: {percent_carga:.1f}% da RLA")
    else:
        res2.info(f"📊 Carga do Compressor: {percent_carga:.1f}%")

# =========================================================
# 5. ABA TERMODINÂMICA - MOTOR DE CÁLCULO SH / SC
# =========================================================
with tab_termo:
    st.subheader("🌡️ Análise de Ciclo Frigorífico")
    
    def get_tsat_preciso(psig, gas):
        """Tabela de saturação revisada para precisão absoluta"""
        ancoras = {
            "R-410A": {"p": [0, 50, 118, 150, 34

        31.0, 43.5, 53.7]}
        }
        if gas not in ancoras or psig is None: return 0.0
        return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

    tr1, tr2, tr3 = st.columns(3)
    p_suc = tr1.number_input("P. Sucção (PSI)", value=118.0)
    t_suc_tubo = tr1.number_input("T. Tubo Sucção (°C)", value=12.0)
    ts_suc = get_tsat_preciso(p_suc, fluido)
    sh_val = round(t_suc_tubo - ts_suc, 1)

    p_liq = tr2.number_input("P. Líquido (PSI)", value=345.0)
    t_liq_tubo = tr2.number_input("T. Tubo Líquido (°C)", value=30.0)
    ts_liq = get_tsat_preciso(p_liq, fluido)
    sc_val = round(ts_liq - t_liq_tubo, 1)

    with tr3:
        st.metric("S.H. (Superaquecimento)", f"{sh_val} K", delta="Ideal: 5-12K", delta_color="normal")
        st.metric("S.C. (Subresfriamento)", f"{sc_val} K", delta="Ideal: 5-8K", delta_color="normal")

# =========================================================
# 6. ABA DIAGNÓSTICO - INTELIGÊNCIA ARTIFICIAL E LAUDO
# =========================================================
with tab_diag:
    st.header("🤖 Diagnóstico e Resolução")
    
    # Lógica de Diagnóstico Automático
    diagnosticos = []
    if sh_val < 5: diagnosticos.append("⚠️ Possível excesso de fluido ou baixa carga térmica.")
    elif sh_val > 12: diagnosticos.append("⚠️ Possível falta de fluido ou restrição na expansão.")
    
    if sc_val < 5: diagnosticos.append("⚠️ Condensação insuficiente ou falta de carga.")
    elif sc_val > 8: diagnosticos.append("⚠️ Sobrecarga de fluido ou obstrução no condensador.")

    if not diagnosticos: diagnosticos.append("✅ Sistema operando com parâmetros ideais.")
    
    diag_ia_resultado = " | ".join(diagnosticos)
    obs_tecnico = st.text_area("Observações Adicionais", placeholder="Descreva detalhes do atendimento...")

    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        # WhatsApp com formatação dinâmica
        num_wpp = "".join(filter(str.isdigit, whatsapp))
        msg = urllib.parse.quote(f"*MPN ENGENHARIA - LAUDO*\n\nCliente: {cliente}\nStatus: {diag_ia_resultado}\nSH: {sh_val}K | SC: {sc_val}K")
        st.markdown(f'<a href="https://wa.me/55{num_wpp}?text={msg}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">🟢 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

    with c_btn2:
        if st.button("📑 Gerar Laudo PDF e Salvar"):
            # Salvar no Banco
            dados = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, endereco_completo, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, diag_ia_resultado, "Verificar parâmetros", obs_tecnico)
            salvar_dados(dados)
            
            # Geração do PDF Profissional
            pdf = FPDF()
            pdf.add_page()
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 15, "RELATÓRIO TÉCNICO DE MANUTENÇÃO", 1, 1, 'C', True)
            
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 1. IDENTIFICAÇÃO", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(110, 7, clean(f"Cliente: {cliente}"), 1, 0)
            pdf.cell(80, 7, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereço: {endereco_completo}"), 1, 1)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 2. ANÁLISE TERMODINÂMICA", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(47.5, 7, f"Fluido: {fluido}", 1, 0)
            pdf.cell(47.5, 7, f"P. Suc: {p_suc} PSI", 1, 0)
            pdf.cell(47.5, 7, f"SH: {sh_val} K", 1, 0)
            pdf.cell(47.5, 7, f"SC: {sc_val} K", 1, 1)

            pdf.ln(5)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 3. PARECER DO DIAGNÓSTICO IA", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(190, 7, clean(diag_ia_resultado), 1)

            st.download_button("📥 Baixar Laudo PDF", data=pdf.output(dest='S').encode('latin-1', 'ignore'), file_name=f"Laudo_{cliente}.pdf", mime="application/pdf")
            st.success("✅ Atendimento registrado com sucesso!")

# =========================================================
# 7. ABA HISTÓRICO - GESTÃO DE DADOS
# =========================================================
with tab_hist:
    st.subheader("📜 Histórico Recente")
    conn = sqlite3.connect('banco_dados.db')
    try:
        df_hist = pd.read_sql_query("SELECT id, data_visita, cliente, sh, sc, problemas FROM atendimentos ORDER BY id DESC", conn)
        if not df_hist.empty:
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado.")
    except: st.error("Erro ao carregar banco de dados.")
    finally: conn.close()
