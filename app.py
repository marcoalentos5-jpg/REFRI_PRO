import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata
import time

# --- 0. CONFIGURAÇÃO E CONSTANTES ---
NOME_APP = "MPN | Engenharia & Diagnóstico"
VERSAO = "2.0.4-PRO"

# --- 1. BANCO DE DADOS (ESTRUTURA BLOQUEADA) ---
def init_db():
    """Inicializa o banco de dados com a estrutura definida e imutável."""
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
    """Executa a persistência dos dados de atendimento."""
    try:
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
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False

# --- 2. MOTOR TERMODINÂMICO (ÂNCORAS DE SATURAÇÃO) ---
def get_tsat_global(psig, gas):
    """Realiza a interpolação linear para encontrar a temperatura de saturação."""
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
    try:
        val = float(np.interp(psig, ancoras[gas]["p"], ancoras[gas]["t"]))
        return round(val, 2)
    except:
        return 0.0

# --- 3. UTILITÁRIOS DE STRING E FORMATAÇÃO ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def clean(txt):
    """Sanitiza strings para o formato PDF (Latin-1)."""
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

def seguro(v, padrao=0.0):
    """Garante que operações matemáticas não falhem por inputs inválidos."""
    try:
        if v is None: return padrao
        return float(v)
    except:
        return padrao

init_db()
# --- 4. CONFIGURAÇÃO DA UI ---
st.set_page_config(page_title=NOME_APP, layout="wide", page_icon="❄️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab-list"] button {
        background-color: #e1e4e8; border-radius: 5px; height: 50px; width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px; font-weight: bold; color: #003366;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #003366; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

with tab_cad:
    st.subheader("👤 Identificação do Cliente")
    c1, c2, c3 = st.columns([2, 1, 1])
    cliente = c1.text_input("Cliente/Empresa", key="f_cli", help="Nome completo ou Razão Social")
    doc_cliente = c2.text_input("CPF/CNPJ", key="f_doc")
    data_visita = c3.date_input("📅 DATA DA VISITA", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217", key="f_wpp")
    celular = c5.text_input("📱 Celular", key="f_cel")
    tel_residencial = c6.text_input("📞 Fixo", key="f_fix")

    st.markdown("---")
    st.subheader("📍 Endereço da Instalação")
    e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Comp.")
    
    e5, e6, e7 = st.columns([1, 1, 2])
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("✉️ E-mail de Contato")

    st.markdown("---")
    st.subheader("⚙️ Especificações Técnicas")
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
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Local Evaporadora")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "VRF", "Chiller"])
        loc_cond = st.text_input("Local Condensadora")

with tab_ele:
    st.subheader("⚡ Parâmetros de Energia")
    el1, el2, el3 = st.columns(3)
    with el1:
        v_rede = st.number_input("Tensão de Rede Nominal (V)", value=220.0, step=1.0)
        v_med = st.number_input("Tensão Medida em Carga (V)", value=218.0, step=1.0)
        diff_v = round(v_rede - v_med, 1)
        st.metric("Queda de Tensão", f"{diff_v} V", delta=f"{round((diff_v/v_rede)*100,1)}%", delta_color="inverse")
    with el2:
        rla_comp = st.number_input("Corrente Nominal RLA (A)", value=1.0, step=0.1)
        a_med = st.number_input("Corrente Medida (A)", value=0.0, step=0.1)
        diff_a = round(a_med - rla_comp, 2)
        st.metric("Diferença de Corrente", f"{diff_a} A", delta=f"{diff_a} A", delta_color="inverse")
    with el3:
        lra_comp = st.number_input("Corrente de Partida LRA (A)", value=0.0, step=1.0)
        st.info("O LRA ajuda a identificar travamento mecânico do compressor.")
with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("<div style='background-color:#e3f2fd;padding:10px;border-radius:5px'><b>LADO DE BAIXA (SUCÇÃO)</b></div>", unsafe_allow_html=True)
        p_suc = st.number_input("Pressão de Sucção (PSI)", value=118.0, key="ps_val")
        t_suc_tubo = st.number_input("Temp. Tubo de Sucção (°C)", value=12.0, key="ts_val")
        ts_suc = get_tsat_global(p_suc, fluido)
        st.write(f"Temperatura de Saturação: **{ts_suc} °C**")
    
    with tr2:
        st.markdown("<div style='background-color:#fff3e0;padding:10px;border-radius:5px'><b>LADO DE ALTA (LÍQUIDO)</b></div>", unsafe_allow_html=True)
        p_liq = st.number_input("Pressão de Líquido (PSI)", value=345.0, key="pl_val")
        t_liq_tubo = st.number_input("Temp. Tubo de Líquido (°C)", value=30.0, key="tl_val")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.write(f"Temperatura de Saturação: **{ts_liq} °C**")

    with tr3:
        st.markdown("<div style='background-color:#e8f5e9;padding:10px;border-radius:5px'><b>RESULTADOS DE PERFORMANCE</b></div>", unsafe_allow_html=True)
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        
        st.metric("Superaquecimento (SH)", f"{sh_val} K")
        st.metric("Subresfriamento (SC)", f"{sc_val} K")

# --- 5. LÓGICA DO MOTOR DE DIAGNÓSTICO IA ---
diagnostico_lista = []
probabilidades = {}

def registrar_evento(msg, falha=None, prob=0):
    if msg not in diagnostico_lista: diagnostico_lista.append(msg)
    if falha: probabilidades[falha] = prob

# Validação Cruzada de Falhas
if sh_val > 12 and sc_val < 3:
    registrar_evento("Superaquecimento alto com baixo Subresfriamento", "Baixa Carga de Fluido", 90)
elif sh_val < 4 and sc_val > 12:
    registrar_evento("Superaquecimento baixo com alto Subresfriamento", "Excesso de Fluido", 85)
elif sh_val > 15 and sc_val > 15:
    registrar_evento("Ambos elevados indicam restrição no fluxo", "Obstrução no Dispositivo de Expansão", 75)

if abs(diff_v) > (v_rede * 0.1):
    registrar_evento("Queda de tensão acima de 10%", "Instabilidade na Rede Elétrica", 95)

if rla_comp > 0 and a_med > (rla_comp * 1.2):
    registrar_evento("Sobrecorrente detectada no compressor", "Sobrecarga Mecânica ou Elétrica", 80)

# Cálculo de Eficiência (COP Estimado)
try:
    cop_aprox = round((seguro(ts_liq) - seguro(t_liq_tubo) + 1) / (seguro(t_suc_tubo) - seguro(ts_suc) + 1), 2)
    if cop_aprox < 1.0: cop_aprox = "Anômalo"
except:
    cop_aprox = "Indeterminado"

diag_ia_resultado = " | ".join(diagnostico_lista) if diagnostico_lista else "Parâmetros de operação normais."
with tab_diag:
    col_prob, col_obs = st.columns(2)
    with col_prob:
        st.subheader("⚠️ Problemas Identificados")
        opcoes_p = ["Vazamento", "Carga Baixa", "Excesso Gás", "Incondensáveis", "Obstrução", "Filtro Sujo", "Compressor sem Compressão", "Falha Ventilador"]
        p_selecionados = [opt for opt in opcoes_p if st.checkbox(opt)]
    
    with col_obs:
        st.subheader("📝 Observações Técnicas")
        obs_tecnico = st.text_area("Parecer final", height=150, key="obs_final")

    if st.button("📄 FINALIZAR E GERAR RELATÓRIO PDF"):
        if not cliente:
            st.warning("Por favor, insira o nome do cliente.")
        else:
            # Preparação dos dados
            end_full = f"{tipo_logr} {nome_logr}, {numero} - {bairro}"
            prob_str = ", ".join(p_selecionados) if p_selecionados else "Nenhum detectado"
            
            dados_banco = (
                str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
                end_full, email_cli, fabricante, modelo_eq, serie_evap, linha,
                cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
                v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
                prob_str, "Medidas aplicadas conforme diagnóstico", obs_tecnico
            )
            
            if salvar_dados(dados_banco):
                # Geração de PDF (Design Bloqueado)
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(190, 10, "RELATORIO DE MANUTENCAO TECNICA", 0, 1, 'C')
                
                pdf.set_font("Arial", 'B', 10); pdf.set_fill_color(240, 240, 240)
                pdf.cell(190, 8, " 1. DADOS DO CLIENTE", 1, 1, 'L', True)
                pdf.set_font("Arial", '', 9)
                pdf.cell(95, 7, clean(f"Cliente: {cliente}"), 1, 0)
                pdf.cell(95, 7, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 2. PERFORMANCE TERMICA", 1, 1, 'L', True)
                pdf.set_font("Arial", '', 9)
                pdf.cell(47, 7, clean(f"SH: {sh_val} K"), 1, 0); pdf.cell(47, 7, clean(f"SC: {sc_val} K"), 1, 0)
                pdf.cell(48, 7, clean(f"P.Suc: {p_suc} PSI"), 1, 0); pdf.cell(48, 7, clean(f"P.Liq: {p_liq} PSI"), 1, 1)

                pdf.ln(10)
                pdf.set_font("Arial", 'B', 10); pdf.cell(190, 8, " 3. DIAGNOSTICO IA", 1, 1, 'L', True)
                pdf.set_font("Arial", '', 9)
                pdf.multi_cell(190, 7, clean(diag_ia_resultado), 1)

                pdf_out = pdf.output(dest='S').encode('latin-1', 'ignore')
                st.download_button("📥 BAIXAR PDF", data=pdf_out, file_name=f"Relatorio_{cliente}.pdf")
                st.success("Relatório processado com sucesso!")

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    df = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # Formatação Brasileira de Data no Histórico
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
        
        st.data_editor(
            df,
            column_config={
                "data_visita": st.column_config.TextColumn("Data Visita"),
                "cliente": "Nome do Cliente",
                "sh": st.column_config.NumberColumn("SH (K)", format="%.1f"),
                "sc": st.column_config.NumberColumn("SC (K)", format="%.1f"),
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("O histórico está vazio.")

# Rodapé de Versão
st.markdown(f"<p style='text-align: center; color: gray;'>{NOME_APP} v{VERSAO} | 2026</p>", unsafe_allow_html=True)
