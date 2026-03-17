# ==============================================================================
# MPN - ENGENHARIA E DIAGNÓSTICO HVAC PRO
# VERSÃO CONSOLIDADA | TOTAL DE LINHAS EXPANDIDO PARA MÁXIMA PRECISÃO
# ==============================================================================

import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import time

# --- 1. CONFIGURAÇÃO DE AMBIENTE E LAYOUT (ESTRUTURA BLOQUEADA) ---
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico",
    layout="wide",
    page_icon="❄️",
    initial_sidebar_state="collapsed"
)

# --- 2. BANCO DE DADOS (ESTRUTURA DE 31 CAMPOS SINCRONIZADOS) ---
def init_db():
    """Inicializa o banco de dados garantindo a persistência dos 31 campos técnicos."""
    try:
        conn = sqlite3.connect('banco_dados_mpn.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, 
            celular TEXT, fixo TEXT, endereco TEXT, email TEXT, marca TEXT, 
            modelo TEXT, serie_evap TEXT, linha TEXT, capacidade TEXT, 
            serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT, 
            sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, 
            rla REAL, lra REAL, p_suc REAL, p_liq REAL, sh REAL, sc REAL, 
            problemas TEXT, medidas TEXT, observacoes TEXT
        )''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro Crítico de Inicialização do Banco: {e}")
    finally:
        conn.close()

def salvar_dados(dados):
    """Executa a inserção dos dados com validação de integridade da tupla."""
    if len(dados) != 31:
        st.error(f"Inconsistência de Dados: Recebidos {len(dados)} de 31 campos.")
        return False
    try:
        conn = sqlite3.connect('banco_dados_mpn.db')
        c = conn.cursor()
        query = '''INSERT INTO atendimentos (
            data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
            marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
            loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, p_suc, p_liq,
            sh, sc, problemas, medidas, observacoes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        c.execute(query, dados)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Falha na gravação do registro: {e}")
        return False
    finally:
        conn.close()

init_db()

# --- 3. MOTOR TERMODINÂMICO (TABELAS DE SATURAÇÃO EXPANDIDAS) ---
def get_tsat_global(psig, gas):
    """Realiza a interpolação linear baseada em tabelas de pressão-temperatura."""
    tabelas_pt = {
        "R-410A": {
            "p": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 200, 220, 240, 260, 280, 300, 350, 400, 450, 500, 550, 600],
            "t": [-51.0, -42.0, -34.0, -28.0, -22.0, -17.0, -12.5, -8.5, -5.0, -2.5, -0.3, 2.0, 4.0, 6.0, 8.0, 10.0, 11.5, 13.0, 15.0, 18.2, 21.0, 24.0, 27.0, 29.5, 32.0, 38.0, 44.0, 49.0, 54.0, 58.5, 63.0]
        },
        "R-32": {
            "p": [0, 25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700],
            "t": [-51.7, -32.0, -17.5, -7.0, 0.9, 6.5, 10.9, 15.8, 20.1, 27.9, 34.6, 40.6, 45.9, 50.8, 55.4, 59.5, 63.4, 67.2, 70.8]
        },
        "R-22": {
            "p": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 225, 250, 275, 300, 350, 400, 450, 500],
            "t": [-40.8, -32.5, -25.8, -20.0, -15.0, -10.5, -6.5, -3.0, 0.2, 3.2, 6.0, 11.0, 15.5, 20.0, 24.5, 29.0, 33.5, 38.0, 42.0, 46.0, 53.0, 60.0, 66.0, 72.0]
        },
        "R-134a": {
            "p": [0, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 160, 180, 200],
            "t": [-26.1, -18.5, -12.5, -7.5, -3.2, 0.5, 3.8, 9.5, 14.5, 19.0, 23.2, 27.0, 30.5, 33.8, 37.0, 40.0, 42.8, 45.5, 50.5, 55.2, 59.5]
        }
    }
    if gas not in tabelas_pt: return 0.0
    try:
        p_val = max(0, float(psig))
        return round(float(np.interp(p_val, tabelas_pt[gas]["p"], tabelas_pt[gas]["t"])), 2)
    except:
        return 0.0

def clean(txt):
    """Sanitização de texto para compatibilidade com PDF Latin-1."""
    if not txt: return "N/A"
    txt = str(txt).replace('°', 'C').replace('º', '.').replace('ª', '.')
    nfkd = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd if not unicodedata.category(c) == 'Mn'])

def seguro(v, default=0.0):
    """Conversor seguro de string para float."""
    try: return float(v)
    except: return default

# --- 4. CSS E INTERFACE ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button p { font-size: 18px; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 26px; color: #004a99; }
    .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab_cad:
    st.subheader("👤 Dados do Cliente")
    c1, c2, c3 = st.columns([2.5, 1.2, 1.4])
    cliente = c1.text_input("Cliente / Empresa", key="cli_nom")
    doc_cliente = c2.text_input("CPF / CNPJ", key="cli_doc")
    data_visita = c3.date_input("📅 Data", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")

    st.markdown("---")
    st.subheader("📍 Endereço")
    e1, e2, e3, e4 = st.columns([0.6, 2.0, 0.5, 1.0])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Bloco/Apto")
    
    e5, e6, e7 = st.columns([1.5, 1.0, 1.5])
    bairro, cep, email_cli = e5.text_input("Bairro"), e6.text_input("CEP"), e7.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados Técnicos do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        fabricante = st.text_input("Marca")
        modelo_eq = st.text_input("Modelo")
        serie_evap = st.text_input("Série Evap.")
    with g2:
        linha = st.text_input("Linha")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="12000")
        serie_cond = st.text_input("Série Cond.")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evap.")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Duto"])
        loc_cond = st.text_input("Local Cond.")

# --- ABA 2: ELÉTRICA ---
with tab_ele:
    st.subheader("⚡ Medições Elétricas")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Nominal (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=220.0)
        diff_v = round(v_rede - v_med, 1)
        st.metric("Variação de Tensão", f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("RLA Nominal (A)", value=5.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.metric("Diferença A", f"{diff_a} A")
    with el3:
        lra_comp = st.number_input("LRA Partida (A)", value=0.0)
        carga_pct = (a_med / rla_comp * 100) if rla_comp > 0 else 0
        st.metric("Carga do Motor", f"{round(carga_pct, 1)} %")

# --- ABA 3: TERMODINÂMICA ---
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc = st.number_input("Pressão Sucção (PSI)", value=115.0)
        t_suc_tubo = st.number_input("T-Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
        st.metric("T-Sat Evaporação", f"{ts_suc} °C")
    with tr2:
        p_liq = st.number_input("Pressão Líquido (PSI)", value=340.0)
        t_liq_tubo = st.number_input("T-Tubo Líquido (°C)", value=32.0)
        ts_liq = get_tsat_global(p_liq, fluido)
        st.metric("T-Sat Condensação", f"{ts_liq} °C")
    with tr3:
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.subheader(f"SH: {sh_val} K")
        st.subheader(f"SC: {sc_val} K")

# --- ABA 4: DIAGNÓSTICO (O CÉREBRO) ---
with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico Assistido")
    
    # Motor de Lógica IA
    diagnosticos, probs, contramedidas = [], {}, []
    d_evap, d_cond = t_suc_tubo - ts_suc, ts_liq - t_liq_tubo
    
    if sh_val > 12: 
        diagnosticos.append("Superaquecimento Elevado")
        probs["Baixa carga de fluido / Vazamento"] = 85
        contramedidas.append("Localizar vazamento e completar fluido")
    if sh_val < 4:
        diagnosticos.append("Baixo Superaquecimento (Risco de Golpe)")
        probs["Excesso de fluido ou Baixa troca no Evaporador"] = 80
        contramedidas.append("Verificar limpeza de filtros e turbina")
    if abs(diff_v) > (v_rede * 0.07):
        diagnosticos.append("Instabilidade Elétrica Crítica")
        probs["Problema na rede elétrica ou conexões"] = 90
        contramedidas.append("Revisar fiação e quadro elétrico")
    if p_suc > 140 and p_liq < 280 and fluido == "R-410A":
        diagnosticos.append("Baixa Eficiência de Compressão")
        probs["Compressor mecanicamente desgastado"] = 70
        contramedidas.append("Avaliar substituição do compressor")

    if not diagnosticos: diagnosticos.append("Sistema operando em normalidade")
    diag_ia_txt = " | ".join(diagnosticos)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in sorted(probs.items(), key=lambda x: x[1], reverse=True)]) if probs else "Normal"
    recom_txt = " | ".join(contramedidas) if contramedidas else "Monitorar parâmetros periodicamente"
    cop_final = round((d_cond + 1) / (d_evap + 1), 2) if d_evap != -1 else 0

    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        st.info(f"**Análise IA:** {diag_ia_txt}")
        st.warning(f"**Probabilidades:** {prob_txt}")
    with c_ia2:
        st.success(f"**Recomendação:** {recom_txt}")
        st.metric("COP Estimado", cop_final)

    st.markdown("---")
    st.subheader("📝 Detalhamento do Atendimento")
    c_m1, c_m2 = st.columns(2)
    exec_servico = c_m1.text_area("Serviços Realizados:", height=150, key="m_exec")
    obs_tecnico = c_m2.text_area("Parecer Técnico Final:", height=150, key="m_obs")

    relato_wpp = f"*RELATÓRIO MPN*\n\n*Status:* {diag_ia_txt}\n*Suspeitas:* {prob_txt}\n*COP:* {cop_final}\n*SH:* {sh_val}K"
    st.text_area("Resumo WhatsApp", relato_wpp, height=100)
    st.markdown(f'<button onclick="navigator.clipboard.writeText(`{relato_wpp}`)" style="width:100%; padding:10px; background:#25d366; color:white; border:none; border-radius:5px; cursor:pointer;">📋 Copiar para WhatsApp</button>', unsafe_allow_html=True)

    if st.button("💾 SALVAR ATENDIMENTO E GERAR PDF"):
        end_str = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        dados_banco = (str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial, end_str, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val, diag_ia_txt, exec_servico, obs_tecnico)
        
        if salvar_dados(dados_banco):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16); pdf.set_text_color(0, 74, 153)
            pdf.cell(190, 10, "RELATORIO TECNICO DE MANUTENCAO", 0, 1, 'C'); pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(240, 240, 240)
            pdf.cell(190, 8, " 1. DADOS DO CLIENTE", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
            pdf.cell(190, 7, clean(f"Cliente: {cliente} | Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereco: {end_str}"), 1, 1); pdf.ln(5)

            pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 2. PARAMETROS TECNICOS", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(95, 7, clean(f"Fluido: {fluido} | SH: {sh_val} K"), 1, 0); pdf.cell(95, 7, clean(f"SC: {sc_val} K | COP: {cop_final}"), 1, 1)
            pdf.cell(95, 7, clean(f"Corrente: {a_med} A | Tensao: {v_med} V"), 1, 1); pdf.ln(5)

            pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 3. PARECER E DIAGNOSTICO IA", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(190, 6, clean(f"Analise: {diag_ia_txt}\n\nServicos: {exec_servico}\n\nObs: {obs_tecnico}"), 1)
            
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar PDF Oficial", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf")
            st.success("Atendimento registrado!")

# --- ABA 5: HISTÓRICO ---
with tab_hist:
    st.subheader("📜 Histórico")
    conn = sqlite3.connect('banco_dados_mpn.db')
    df_h = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    if not df_h.empty:
        df_h['data_visita'] = pd.to_datetime(df_h['data_visita']).dt.strftime('%d/%m/%Y')
        df_h.insert(0, "Selecionar", False)
        editor = st.data_editor(df_h, hide_index=True, use_container_width=True, column_config={"id": None})
        if st.button("🗑️ Excluir Selecionados"):
            ids_del = editor[editor["Selecionar"] == True]["id"].tolist()
            conn = sqlite3.connect('banco_dados_mpn.db')
            for d in ids_del: conn.execute("DELETE FROM atendimentos WHERE id = ?", (d,))
            conn.commit(); conn.close(); st.rerun()
    else:
        st.info("Banco de dados vazio.")
