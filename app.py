import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata

# --- 0. BANCO DE DADOS (ESTRUTURA BLOQUEADA) ---
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

# --- 1. CONFIGURAÇÃO DA PÁGINA (LAYOUT BLOQUEADO) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. UTILITÁRIOS E MOTOR TERMODINÂMICO ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def get_tsat_global(psig, gas):
    ancoras = {
        "R-410A": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                   "t": [-51.0, -17.02, -0.29, 11.55, 20.93, 28.84, 35.58, 41.74, 47.3, 52.1, 56.59, 60.7, 64.59]},
        "R-32": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0], 
                 "t": [-51.7, -17.46, 0.87, 10.86, 20.14, 27.9, 34.63, 40.6, 45.96, 50.8, 55.36, 59.5, 63.43]},
        "R-22": {"p": [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0], 
                 "t": [-40.8, -3.34, 15.80, 28.15, 38.56, 47.30, 54.89, 61.63, 73.2, 78.38, 87.53]},
        "R-134a": {"p": [0.0, 20.0, 50.0, 80.0, 100.0, 130.0, 150.0, 180.0, 200.0], 
                   "t": [-26.08, -1.0, 12.23, 22.8, 30.92, 38.4, 43.65, 50.1, 53.74]}
    }
    if gas not in ancoras or psig is None: return 0.0
    try: return round(float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except: return 0.0

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def seguro(v):
    try:
        if v is None: return 0.0
        return float(v)
    except: return 0.0

# --- 3. INTERFACE (ESTRUTURA BLOQUEADA) ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

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
        v_rede = st.number_input("Tensão Rede (V)", value=220.0)
        v_med = st.number_input("Tensão Medida (V)", value=218.0)
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença entre Tensões"); st.success(f"{diff_v} V")
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença entre Correntes"); st.success(f"{diff_a} A")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("**Sucção (Baixa)**")
        p_suc = st.number_input("Pressão (PSI)", value=118.0, key="ps")
        t_suc_tubo = st.number_input("Temp. Tubo (°C)", value=12.0, key="ts")
        ts_suc = get_tsat_global(p_suc, fluido)
        st.write("T-Sat Sucção"); st.info(f"{ts_suc} °C")
    with tr2:
        st.markdown("**Líquido (Alta)**")
        p_liq = st.number_input("Pressão (PSI)", value=345.0, key="pl")
        t_liq_tubo = st.number_input("Temp. Tubo (°C)", value=30.0, key="tl")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.write("T-Sat Líquido"); st.info(f"{ts_liq} °C")
    with tr3:
        st.markdown("**Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.write("Superaquecimento (SH)"); st.success(f"**{sh_val} K**")
        st.write("Subresfriamento (SC)"); st.success(f"**{sc_val} K**")

with tab_diag:
    # =============================
    # LÓGICA DO MOTOR DE DIAGNÓSTICO
    # =============================
    diagnostico = []
    probabilidades = {}
    def registrar(msg, falha=None, prob=0):
        diagnostico.append(msg)
        if falha: probabilidades[falha] = prob

    # Proteção de valores para o motor
    v_sh, v_sc = seguro(sh_val), seguro(sc_val)
    v_psuc, v_pliq = seguro(p_suc), seguro(p_liq)
    v_tsuc_tubo, v_tssuc = seguro(t_suc_tubo), seguro(ts_suc)
    v_tliq_tubo, v_tsliq = seguro(t_liq_tubo), seguro(ts_liq)
    v_amed, v_rla = seguro(a_med), seguro(rla_comp)

    # Cálculo de Eficiência
    try:
        delta_cond = v_tsliq - v_tliq_tubo
        delta_evap = v_tsuc_tubo - v_tssuc
        cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)
        if cop_aprox < 1.5: registrar("Baixa eficiência energética")
        elif cop_aprox > 4: registrar("Alta eficiência operacional")
    except: cop_aprox = 0

    # Regras de Diagnóstico
    if delta_evap < 2: registrar("Baixa troca no evaporador", "Fluxo de ar insuficiente", 60)
    if delta_cond < 2: registrar("Condensação ineficiente", "Sujeira ou má ventilação", 55)
    if v_rla > 0:
        carga_pct = (v_amed / v_rla) * 100
        if carga_pct > 120: registrar("Compressor sobrecarregado", "Excesso de fluido ou alta pressão", 65)
    if v_psuc > 140 and v_pliq < 300: registrar("Perda de compressão", "Compressor desgastado", 70)
    
    if not diagnostico: diagnostico.append("Sistema operando dentro dos parâmetros")
    diag_ia_txt = " | ".join(diagnostico)

    # Interface Visual
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Encontrados")
        pi1, pi2 = st.columns(2)
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", "Ar/Incondensaveis no Ciclo", "Obstrucao Dispositivo Expansao", "Linha de Liquido Congelando", "Colmeia Congelando", "Filtro Secador Obstruido", "Compressor Sem Compressao", "Falha na Ventilacao", "Falha na Placa Inverter", "Instabilidade na Rede Eletrica", "Evaporadora Pingando", "Linha de Descarga Congelando"]
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt): p_sel.append(opt)
            else:
                if pi2.checkbox(opt): p_sel.append(opt)
    with col_obs:
        st.subheader("📝 Observações do Técnico")
        obs_tecnico = st.text_area("", placeholder="Parecer técnico...", height=215, label_visibility="collapsed", key="obs_tec_diag")
    
    st.markdown("---")
    col_prop_ia, col_exec = st.columns(2)
    with col_prop_ia:
        st.subheader("🤖 Diagnóstico IA")
        st.info(f"**Análise:** {diag_ia_txt}")
        st.write(f"**COP Aproximado:** {cop_aprox}")
        st.subheader("🔧 Medidas Propostas IA")
        if "sobrecarregado" in diag_ia_txt.lower():
            st.warning("1. Limpar condensadora. 2. Ajustar carga de fluido.")
        else:
            st.warning("1. Verificar estanqueidade e parâmetros nominais.")
            
    with col_exec:
        st.subheader("📋 Medidas Executadas")
        executadas_input = st.text_area("", placeholder="Descreva as medidas executadas...", key="exec_diag", height=200, label_visibility="collapsed")

    if st.button("📄 Gerar Relatório Profissional"):
        endereco_completo = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro} | CEP: {cep}"
        prob_txt = ', '.join(p_sel) if p_sel else 'Nenhum'
        dados_para_banco = (
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            endereco_completo, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            prob_txt, executadas_input, obs_tecnico
        )
        salvar_dados(dados_para_banco)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 15, "Relatorio Tecnico HVAC", 0, 1, 'C'); pdf.ln(10)

        # DESIGN DO RELATÓRIO
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO DO CLIENTE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
        pdf.cell(45, 6, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 0)
        pdf.cell(100, 6, clean(f"Cliente: {cliente}"), 1, 0)
        pdf.cell(45, 6, clean(f"Doc: {doc_cliente}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {endereco_completo}"), 1, 1); pdf.ln(4)

        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. PERFORMANCE TECNICA", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.cell(95, 6, clean(f"SH: {sh_val} K"), 1, 0); pdf.cell(95, 6, clean(f"SC: {sc_val} K"), 1, 1)
        pdf.cell(95, 6, clean(f"Pressao Suc: {p_suc} PSI"), 1, 0); pdf.cell(95, 6, clean(f"Pressao Liq: {p_liq} PSI"), 1, 1)
        pdf.cell(190, 6, clean(f"Diagnostico IA: {diag_ia_txt}"), 1, 1); pdf.ln(4)

        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 3. PARECER FINAL", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(f"Medidas: {executadas_input}"), 1)

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
        st.toast("✅ Relatório gerado!")

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    query = "SELECT id, data_visita, cliente, doc_cliente, marca, modelo, tecnologia, sh, sc FROM atendimentos ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.date
        f_col1, f_col2 = st.columns(2)
        with f_col1: 
            busca = st.text_input("🔍 Pesquisar por Cliente")
        with f_col2: 
            periodo = st.date_input("📅 Filtrar por Período", 
                                    value=[df['data_visita'].min(), df['data_visita'].max()],
                                    format="DD/MM/YYYY")
        
        if busca:
            df = df[df['cliente'].apply(lambda x: remover_acentos(busca) in remover_acentos(x))]
            
        df_editado = st.data_editor(
            df, 
            column_config={
                "data_visita": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "id": None 
            },
            hide_index=True,
            use_container_width=True
        )
        
# =============================
# PROTECAO CONTRA ERROS DE VALORES
# =============================

def seguro(v):
    try:
        if v is None:
            return 0.0
        return float(v)
    except:
        return 0.0

# Aplicação da proteção
sh_val = seguro(sh_val)
sc_val = seguro(sc_val)
p_suc = seguro(p_suc)
p_liq = seguro(p_liq)
t_suc_tubo = seguro(t_suc_tubo)
ts_suc = seguro(ts_suc)
t_liq_tubo = seguro(t_liq_tubo)
ts_liq = seguro(ts_liq)
a_med = seguro(a_med)
rla_comp = seguro(rla_comp)
diff_v = seguro(diff_v)

# =============================
# MOTOR DE DIAGNOSTICO HVAC
# =============================

diagnostico = []
probabilidades = {}

def registrar(msg, falha=None, prob=0):
    if msg not in diagnostico:
        diagnostico.append(msg)
    if falha:
        probabilidades[falha] = prob

# =============================
# ANALISE TECNICA (LÓGICA ANTES DA EXIBIÇÃO)
# =============================

# Eficiência Evaporador
delta_evap = t_suc_tubo - ts_suc
if delta_evap < 2:
    registrar("Baixa transferencia de calor no evaporador", "Fluxo de ar insuficiente", 60)

# Eficiência Condensador
delta_cond = ts_liq - t_liq_tubo
if delta_cond < 2:
    registrar("Condensacao ineficiente", "Ventilacao insuficiente", 55)

# Compressor e Carga
if rla_comp > 0:
    carga_pct = (a_med / rla_comp) * 100
    if carga_pct > 120:
        registrar("Compressor sobrecarregado", "Alta pressao ou excesso refrigerante", 65)
    elif carga_pct < 40:
        registrar("Compressor operando com carga muito baixa", "Baixa carga termica", 60)

# Compressor Desgastado
if p_suc > 140 and p_liq < 300:
    registrar("Possivel perda de compressao", "Compressor desgastado", 70)

# Elétrica
if abs(diff_v) > 10:
    registrar("Variacao significativa de tensao", "Problema na rede eletrica", 80)

# Tecnologia Inverter
if 'tecnologia' in locals() and tecnologia == "Inverter":
    if sh_val < 2:
        registrar("Controle inverter possivelmente modulando excessivamente", "Ajuste de controle do compressor", 40)
    if p_liq > 420:
        registrar("Possivel limitacao de frequencia por alta pressao", "Alta pressao de condensacao", 50)

# =============================
# PROCESSAMENTO DOS RESULTADOS
# =============================

# Cálculo COP
try:
    cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)
    if cop_aprox < 1.5:
        diagnostico.append("Baixa eficiencia energetica do sistema")
    elif cop_aprox > 4:
        diagnostico.append("Sistema operando com alta eficiencia")
except:
    cop_aprox = 0.0

if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parametros")

diag_ia = " | ".join(diagnostico)

# Ranking de Probabilidades
if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha critica detectada"

# Contramedidas
contramedidas = []
for falha in probabilidades:
    f_lower = falha.lower()
    if "refrigerante" in f_lower: contramedidas.append("Verificar carga de refrigerante e vazamentos")
    if "condensador" in f_lower: contramedidas.append("Limpar condensador e verificar ventilacao")
    if "evaporador" in f_lower: contramedidas.append("Limpar evaporador e verificar fluxo de ar")
    if "compressor" in f_lower: contramedidas.append("Verificar eficiencia mecanica do compressor")
    if "rede eletrica" in f_lower: contramedidas.append("Verificar tensao da rede e conexoes")

contramedidas_txt = " | ".join(contramedidas) if contramedidas else "Nenhuma acao corretiva necessaria"

# Texto do Relatório
relatorio_txt = f"""RELATORIO TECNICO HVAC
---------------------------
Diagnostico IA: {diag_ia}
Probabilidade de Falhas: {prob_txt}
Contramedidas: {contramedidas_txt}
COP Aproximado: {cop_aprox}
"""

# =============================
# EXIBICAO NA INTERFACE
# =============================

st.header("DIAGNÓSTICO")

st.subheader("🤖 Diagnóstico IA")
st.markdown(f"**🔎 Análise do Sistema:**\n{diag_ia}")
st.markdown(f"**📊 Probabilidade de Falhas:**\n{prob_txt}")
st.markdown(f"**🛠️ Contramedidas Recomendadas:**\n{contramedidas_txt}")
st.metric("Eficiência (COP aprox)", cop_aprox)

st.write("### 📄 Relatório Técnico")
st.text_area("Conteúdo do Relatório", relatorio_txt, height=220)

st.markdown(
    f"""
    <button onclick="navigator.clipboard.writeText(`{relatorio_txt}`)"
    style="padding:10px;font-size:16px;border-radius:6px;cursor:pointer;">
    📋 Copiar Relatório
    </button>
    """,
    unsafe_allow_html=True
)
