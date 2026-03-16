import streamlit as st
import numpy as np
import math
from datetime import date, datetime
from fpdf import FPDF
import sqlite3
import pandas as pd
import unicodedata
import io
import urllib.parse

# --- 0. BANCO DE DADOS (ESTRUTURA INTEGRADA) ---
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

# --- 1. CONFIGURAÇÃO DA PÁGINA E CSS (FIX DE SINTAXE) ---
st.set_page_config(page_title="MPN | Engenharia Pro", layout="wide", page_icon="❄️")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. UTILITÁRIOS E MOTOR TERMODINÂMICO ---
def remover_acentos(texto):
    if not texto: return ""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn').lower()

def clean(txt):
    if not txt: return "N/A"
    replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ã': 'a', 'õ': 'o', 'ç': 'c', 
                    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ã': 'A', 'Õ': 'O', 'Ç': 'C', '°': 'C', 'º': '.'}
    res = str(txt)
    for old, new in replacements.items(): res = res.replace(old, new)
    return res.encode('ascii', 'ignore').decode('ascii')

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

# --- 3. INTERFACE ---
st.title("❄️ MPN | Engenharia & Diagnóstico")
tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs(["📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"])

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
        # --- GERAÇÃO DO PDF (PRIMEIRA METADE) ---
        pdf = FPDF()
        pdf.add_page()
        
        # Logo e Título
        try: pdf.image("logo.png", 10, 8, 50)
        except: pass
        
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(190, 15, "Relatorio Tecnico", 0, 1, 'C')
        pdf.ln(10)

        # 1. IDENTIFICAÇÃO (DESIGN BLOQUEADO)
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", 'B', 10)
        pdf.set_text_color(0)
        pdf.cell(190, 7, " 1. IDENTIFICACAO DO CLIENTE E CONTATO", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 9)
        pdf.cell(45, 6, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 0)
        pdf.cell(100, 6, clean(f"Cliente: {cliente}"), 1, 0)
        pdf.cell(45, 6, clean(f"CPF/CNPJ: {doc_cliente}"), 1, 1)
        
        pdf.cell(190, 6, clean(f"Endereco: {endereco_completo}"), 1, 1)
        
        pdf.cell(63, 6, clean(f"Wpp: {whatsapp}"), 1, 0)
        pdf.cell(63, 6, clean(f"Cel: {celular}"), 1, 0)
        pdf.cell(64, 6, clean(f"Fixo: {tel_residencial}"), 1, 1)
        
        pdf.cell(190, 6, clean(f"E-mail: {email_cli}"), 1, 1)
        pdf.ln(4)

        # 2. EQUIPAMENTO (DESIGN BLOQUEADO)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 2. ESPECIFICACOES DO EQUIPAMENTO", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 9)
        pdf.cell(63, 6, clean(f"Marca: {fabricante}"), 1, 0)
        pdf.cell(63, 6, clean(f"Modelo: {modelo_eq}"), 1, 0)
        pdf.cell(64, 6, clean(f"Linha: {linha}"), 1, 1)
        
        pdf.cell(63, 6, clean(f"Cap: {cap_digitada} BTU/h"), 1, 0)
        pdf.cell(63, 6, clean(f"Tec: {tecnologia}"), 1, 0)
        pdf.cell(64, 6, clean(f"Gas: {fluido}"), 1, 1)
        
        pdf.cell(95, 6, clean(f"Sistema: {tipo_eq}"), 1, 0)
        pdf.cell(95, 6, clean(f"Local Evap: {loc_evap}"), 1, 1)
        
        pdf.cell(95, 6, clean(f"Serie Evap: {serie_evap}"), 1, 0)
        pdf.cell(95, 6, clean(f"Local Cond: {loc_cond}"), 1, 1)
        
        pdf.cell(190, 6, clean(f"Serie Cond: {serie_cond}"), 1, 1)
        pdf.ln(4)
        
        # Variável temporária para continuação na Parte 3
        st.session_state['pdf_em_geracao'] = pdf
       # --- CONTINUAÇÃO DO PDF (PARTE 3: PERFORMANCE E DIAGNÓSTICO) ---
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(190, 7, " 3. ANALISE TECNICA E PERFORMANCE", 1, 1, 'L', True)
        
        pdf.set_font("Arial", '', 9); pdf.set_fill_color(240, 240, 240)
        pdf.cell(38, 6, clean(f"Rede: {v_rede}V"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(38, 6, clean(f"Med: {v_med}V"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(38, 6, clean(f"Dif: {diff_v}V"), 1, 0)
        pdf.cell(38, 6, clean(f"RLA: {rla_comp}A"), 1, 0)
        pdf.cell(38, 6, clean(f"LRA: {lra_comp}A"), 1, 1)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(95, 6, clean(f"Corrente Medida: {a_med} A"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(95, 6, clean(f"Diferenca Corrente: {diff_a} A"), 1, 1)
        
        pdf.cell(63, 6, clean(f"P-Suc: {p_suc} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Suc: {ts_suc}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Suc: {t_suc_tubo}C"), 1, 1)
        
        pdf.cell(63, 6, clean(f"P-Liq: {p_liq} PSI"), 1, 0)
        pdf.set_font("Arial", 'B', 9); pdf.cell(63, 6, clean(f"T-Sat Liq: {ts_liq}C"), 1, 0, True); pdf.set_font("Arial", '', 9)
        pdf.cell(64, 6, clean(f"T-Tubo Liq: {t_liq_tubo}C"), 1, 1)
        
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(95, 7, clean(f"SUPERAQUECIMENTO (SH): {sh_val} K"), 1, 0)
        pdf.cell(95, 7, clean(f"SUBRESFRIAMENTO (SC): {sc_val} K"), 1, 1)
        pdf.ln(4)

        # 4. DIAGNÓSTICO E PARECER (ESTRUTURA BLOQUEADA)
        pdf.set_font("Arial", 'B', 10); pdf.cell(190, 7, " 4. DIAGNOSTICO E PARECER FINAL", 1, 1, 'L', True)
        pdf.set_font("Arial", '', 9)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Problemas Encontrados:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(prob_txt), "LRB")
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Medidas Executadas pelo Tecnico:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(executadas_input if executadas_input else "Nenhuma medida descrita"), "LRB")
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, clean("Parecer Tecnico e Observacoes:"), "LTR", 1); pdf.set_font("Arial", '', 9)
        pdf.multi_cell(190, 6, clean(obs_tecnico if obs_tecnico else "Sem observacoes adicionais"), "LRB")

        # ASSINATURAS
        pdf.ln(25); y_pos = pdf.get_y(); pdf.line(20, y_pos, 90, y_pos); pdf.line(120, y_pos, 190, y_pos)
        pdf.set_xy(20, y_pos + 1); pdf.set_font("Arial", 'B', 8); pdf.cell(70, 4, "Marcos Alexandre Almeida do Nascimento", 0, 1, 'C')
        pdf.set_x(20); pdf.set_font("Arial", '', 8); pdf.cell(70, 4, "CNPJ 51.274.762/0001-17", 0, 1, 'C')
        pdf.set_xy(120, y_pos + 1); pdf.set_font("Arial", 'B', 8); pdf.cell(70, 4, clean(f"{cliente}"), 0, 1, 'C')
        pdf.set_x(120); pdf.set_font("Arial", '', 8); pdf.cell(70, 4, "Cliente", 0, 1, 'C')

   # =========================================================
# 4. FINALIZAÇÃO DO MOTOR DE DIAGNÓSTICO E IA
# =========================================================

# D. LÓGICA ESPECÍFICA INVERTER (CONTINUAÇÃO)
if tecnologia == "Inverter":
    if sh_val < 2:
        registrar_falha("Controle inverter modulando excessivamente", "Ajuste de controle do compressor", 40)
    if p_liq > 420:
        registrar_falha("Limitação de frequência por alta pressão", "Alta pressão de condensação", 50)

# --- RESULTADOS FINAIS DO MOTOR ---
if not diagnostico_ia_lista:
    diagnostico_ia_lista.append("Sistema operando dentro dos parâmetros")

diag_ia_resultado = " | ".join(diagnostico_ia_lista)

# Ranking de Probabilidades
if probabilidades:
    ranking = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt_resultado = " | ".join([f"{f} ({p}%)" for f, p in ranking])
else:
    prob_txt_resultado = "Nenhuma falha crítica detectada"

# Contramedidas Automáticas
contramedidas = []
for falha in probabilidades:
    f_lower = falha.lower()
    if "refrigerante" in f_lower: contramedidas.append("Verificar carga e vazamentos")
    if "condensador" in f_lower: contramedidas.append("Limpar condensador e verificar ventilação")
    if "evaporador" in f_lower: contramedidas.append("Limpar evaporador e fluxo de ar")
    if "compressor" in f_lower: contramedidas.append("Verificar eficiência mecânica")
    if "rede eletrica" in f_lower: contramedidas.append("Verificar conexões elétricas")

if not contramedidas: 
    contramedidas.append("Nenhuma ação corretiva necessária")
contramedidas_txt = " | ".join(contramedidas)

# --- INTERFACE DE EXIBIÇÃO NA ABA DIAGNÓSTICO ---
with tab_diag:
    st.header("🤖 Inteligência de Diagnóstico")
    
    col_ia1, col_ia2 = st.columns(2)
    with col_ia1:
        st.info(f"### 🔎 Análise do Sistema\n{diag_ia_resultado}")
        st.warning(f"### 📊 Probabilidade de Falhas\n{prob_txt_resultado}")
    
    with col_ia2:
        st.success(f"### 🛠️ Contramedidas\n{contramedidas_txt}")
        st.metric("Eficiência (COP aprox.)", cop_aprox)

    st.markdown("---")
    
    # ÁREA DE RELATÓRIO E BOTÕES DE AÇÃO
    st.subheader("📄 Geração de Documentos")
    
    relatorio_texto_formatado = f"""DIAGNÓSTICO HVAC - MPN ENGENHARIA
Cliente: {cliente}
Data: {data_visita.strftime('%d/%m/%Y')}
------------------------------------------
Análise: {diag_ia_resultado}
Falhas: {prob_txt_resultado}
Medidas: {contramedidas_txt}
COP: {cop_aprox}"""

    st.text_area("Prévia do Relatório", relatorio_texto_formatado, height=150)

    # Lógica de Disparo e Geração
    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        # Botão WhatsApp com codificação de URL segura
        msg_wpp = urllib.parse.quote(f"*MPN ENGENHARIA - RELATÓRIO*\n\nOlá {cliente},\nSeguem os dados técnicos:\n\n*Status:* {diag_ia_resultado}\n*COP:* {cop_aprox}\n*Recomendação:* {contramedidas_txt}")
        num_limpo = whatsapp.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        link_wpp = f"https://wa.me/55{num_limpo}?text={msg_wpp}"
        st.markdown(f'<a href="{link_wpp}" target="_blank"><button style="width:100%; height:3em; background-color:#25D366; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">🟢 Enviar via WhatsApp</button></a>', unsafe_allow_html=True)

    with c_btn2:
        if st.button("📑 Gerar e Salvar Laudo PDF"):
            # 1. Salvar no Banco de Dados
            dados_banco = (
                str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
                f"{tipo_logr} {nome_logr}, {numero}", email_cli, fabricante, modelo_eq,
                serie_evap, linha, cap_digitada, serie_cond, tecnologia, fluido,
                loc_evap, tipo_eq, loc_cond, v_rede, v_med, a_med, rla_comp, lra_comp,
                p_suc, p_liq, sh_val, sc_val, prob_txt_resultado, contramedidas_txt, obs_tecnico
            )
            salvar_dados(dados_banco)
            endereco_completo = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro}"

# Agora o código do PDF funcionará:
pdf.set_font("Arial", '', 9)
pdf.cell(190, 7, clean(f"Endereco: {endereco_completo}"), 1, 1)
            # 2. Gerar PDF Profissional (Layout Cinza/Tabelas)
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 12, "RELATORIO TECNICO DE MANUTENCAO", 1, 1, 'C', True)
            pdf.ln(5)
            
            # Tabela 1: Identificação
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 1. DADOS DO CLIENTE E ATENDIMENTO", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(95, 7, clean(f"Cliente: {cliente}"), 1, 0)
            pdf.cell(95, 7, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereco: {tipo_logr} {nome_logr}, {numero}"), 1, 1)
            pdf.ln(3)

            # Tabela 2: Performance Termodinâmica
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 2. ANALISE DE PERFORMANCE (S.H / S.C)", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(47.5, 7, clean(f"P. Suc: {p_suc} PSI"), 1, 0)
            pdf.cell(47.5, 7, clean(f"T. Sat: {ts_suc} C"), 1, 0)
            pdf.cell(47.5, 7, clean(f"SH: {sh_val} K"), 1, 0)
            pdf.set_font("Arial", 'B', 9)
            pdf.cell(47.5, 7, "STATUS: OK" if 5<=sh_val<=12 else "ALERTA", 1, 1)
            pdf.ln(3)

            # Tabela 3: Diagnóstico IA
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 3. DIAGNOSTICO IA E PARECER", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(190, 7, clean(f"Analise: {diag_ia_resultado}"), 1, 'L')
            pdf.multi_cell(190, 7, clean(f"Medidas: {contramedidas_txt}"), 1, 'L')

            # Rodapé / Assinatura
            pdf.ln(15)
            pdf.line(20, pdf.get_y(), 90, pdf.get_y())
            pdf.line(120, pdf.get_y(), 190, pdf.get_y())
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(95, 5, "Assinatura do Tecnico", 0, 0, 'C')
            pdf.cell(95, 5, "Assinatura do Cliente", 0, 1, 'C')

            # Download
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar Agora o Laudo PDF", data=pdf_bytes, file_name=f"Laudo_MPN_{cliente}.pdf", mime="application/pdf")
            st.toast("✅ Dados salvos e PDF pronto!")
