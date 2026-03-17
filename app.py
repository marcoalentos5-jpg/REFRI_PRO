import streamlit as st
import numpy as np
from datetime import date, datetime
from fpdf import FPDF
import io
import sqlite3
import pandas as pd
import unicodedata

# --- 0. BANCO DE DADOS (ESTRUTURA BLOQUEADA & AMPLIADA) ---
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
    # Sincronização rigorosa: 31 placeholders para 31 campos
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
    try: return float(v) if v is not None else 0.0
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
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."], key="f_tlog")
    nome_logr, numero, complemento, bairro, cep, email_cli = e2.text_input("Logradouro", key="f_nlog"), e3.text_input("Nº", key="f_num"), e4.text_input("Comp.", key="f_comp"), e5.text_input("Bairro", key="f_bai"), e6.text_input("CEP", key="f_cep"), e7.text_input("✉️ E-mail", key="f_mail")
    
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
        v_rede = st.number_input("Tensão Nominal da Rede (V)", value=220.0, key="v_nom")
        v_med = st.number_input("Tensão Medida (V)", value=218.0, key="v_real")
        diff_v = round(v_rede - v_med, 1)
        st.write("Diferença de Tensão")
        if abs(diff_v) > 15:
            st.error(f"{diff_v} V - Fora dos 7%")
        else:
            st.success(f"{diff_v} V - Estável")
            
    with el2:
        rla_comp = st.number_input("Corrente Nominal RLA (A)", value=1.0, key="rla_nom")
        a_med = st.number_input("Corrente Medida (A)", value=0.0, key="a_real")
        diff_a = round(a_med - rla_comp, 1)
        st.write("Diferença de Corrente")
        st.info(f"{diff_a} A")
        
    with el3:
        lra_comp = st.number_input("Corrente de Partida LRA (A)", value=0.0, key="lra_nom")
        st.write("Status de Carga")
        if rla_comp > 0:
            carga_pct = (a_med / rla_comp) * 100
            st.metric("Carga do Compressor", f"{round(carga_pct, 1)} %")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Performance")
    tr1, tr2, tr3 = st.columns(3)
    with tr1:
        st.markdown("**Lado de Baixa (Sucção)**")
        p_suc = st.number_input("Pressão de Sucção (PSI)", value=118.0, key="ps_in")
        t_suc_tubo = st.number_input("Temperatura Tubo Sucção (°C)", value=12.0, key="ts_in")
        ts_suc = get_tsat_global(p_suc, fluido)
        st.metric("T-Sat Sucção", f"{ts_suc} °C")
        
    with tr2:
        st.markdown("**Lado de Alta (Líquido)**")
        p_liq = st.number_input("Pressão de Líquido (PSI)", value=345.0, key="pl_in")
        t_liq_tubo = st.number_input("Temperatura Tubo Líquido (°C)", value=30.0, key="tl_in")
        ts_liq = get_tsat_global(p_liq, fluido)
        st.metric("T-Sat Líquido", f"{ts_liq} °C")
        
    with tr3:
        st.markdown("**Análise Termodinâmica**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        st.write("Superaquecimento (SH)")
        st.success(f"{sh_val} K")
        st.write("Subresfriamento (SC)")
        st.success(f"{sc_val} K")

# =============================
# MOTOR DE DIAGNÓSTICO IA (PARTE 3 INTEGRADA)
# =============================
diagnostico = []
probabilidades = {}

def registrar(msg, falha=None, prob=0):
    if msg not in diagnostico:
        diagnostico.append(msg)
    if falha:
        probabilidades[falha] = prob

# 1. Eficiência por COP Aproximado
try:
    delta_cond = ts_liq - t_liq_tubo
    delta_evap = t_suc_tubo - ts_suc
    cop_aprox = round((delta_cond + 1) / (delta_evap + 1), 2)
    if cop_aprox < 1.5:
        registrar("Baixa eficiencia energetica do sistema", "Falha de Troca Térmica", 70)
    elif cop_aprox > 4:
        registrar("Sistema operando com alta eficiencia")
except:
    cop_aprox = 0

# 2. Análise de Eficiência Evaporador/Condensador
if delta_evap < 2:
    registrar("Baixa transferencia de calor no evaporador", "Fluxo de ar insuficiente", 60)
if delta_cond < 2:
    registrar("Condensacao ineficiente", "Ventilacao insuficiente", 55)

# 3. Análise de Compressor e Carga
if rla_comp > 0:
    carga_pct = (a_med / rla_comp) * 100
    if carga_pct > 120:
        registrar("Compressor sobrecarregado", "Excesso de fluido ou Alta Pressão", 65)
    elif carga_pct < 40 and a_med > 0:
        registrar("Compressor operando com carga muito baixa", "Baixa carga termica", 60)

if p_suc > 140 and p_liq < 300 and fluido == "R-410A":
    registrar("Possivel perda de compressao", "Compressor desgastado", 70)

# 4. Análise Elétrica e Inverter
if abs(diff_v) > 10:
    registrar("Variacao significativa de tensao", "Problema na rede eletrica", 80)

if tecnologia == "Inverter":
    if sh_val < 2:
        registrar("Controle inverter possivelmente modulando excessivamente", "Ajuste de controle do compressor", 40)
    if p_liq > 420:
        registrar("Possivel limitacao de frequencia por alta pressao", "Alta pressao de condensacao", 50)

# Consolidação Final do Diagnóstico IA
if not diagnostico:
    diagnostico.append("Sistema operando dentro dos parametros")

diag_ia = " | ".join(diagnostico)

if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt = "Nenhuma falha critica detectada"

# Contramedidas Automáticas
contramedidas = []
for falha in probabilidades:
    f_lower = falha.lower()
    if "refrigerante" in f_lower or "fluido" in f_lower:
        contramedidas.append("Verificar carga de refrigerante e possiveis vazamentos")
    if "condensador" in f_lower or "ventilação" in f_lower:
        contramedidas.append("Limpar condensador e verificar motor ventilador")
    if "evaporador" in f_lower or "fluxo" in f_lower:
        contramedidas.append("Limpar evaporador e filtros de ar")
    if "compressor" in f_lower:
        contramedidas.append("Verificar eficiencia mecanica e oleo do compressor")
    if "rede eletrica" in f_lower or "tensao" in f_lower:
        contramedidas.append("Revisar quadro eletrico e apertos de bornes")

if not contramedidas:
    contramedidas.append("Nenhuma acao corretiva necessaria no momento")
contramedidas_txt = " | ".join(contramedidas)
with tab_diag:
    st.header("DIAGNÓSTICO E PARECER IA")
    
    # Grid Superior: Diagnóstico e Observações
    col_ia, col_man = st.columns(2)
    with col_ia:
        st.subheader("🤖 Diagnóstico IA")
        st.info(f"**Análise de Ciclo:** {diag_ia}")
        st.warning(f"**Probabilidades:** {prob_txt}")
        st.success(f"**Contramedidas:** {contramedidas_txt}")
        st.metric("Eficiência (COP)", cop_aprox)
        
    with col_man:
        st.subheader("📝 Observações e Problemas (Manual)")
        p_sel = []
        opcoes = ["Vazamento de Fluido", "Baixa Carga de Fluido", "Excesso de Fluido", "Ar/Incondensaveis no Ciclo", 
                  "Obstrucao Dispositivo Expansao", "Colmeia Congelando", "Filtro Secador Obstruido", 
                  "Compressor Sem Compressao", "Falha na Ventilacao", "Falha na Placa Inverter", 
                  "Instabilidade na Rede Eletrica", "Evaporadora Pingando"]
        
        # Checkbox em 2 colunas internas
        pi1, pi2 = st.columns(2)
        for i, opt in enumerate(opcoes):
            if i % 2 == 0:
                if pi1.checkbox(opt, key=f"chk_{i}"): p_sel.append(opt)
            else:
                if pi2.checkbox(opt, key=f"chk_{i}"): p_sel.append(opt)

    st.markdown("---")
    
    # Seção de Texto Livre e Relatório Rápido
    col_exec, col_relat = st.columns(2)
    with col_exec:
        st.subheader("📋 Medidas Executadas")
        executadas_input = st.text_area("Descreva o que foi feito no local:", height=150, key="exec_txt")
        obs_tecnico = st.text_area("Parecer Técnico Final:", height=100, key="obs_final")
        
    with col_relat:
        st.subheader("📄 Relatório para Cópia (WhatsApp)")
        relatorio_txt = f"""*RELATÓRIO TÉCNICO HVAC*
        
*Diagnóstico IA:* {diag_ia}
*Falhas:* {prob_txt}
*Recomendação:* {contramedidas_txt}
*COP:* {cop_aprox}"""
        
        st.text_area("Conteúdo do Relatório", relatorio_txt, height=180, key="rel_area")
        st.markdown(f"""
            <button onclick="navigator.clipboard.writeText(`{relatorio_txt}`)"
            style="width:100%; padding:10px; background-color:#25d366; color:white; border:none; border-radius:5px; cursor:pointer;">
            📋 Copiar para WhatsApp
            </button>
        """, unsafe_allow_html=True)

    # Botão de Gerar PDF e Salvar no Banco
    if st.button("💾 SALVAR ATENDIMENTO E GERAR PDF"):
        prob_manual = ', '.join(p_sel) if p_sel else 'Nenhum'
        endereco_completo = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro} | CEP: {cep}"
        
        # Consolidação dos 31 campos (Ordem idêntica ao init_db)
        dados_banco = (
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            endereco_completo, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            f"IA: {diag_ia} | Manual: {prob_manual}", executadas_input, obs_tecnico
        )
        
        salvar_dados(dados_banco)
        
        # GERAÇÃO DO PDF (LAYOUT BLOQUEADO)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 20); pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 15, "Relatorio Tecnico de Manutencao", 0, 1, 'C'); pdf.ln(5)

        # 1. IDENTIFICAÇÃO
        pdf.set_fill_color(230, 230, 230); pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 1. IDENTIFICACAO DO CLIENTE E CONTATO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
        pdf.cell(45, 6, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 0)
        pdf.cell(100, 6, clean(f"Cliente: {cliente}"), 1, 0)
        pdf.cell(45, 6, clean(f"CPF/CNPJ: {doc_cliente}"), 1, 1)
        pdf.cell(190, 6, clean(f"Endereco: {endereco_completo}"), 1, 1); pdf.ln(4)

        # 2. ESPECIFICAÇÕES
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 2. ESPECIFICACOES DO EQUIPAMENTO", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        pdf.cell(63, 6, clean(f"Marca: {fabricante}"), 1, 0); pdf.cell(63, 6, clean(f"Modelo: {modelo_eq}"), 1, 0); pdf.cell(64, 6, clean(f"Linha: {linha}"), 1, 1)
        pdf.cell(63, 6, clean(f"Cap: {cap_digitada} BTU/h"), 1, 0); pdf.cell(63, 6, clean(f"Tec: {tecnologia}"), 1, 0); pdf.cell(64, 6, clean(f"Gas: {fluido}"), 1, 1); pdf.ln(4)

        # 3. ANÁLISE TÉCNICA
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 3. ANALISE TECNICA E PERFORMANCE", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9); pdf.set_fill_color(240, 240, 240)
        pdf.cell(95, 6, clean(f"Corrente Medida: {a_med} A"), 1, 0, True); pdf.cell(95, 6, clean(f"Diferenca Corrente: {diff_a} A"), 1, 1)
        pdf.cell(95, 7, clean(f"SUPERAQUECIMENTO (SH): {sh_val} K"), 1, 0); pdf.cell(95, 7, clean(f"SUBRESFRIAMENTO (SC): {sc_val} K"), 1, 1); pdf.ln(4)

        # 4. DIAGNÓSTICO
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 4. DIAGNOSTICO E PARECER FINAL", 1, 1, 'L', True)
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Problemas Encontrados:", "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(f"{diag_ia} | {prob_manual}"), "LRB")
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Medidas Executadas:", "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(executadas_input), "LRB")

        # ASSINATURAS
        pdf.ln(20); y_pos = pdf.get_y(); pdf.line(20, y_pos, 90, y_pos); pdf.line(120, y_pos, 190, y_pos)
        pdf.set_xy(20, y_pos + 1); pdf.set_font("Arial", 'B', 8); pdf.cell(70, 4, "Marcos Alexandre Almeida do Nascimento", 0, 1, 'C')
        pdf.set_xy(120, y_pos + 1); pdf.cell(70, 4, clean(cliente), 0, 1, 'C')

        pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button("📥 Baixar Relatório PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
        st.toast("✅ Relatório gerado e salvo no banco!")

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos")
    conn = sqlite3.connect('banco_dados.db')
    df_h = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, tecnologia, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    
    if not df_h.empty:
        df_h['data_visita'] = pd.to_datetime(df_h['data_visita']).dt.strftime('%d/%m/%Y')
        df_h.insert(0, "Selecionar", False)
        
        # Filtros de Busca
        f_c1, f_c2 = st.columns(2)
        with f_c1: busca_h = st.text_input("🔍 Pesquisar Cliente", key="search_h")
        if busca_h: df_h = df_h[df_h['cliente'].str.contains(busca_h, case=False)]

        editado = st.data_editor(df_h, hide_index=True, use_container_width=True, 
                                 column_config={"Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False),
                                                "id": None}, key="editor_h")
        
        if st.button("🗑️ Excluir Selecionados"):
            ids_del = editado[editado["Selecionar"] == True]["id"].tolist()
            if ids_del:
                conn = sqlite3.connect('banco_dados.db')
                for d in ids_del: conn.execute("DELETE FROM atendimentos WHERE id = ?", (d,))
                conn.commit(); conn.close()
                st.rerun()
    else:
        st.info("Nenhum atendimento registrado.")
