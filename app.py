import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
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

# --- 3. INTERFACE (ABAS) ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

# ABA 1: IDENTIFICAÇÃO
with tab_cad:
    st.subheader("👤 Identificação e Contato")
    c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.2, 1.4, 1.0, 1.0, 1.0])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY", key="f_date")
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp")
    celular = c5.text_input("📱 Celular", key="f_cel")
    tel_residencial = c6.text_input("📞 Fixo", key="f_fix")
    
    e1, e2, e3, e4, e5, e6, e7 = st.columns([0.6, 1.5, 0.4, 0.6, 1.0, 0.8, 1.5])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog")
    nome_logr = e2.text_input("Logradouro", key="f_nlog")
    numero = e3.text_input("Nº", key="f_num")
    complemento = e4.text_input("Comp.", key="f_comp")
    bairro = e5.text_input("Bairro", key="f_bai")
    cep = e6.text_input("CEP", key="f_cep")
    email_cli = e7.text_input("✉️ E-mail", key="f_mail")
    
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

# ABA 2: ELÉTRICA
with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_nom = st.number_input("Tensão Rede (V)", value=220.0, key="v_nom_in")
        v_med = st.number_input("Tensão Medida (V)", value=218.0, key="v_med_in")
        v_rede = v_nom # Alias para compatibilidade com o Motor
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0, key="rla_in")
        a_med = st.number_input("Corrente Medida (A)", value=0.0, key="a_med_in")
    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0, key="lra_in")

# ABA 3: TERMODINÂMICA
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
# =========================================================
# PARTE 2: MOTOR DE INTELIGÊNCIA E ABA DIAGNÓSTICO
# =========================================================

# --- 1. PROTEÇÃO CONTRA ERROS DE VALORES (SANITIZAÇÃO) ---
def seguro(v):
    """Garante que entradas nulas ou inválidas não quebrem os cálculos."""
    try:
        if v is None: return 0.0
        return float(v)
    except:
        return 0.0

# Sanitização de todas as variáveis críticas antes dos cálculos
# (Certifique-se que essas variáveis foram criadas nos inputs da Parte 1)
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

# Cálculo do desvio de tensão (assumindo v_med e v_nom da Parte 1)
diff_v = seguro(v_med - v_nom) if 'v_med' in locals() and 'v_nom' in locals() else 0.0

# --- 2. INICIALIZAÇÃO DO MOTOR DE DIAGNÓSTICO ---
diagnostico = []
probabilidades = {}

def registrar(msg, falha=None, prob=0):
    if msg not in diagnostico:
        diagnostico.append(msg)
    if falha:
        probabilidades[falha] = prob

# --- 3. REGRAS DE PERFORMANCE (MOTOR DE IA) ---

# Eficiência Evaporador (Corrigido: Movido para antes do relatório)
delta_evap = t_suc_tubo - ts_suc
if delta_evap < 2:
    registrar("Baixa transferência de calor no evaporador", "Fluxo de ar insuficiente", 60)

# Eficiência Condensador (Corrigido: Movido para antes do relatório)
delta_cond = ts_liq - t_liq_tubo
if delta_cond < 2:
    registrar("Condensação ineficiente", "Ventilação insuficiente", 55)

# Análise de Carga do Compressor
if rla_comp > 0:
    carga_pct = (a_med / rla_comp) * 100
    if carga_pct > 120:
        registrar("Compressor sobrecarregado", "Alta pressão ou excesso refrigerante", 65)
    elif carga_pct < 40:
        registrar("Compressor operando com carga muito baixa", "Baixa carga térmica", 60)

# Performance Mecânica (Compressor Fraco)
if p_suc > 140 and p_liq < 300:
    registrar("Possível perda de compressão", "Compressor desgastado", 70)

# Estabilidade Elétrica
if abs(diff_v) > 10:
    registrar("Variação significativa de tensão", "Problema na rede elétrica", 80)

# Lógica Inverter
if 'tecnologia' in locals() and tecnologia == "Inverter":
    if sh_val < 2:
        registrar("Inverter modulando excessivamente", "Ajuste de controle do compressor", 40)
    if p_liq > 420:
        registrar("Limitação de frequência por alta pressão", "Alta pressão de condensação", 50)

# --- 4. CÁLCULO DE EFICIÊNCIA (COP APROX) ---
try:
    # Lógica de eficiência baseada nos diferenciais térmicos
    cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)
    if cop_aprox < 1.5:
        diagnostico.append("Baixa eficiência energética do sistema")
    elif cop_aprox > 4:
        diagnostico.append("Sistema operando com alta eficiência")
except:
    cop_aprox = 0.0

# --- 5. CONSOLIDAÇÃO DE TEXTOS ---
if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parâmetros")

diag_ia = " | ".join(diagnostico)

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha crítica detectada"

# --- 6. CONTRAMEDIDAS AUTOMÁTICAS ---
contramedidas = []
for falha in probabilidades:
    f_lower = falha.lower()
    if "refrigerante" in f_lower: contramedidas.append("Verificar carga de fluido e buscar vazamentos")
    if "condensador" in f_lower: contramedidas.append("Limpar condensador e verificar ventilação")
    if "evaporador" in f_lower: contramedidas.append("Limpar evaporador e verificar fluxo de ar")
    if "compressor" in f_lower: contramedidas.append("Avaliar eficiência mecânica/isolamento do compressor")
    if "rede elétrica" in f_lower: contramedidas.append("Revisar tensão da rede e aperto de bornes")

contramedidas_txt = " | ".join(contramedidas) if contramedidas else "Manutenção preventiva padrão sugerida"

# --- 7. MONTAGEM DO RELATÓRIO FINAL ---
relatorio_txt = f"""*RELATÓRIO TÉCNICO HVAC - MPN*
-------------------------------------------
*Diagnóstico IA:* {diag_ia}

*Falhas Prováveis:* {prob_txt}

*Ações Recomendadas:* {contramedidas_txt}

*Eficiência Estimada (COP):* {cop_aprox}
-------------------------------------------
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

# --- 8. EXIBIÇÃO NA ABA DIAGNÓSTICO ---
with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico")
    
    # Dashboard de Resumo
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"### 🔎 Análise\n{diag_ia}")
        st.warning(f"### 📊 Probabilidades\n{prob_txt}")
    with c2:
        st.success(f"### 🛠️ Contramedidas\n{contramedidas_txt}")
        st.metric("COP Estimado", cop_aprox)

    st.divider()
    
    # Área de Cópia e PDF
    st.subheader("📄 Relatório Consolidado")
    st.text_area("Texto para WhatsApp", relatorio_txt, height=200)

    # Botão de Cópia Inteligente (JS)
    js_limpo = relatorio_txt.replace("\n", "\\n").replace("*", "")
    st.markdown(f"""
        <button onclick="navigator.clipboard.writeText('{js_limpo}')" 
        style="width:100%; padding:15px; background-color:#2e7d32; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
        📋 COPIAR RELATÓRIO PARA WHATSAPP
        </button>
    """, unsafe_allow_html=True)

# =============================
# COMPRESSOR
# =============================

if rla_comp > 0:

    carga_pct = (a_med / rla_comp) * 100

    if carga_pct > 120:
        registrar(
            "Compressor sobrecarregado",
            "Alta pressao ou excesso refrigerante",
            65
        )

    elif carga_pct < 40:
        registrar(
            "Compressor operando com carga muito baixa",
            "Baixa carga termica",
            60
        )


# =============================
# COMPRESSOR FRACO
# =============================

if p_suc > 140 and p_liq < 300:
    registrar(
        "Possivel perda de compressao",
        "Compressor desgastado",
        70
    )


# =============================
# TENSAO ELETRICA
# =============================

if abs(diff_v) > 10:
    registrar(
        "Variacao significativa de tensao",
        "Problema na rede eletrica",
        80
    )


# =============================
# INVERTER
# =============================

if tecnologia == "Inverter":

    if sh_val < 2:
        registrar(
            "Controle inverter possivelmente modulando excessivamente",
            "Ajuste de controle do compressor",
            40
        )

    if p_liq > 420:
        registrar(
            "Possivel limitacao de frequencia por alta pressao",
            "Alta pressao de condensacao",
            50
        )


# =============================
# RESULTADO FINAL
# =============================

if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parametros")

diag_ia = " | ".join(diagnostico)


# =============================
# PROBABILIDADE DE FALHAS
# =============================

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha critica detectada"

# =========================================================
# 5. MOTOR DE INTELIGÊNCIA HVAC (PROCESSAMENTO)
# =========================================================

# Inicialização de listas para evitar erros de persistência
diagnostico = []
probabilidades = {}

def registrar(falha, causa, peso):
    diagnostico.append(falha)
    probabilidades[causa] = peso

# --- EFICIENCIA EVAPORADOR ---
delta_evap = t_suc_tubo - ts_suc
if delta_evap < 2 and a_med > 0.5:
    registrar("Baixa troca de calor no evaporador", "Fluxo de ar insuficiente ou sujeira", 60)

# --- EFICIENCIA CONDENSADOR ---
delta_cond = ts_liq - t_liq_tubo
if delta_cond < 2 and a_med > 0.5:
    registrar("Condensação ineficiente", "Ventilação obstruída ou condensador sujo", 55)

# --- ANÁLISE DO COMPRESSOR (CARGA E PERFORMANCE) ---
if rla_comp > 0 and a_med > 0:
    carga_pct = (a_med / rla_comp) * 100
    if carga_pct > 120:
        registrar("Compressor em sobrecarga elétrica", "Alta pressão ou excesso de fluido", 75)
    elif carga_pct < 40:
        registrar("Compressor operando em subcarga", "Baixa carga térmica ou falta de fluido", 60)

# --- ANÁLISE DE COMPRESSÃO MECÂNICA (COMPRESSOR FRACO) ---
# Lógica específica para R-410A/R-32 (Pressão de sucção alta e descarga baixa)
if p_suc > 140 and p_liq < 300 and fluido in ["R-410A", "R-32"]:
    registrar("Baixa performance de compressão", "Compressor com desgaste mecânico (Válvulas/Scroll)", 70)

# --- LOGICA ESPECIFICA INVERTER ---
if tecnologia == "Inverter":
    if sh_val < 2:
        registrar("Modulação excessiva do Inverter", "Ajuste de controle do compressor/EEV", 40)
    if p_liq > 420:
        registrar("Limitação de frequência por alta pressão", "Proteção térmica/pressostática ativa", 50)

# --- TENSAO ELETRICA ---
diff_v = v_med - v_rede
if abs(diff_v) > 15:
    registrar("Variação crítica de tensão detectada", "Instabilidade na Rede Elétrica", 85)

# =========================================================
# 6. CONSOLIDAÇÃO E CONTRAMEDIDAS
# =========================================================

if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parâmetros nominais")

diag_ia = " | ".join(diagnostico)

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha crítica detectada"

# Geração automática de contramedidas baseada nas falhas registradas
contramedidas = []
falhas_detectadas_str = " ".join(diagnostico).lower() + " " + " ".join(probabilidades.keys()).lower()

if any(x in falhas_detectadas_str for x in ["refrigerante", "fluido", "vazamento"]):
    contramedidas.append("Verificar carga de fluido e buscar vazamentos com detector/nitrogênio")
if "condensador" in falhas_detectadas_str or "condensação" in falhas_detectadas_str:
    contramedidas.append("Realizar limpeza química e desobstrução das aletas do condensador")
if any(x in falhas_detectadas_str for x in ["evaporador", "fluxo de ar", "sujeira"]):
    contramedidas.append("Limpar filtros, turbina e serpentina da unidade evaporadora")
if "compressor" in falhas_detectadas_str:
    contramedidas.append("Medir isolamento ôhmico (megômetro) e testar capacitor/inverter")
if "rede eletrica" in falhas_detectadas_str or "tensão" in falhas_detectadas_str:
    contramedidas.append("Revisar aperto de bornes, quadro elétrico e estabilidade da fase")

if not contramedidas:
    contramedidas.append("Manter plano de manutenção preventiva mensal (PMOC)")

contramedidas_txt = " | ".join(list(set(contramedidas)))

# =========================================================
# 7. EXIBIÇÃO FINAL (ABA DIAGNÓSTICO)
# =========================================================

with tab_diag:
    st.header("🤖 DIAGNÓSTICO FINAL")

    # Garantia de segurança contra variáveis nulas
    d_ia = diag_ia if 'diag_ia' in locals() else "Análise não disponível"
    p_txt = prob_txt if 'prob_txt' in locals() else "Nenhuma falha detectada"
    c_txt = contramedidas_txt if 'contramedidas_txt' in locals() else "Manutenção padrão"

    c1, c2 = st.columns(2)
    with c1:
        st.info(f"### 🔎 Análise do Sistema\n{d_ia}")
        st.warning(f"### 📊 Probabilidades\n{p_txt}")
    with c2:
        st.success(f"### 🛠️ Contramedidas\n{c_txt}")
        st.metric("Eficiência Estimada (COP)", f"{cop_aprox}")

    st.divider()
    st.write("### 📄 Relatório Consolidado")
    
    relatorio_txt = f"""RELATÓRIO TÉCNICO HVAC - MPN
-------------------------------------------
CLIENTE: {cliente}
DIAGNÓSTICO: {d_ia}
FALHAS: {p_txt}
MEDIDAS SUGERIDAS: {c_txt}
COP ESTIMADO: {cop_aprox}
-------------------------------------------
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

    st.text_area("Texto para WhatsApp", relatorio_txt, height=200, key="rel_final_area")

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        # JS seguro para cópia (escapando quebras de linha)
        js_copia = relatorio_txt.replace("\n", "\\n").replace("'", "\\'")
        st.markdown(
            f"""<button onclick="navigator.clipboard.writeText('{js_copia}')" 
            style="width:100%; padding:12px; background-color:#2e7d32; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">
            📋 Copiar para WhatsApp</button>""", 
            unsafe_allow_html=True
        )

    with col_btn2:
        if st.button("📄 Gerar PDF Profissional", use_container_width=True):
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Courier", 'B', 16)
                pdf.set_text_color(0, 51, 102)
                pdf.cell(0, 10, clean("MPN ENGENHARIA - RELATORIO TECNICO"), 0, 1, 'C')
                pdf.ln(5)

                # Seções do PDF
                def add_section(titulo, conteudo):
                    pdf.set_fill_color(240, 240, 240)
                    pdf.set_font("Courier", 'B', 11)
                    pdf.cell(0, 8, clean(f" {titulo}"), 0, 1, 'L', fill=True)
                    pdf.set_font("Courier", '', 10)
                    pdf.set_text_color(0, 0, 0)
                    pdf.multi_cell(0, 7, clean(conteudo), 0, 'L')
                    pdf.ln(4)

                add_section("1. DADOS DO ATENDIMENTO", f"Cliente: {cliente}\nData: {data_visita.strftime('%d/%m/%Y')}")
                add_section("2. DIAGNÓSTICO E PERFORMANCE", f"Análise: {d_ia}\nCOP: {cop_aprox}")
                add_section("3. PROBABILIDADE DE FALHAS", p_txt)
                add_section("4. RECOMENDAÇÕES", c_txt)

                pdf.ln(10)
                pdf.cell(0, 0, "", "T", 1, 'C')
                pdf.cell(0, 10, clean("Responsavel Tecnico - MPN Engenharia"), 0, 1, 'C')

                pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                st.download_button(
                    label="📥 BAIXAR RELATÓRIO PDF",
                    data=pdf_output,
                    file_name=f"Relatorio_{remover_acentos(cliente)[:10]}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro na geração: {e}")
