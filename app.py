import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import urllib.parse
import unicodedata
import sqlite3
import pandas as pd
import io

# =========================================================
# 0. NÚCLEO TÉCNICO E BANCO DE DADOS (ESTRUTURA INTEGRADA)
# =========================================================
def init_db():
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_visita TEXT, cliente TEXT, doc_cliente TEXT, whatsapp TEXT, celular TEXT, fixo TEXT,
        endereco TEXT, email TEXT, marca TEXT, modelo TEXT, serie_evap TEXT, linha TEXT, 
        capacidade TEXT, serie_cond TEXT, tecnologia TEXT, fluido TEXT, loc_evap TEXT, 
        sistema TEXT, loc_cond TEXT, v_rede REAL, v_med REAL, a_med REAL, rla REAL, lra REAL,
        fp REAL, p_suc REAL, p_liq REAL, t_suc_tubo REAL, t_liq_tubo REAL, t_ret REAL, t_ins REAL,
        sh REAL, sc REAL, delta_t REAL, problemas TEXT, medidas TEXT, observacoes TEXT
    )''')
    
    # Migração segura para colunas que podem faltar em versões anteriores
    colunas_extras = [
        ("fp", "REAL DEFAULT 0.87"),
        ("delta_t", "REAL DEFAULT 0.0"),
        ("t_ret", "REAL DEFAULT 0.0"),
        ("t_ins", "REAL DEFAULT 0.0"),
        ("t_suc_tubo", "REAL DEFAULT 0.0"),
        ("t_liq_tubo", "REAL DEFAULT 0.0")
    ]
    for col, tipo in colunas_extras:
        try:
            c.execute(f"SELECT {col} FROM atendimentos LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(f"ALTER TABLE atendimentos ADD COLUMN {col} {tipo}")
            
    conn.commit()
    conn.close()

def salvar_dados(dados):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    # 37 interrogações para bater com a estrutura completa
    c.execute('''INSERT INTO atendimentos (
        data_visita, cliente, doc_cliente, whatsapp, celular, fixo, endereco, email,
        marca, modelo, serie_evap, linha, capacidade, serie_cond, tecnologia, fluido,
        loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla, lra, fp, p_suc, p_liq,
        t_suc_tubo, t_liq_tubo, t_ret, t_ins, sh, sc, delta_t, problemas, medidas, observacoes
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', dados)
    conn.commit()
    conn.close()

init_db()

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def remover_acentos(txt):
    if not txt: return ""
    return "".join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn').lower()

def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 35.58, 47.3, 56.59, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 34.63, 45.96, 55.36, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0, 600.0], "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 54.89, 67.8, 87.53, 100.0]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 150.0, 200.0], "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 43.65, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)

# =========================================================
# 1. CONFIGURAÇÃO E INTERFACE (LAYOUT BLOQUEADO)
# =========================================================
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")
st.markdown("""<style>.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 20px; font-weight: bold;}</style>""", unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular, tel_fixo = c5.text_input("📱 Celular"), c6.text_input("📞 Fixo")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr, numero, complemento = e2.text_input("Logradouro"), e3.text_input("Nº"), e4.text_input("Comp.")
    bairro, cep, email_cli = e5.text_input("Bairro"), e6.text_input("CEP"), e7.text_input("✉️ E-mail")
    
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: fabricante, modelo_eq, serie_evap = st.text_input("Marca"), st.text_input("Modelo Geral"), st.text_input("Série Evaporadora")
    with g2: linha, cap_btu, serie_cond = st.text_input("Linha"), st.text_input("Capacidade (BTU/h)", value="0"), st.text_input("Série Condensadora")
    with g3: tecnologia, fluido, loc_evap = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"]), st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"]), st.text_input("Local Evaporadora")
    with g4: sistema, loc_cond = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"]), st.text_input("Local Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    v_rede, v_med = el1.number_input("Tensão Rede (V)", value=220.0), el1.number_input("Tensão Medida (V)", value=218.0)
    rla_comp, a_med = el2.number_input("Corrente RLA (A)", value=1.0), el2.number_input("Corrente Medida (A)", value=0.0)
    fp_in, lra_comp = el3.number_input("Fator de Potência (cos Φ)", value=0.87), el3.number_input("LRA (A)", value=0.0)
    
    p_ativa = v_med * a_med * fp_in
    diff_v, diff_a = round(v_med - v_rede, 1), round(a_med - rla_comp, 1)
    st.divider()
    re1, re2, re3 = st.columns(3)
    re1.metric("Potência Ativa", f"{p_ativa:.1f} W"); re2.metric("Dif. Tensão", f"{diff_v} V"); re3.metric("Dif. Corrente", f"{diff_a} A")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        p_suc, t_suc_tubo = st.number_input("Pressão Sucção (PSI)", value=118.0), st.number_input("Temp. Tubo Sucção (°C)", value=12.0)
        ts_suc = get_tsat_global(p_suc, fluido)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        st.info(f"T-Sat Sucção: {ts_suc} °C")
        st.success(f"SH: {sh_val} K")
    with tr2:
        p_liq, t_liq_tubo = st.number_input("Pressão Líquido (PSI)", value=345.0), st.number_input("Temp. Tubo Líquido (°C)", value=30.0)
        ts_liq = get_tsat_global(p_liq, fluido)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.info(f"T-Sat Líquido: {ts_liq} °C")
        st.success(f"SC: {sc_val} K")
    with tr3:
        t_ret, t_ins = st.number_input("Temp. Retorno (°C)", value=25.0), st.number_input("Temp. Insuflação (°C)", value=12.0)
        delta_t = round(t_ret - t_ins, 1)
        st.metric("DELTA T", f"{delta_t} °C")

# =========================================================
# 2. MOTOR DE DIAGNÓSTICO IA E RELATÓRIO
# =========================================================
with tab_diag:
    # Lógica de Diagnóstico Automático
    diagnostico_ia = []
    probabilidades = {}
    
    # Eficiência
    try:
        cop_aprox = round(( (ts_liq - t_liq_tubo) + 1) / ( (t_suc_tubo - ts_suc) + 1), 2)
        if cop_aprox < 1.5: diagnostico_ia.append("Baixa eficiência energética")
        elif cop_aprox > 4: diagnostico_ia.append("Alta eficiência detectada")
    except: cop_aprox = 0

    # Alertas Técnicos
    if sh_val < 5: diagnostico_ia.append("Risco de retorno de líquido")
    if sh_val > 12: diagnostico_ia.append("Superaquecimento elevado (falta fluido/obstrução)")
    if sc_val < 3: diagnostico_ia.append("Subresfriamento baixo (baixa carga)")
    if abs(diff_v) > 22: diagnostico_ia.append("Tensão fora da margem de 10%")
    
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        opcoes = ["Vazamento de Fluido", "Baixa Carga", "Excesso de Fluido", "Ar no Ciclo", "Obstrução Dispositivo", "Filtro Obstruído", "Compressor Falhando", "Falha Ventilação", "Falha Placa", "Rede Instável", "Evaporadora Suja", "Condensadora Suja"]
        p_sel = [opt for opt in opcoes if (pi1.checkbox(opt) if opcoes.index(opt)%2==0 else pi2.checkbox(opt))]
    
    with col_obs:
        st.subheader("📝 Observações e Medidas")
        executadas = st.text_area("Medidas Executadas", placeholder="O que foi feito...", height=100)
        obs_tecnico = st.text_area("Parecer Final", placeholder="Conclusões...", height=100)

    st.info(f"🤖 **Análise IA:** {' | '.join(diagnostico_ia) if diagnostico_ia else 'Sistema dentro dos parâmetros nominais.'}")

    if st.button("📄 GERAR RELATÓRIO E SALVAR", use_container_width=True):
        endereco_full = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro}"
        prob_txt = ', '.join(p_sel) if p_sel else 'Nenhum'
        
        # Salva no Banco
        salvar_dados((str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_fixo, endereco_full, email_cli, fabricante, modelo_eq, serie_evap, linha, cap_btu, serie_cond, tecnologia, fluido, loc_evap, sistema, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp, fp_in, p_suc, p_liq, t_suc_tubo, t_liq_tubo, t_ret, t_ins, sh_val, sc_val, delta_t, prob_txt, executadas, obs_tecnico))

        # Geração do PDF (Layout Bloqueado)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16); pdf.cell(190, 10, "MPN ENGENHARIA - RELATORIO TECNICO", 0, 1, 'C'); pdf.ln(5)
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(190, 6, clean(f"Cliente: {cliente} | Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {endereco_full}"), 1, 1); pdf.ln(2)
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. PERFORMANCE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(47, 6, clean(f"V: {v_med}V"), 1, 0); pdf.cell(47, 6, clean(f"A: {a_med}A"), 1, 0); pdf.cell(48, 6, clean(f"SH: {sh_val}K"), 1, 0); pdf.cell(48, 6, clean(f"DeltaT: {delta_t}C"), 1, 1)
        pdf.ln(2); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 3. PARECER TECNICO", 1, 1, 'L', True)
        pdf.multi_cell(190, 6, clean(f"Problemas: {prob_txt}\nMedidas: {executadas}\nObs: {obs_tecnico}"), 1)
        
        # Assinaturas
        pdf.ln(20); y = pdf.get_y(); pdf.line(20, y, 90, y); pdf.line(120, y, 190, y)
        pdf.set_xy(20, y+1); pdf.cell(70, 4, "Tecnico Responsavel", 0, 0, 'C'); pdf.set_xy(120, y+1); pdf.cell(70, 4, "Assinatura Cliente", 0, 1, 'C')
        
        st.download_button("📥 Baixar PDF", data=pdf.output(dest='S').encode('latin-1', 'ignore'), file_name=f"Relatorio_{remover_acentos(cliente)}.pdf")

# =========================================================
# 3. HISTÓRICO COM BUSCA E EXCLUSÃO (FORMATO BRASILEIRO)
# =========================================================
with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    try:
        query = "SELECT id, data_visita, cliente, marca, sh, sc, delta_t FROM atendimentos ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            # Filtros
            f1, f2 = st.columns(2)
            busca = f1.text_input("🔍 Pesquisar Cliente (sem acentos)")
            if busca:
                df = df[df['cliente'].apply(lambda x: remover_acentos(busca) in remover_acentos(x))]
            
            # Formatação de Data BR para exibição
            df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
            
            # Editor com Checkbox para Excluir
            df.insert(0, "Selecionar", False)
            df_editado = st.data_editor(
                df,
                column_config={
                    "Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False),
                    "id": None # Esconde o ID
                },
                use_container_width=True, hide_index=True, key="editor_hist"
            )
            
            if st.button("🗑️ EXCLUIR REGISTROS SELECIONADOS"):
                ids_del = df_editado[df_editado["Selecionar"] == True]["id"].tolist()
                if ids_del:
                    c = conn.cursor()
                    for id_id in ids_del:
                        c.execute("DELETE FROM atendimentos WHERE id = ?", (id_id,))
                    conn.commit()
                    st.success("Registros excluídos!")
                    st.rerun()
        else:
            st.info("Nenhum registro encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
    finally:
        conn.close()
