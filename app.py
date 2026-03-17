# =============================================================
# MPN - ENGENHARIA E DIAGNÓSTICO HVAC PRO
# VERSÃO CONSOLIDADA - ALTA PERFORMANCE
# =============================================================

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

# --- 2. BANCO DE DADOS (ESTRUTURA DE 31 CAMPOS) ---
def init_db():
    """Garante a criação da tabela com todos os 31 parâmetros técnicos."""
    try:
        conn = sqlite3.connect('banco_dados_mpn.db')
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
        st.error(f"Erro Crítico no Banco de Dados: {e}")
    finally:
        conn.close()

def salvar_dados(dados):
    """Sincronização rigorosa dos 31 campos para evitar erro de inconsistência."""
    if len(dados) != 31:
        st.error(f"Erro de Sincronização: Esperados 31 campos, recebidos {len(dados)}")
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
        st.error(f"Falha ao gravar no banco: {e}")
        return False
    finally:
        conn.close()

init_db()

# --- 3. MOTOR TERMODINÂMICO (TABELAS PT COMPLETAS) ---
def get_tsat_global(psig, gas):
    """Interpolação linear de alta precisão para múltiplos gases."""
    tab = {
        "R-410A": {
            "p": [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 550, 600], 
            "t": [-51.0, -34.0, -22.0, -12.5, -5.0, -0.3, 4.0, 8.0, 11.5, 15.0, 18.2, 25.0, 32.0, 38.0, 44.0, 49.0, 54.0, 58.5, 63.0]
        },
        "R-32": {
            "p": [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600], 
            "t": [-51.7, -17.5, 0.9, 10.9, 20.1, 27.9, 34.6, 40.6, 45.9, 50.8, 55.4, 59.5, 63.4]
        },
        "R-22": {
            "p": [0, 20, 40, 60, 80, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500], 
            "t": [-40.8, -25.8, -15.0, -6.5, 0.2, 6.0, 12.5, 18.5, 24.0, 29.0, 38.0, 46.0, 53.0, 60.0, 66.0, 72.0]
        },
        "R-134a": {
            "p": [0, 10, 20, 30, 40, 50, 60, 80, 100, 120, 140, 160, 180, 200], 
            "t": [-26.1, -12.5, -3.2, 3.8, 9.5, 14.5, 19.0, 27.0, 33.8, 40.0, 45.5, 50.5, 55.2, 59.5]
        }
    }
    if gas not in tab: return 0.0
    return round(float(np.interp(max(0, psig), tab[gas]["p"], tab[gas]["t"])), 2)

def clean(txt):
    """Sanitização de strings para PDF."""
    if not txt: return "N/A"
    res = str(txt).replace('°', 'C').replace('º', '.').replace('ª', '.')
    return "".join(c for c in unicodedata.normalize('NFKD', res) if not unicodedata.category(c) == 'Mn')

def seguro(v, default=0.0):
    """Validador de entrada numérica."""
    try: return float(v)
    except: return default

# --- 4. CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button p { font-size: 18px; font-weight: bold; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #004a99; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004a99; color: white; }
    </style>
""", unsafe_allow_html=True)
# --- 5. INTERFACE PRINCIPAL E TABS ---
st.title("❄️ MPN | Engenharia & Diagnóstico HVAC")

tab_cad, tab_ele, tab_termo, tab_diag, tab_hist = st.tabs([
    "📋 Identificação", "⚡ Elétrica", "🌡️ Termodinâmica", "🤖 Diagnóstico", "📜 Histórico"
])

with tab_cad:
    st.subheader("👤 Identificação do Cliente e Contato")
    c1, c2, c3 = st.columns([2.5, 1.2, 1.4])
    with c1:
        cliente = st.text_input("Cliente / Empresa", placeholder="Ex: Condomínio Solar")
    with c2:
        doc_cliente = st.text_input("CPF / CNPJ")
    with c3:
        data_visita = st.date_input("📅 Data da Visita", value=date.today(), format="DD/MM/YYYY")

    c4, c5, c6 = st.columns(3)
    with c4:
        whatsapp = st.text_input("🟢 WhatsApp", value="21980264217")
    with c5:
        celular = st.text_input("📱 Celular Alternativo")
    with c6:
        tel_residencial = st.text_input("📞 Telefone Fixo")

    st.markdown("---")
    st.subheader("📍 Endereço da Prestação de Serviço")
    e1, e2, e3, e4 = st.columns([0.6, 2.0, 0.5, 1.0])
    with e1:
        tipo_logr = st.selectbox("Tipo", ["Rua", "Av.", "Trav.", "Alam.", "Estr.", "Rod.", "Pça."])
    with e2:
        nome_logr = st.text_input("Logradouro")
    with e3:
        numero = st.text_input("Nº")
    with e4:
        complemento = st.text_input("Complemento / Bloco")
    
    e5, e6, e7 = st.columns([1.5, 1.0, 1.5])
    with e5:
        bairro = st.text_input("Bairro")
    with e6:
        cep = st.text_input("CEP")
    with e7:
        email_cli = st.text_input("✉️ E-mail para envio do Relatório")

    st.markdown("---")
    st.subheader("⚙️ Dados do Equipamento")
    g1, g2, g3, g4 = st.columns(4)
    with g1:
        fabricante = st.text_input("Marca / Fabricante")
        modelo_eq = st.text_input("Modelo Geral")
        serie_evap = st.text_input("Nº Série Evaporadora")
    with g2:
        linha = st.text_input("Linha (Ex: Multi-Split)")
        cap_digitada = st.text_input("Capacidade (BTU/h)", value="0")
        serie_cond = st.text_input("Nº Série Condensadora")
    with g3:
        tecnologia = st.selectbox("Tecnologia", ["Inverter", "WindFree", "Scroll", "On-Off", "VRF", "Multisplit", "Chiller"])
        fluido = st.selectbox("Gás Refrigerante", ["R-410A", "R-32", "R-22", "R-134a"])
        loc_evap = st.text_input("Localização Evap.")
    with g4:
        tipo_eq = st.selectbox("Sistema", ["Split", "Cassete", "Piso Teto", "Duto", "VRF", "Chiller"])
        loc_cond = st.text_input("Localização Cond.")

with tab_ele:
    st.subheader("⚡ Parâmetros Elétricos e Medições")
    el1, el2, el3 = st.columns(3)
    
    with el1:
        st.markdown("**Tensões (V)**")
        v_rede = st.number_input("Tensão Nominal da Rede", value=220.0, step=1.0)
        v_med = st.number_input("Tensão Medida no Borne", value=220.0, step=1.0)
        diff_v = round(v_rede - v_med, 1)
        if abs(diff_v) > (v_rede * 0.07):
            st.error(f"⚠️ Queda de Tensão crítica: {diff_v}V")
        else:
            st.success(f"✅ Variação estável: {diff_v}V")
            
    with el2:
        st.markdown("**Correntes (A)**")
        rla_comp = st.number_input("Corrente de Placa (RLA)", value=0.0, step=0.1)
        a_med = st.number_input("Corrente Operacional Medida", value=0.0, step=0.1)
        diff_a = round(a_med - rla_comp, 1)
        st.info(f"Diferencial: {diff_a} A")
        
    with el3:
        st.markdown("**Carga e Partida**")
        lra_comp = st.number_input("Corrente de Partida (LRA)", value=0.0, step=0.1)
        carga_calc = (a_med / rla_comp * 100) if rla_comp > 0 else 0
        st.metric("Carga do Compressor", f"{round(carga_calc, 1)} %")
        if carga_calc > 110:
            st.warning("⚠️ Compressor em Sobrecarga")

with tab_termo:
    st.subheader("🌡️ Ciclo Frigorífico e Termodinâmica")
    tr1, tr2, tr3 = st.columns(3)
    
    with tr1:
        st.markdown("**Baixa Pressão (Sucção)**")
        p_suc = st.number_input("Pressão de Sucção (PSIG)", value=115.0, step=1.0)
        t_suc_tubo = st.number_input("Temperatura Tubo Sucção (°C)", value=12.0, step=0.1)
        ts_suc = get_tsat_global(p_suc, fluido)
        st.metric("T-Sat Sucção (Evaporação)", f"{ts_suc} °C")
        
    with tr2:
        st.markdown("**Alta Pressão (Líquido)**")
        p_liq = st.number_input("Pressão de Líquido (PSIG)", value=340.0, step=1.0)
        t_liq_tubo = st.number_input("Temperatura Tubo Líquido (°C)", value=32.0, step=0.1)
        ts_liq = get_tsat_global(p_liq, fluido)
        st.metric("T-Sat Líquido (Condensação)", f"{ts_liq} °C")
        
    with tr3:
        st.markdown("**Análise de Performance**")
        sh_val = round(t_suc_tubo - ts_suc, 1)
        sc_val = round(ts_liq - t_liq_tubo, 1)
        
        # Estilização visual dos resultados
        st.write("Superaquecimento (SH)")
        if 5 <= sh_val <= 12:
            st.success(f"**{sh_val} K** (Ideal)")
        else:
            st.error(f"**{sh_val} K** (Fora do padrão)")
            
        st.write("Subresfriamento (SC)")
        if 4 <= sc_val <= 10:
            st.success(f"**{sc_val} K** (Ideal)")
        else:
            st.warning(f"**{sc_val} K** (Atenção)")
# =============================================================
# MOTOR DE DIAGNÓSTICO E INTELIGÊNCIA DE FALHAS
# =============================================================

# Inicialização de Containers de Diagnóstico
diagnostico_ia = []
probabilidades = {}

def registrar_falha(msg, falha_chave=None, peso=0):
    """Adiciona mensagens ao diagnóstico e alimenta o ranking de probabilidades."""
    if msg not in diagnostico_ia:
        diagnostico_ia.append(msg)
    if falha_chave:
        # Acumula peso se a falha for detectada por múltiplos sensores
        probabilidades[falha_chave] = probabilidades.get(falha_chave, 0) + peso

# 1. Análise de Eficiência e Troca Térmica
delta_evap = t_suc_tubo - ts_suc
delta_cond = ts_liq - t_liq_tubo

if delta_evap < 2:
    registrar_falha("Baixa transferência de calor no evaporador", "Fluxo de ar insuficiente / Sujeira", 60)
if delta_cond < 2:
    registrar_falha("Condensação ineficiente", "Ventilação insuficiente / Sujeira Condensadora", 55)

# 2. Análise de Carga e Compressor
if rla_comp > 0:
    if carga_calc > 120:
        registrar_falha("Compressor operando em sobrecarga", "Excesso de refrigerante ou Alta pressão", 65)
    elif 0 < carga_calc < 40:
        registrar_falha("Compressor com carga muito baixa", "Baixa carga térmica ou restrição", 60)

if p_suc > 145 and p_liq < 280 and fluido == "R-410A":
    registrar_falha("Pressões equalizando em funcionamento", "Possível perda de compressão / Compressor desgastado", 75)

# 3. Análise de Tensão e Elétrica
if abs(diff_v) > 12:
    registrar_falha("Variação de tensão fora do limite operacional", "Instabilidade na rede elétrica", 80)

# 4. Lógica Específica Inverter / WindFree
if tecnologia in ["Inverter", "WindFree"]:
    if sh_val < 2:
        registrar_falha("Risco de golpe de líquido (SH muito baixo)", "Falha na válvula de expansão / Sensor", 50)
    if p_liq > 430:
        registrar_falha("Pressão de descarga elevada", "Limitador de frequência ativado por alta pressão", 45)

# 5. Consolidação e Ranking
if not diagnostico_ia:
    diagnostico_ia.append("Sistema operando dentro dos parâmetros ideais")

diag_ia_final = " | ".join(diagnostico_ia)

# Ordenação do Ranking de Probabilidades (Mais provável primeiro)
if probabilidades:
    ranking_ordenado = sorted(probabilidades.items(), key=lambda x: x[1], reverse=True)
    prob_txt = " | ".join([f"{f} ({p}%)" for f, p in ranking_ordenado])
else:
    prob_txt = "Nenhuma anomalia crítica detectada"

# 6. Geração de Contramedidas Automáticas
contramedidas_lista = []
for falha, peso in probabilidades.items():
    f_low = falha.lower()
    if "refrigerante" in f_low or "carga" in f_low:
        contramedidas_lista.append("Verificar carga de fluido e possíveis vazamentos")
    if "fluxo" in f_low or "sujeira" in f_low:
        contramedidas_lista.append("Realizar limpeza química dos trocadores e filtros")
    if "compressor" in f_low:
        contramedidas_lista.append("Avaliar eficiência mecânica e partida do compressor")
    if "rede elétrica" in f_low:
        contramedidas_lista.append("Revisar conexões, bornes e estabilidade da rede")

if not contramedidas_lista:
    contramedidas_lista.append("Nenhuma ação corretiva imediata necessária")
contramedidas_txt = " | ".join(contramedidas_lista)

# Cálculo de COP Aproximado para o Relatório
cop_aprox = round((delta_cond + 1.5) / (delta_evap + 1.5), 2) if delta_evap != -1.5 else 0

# --- INTERFACE NA ABA DIAGNÓSTICO ---
with tab_diag:
    st.header("🤖 Diagnóstico Assistido por IA")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.info(f"**Análise do Sistema:**\n\n{diag_ia_final}")
        st.warning(f"**Probabilidade de Falhas:**\n\n{prob_txt}")
    with col_res2:
        st.success(f"**Contramedidas Recomendadas:**\n\n{contramedidas_txt}")
        st.metric("Eficiência Estável (COP)", cop_aprox)

    st.markdown("---")
    st.subheader("📄 Relatório Técnico para Cópia")
    
    relatorio_whats = f"""*RELATÓRIO TÉCNICO HVAC - MPN*
    
*Diagnóstico IA:* {diag_ia_final}
*Principais Suspeitas:* {prob_txt}
*Ações Sugeridas:* {contramedidas_txt}
*Eficiência (COP):* {cop_aprox}
*SH/SC:* {sh_val}K / {sc_val}K"""

    st.text_area("Conteúdo (WhatsApp / E-mail)", relatorio_whats, height=180)
    
    st.markdown(f"""
        <button onclick="navigator.clipboard.writeText(`{relatorio_whats}`)"
        style="width:100%; padding:12px; background-color:#25d366; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer;">
        📋 Copiar Relatório Completo
        </button>
    """, unsafe_allow_html=True)
st.markdown("---")
    col_man1, col_man2 = st.columns(2)
    with col_man1:
        st.subheader("📝 Medidas Executadas")
        executadas_input = st.text_area("Descreva os serviços realizados:", height=150)
    with col_man2:
        st.subheader("💡 Parecer do Técnico")
        obs_tecnico = st.text_area("Observações adicionais ou recomendações ao cliente:", height=150)

    # --- BOTÃO DE SALVAMENTO E PDF ---
    if st.button("💾 FINALIZAR, SALVAR E GERAR PDF"):
        # Preparação dos dados para o Banco (31 campos exatos)
        endereco_full = f"{tipo_logr} {nome_logr}, {numero} {complemento} - {bairro} | CEP: {cep}"
        
        dados_final = (
            str(data_visita), cliente, doc_cliente, whatsapp, celular, tel_residencial,
            endereco_full, email_cli, fabricante, modelo_eq, serie_evap, linha,
            cap_digitada, serie_cond, tecnologia, fluido, loc_evap, tipo_eq, loc_cond,
            v_rede, v_med, a_med, rla_comp, lra_comp, p_suc, p_liq, sh_val, sc_val,
            f"IA: {diag_ia_final} | Prob: {prob_txt}", executadas_input, obs_tecnico
        )
        
        if salvar_dados(dados_final):
            # Geração do PDF Blindado
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 18)
            pdf.set_text_color(0, 74, 153)
            pdf.cell(190, 15, "RELATORIO TECNICO DE MANUTENCAO HVAC", 0, 1, 'C')
            
            # 1. Dados do Cliente
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 1. IDENTIFICACAO DO CLIENTE", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9); pdf.set_text_color(0)
            pdf.cell(40, 7, clean(f"Data: {data_visita.strftime('%d/%m/%Y')}"), 1)
            pdf.cell(100, 7, clean(f"Cliente: {cliente}"), 1)
            pdf.cell(50, 7, clean(f"Doc: {doc_cliente}"), 1, 1)
            pdf.cell(190, 7, clean(f"Endereco: {endereco_full}"), 1, 1)
            
            # 2. Dados Técnicos
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 2. ESPECIFICACOES E MEDICOES", 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.cell(63, 7, clean(f"Marca: {fabricante}"), 1); pdf.cell(63, 7, clean(f"Cap: {cap_digitada} BTU"), 1); pdf.cell(64, 7, clean(f"Fluido: {fluido}"), 1, 1)
            pdf.cell(47, 7, clean(f"V. Rede: {v_rede}V"), 1); pdf.cell(48, 7, clean(f"V. Med: {v_med}V"), 1); pdf.cell(47, 7, clean(f"A. Med: {a_med}A"), 1); pdf.cell(48, 7, clean(f"RLA: {rla_comp}A"), 1, 1)
            pdf.cell(95, 7, clean(f"Superaquecimento: {sh_val} K"), 1); pdf.cell(95, 7, clean(f"Subresfriamento: {sc_val} K"), 1, 1)
            
            # 3. Diagnóstico IA e Parecer
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(190, 8, " 3. PARECER TECNICO E DIAGNOSTICO", 1, 1, 'L', True)
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Diagnostico Assistido:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(f"{diag_ia_final} | Suspeitas: {prob_txt}"), "LRB")
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Medidas Executadas:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(executadas_input), "LRB")
            pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, "Observacoes:", "LTR", 1)
            pdf.set_font("Arial", '', 8); pdf.multi_cell(190, 5, clean(obs_tecnico), "LRB")

            # Assinaturas
            pdf.ln(15)
            y_pos = pdf.get_y()
            pdf.line(20, y_pos, 85, y_pos); pdf.line(105, y_pos, 170, y_pos)
            pdf.set_font("Arial", 'B', 7)
            pdf.set_xy(20, y_pos + 1); pdf.cell(65, 4, "MARCOS ALEXANDRE ALMEIDA DO NASCIMENTO", 0, 0, 'C')
            pdf.set_xy(105, y_pos + 1); pdf.cell(65, 4, clean(cliente.upper()), 0, 0, 'C')

            pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
            st.download_button("📥 Baixar Relatório PDF Profissional", data=pdf_output, file_name=f"Relatorio_{cliente}.pdf", mime="application/pdf")
            st.success("✅ Dados salvos e PDF gerado!")

with tab_hist:
    st.subheader("📜 Histórico de Atendimentos Realizados")
    conn = sqlite3.connect('banco_dados_mpn.db')
    df = pd.read_sql_query("SELECT id, data_visita, cliente, marca, modelo, sh, sc FROM atendimentos ORDER BY id DESC", conn)
    conn.close()
    
    if not df.empty:
        # Formatação Brasileira da Data no DataFrame
        df['data_visita'] = pd.to_datetime(df['data_visita']).dt.strftime('%d/%m/%Y')
        df.insert(0, "Selecionar", False)
        
        busca = st.text_input("🔍 Filtrar por Cliente ou Data", placeholder="Digite para buscar...")
        if busca:
            df = df[df['cliente'].str.contains(busca, case=False) | df['data_visita'].str.contains(busca)]

        editor = st.data_editor(df, hide_index=True, use_container_width=True, 
                                 column_config={"Selecionar": st.column_config.CheckboxColumn("Excluir", default=False), "id": None})
        
        if st.button("🗑️ Excluir Registros Selecionados"):
            ids_para_excluir = editor[editor["Selecionar"] == True]["id"].tolist()
            if ids_para_excluir:
                conn = sqlite3.connect('banco_dados_mpn.db')
                for idx in ids_para_excluir:
                    conn.execute("DELETE FROM atendimentos WHERE id = ?", (idx,))
                conn.commit()
                conn.close()
                st.rerun()
    else:
        st.info("Nenhum atendimento encontrado no banco de dados.")
