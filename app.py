# ==============================================================================
# MPN - ENGENHARIA E DIAGNÓSTICO HVAC PRO
# PARTE 1: NÚCLEO, SEGURANÇA E PERSISTÊNCIA DE DADOS
# ==============================================================================

import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata
import os

# --- 1. CONFIGURAÇÃO DE AMBIENTE (LAYOUT BLOQUEADO) ---
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico",
    layout="wide",
    page_icon="❄️",
    initial_sidebar_state="collapsed"
)

# Caminho absoluto para o banco de dados não sumir
DB_PATH = os.path.join(os.getcwd(), 'banco_dados_mpn.db')

# --- 2. BANCO DE DADOS (31 CAMPOS) ---
def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
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
        st.error(f"Erro ao inicializar banco: {e}")
    finally:
        conn.close()

def salvar_dados(dados):
    if len(dados) != 31:
        st.error(f"Erro de integridade: {len(dados)}/31 campos.")
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
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
        st.error(f"Erro na gravação: {e}")
        return False
    finally:
        conn.close()

init_db()

# --- 3. MOTOR TERMODINÂMICO (TABELAS PT) ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {
            "p": [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 500, 600],
            "t": [-51.0, -34.0, -22.0, -12.5, -5.0, -0.3, 4.0, 8.0, 11.5, 15.0, 18.2, 25.0, 32.0, 38.0, 44.0, 54.0, 63.0]
        },
        "R-32": {
            "p": [0, 50, 100, 150, 200, 300, 400, 500, 600, 700],
            "t": [-51.7, -17.5, 0.9, 10.9, 20.1, 34.6, 45.9, 55.4, 63.4, 70.8]
        },
        "R-22": {
            "p": [0, 30, 60, 90, 120, 150, 200, 250, 300, 400, 500],
            "t": [-40.8, -20.0, -6.5, 3.2, 11.0, 18.5, 29.0, 38.0, 46.0, 60.0, 72.0]
        }
    }
    if gas not in ancoras: return 0.0
    return round(float(np.interp(max(0, float(psig)), ancoras[gas]["p"], ancoras[gas]["t"])), 2)

def clean(txt):
    if not txt: return "N/A"
    txt = str(txt).replace('°', 'C').replace('º', '.').replace('ª', '.')
    nfkd = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd if not unicodedata.category(c) == 'Mn'])

# --- 4. CSS E TÍTULO ---
st.markdown("<style>.stTabs [data-baseweb='tab-list'] button p { font-size: 18px; font-weight: bold; }</style>", unsafe_allow_html=True)
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])


with tab_cad:
    st.subheader("👤 Identificação do Cliente (BLOQUEADO)")
    c1, c2, c3 = st.columns([2.5, 1.2, 1.4])
    cliente = c1.text_input("Cliente / Empresa")
    doc_cliente = c2.text_input("CPF / CNPJ")
    data_visita = c3.date_input("📅 Data", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")

    st.markdown("---")
    e1, e2, e3, e4 = st.columns([0.6, 2.0, 0.5, 1.0])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Bloco/Apto")
    
    e5, e6, e7 = st.columns([1.5, 1.0, 1.5])
    bairro, cep, email_cli = e5.text_input("Bairro"), e6.text_input("CEP"), e7.text_input("✉️ E-mail")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
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

with tab_ele:
    st.subheader("⚡ Medições Elétricas")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Nominal (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=220.0)
        st.metric("Variação", f"{round(v_rede - v_med, 1)} V")
    with el2:
        rla_comp = st.number_input("Corrente Nominal (RLA)", value=5.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
    with el3:
        lra_comp = st.number_input("Corrente Partida (LRA)", value=0.0)
        carga_pct = (a_med / rla_comp * 100) if rla_comp > 0 else 0
        st.metric("Carga Motor", f"{round(carga_pct, 1)} %")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance de Ar")
    st.markdown("**🌬️ Temperaturas de Ar (Troca Térmica)**")
    ta1, ta2, ta3 = st.columns(3)
    t_retorno = ta1.number_input("Temp. Retorno (°C)", value=24.0)
    t_insuflacao = ta2.number_input("Temp. Insuflação (°C)", value=12.0)
    delta_ar = round(t_retorno - t_insuflacao, 1)
    ta3.metric("Delta T (Ar)", f"{delta_ar} °C")

    st.markdown("---")
    st.markdown("**⚙️ Pressões e Temperaturas de Tubo**")
    tr1, tr2, tr3 = st.columns(3)
    p_suc = tr1.number_input("P. Sucção (PSI)", value=115.0)
    t_suc_tubo = tr1.number_input("T-Tubo Sucção (°C)", value=12.0)
    ts_suc = get_tsat_global(p_suc, fluido)
    
    p_liq = tr2.number_input("P. Líquido (PSI)", value=340.0)
    t_liq_tubo = tr2.number_input("T-Tubo Líquido (°C)", value=32.0)
    ts_liq = get_tsat_global(p_liq, fluido)
    
    sh_val = round(t_suc_tubo - ts_suc, 1)
    sc_val = round(ts_liq - t_liq_tubo, 1)
    tr3.metric("SH", f"{sh_val} K")
    tr3.metric("SC", f"{sc_val} K")


with tab_diag:
    st.header("🤖 Diagnóstico Assistido")
    diagnosticos, probs, acoes = [], {}, []
    
    if delta_ar < 8:
        diagnosticos.append("Baixa troca térmica no evaporador")
        probs["Sujeira ou Obstrução de Ar"] = 80
        acoes.append("Limpeza de filtros e serpentina")
    
    if sh_val > 12:
        diagnosticos.append("Superaquecimento Elevado")
        probs["Falta de Fluido / Vazamento"] = 85
        acoes.append("Localizar vazamento e completar carga")
    elif sh_val < 4:
        diagnosticos.append("Baixo Superaquecimento")
        probs["Excesso de Fluido / Baixa Troca"] = 70
        acoes.append("Ajustar carga ou verificar ventilador")

    if not diagnosticos: diagnosticos.append("Sistema operando dentro dos parâmetros de projeto")
    diag_txt = " | ".join(diagnosticos)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in probs.items()]) if probs else "Nenhuma anomalia identificada"
    acoes_txt = " | ".join(acoes) if acoes else "Monitoramento periódico"
    cop_est = round((sc_val + 1.5) / (sh_val + 1.5), 2) if sh_val != -1.5 else 0

    c_ia1, c_ia2 = st.columns(2)
    c_ia1.info(f"**Análise:** {diag_txt}")
    c_ia1.warning(f"**Suspeitas:** {prob_txt}")
    c_ia2.success(f"**Recomendação:** {acoes_txt}")
    c_ia2.metric("COP Estimado", cop_est)

    st.markdown("---")
    # RELATÓRIO EXATO SOLICITADO
    relatorio_whats = f"""MPN - LAUDO TÉCNICO
Diagnóstico: {diag_txt}
Suspeitas: {prob_txt}
Ações: {acoes_txt}
SH/SC: {sh_val}K / {sc_val}K
COP: {cop_est}"""

    st.text_area("Texto para WhatsApp", relatorio_whats, height=130)
    st.markdown(f"""<button onclick="navigator.clipboard.writeText(`{relatorio_whats}`)" style="width:100%; padding:12px; background:#25d366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">📋 Copiar para WhatsApp</button>""", unsafe_allow_html=True)

    st.markdown("---")
    col_med1, col_med2 = st.columns(2)
    executadas_in = col_med1.text_area("🛠️ Medidas Executadas", height=150, key="e_in")
    parecer_in = col_med2.text_area("💡 Parecer Técnico Final", height=150, key="p_in")


if st.button("💾 FINALIZAR, SALVAR E GERAR PDF"):
        end_str = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
        obs_completas = f"Delta Ar: {delta_ar}C (Ret:{t_retorno}/Ins:{t_insuflacao}). {parecer_in}"
        
        dados_banco = (
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            end_str, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            diag_txt, executadas_in, obs_completas
        )
        
        if salvar_dados(dados_banco):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16); pdf.set_text_color(0, 74, 153)
            pdf.cell(190, 10, "MPN - RELATORIO TECNICO HVAC", 0, 1, 'C'); pdf.ln(10)
            
            pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 1. IDENTIFICACAO", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
            pdf.cell(190, 7, clean(f"Cliente: {cliente} | Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereco: {end_str}"), 1, 1)

            pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 2. PERFORMANCE", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(63, 7, clean(f"Delta Ar: {delta_ar} C"), 1); pdf.cell(63, 7, clean(f"SH: {sh_val} K"), 1); pdf.cell(64, 7, clean(f"SC: {sc_val} K"), 1, 1)
            
            pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 3. PARECER", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(f"Diagnostico: {diag_txt}\n\nMedidas: {executadas_in}\n\nObs: {obs_completas}"), 1)

            pdf_out = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar PDF", data=pdf_out, file_name=f"Laudo_MPN_{cliente}.pdf")
            st.success("Salvo!")

with tab_hist:
    st.subheader("📜 Histórico")
    conn = sqlite3.connect(DB_PATH)
    df_h = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    
    if not df_h.empty:
        df_h['data_visita'] = pd.to_datetime(df_h['data_visita']).dt.strftime('%d/%m/%Y')
        df_h.insert(0, "Excluir", False)
        ed_h = st.data_editor(df_h, hide_index=True, use_container_width=True, column_config={"id": None})
        if st.button("🗑️ Apagar Selecionados"):
            ids_del = ed_h[ed_h["Excluir"] == True]["id"].tolist()
            conn = sqlite3.connect(DB_PATH)
            for d in ids_del: conn.execute("DELETE FROM atendimentos WHERE id = ?", (d,))
            conn.commit(); conn.close(); st.rerun()
    else:
        st.info("Banco vazio.")
