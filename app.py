import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd

# --- 0. BANCO DE DADOS ---
def init_db():
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
    c.execute('''CREATE TABLE IF NOT EXISTS base_conhecimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fabricante TEXT, modelo TEXT, tipo_dado TEXT, 
        codigo_erro TEXT, descricao TEXT, link_manual TEXT, data_registro TEXT
    )''')
    conn.commit()
    conn.close()

def salvar_conhecimento(fab, mod, tipo, code, desc, link):
    conn = sqlite3.connect('banco_dados.db')
    c = conn.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute('''INSERT INTO base_conhecimento (fabricante, modelo, tipo_dado, codigo_erro, descricao, link_manual, data_registro) 
                 VALUES (?,?,?,?,?,?,?)''', (fab, mod, tipo, code, desc, link, data_hoje))
    conn.commit()
    conn.close()

init_db()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] button [data-testid='stMarkdownContainer'] p {font-size: 20px; font-weight: bold;}</style>", unsafe_allow_html=True)

# --- 2. MOTOR TERMODINÂMICO ---
def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

# --- 3. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist, tab_manual = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico", "📥 Cadastro Técnico"])

with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente, doc_cliente = c1.text_input("Cliente/Empresa", key="f_cli"), c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp, celular, tel_residencial = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp"), c5.text_input("📱 Celular", key="f_cel"), c6.text_input("📞 Fixo", key="f_fix")
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr, nome_logr, numero, complemento, bairro, cep, email_cli = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog"), e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1: 
        fabricante = st.text_input("Marca", key="f_fab")
        modelo_eq = st.text_input("Modelo Geral", key="f_mod")
        serie_evap = st.text_input("Série Evaporadora", key="f_sevap")
    with g2:
        linha = st.text_input("Linha", key="f_lin")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0", key="f_cap")
        serie_cond = st.text_input("Série Condensadora", key="f_scond")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"], key="f_tec")
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"], key="f_gas")
        loc_evap = st.text_input("Local Evaporadora", key="f_le")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"], key="f_sis")
        loc_cond = st.text_input("Local Condensadora", key="f_lc")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão Rede (V)", value=220.0); v_med = st.number_input("Tensão Medida (V)", value=218.0)
        st.write("Diferença entre Tensões"); st.success(f"{round(v_rede - v_med, 1)} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0); a_med = st.number_input("Corrente Medida (A)", value=0.0)
        st.write("Diferença entre Correntes"); st.success(f"{round(a_med - rla_comp, 1)} A")
    with el3: lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("**Sucção (Baixa)**")
        p_suc = st.number_input("Pressão (PSI)", value=118.0, key="ps"); t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
        ts_suc = get_tsat_global(p_suc, fluido); st.write("T-Sat Sucção"); st.info(f"{ts_suc} °C")
    with tr2:
        st.markdown("**Líquido (Alta)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl"); t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido); st.write("T-Sat Líquido"); st.info(f"{ts_liq} °C")
    with tr3:
        st.markdown("**Performance**")
        st.write("Superaquecimento (SH)"); st.success(f"**{round(t_suc_tubo - ts_suc, 1)} K**")
        st.write("Subresfriamento (SC)"); st.success(f"**{round(ts_liq - t_liq_tubo, 1)} K**")
    
    st.markdown("---")
    st.subheader("⚖️ Calculadora de Carga por Balança")
    cal1, cal2, cal3 = st.columns(3)
    distancia = cal1.number_input("Distância Total (m)", value=3.0, min_value=0.0)
    limite_fab = cal2.number_input("Limite sem Carga (m)", value=7.5, min_value=0.0)
    gramatura = cal3.number_input("Gramas por metro (g/m)", value=20.0, min_value=0.0)
    
    excedente = max(0.0, distancia - limite_fab)
    carga_total = excedente * gramatura
    st.info(f"**Adicional de Fluido:** {carga_total} g")

with tab_diag:
    # FUNCIONALIDADE: CRUZAMENTO AUTOMÁTICO DE DADOS
    if fabricante or modelo_eq:
        conn = sqlite3.connect('banco_dados.db')
        check_q = f"SELECT COUNT(*) FROM base_conhecimento WHERE fabricante LIKE '%{fabricante}%' OR modelo LIKE '%{modelo_eq}%'"
        num_notas = conn.execute(check_q).fetchone()[0]
        if num_notas > 0:
            st.warning(f"🔔 **Atenção:** Existem {num_notas} nota(s) de peritos cadastradas para este fabricante/modelo na sua base de conhecimento.")
        conn.close()

    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", "Ar/Incondensaveis no Ciclo", "Obstrucao Dispositivo Expansao", "Linha de Liquido Congelando", "Colmeia Congelando", "Filtro Secador Obstruido", "Compressor Sem Compressao", "Falha na Ventilacao", "Falha na Placa Inverter", "Instabilidade na Rede Eletrica", "Evaporadora Pingando", "Linha de Descarga Congelando"]
        for opt in opcoes:
            if st.checkbox(opt): p_sel.append(opt)
    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("Digite o parecer técnico...", height=200)
    
    st.markdown("---")
    st.subheader("🧠 Consulta de Inteligência (Base de Conhecimento)")
    busca = st.text_input("🔍 Pesquisar por Fabricante, Modelo ou Código de Erro")
    if busca:
        conn = sqlite3.connect('banco_dados.db')
        query = f"SELECT * FROM base_conhecimento WHERE fabricante LIKE '%{busca}%' OR modelo LIKE '%{busca}%' OR codigo_erro LIKE '%{busca}%'"
        df_res = pd.read_sql_query(query, conn)
        if not df_res.empty:
            for idx, row in df_res.iterrows():
                with st.expander(f"📌 {row['tipo_dado']} - {row['fabricante']} ({row['modelo']})"):
                    if row['codigo_erro']: st.warning(f"**Código de Erro:** {row['codigo_erro']}")
                    st.write(f"**Conteúdo:**\n{row['descricao']}")
                    if row['link_manual']: st.link_button("Acessar Link/Manual", row['link_manual'])
        else: st.info("Nenhuma informação encontrada para esta busca.")
        conn.close()

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db'); df_atend = pd.read_sql_query("SELECT * FROM atendimentos", conn); st.dataframe(df_atend); conn.close()

with tab_manual:
    st.subheader("📥 Cadastro de Conhecimento Técnico")
    with st.form("form_conhecimento", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        fabricante_c, modelo_c, tipo_c = f1.text_input("Fabricante"), f2.text_input("Modelo / Linha"), f3.selectbox("Tipo de Informação", ["Manual de Serviço", "Código de Erro", "Tabela de Referência", "Experiência de Perito", "Opinião do Fabricante"])
        c_erro, desc_c, link_c = st.text_input("Código de Erro"), st.text_area("Conteúdo Detalhado"), st.text_input("Link URL")
        if st.form_submit_button("📥 SALVAR NO BANCO DE CONHECIMENTO"):
            if fabricante_c and desc_c:
                salvar_conhecimento(fabricante_c, modelo_c, tipo_c, c_erro, desc_c, link_c)
                st.success("Informação armazenada!")
            else: st.error("Preencha os campos obrigatórios.")
