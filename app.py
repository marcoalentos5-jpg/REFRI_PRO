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
    # Mantendo a estrutura, mas garantindo compatibilidade de nomes
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
    # BUG FIX: Garantindo que o número de argumentos bata com as colunas da tabela
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
    # Melhoria no encoding para PDF (FPDF1 compatibilidade)
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

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
        # Novidade: Alerta de queda de tensão acima de 10%
        st.write("Queda de Tensão")
        if abs(diff_v) > (v_rede * 0.1): st.error(f"{diff_v} V")
        else: st.success(f"{diff_v} V")
        
    with el2:
        rla_comp = st.number_input("Corrente RLA (A)", value=1.0)
        a_med = st.number_input("Corrente Medida (A)", value=0.0)
        # Novidade: Potência Aparente Calculada VA
        va_total = round(v_med * a_med, 1)
        st.write("Potência Aparente (VA)")
        st.info(f"{va_total} VA")

    with el3:
        lra_comp = st.number_input("LRA (A)", value=0.0)
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença A vs RLA")
        if a_med > rla_comp: st.warning(f"+ {diff_a} A")
        else: st.success(f"{diff_a} A")

# Interrompendo aqui conforme sua solicitação (até o fim da aba elétrica/início termo)

        # DESIGN DO RELATÓRIO (BLOQUEADO)
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO DO CLIENTE E CONTATO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
        pdf.cell(45, 6, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 0)
        pdf.cell(100, 6, clean(f"Cliente: {cliente}"), 1, 0)
        pdf.cell(45, 6, clean(f"CPF/CNPJ: {doc_cliente}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {endereco_completo}"), 1, 1)
        pdf.cell(63, 6, clean(f"Wpp: {whatsapp}"), 1, 0); pdf.cell(63, 6, clean(f"Cel: {celular}"), 1, 0); pdf.cell(64, 6, clean(f"Fixo: {tel_residencial}"), 1, 1)
        pdf.cell(190, 6, clean(f"E-mail: {email_cli}"), 1, 1); pdf.ln(4)

        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. ESPECIFICACOES DO EQUIPAMENTO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.cell(63, 6, clean(f"Marca: {fabricante}"), 1, 0); pdf.cell(63, 6, clean(f"Modelo: {modelo_eq}"), 1, 0); pdf.cell(64, 6, clean(f"Linha: {linha}"), 1, 1)
        pdf.cell(63, 6, clean(f"Cap: {cap_digitada} BTU/h"), 1, 0); pdf.cell(63, 6, clean(f"Tec: {tecnologia}"), 1, 0); pdf.cell(64, 6, clean(f"Gas: {fluido}"), 1, 1)
        pdf.cell(95, 6, clean(f"Sistema: {tipo_eq}"), 1, 0); pdf.cell(95, 6, clean(f"Local Evap: {loc_evap}"), 1, 1)
        pdf.cell(95, 6, clean(f"Serie Evap: {serie_evap}"), 1, 0); pdf.cell(95, 6, clean(f"Local Cond: {loc_cond}"), 1, 1)
        pdf.cell(190, 6, clean(f"Serie Cond: {serie_cond}"), 1, 1); pdf.ln(4)

        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 3. ANALISE TECNICA E PERFORMANCE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_fill_color(240, 240, 240)
        pdf.cell(38, 6, clean(f"Rede: {v_rede}V"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(38, 6, clean(f"Med: {v_med}V"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(38, 6, clean(f"Dif: {diff_v}V"), 1, 0); pdf.cell(38, 6, clean(f"RLA: {rla_comp}A"), 1, 0); pdf.cell(38, 6, clean(f"LRA: {lra_comp}A"), 1, 1)
        pdf.set_font("Arial", 'B', 9); pdf.cell(95, 6, clean(f"Corrente Medida: {a_med} A"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(95, 6, clean(f"Diferenca Corrente: {diff_a} A"), 1, 1)
        pdf.cell(63, 6, clean(f"P-Suc: {p_suc} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Suc: {ts_suc}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Suc: {t_suc_tubo}C"), 1, 1)
        pdf.cell(63, 6, clean(f"P-Liq: {p_liq} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Liq: {ts_liq}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Liq: {t_liq_tubo}C"), 1, 1)
        pdf.set_font("Arial", 'B', 9); pdf.cell(95, 7, clean(f"SUPERAQUECIMENTO (SH): {sh_val} K"), 1, 0); pdf.cell(95, 7, clean(f"SUBRESFRIAMENTO (SC): {sc_val} K"), 1, 1); pdf.ln(4)

        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 4. DIAGNOSTICO E PARECER FINAL", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Problemas Encontrados:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(prob_txt), "LRB")
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Medidas Executadas pelo Tecnico:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(executadas_input if executadas_input else "Nenhuma medida descrita"), "LRB")
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Parecer Tecnico e Observacoes:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(obs_tecnico if obs_tecnico else "Sem observacoes adicionais"), "LRB")

        pdf.ln(25); y_pos = pdf.get_y(); pdf.line(20, y_pos, 90, y_pos); pdf.line(120, y_pos, 190, y_pos)
        pdf.set_xy(20, y_pos + 1); pdf.set_font("Arial", 'B', 8); pdf.cell(70, 4, "Marcos Alexandre Almeida do Nascimento", 0, 1, 'C')
        pdf.set_x(20); pdf.set_font("Arial", '', 8); pdf.cell(70, 4, "CNPJ 51.274.762/0001-17", 0, 1, 'C')
        pdf.set_xy(120, y_pos + 1); pdf.set_font("Arial", 'B', 8); pdf.cell(70, 4, clean(f"{cliente}"), 0, 1, 'C')
        pdf.set_x(120); pdf.set_font("Arial", '', 8); pdf.cell(70, 4, "Cliente", 0, 1, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 Baixar Relatorio PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
        st.toast("✅ Relatório gerado com sucesso!")
with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    # Novidade: Trazendo mais campos para análise rápida no histórico
    query = "SELECT id, data_visita, cliente, marca, modelo, tecnologia, v_med, a_med, sh, sc FROM atendimentos ORDER BY id DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        # Correção: Tratamento de erro na conversão de data
        df['data_visita'] = pd.to_datetime(df['data_visita'], errors='coerce').dt.date
        
        f_col1, f_col2 = st.columns(2)
        with f_col1: 
            busca = st.text_input("🔍 Pesquisar por Cliente", placeholder="Digite o nome...", key="busca_hist")
        with f_col2: 
            # Garantindo que o filtro de data brasileira funcione mesmo com datas nulas
            min_date = df['data_visita'].min() if pd.notnull(df['data_visita'].min()) else date.today()
            max_date = df['data_visita'].max() if pd.notnull(df['data_visita'].max()) else date.today()
            periodo = st.date_input("📅 Filtrar por Período", 
                                    value=[min_date, max_date],
                                    format="DD/MM/YYYY") 
        
        # Filtro de Busca Insensível
        if busca:
            df = df[df['cliente'].apply(lambda x: remover_acentos(busca) in remover_acentos(str(x)))]
            
        if len(periodo) == 2:
            df = df[(df['data_visita'] >= periodo[0]) & (df['data_visita'] <= periodo[1])]
        
        df.insert(0, "Selecionar", False)
        
        # Novidade: Configuração de colunas mais rica
        df_editado = st.data_editor(
            df, 
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Excluir?", help="Marque para deletar", default=False),
                "data_visita": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "v_med": st.column_config.NumberColumn("Tensão (V)", format="%d V"),
                "a_med": st.column_config.NumberColumn("Corr. (A)", format="%.1f A"),
                "id": None 
            },
            disabled=["data_visita", "cliente", "marca", "modelo", "tecnologia", "sh", "sc", "v_med", "a_med"],
            hide_index=True,
            use_container_width=True,
            key="historico_editor_main"
        )
        
        if st.button("🗑️ Excluir Relatórios Selecionados"):
            ids_para_excluir = df_editado[df_editado["Selecionar"] == True]["id"].tolist()
            if ids_para_excluir:
                conn = sqlite3.connect('banco_dados.db')
                c = conn.cursor()
                for id_del in ids_para_excluir:
                    c.execute("DELETE FROM atendimentos WHERE id = ?", (id_del,))
                conn.commit()
                conn.close()
                st.success(f"✅ {len(ids_para_excluir)} registro(s) removido(s)!")
                st.rerun()
            else:
                st.warning("⚠️ Selecione ao menos um relatório para excluir.")
    else:
        st.info("Nenhum atendimento registrado no histórico.")

# =========================================================
# 4. MOTOR DE PROTEÇÃO E CÁLCULOS (ESTRUTURA BLOQUEADA)
# =========================================================

def seguro(v):
    try:
        if v is None: return 0.0
        return float(v)
    except: return 0.0

# Novidade: Sincronização automática com variáveis globais da Parte 1
sh_val = seguro(sh_val); sc_val = seguro(sc_val)
p_suc = seguro(p_suc); p_liq = seguro(p_liq)
t_suc_tubo = seguro(t_suc_tubo); ts_suc = seguro(ts_suc)
t_liq_tubo = seguro(t_liq_tubo); ts_liq = seguro(ts_liq)
a_med = seguro(a_med); rla_comp = seguro(rla_comp); diff_v = seguro(diff_v)

# =========================================================
# 5. MOTOR DE DIAGNÓSTICO HVAC INTELIGENTE
# =========================================================

diagnostico = []; probabilidades = {}

def registrar(msg, falha=None, prob=0):
    diagnostico.append(msg)
    if falha:
        probabilidades[falha] = prob

# --- CÁLCULO EFICIÊNCIA (COP APROXIMADO) ---
try:
    if a_med > 0.5: # Só calcula COP se a máquina estiver operando
        delta_cond = ts_liq - t_liq_tubo
        delta_evap = t_suc_tubo - ts_suc
        cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)

        if cop_aprox < 1.5:
            registrar("Baixa eficiência energética detectada", "Sujeira ou Obstrução", 45)
        elif cop_aprox > 4.5:
            registrar("Eficiência térmica excepcional", None, 0)
    else:
        cop_aprox = 0.0
except:
    cop_aprox = 0.0

# --- LÓGICA DE SOBRECARGA ELÉTRICA (NOVIDADE) ---
if rla_comp > 0 and a_med > (rla_comp * 1.15):
    registrar("Sobrecorrente detectada (15% acima do RLA)", "Compressor sobrecarregado", 85)

if abs(diff_v) > 20:
    registrar(f"Instabilidade de tensão crítica: {diff_v}V", "Problema na Rede Elétrica", 90)

# =========================================================
# 6. CONSOLIDADO DE FALHAS
# =========================================================

if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parâmetros ideais")

diag_ia = " | ".join(diagnostico)

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma anomalia crítica detectada"
# =========================================================
# 5. MOTOR DE INTELIGÊNCIA HVAC (PROCESSAMENTO)
# =========================================================

# --- EFICIENCIA EVAPORADOR ---
delta_evap = t_suc_tubo - ts_suc
if delta_evap < 2 and a_med > 0.5:
    registrar("Baixa troca de calor no evaporador", "Fluxo de ar insuficiente ou sujeira", 60)

# --- EFICIENCIA CONDENSADOR ---
delta_cond = ts_liq - t_liq_tubo
if delta_cond < 2 and a_med > 0.5:
    registrar("Condensação ineficiente", "Ventilação obstruída ou condensador sujo", 55)

# --- ANÁLISE DO COMPRESSOR (CARGA) ---
if rla_comp > 0 and a_med > 0:
    carga_pct = (a_med / rla_comp) * 100
    if carga_pct > 120:
        registrar("Compressor em sobrecarga elétrica", "Alta pressão ou excesso de fluido", 75)
    elif carga_pct < 40:
        registrar("Compressor operando em subcarga", "Baixa carga térmica ou falta de fluido", 60)

# --- ANÁLISE DE COMPRESSÃO MECÂNICA ---
if p_suc > 140 and p_liq < 300 and fluido in ["R-410A", "R-32"]:
    registrar("Baixa performance de compressão", "Compressor com desgaste mecânico", 70)

# --- TENSAO ELETRICA ---
if abs(diff_v) > 15:
    registrar("Variação crítica de tensão detectada", "Instabilidade na Rede Elétrica", 85)

# --- LÓGICA ESPECÍFICA INVERTER ---
if tecnologia == "Inverter":
    if sh_val < 2:
        registrar("Superaquecimento baixo (Risco de Golpe)", "Ajuste de expansão ou sensor", 45)
    if p_liq > 420:
        registrar("Limitação de frequência por alta pressão", "Alta temperatura de condensação", 50)

# =========================================================
# 6. CONSOLIDAÇÃO DOS RESULTADOS (PÓS-PROCESSAMENTO)
# =========================================================

if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parâmetros nominais")

diag_ia = " | ".join(diagnostico)

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha crítica detectada"

# --- CONTRAMEDIDAS AUTOMÁTICAS ---
contramedidas = []
for falha in probabilidades:
    falha_l = falha.lower()
    if "refrigerante" in falha_l or "fluido" in falha_l:
        contramedidas.append("Verificar carga de fluido e buscar vazamentos")
    if "condensador" in falha_l:
        contramedidas.append("Realizar limpeza química do condensador")
    if "evaporador" in falha_l or "fluxo de ar" in falha_l:
        contramedidas.append("Limpar filtros e serpentina da evaporadora")
    if "compressor" in falha_l:
        contramedidas.append("Medir isolamento e pressões de descarga")
    if "rede eletrica" in falha_l:
        contramedidas.append("Revisar aperto de bornes e tensão de entrada")

if not contramedidas:
    contramedidas.append("Manter plano de manutenção preventiva mensal")

contramedidas_txt = " | ".join(list(set(contramedidas))) # Remove duplicados

# =========================================================
# 7. EXIBIÇÃO E RELATÓRIO FINAL
# =========================================================

relatorio_txt = f"""RELATÓRIO TÉCNICO HVAC - MPN
-------------------------------------------
DIAGNÓSTICO IA: {diag_ia}
PROBABILIDADE DE FALHAS: {prob_txt}
CONTRAMEDIDAS: {contramedidas_txt}
EFICIÊNCIA (COP): {cop_aprox}
-------------------------------------------
Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"""

st.header("🤖 DIAGNÓSTICO FINAL")

c1, c2 = st.columns(2)
with c1:
    st.info(f"### 🔎 Análise do Sistema\n{diag_ia}")
    st.warning(f"### 📊 Probabilidades\n{prob_txt}")
with c2:
    st.success(f"### 🛠️ Contramedidas\n{contramedidas_txt}")
    st.metric("Eficiência Estimada (COP)", cop_aprox)

st.write("### 📄 Relatório Consolidado")
st.text_area("Texto para Copiar/Colar", relatorio_txt, height=200, key="relatorio_final_area")

# Botão de Cópia (Layout original preservado)
st.markdown(
    f"""<button onclick="navigator.clipboard.writeText(`{relatorio_txt}`)" 
    style="width:100%; padding:10px; background-color:#2e7d32; color:white; border:none; border-radius:5px; cursor:pointer;">
    📋 Copiar Relatório para o WhatsApp</button>""", 
    unsafe_allow_html=True
)
