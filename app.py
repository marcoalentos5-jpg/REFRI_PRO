# ==============================================================================
# MPN - ENGENHARIA E DIAGNÓSTICO HVAC PRO
# PARTE 1: NÚCLEO DO SISTEMA, SEGURANÇA E BANCO DE DATA
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

# --- 1. CONFIGURAÇÃO DE AMBIENTE (LAYOUT BLOQUEADO) ---
st.set_page_config(
    page_title="MPN | Engenharia & Diagnóstico",
    layout="wide",
    page_icon="❄️",
    initial_sidebar_state="collapsed"
)

# --- 2. BANCO DE DADOS (31 CAMPOS REAIS) ---
def init_db():
    """
    Cria a estrutura do banco de dados SQLite. 
    A ordem dos campos é vital para a sincronização do relatório final.
    """
    try:
        conn = sqlite3.connect('banco_dados_mpn.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_visita TEXT, 
            cliente TEXT, 
            doc_cliente TEXT, 
            whatsapp TEXT, 
            celular TEXT, 
            fixo TEXT,
            endereco TEXT, 
            email TEXT, 
            marca TEXT, 
            modelo TEXT, 
            serie_evap TEXT, 
            linha TEXT, 
            capacidade TEXT, 
            serie_cond TEXT, 
            tecnologia TEXT, 
            fluido TEXT, 
            loc_evap TEXT, 
            sistema TEXT, 
            loc_cond TEXT, 
            v_rede REAL, 
            v_med REAL, 
            a_med REAL, 
            rla REAL, 
            lra REAL,
            p_suc REAL, 
            p_liq REAL, 
            sh REAL, 
            sc REAL, 
            problemas TEXT, 
            medidas TEXT, 
            observacoes TEXT
        )''')
        conn.commit()
    except Exception as e:
        st.error(f"Erro fatal ao inicializar banco: {e}")
    finally:
        conn.close()

def salvar_dados(dados):
    """
    Insere os 31 parâmetros no SQLite. 
    Qualquer falha na contagem da tupla impede a gravação.
    """
    if len(dados) != 31:
        st.error(f"Erro de integridade: Recebidos {len(dados)} campos, mas o sistema exige 31.")
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
        st.error(f"Erro na gravação: {e}")
        return False
    finally:
        conn.close()

init_db()

# --- 3. MOTOR TERMODINÂMICO (TABELAS PT EXPANDIDAS) ---
def get_tsat_global(psig, gas):
    """
    Realiza a interpolação linear baseada em tabelas de pressão-temperatura.
    As listas foram expandidas para cobrir faixas extremas de operação.
    """
    ancoras = {
        "R-410A": {
            "p": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 225, 250, 275, 300, 325, 350, 400, 450, 500, 550, 600],
            "t": [-51.0, -42.0, -34.0, -28.0, -22.0, -17.0, -12.5, -8.5, -5.0, -2.5, -0.3, 4.0, 8.0, 11.5, 15.0, 18.2, 22.0, 25.0, 28.5, 32.0, 35.2, 38.0, 44.0, 49.0, 54.0, 58.5, 63.0]
        },
        "R-32": {
            "p": [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700],
            "t": [-51.7, -17.5, 0.9, 10.9, 20.1, 27.9, 34.6, 40.6, 45.9, 50.8, 55.4, 59.5, 63.4, 67.2, 70.8]
        },
        "R-22": {
            "p": [0, 20, 40, 60, 80, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500],
            "t": [-40.8, -25.8, -15.0, -6.5, 0.2, 6.0, 12.5, 18.5, 24.0, 29.0, 33.5, 38.0, 42.0, 46.0, 53.0, 60.0, 66.0, 72.0]
        },
        "R-134a": {
            "p": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220],
            "t": [-26.1, -12.5, -3.2, 3.8, 9.5, 14.5, 19.0, 23.2, 27.0, 30.5, 33.8, 40.0, 45.5, 50.5, 55.2, 59.5, 63.5]
        }
    }
    if gas not in ancoras: return 0.0
    try:
        p_val = max(0, float(psig))
        return round(float(np.interp(p_val, ancoras[gas]["p"], ancoras[gas]["t"])), 2)
    except:
        return 0.0

def clean(txt):
    """Filtro de strings para evitar quebra de caracteres no PDF."""
    if not txt: return "N/A"
    txt = str(txt).replace('°', 'C').replace('º', '.').replace('ª', '.')
    nfkd = unicodedata.normalize('NFKD', txt)
    return "".join([c for c in nfkd if not unicodedata.category(c) == 'Mn'])

def seguro(v, default=0.0):
    """Validador numérico para impedir travamento do sistema por entrada inválida."""
    try: return float(v)
    except: return default

# --- 4. CSS CUSTOMIZADO (VISUAL PROFISSIONAL) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab-list"] button p { font-size: 19px; font-weight: bold; color: #333; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p { color: #004a99; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #004a99; font-weight: 700; }
    .stButton>button { width: 100%; border-radius: 6px; height: 3.2em; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)
# --- 5. INTERFACE PRINCIPAL ---
st.title("❄️ MPN | Engenharia & Diagnóstico")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

with tab_cad:
    st.subheader("👤 Identificação do Cliente")
    c1, c2, c3 = st.columns([2.5, 1.2, 1.4])
    with c1:
        cliente = st.text_input("Cliente / Empresa", placeholder="Nome completo ou Razão Social")
    with c2:
        doc_cliente = st.text_input("CPF / CNPJ")
    with c3:
        data_visita = st.date_input("📅 Data da Visita", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    whatsapp = c4.text_input("🟢 WhatsApp", value="21980264217")
    celular = c5.text_input("📱 Celular")
    tel_residencial = c6.text_input("📞 Fixo")

    st.markdown("---")
    st.subheader("📍 Localização do Serviço")
    e1, e2, e3, e4 = st.columns([0.6, 2.0, 0.5, 1.0])
    tipo_logr = e1.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    nome_logr = e2.text_input("Logradouro")
    numero = e3.text_input("Nº")
    complemento = e4.text_input("Bloco / Apto / Sala")
    
    e5, e6, e7 = st.columns([1.5, 1.0, 1.5])
    bairro = e5.text_input("Bairro")
    cep = e6.text_input("CEP")
    email_cli = e7.text_input("✉️ E-mail do Cliente")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        fabricante = st.text_input("Marca / Fabricante")
        modelo_eq = st.text_input("Modelo Geral")
        serie_evap = st.text_input("Nº Série Evaporadora")
    with g2:
        linha = st.text_input("Linha (Ex: Multi-Split)")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="12000")
        serie_cond = st.text_input("Nº Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit", "Chiller"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Localização Evap.")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Duto", "VRF", "Chiller"])
        loc_cond = st.text_input("Localização Cond.")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos")
    el1, el2, el3 = st.columns(3)
    
    with el1:
        st.markdown("**Tensões (V)**")
        v_rede = st.number_input("Tensão Nominal (V)", value=220.0, step=1.0)
        v_med = st.number_input("Tensão Medida (V)", value=220.0, step=1.0)
        diff_v = round(v_rede - v_med, 1)
        st.metric("Queda de Tensão", f"{diff_v} V", delta=f"{round((diff_v/v_rede)*100,1)}%", delta_color="inverse")
            
    with el2:
        st.markdown("**Correntes (A)**")
        rla_comp = st.number_input("Corrente Nominal (RLA)", value=5.0, step=0.1)
        a_med = st.number_input("Corrente Medida (Amp)", value=0.0, step=0.1)
        diff_a = round(a_med - rla_comp, 1)
        st.metric("Diferencial Amperagem", f"{diff_a} A")
        
    with el3:
        st.markdown("**Status de Carga**")
        lra_comp = st.number_input("Corrente de Partida (LRA)", value=0.0, step=0.1)
        carga_pct = (a_med / rla_comp * 100) if rla_comp > 0 else 0
        st.metric("Carga do Motor", f"{round(carga_pct, 1)} %")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico")
    tr1, tr2, tr3 = st.columns(3)
    
    with tr1:
        st.markdown("**Baixa Pressão (Sucção)**")
        p_suc = st.number_input("Pressão Sucção (PSI)", value=115.0, step=1.0)
        t_suc_tubo = st.number_input("Temp. Tubo Sucção (°C)", value=12.0, step=0.1)
        ts_suc = get_tsat_global(p_suc, fluido)
        st.metric("T-Sat Evaporação", f"{ts_suc} °C")
        
    with tr2:
        st.markdown("**Alta Pressão (Líquido)**")
        p_liq = st.number_input("Pressão Líquido (PSI)", value=340.0, step=1.0)
        t_liq_tubo = st.number_input("Temp. Tubo Líquido (°C)", value=32.0, step=0.1)
        ts_liq = get_tsat_global(p_liq, fluido)
        st.metric("T-Sat Condensação", f"{ts_liq} °C")
        
    with tr3:
        st.markdown("**Análise de Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        
        st.write("Superaquecimento (SH)")
        st.info(f"Calculado: {sh_val} K")
        st.write("Subresfriamento (SC)")
        st.success(f"Calculado: {sc_val} K")
# =============================================================
# PARTE 3: MOTOR DE DIAGNÓSTICO E INTELIGÊNCIA DE FALHAS
# =============================================================

with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico Assistido")
    
    # Inicialização de Containers de Diagnóstico
    diagnostico_ia = []
    probabilidades = {}
    contramedidas_lista = []

    # 1. Análise de Eficiência e Troca Térmica
    delta_evap = t_suc_tubo - ts_suc
    delta_cond = ts_liq - t_liq_tubo
    
    # 2. Lógica de Superaquecimento e Carga de Fluido
    if sh_val > 12:
        diagnostico_ia.append("Superaquecimento elevado detectado")
        probabilidades["Baixa carga de fluido / Vazamento"] = 85
        contramedidas_lista.append("Localizar vazamento e realizar carga por balança")
    elif sh_val < 4:
        diagnostico_ia.append("Superaquecimento baixo (Risco de Golpe)")
        probabilidades["Excesso de fluido ou Baixa troca no Evaporador"] = 80
        contramedidas_lista.append("Verificar limpeza de filtros e turbina da evaporadora")

    # 3. Análise de Subresfriamento e Condensação
    if sc_val > 12:
        probabilidades["Obstrução no dispositivo de expansão / Excesso"] = 70
    elif sc_val < 3:
        probabilidades["In eficiência de condensação ou falta de fluido"] = 65

    # 4. Análise Elétrica e Motor-Compressor
    if rla_comp > 0:
        if carga_pct > 115:
            diagnostico_ia.append("Motor operando em regime de sobrecarga")
            probabilidades["Alta pressão de descarga ou falha mecânica"] = 75
            contramedidas_lista.append("Revisar limpeza da condensadora e capacitores")
        elif 0 < carga_pct < 45:
            diagnostico_ia.append("Motor operando com carga muito baixa")
            probabilidades["Baixa compressão ou restrição na sucção"] = 60

    # 5. Lógica Específica Inverter / WindFree
    if tecnologia in ["Inverter", "WindFree"] and p_liq > 420:
        diagnostico_ia.append("Pressão de alta elevada para sistema Inverter")
        probabilidades["Limitador de frequência ativado por temperatura"] = 55

    # 6. Consolidação dos Resultados
    if not diagnostico_ia:
        diagnostico_ia.append("Sistema operando dentro dos parâmetros de projeto")
    
    diag_ia_txt = " | ".join(diagnostico_ia)
    
    # Ordenação do Ranking de Probabilidades
    if probabilidades:
        ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
        prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking])
    else:
        prob_txt = "Nenhuma anomalia crítica identificada"

    if not contramedidas_lista:
        contramedidas_lista.append("Realizar monitoramento periódico dos parâmetros")
    
    recom_final = " | ".join(contramedidas_lista)
    cop_est = round((delta_cond + 1.2) / (delta_evap + 1.2), 2) if delta_evap != -1.2 else 0

    # Interface Visual do Diagnóstico
    c_ia1, c_ia2 = st.columns(2)
    with c_ia1:
        st.info(f"**Análise do Sistema:**\n\n{diag_ia_txt}")
        st.warning(f"**Ranking de Suspeitas:**\n\n{prob_txt}")
    with c_ia2:
        st.success(f"**Contramedidas Sugeridas:**\n\n{recom_final}")
        st.metric("Eficiência Estável (COP)", cop_est)

    st.markdown("---")
    st.subheader("📄 Relatório Rápido")
    
    relatorio_whats = f"""*MPN - LAUDO TÉCNICO*
    
*Diagnóstico:* {diag_ia_txt}
*Suspeitas:* {prob_txt}
*Ações:* {recom_final}
*SH/SC:* {sh_val}K / {sc_val}K
*COP:* {cop_est}"""

    st.text_area("Cópia de Segurança do Relatório", relatorio_whats, height=140)
    
    st.markdown(f"""
        <button onclick="navigator.clipboard.writeText(`{relatorio_whats}`)"
        style="width:100%; padding:12px; background-color:#25d366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
        📋 Copiar para WhatsApp
        </button>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        executadas_in = st.text_area("🛠️ Medidas Executadas no Local", height=150)
    with col_med2:
        parecer_in = st.text_area("💡 Parecer Técnico Final", height=150)
# =============================================================
# PARTE 4: GERADOR DE PDF, PERSISTÊNCIA E HISTÓRICO
# =============================================================

    # Botão de Finalização (Ainda dentro do 'with tab_diag')
    if st.button("💾 FINALIZAR, SALVAR E GERAR PDF"):
        # Preparação dos 31 campos para o banco de dados
        endereco_full = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro} | CEP: {cep}"
        
        dados_final = (
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            endereco_full, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            diag_ia_txt, executadas_in, parecer_in
        )
        
        if salvar_dados(dados_final):
            # Construção do PDF Profissional
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 18)
            pdf.set_text_color(0, 74, 153)
            pdf.cell(190, 15, "RELATORIO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
            
            # Seção 1: Identificação
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 1. IDENTIFICACAO DO CLIENTE E LOCAL", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
            pdf.cell(40, 7, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1)
            pdf.cell(100, 7, clean(f"Cliente: {cliente}"), 1)
            pdf.cell(50, 7, clean(f"Doc: {doc_cliente}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereco: {endereco_full}"), 1, 1)
            
            # Seção 2: Dados do Equipamento e Medições
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 2. ESPECIFICACOES E MEDICOES TECNICAS", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(63, 7, clean(f"Marca: {fabricante}"), 1); pdf.cell(63, 7, clean(f"Capacidade: {cap_digitada}"), 1); pdf.cell(64, 7, clean(f"Fluido: {fluido}"), 1, 1)
            pdf.cell(47, 7, clean(f"V. Rede: {v_rede}V"), 1); pdf.cell(48, 7, clean(f"V. Med: {v_med}V"), 1); pdf.cell(47, 7, clean(f"A. Med: {a_med}A"), 1); pdf.cell(48, 7, clean(f"RLA: {rla_comp}A"), 1, 1)
            pdf.cell(95, 7, clean(f"Superaquecimento: {sh_val} K"), 1); pdf.cell(95, 7, clean(f"Subresfriamento: {sc_val} K"), 1, 1)
            
            # Seção 3: Diagnóstico e Parecer
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 3. ANALISE E PARECER TECNICO", 1, 1, 'L', True)
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Diagnostico do Sistema:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(f"{diag_ia_txt} | Probabilidades: {prob_txt}"), "LRB")
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Servicos Executados:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(executadas_in), "LRB")
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Parecer e Recomendacoes:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(parecer_in), "LRB")

            # Assinaturas
            pdf.ln(15)
            y_final = pdf.get_y()
            pdf.line(20, y_final, 85, y_final); pdf.line(105, y_final, 170, y_final)
            pdf.set_font("Arial", 'B', 7)
            pdf.set_xy(20, y_final + 1); pdf.cell(65, 4, "RESPONSAVEL TECNICO", 0, 0, 'C')
            pdf.set_xy(105, y_final + 1); pdf.cell(65, 4, "CIENTE / CLIENTE", 0, 0, 'C')

            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar Laudo PDF", data=pdf_bytes, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
            st.success("✅ Atendimento registrado com sucesso no banco de dados!")

with tab_hist:
    st.subheader("📜 Histórico de Manutenções")
    try:
        conn = sqlite3.connect('banco_dados_mpn.db')
        df_historico = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC", conn)
        conn.close()
        
        if not df_historico.empty:
            # Conversão para formato brasileiro de data (DD/MM/YYYY)
            df_historico['data_visita'] = pd.to_datetime(df_historico['data_visita']).dt.strftime('%d/%m/%Y')
            df_historico.insert(0, "Excluir", False)
            
            busca_termo = st.text_input("🔍 Pesquisar por Cliente ou Data", placeholder="Ex: Março ou Nome do Cliente")
            if busca_termo:
                df_historico = df_historico[df_historico['cliente'].str.contains(busca_termo, case=False) | df_historico['data_visita'].str.contains(busca_termo)]

            editor_h = st.data_editor(df_historico, hide_index=True, use_container_width=True, 
                                      column_config={"Excluir": st.column_config.CheckboxColumn("Selecionar"), "id": None})
            
            if st.button("🗑️ Remover Registros Selecionados"):
                ids_excluir = editor_h[editor_h["Excluir"] == True]["id"].tolist()
                if ids_excluir:
                    conn = sqlite3.connect('banco_dados_mpn.db')
                    for d_id in ids_excluir:
                        conn.execute("DELETE FROM atendimentos WHERE id = ?", (d_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
        else:
            st.info("Nenhum registro encontrado no banco de dados.")
    except Exception as err:
        st.error(f"Erro ao carregar histórico: {err}")
