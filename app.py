
# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np
import urllib.parse
import pandas as pd
from datetime import date

import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# 1. CONFIGURAÇÕES DE PÁGINA E ESTILIZAÇÃO CSS (LINHAS 1-45)
# ==============================================================================
st.set_page_config(page_title="Expert HVAC-R Diagnostic", layout="wide", page_icon="❄️")

# Inicialização Robusta do Session State (Proteção contra perda de dados)
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'cliente': '', 'cpf_cnpj': '', 'contato': '', 'email': '',
        'cep': '', 'logradouro': '', 'numero': '',
        'fabricante': 'Midea', 'modelo': '', 'capacidade': '12.000 BTU',
        'fluido': 'R410A', 'tipo_oleo': 'POE', 'carga_gas': '',
        'tensao_nominal': '220V', 'status_eq': 'Operacional',
        'laudo_diag': 'Análise: Estável.'
    }

d = st.session_state.dados

# CSS Personalizado para manter o Layout Profissional Dark
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetric"] { background-color: #1A1C23; border-radius: 10px; padding: 12px; border: 1px solid #333; }
    div[data-testid="stVerticalBlock"] > div:has(div.stMetric) { background-color: #1A1C23; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. ABA 1: CADASTRO - LÓGICA DE PERSISTÊNCIA E INTERFACE (LINHAS 46-172)
# ==============================================================================
def renderizar_aba_cadastro():
    st.header("📋 Cadastro de Cliente e Equipamento")
    st.markdown("---")

    # --- 2.1 DADOS DO CLIENTE (ATUALIZAÇÃO EM TEMPO REAL) ---
    st.subheader("1. Informações do Cliente")
    col1, col2 = st.columns(2)
    
    with col1:
        # Uso de value=d.get() garante que o dado não suma ao trocar de aba
        d['cliente'] = st.text_input("Nome do Cliente ou Empresa:", value=d.get('cliente', ''), placeholder="Nome Completo / Razão Social")
        d['cpf_cnpj'] = st.text_input("CPF ou CNPJ:", value=d.get('cpf_cnpj', ''), placeholder="Somente números ou com pontos")
    
    with col2:
        d['contato'] = st.text_input("Telefone / WhatsApp:", value=d.get('contato', ''), placeholder="(00) 00000-0000")
        d['email'] = st.text_input("E-mail para Envio do Laudo:", value=d.get('email', ''), placeholder="contato@cliente.com")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📍 Localização e Endereço")
    
    # CORREÇÃO DO CEP E LOGRADOURO (KEY SYNC PARA EVITAR DELAY)
    l1, l2, l3 = st.columns([2, 5, 1])
    # O uso da KEY força o Streamlit a salvar no Session State sem precisar de Rerun
    d['cep'] = l1.text_input("CEP:", value=str(d.get('cep', '')), key="cep_persist", help="Digite o CEP para registro")
    d['logradouro'] = l2.text_input("Logradouro (Endereço Completo):", value=d.get('logradouro', ''), key="log_persist")
    d['numero'] = l3.text_input("Nº:", value=d.get('numero', ''), key="num_persist")

    st.markdown("---")

    # --- 2.2 DADOS DO EQUIPAMENTO (CATÁLOGO ATUALIZADO) ---
    st.subheader("2. Especificações Técnicas do Equipamento")
    
    # LISTA DE FABRICANTES: HITACHI INCLUÍDA + ORDEM ALFABÉTICA + OUTROS NO FIM
    fabs_raw = ["Carrier", "Daikin", "Fujitsu", "Gree", "Hitachi", "LG", "Midea", "Panasonic", "Samsung", "Trane", "York", "Elgin", "Springer", "Eletrolux"]
    lista_fabricantes = sorted(list(set(fabs_raw))) + ["OUTROS"]
    
    # LISTA DE CAPACIDADES: EXPANSÃO BTU E TR (CHILLERS/VRF)
    lista_capacidades = [
        "7.000 BTU", "9.000 BTU", "12.000 BTU", "18.000 BTU", "22.000 BTU", "24.000 BTU", 
        "30.000 BTU", "31.000 BTU", "36.000 BTU", "48.000 BTU", "60.000 BTU", "80.000 BTU",
        "5 TR", "7.5 TR", "10 TR", "15 TR", "20 TR", "30 TR", "40 TR", "50 TR", "Outra"
    ]

    # FUNÇÃO INTERNA DE ÍNDICE (Garante que a escolha do técnico não mude sozinha)
    def buscar_index(lista, chave):
        val = d.get(chave)
        return lista.index(val) if val in lista else 0

    e1, e2, e3 = st.columns(3)
    
    with e1:
        st.markdown("##### 🏷️ Identificação")
        d['fabricante'] = st.selectbox("Fabricante:", lista_fabricantes, index=buscar_index(lista_fabricantes, 'fabricante'))
        d['modelo'] = st.text_input("Modelo / Tag da Unidade:", value=d.get('modelo', ''))
        d['capacidade'] = st.selectbox("Capacidade (BTU/TR):", lista_capacidades, index=buscar_index(lista_capacidades, 'capacidade'))

    with e2:
        st.markdown("##### 🧪 Fluido e Óleo")
        lista_fluidos = ["R410A", "R22", "R134a", "R404A", "R32", "R290", "R407C"]
        d['fluido'] = st.selectbox("Fluido Refrigerante:", lista_fluidos, index=buscar_index(lista_fluidos, 'fluido'))
        
        # CORREÇÃO: TIPO DE ÓLEO SEGURANDO A ESCOLHA (PERSISTENTE)
        lista_oleos = ["POE", "PVE", "MINERAL", "AB", "PAG"]
        d['tipo_oleo'] = st.selectbox("Tipo de Óleo Lubrificante:", lista_oleos, index=buscar_index(lista_oleos, 'tipo_oleo'))
        d['carga_gas'] = st.text_input("Carga de Fluido (kg):", value=d.get('carga_gas', ''))

    with e3:
        st.markdown("##### ⚡ Elétrica e Operação")
        # CORREÇÃO: TENSÃO NOMINAL SEGURANDO A ESCOLHA
        lista_tensoes = ["110V", "220V", "380V", "440V"]
        d['tensao_nominal'] = st.selectbox("Tensão de Alimentação:", lista_tensoes, index=buscar_index(lista_tensoes, 'tensao_nominal'))
        
        # CORREÇÃO: STATUS SEGURANDO A ESCOLHA
        lista_status = ["Operacional", "Parado (Defeito)", "Manutenção Preventiva", "Avaliação Técnica", "Instalação"]
        d['status_eq'] = st.selectbox("Status do Equipamento:", lista_status, index=buscar_index(lista_status, 'status_eq'))
        d['data_visita'] = st.date_input("Data da Análise:", value=date.today())

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("📌 **Nota:** Certifique-se de que o Fluido selecionado corresponde à etiqueta da máquina para precisão nos cálculos da Aba 2.")

    # SINCRONIZAÇÃO FINAL DO ESTADO (BLINDAGEM CONTRA PERDA DE DADOS)
    st.session_state.dados.update(d)

# EXECUÇÃO DO BLOCO (SIMULADO)
if __name__ == "__main__":
    renderizar_aba_cadastro()
# FINAL DO BLOCO 1 - INTEGRIDADE MANTIDA - LINHA 172
    

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO MASTER - CORREÇÃO DE PERSISTÊNCIA TOTAL)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    d = st.session_state.dados
    fluido = d.get('fluido', 'R410A')

    # Função auxiliar interna para evitar crash de conversão
    def safe_float(key, default=0.0):
        val = d.get(key)
        try:
            return float(val) if val not in [None, ""] else default
        except:
            return default

    # --- 1. PAINEL DE REFERÊNCIA IDEAL (DINÂMICO POR GÁS) ---
    referencias = {
        'R410A': {"p_suc": "110 a 130 PSI", "t_sat": "2°C a 6°C", "sh": "5K a 9K", "sc": "5K a 8K"},
        'R22':   {"p_suc": "60 a 75 PSI", "t_sat": "1°C a 5°C", "sh": "7K a 11K", "sc": "3K a 6K"},
        'R134a': {"p_suc": "25 a 40 PSI", "t_sat": "-1°C a 4°C", "sh": "5K a 10K", "sc": "4K a 8K"},
        'R404A': {"p_suc": "80 a 95 PSI", "t_sat": "-5°C a 0°C", "sh": "4K a 8K", "sc": "2K a 5K"}
    }
    ref = referencias.get(fluido, referencias['R410A'])

    st.markdown(f"""
        <div style="background-color: #1E1E1E; border-left: 5px solid #00CCFF; padding: 15px; border-radius: 10px; margin-bottom: 25px; border: 1px solid #333;">
            <h4 style="margin-top:0; color: #00CCFF;">🎯 Referência Ideal para {fluido}</h4>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                <div style="color: #FFFFFF;"><small style="color: #888;">SUCÇÃO ALVO</small><br><b>{ref['p_suc']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SATURAÇÃO ALVO</small><br><b>{ref['t_sat']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SH (SUPERAQUEC.)</small><br><b>{ref['sh']}</b></div>
                <div style="color: #FFFFFF;"><small style="color: #888;">SC (SUB-RESFR.)</small><br><b>{ref['sc']}</b></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 2. MEDIÇÕES DE CAMPO ---
    st.subheader("1. Medições de Campo")
    
    # SEÇÃO A: 🔵 CICLO FRIGORÍFICO
    st.markdown("##### 🔵 Ciclo Frigorífico")
    a1, a2, a3, a4, a5 = st.columns(5)
    p_suc = a1.number_input("SUCÇÃO (PSI)", value=safe_float('p_baixa'), format="%.1f", key="ps_m")
    t_suc = a2.number_input("TUB. SUCÇÃO (°C)", value=safe_float('temp_sucção'), format="%.1f", key="ts_m")
    p_des = a3.number_input("DESCARGA (PSI)", value=safe_float('p_alta'), format="%.1f", key="pd_m")
    t_liq = a4.number_input("TUB. LÍQUIDO (°C)", value=safe_float('temp_liquido'), format="%.1f", key="tl_m")
    t_com = a5.number_input("TUB. Desc. Comp. (°C)", value=safe_float('temp_descarga'), format="%.1f", key="tc_m")

    # SEÇÃO B: 🔴 AR E AMBIENTE (CORREÇÃO DE PERSISTÊNCIA: UMIDADE E ÓLEO)
    st.markdown("##### 🔴 Ar e Ambiente")
    b1, b2, b3, b4, b5 = st.columns(5)
    t_ret = b1.number_input("Retorno Ar (°C)", value=safe_float('temp_entrada_ar'), format="%.1f", key="tr_m")
    t_ins = b2.number_input("Insuflação (°C)", value=safe_float('temp_saida_ar'), format="%.1f", key="ti_m")
    t_amb = b3.number_input("TEMP. Amb. Ext. (°C)", value=safe_float('temp_amb_ext', 35.0), format="%.1f", key="ta_m")
    # CORRIGIDO: Agora lê 'umidade' e salvará em 'umidade'
    u_rel = b4.number_input("Umid. Rel. DO AR (%)", value=safe_float('umidade', 50.0), format="%.1f", key="ur_m")
    # CORRIGIDO: Agora lê 'p_oleo' e salvará em 'p_oleo'
    p_oil = b5.number_input("Pressão Óleo (PSI)", value=safe_float('p_oleo', 0.0), format="%.1f", key="po_m")

    # SEÇÃO C: ⚡ PARÂMETROS ELÉTRICOS (CORREÇÃO DE PERSISTÊNCIA: TENSÃO MEDIDA)
    st.markdown("##### ⚡ Parâmetros Elétricos")
    c1, c2, c3, c4, c5 = st.columns(5)
    v_lin = c1.number_input("Tensão Nominal (V)", value=safe_float('v_nominal', 220.0), key="vn_m")
    # CORRIGIDO: Agora lê 'v_medida' e salvará em 'v_medida'
    v_med = c2.number_input("Tensão Medida (V)", value=safe_float('v_medida', 220.0), key="vm_m")
    i_med = c3.number_input("Corrente Medida (A)", value=safe_float('i_medida'), key="im_m")
    rla   = c4.number_input("RLA - Nominal (A)", value=safe_float('rla'), key="rla_m")
    lra   = c5.number_input("LRA - Partida (A)", value=safe_float('lra'), key="lra_m")

    # SEÇÃO D: 🔋 CAPACITÂNCIA E VENTILAÇÃO
    st.markdown("##### 🔋 Capacitância e Ventilação")
    d1, d2, d3, d4, d5 = st.columns(5)
    cn_c  = d1.number_input("CAPACITÂNCIA Nom. Comp", value=safe_float('cn_c'), format="%.1f", key="cnc_m")
    cm_c  = d2.number_input("CAPACITÂNCIA Lido Comp", value=safe_float('cm_c'), format="%.1f", key="cmc_m")
    cn_f  = d3.number_input("CAPACITÂNCIA Nom. Fan", value=safe_float('cn_f'), format="%.1f", key="cnf_m")
    cm_f  = d4.number_input("CAPACITÂNCIA Lido Fan", value=safe_float('cm_f'), format="%.1f", key="cmf_m")
    i_fan = d5.number_input("CORRENTE Fan (A)", value=safe_float('i_fan'), format="%.2f", key="if_m")

    # --- 3. PROCESSAMENTO TÉCNICO (CÁLCULOS) ---
    t_sat_s = f_sat_precisao(p_suc, fluido) if p_suc > 5 else 0.0
    t_sat_d = f_sat_precisao(p_des, fluido) if p_des > 5 else 0.0
    sh = round(t_suc - t_sat_s, 2) if t_sat_s != 0 else 0.0
    sc = round(t_sat_d - t_liq, 2) if t_sat_d != 0 else 0.0
    dt_ar = round(t_ret - t_ins, 2)
    d_tensao = round(v_med - v_lin, 2)
    d_corrente = round(i_med - rla, 2) if rla > 0 else 0.0
    sh_util = round(sh * 0.8, 2) 
    d_cap_f = round(cm_f - cn_f, 2)
    d_cap_c = round(cm_c - cn_c, 2)

    # --- 4. RESULTADOS CALCULADOS (CSS PRESERVADO) ---
    st.markdown("---")
    st.subheader("2. Resultados Calculados")

    st.markdown("""
        <style>
        div[data-testid="stMetric"] {
            background-color: #1A1C23; border: 1px solid #333; padding: 8px;
            border-radius: 8px; margin-bottom: 5px; border-left: 4px solid #00CCFF;
        }
        div[data-testid="stMetricLabel"] p { font-size: 0.85rem !important; color: #888 !important; }
        div[data-testid="stMetricValue"] div { font-size: 1.1rem !important; color: #B0C4DE !important; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

    res = st.columns(5)
    with res[0]:
        st.metric("SH TOTAL", f"{sh:.1f} K")
        st.metric("SH ÚTIL", f"{sh_util:.1f} K")
    with res[1]:
        st.metric("SAT. SUCÇÃO", f"{t_sat_s:.1f} °C")
        st.metric("Δ T (AR)", f"{dt_ar:.1f} K")
    with res[2]:
        st.metric("SC FINAL", f"{sc:.1f} K")
        st.metric("SUCÇÃO ALVO", f"{ref['p_suc']}")
    with res[3]:
        st.metric("Δ TENSÃO", f"{d_tensao:.1f} V")
        st.metric("Δ CORRENTE", f"{d_corrente:.1f} A")
    with res[4]:
        st.metric("Δ CAP. COMP.", f"{d_cap_c:.1f} µF")
        st.metric("Δ CAP. FAN", f"{d_cap_f:.1f} µF")
    
    # --- 5. DIAGNÓSTICO INTELIGENTE ---
    st.markdown("---")
    st.subheader("🤖 Diagnóstico Inteligente (IA)")
    alertas_ia = []
    if sh < 5: alertas_ia.append("⚠️ **SH Baixo:** Risco de golpe de líquido.")
    if sh > 12: alertas_ia.append("⚠️ **SH Alto:** Compressor aquecendo demais.")
    if dt_ar < 8 and t_ret > 0: alertas_ia.append("❄️ **Delta T Baixo:** Verifique filtros ou carga.")
    if t_com > 100: alertas_ia.append("🔥 **Descarga Crítica:** Risco de queima do óleo.")
    
    texto_ia = "\n".join(alertas_ia) if alertas_ia else "✅ Sistema operando conforme lógica nominal."
    st.info(texto_ia)

    # --- 6. PARECER TÉCNICO FINAL ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    d['laudo_diag'] = st.text_area("Diagnóstico e Observações:", value=d.get('laudo_diag', "Análise: Estável."), height=150)

    # SINCRONIZAÇÃO FINAL (CORRIGIDA: MAPEAMENTO TOTAL DE CHAVES)
    st.session_state.dados.update({
        'p_baixa': p_suc, 'temp_sucção': t_suc, 'p_alta': p_des, 'temp_liquido': t_liq,
        'temp_entrada_ar': t_ret, 'temp_saida_ar': t_ins, 'temp_amb_ext': t_amb,
        'umidade': u_rel, 'p_oleo': p_oil, 'v_nominal': v_lin, 'v_medida': v_med,
        'i_medida': i_med, 'cn_c': cn_c, 'cm_c': cm_c, 'cn_f': cn_f, 'cm_f': cm_f, 
        'i_fan': i_fan, 'lra': lra, 'rla': rla, 'temp_descarga': t_com,
        'sh_calculado': sh, 'sc_calculado': sc
    })


# FIM DO BLOCO 2 (LINHA 289)
# FINAL DO BLOCO 2 (LINHA 384)   


# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E NAVEGAÇÃO (ATIVADA ANTES DA EXIBIÇÃO)
# ==============================================================================
# Mudamos esta seção para antes da Lógica de Exibição das Abas para definir aba_selecionada
with st.sidebar:
    st.title("🚀 Painel de Controle")

    # A. NAVEGAÇÃO E EXIBIÇÃO DAS ABAS (ATIVADA AQUI)
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    # Use st.sidebar.radio para criar os botões de seleção de aba e DEFINIR a variável
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    
   # B. DADOS DO TÉCNICO RESPONSÁVEL
    st.subheader("👤 Técnico Responsável")
    
    # Correção: Uso de .get() para evitar erro de chave inexistente e inclusão de 'key' única
    st.session_state.dados['tecnico_nome'] = st.text_input(
        "Nome:", 
        value=st.session_state.dados.get('tecnico_nome', ''), 
        key="tec_nome_sidebar_v1"
    )
    
    st.session_state.dados['tecnico_documento'] = st.text_input(
        "CPF/CNPJ Técnico:", 
        value=st.session_state.dados.get('tecnico_documento', ''), 
        key="tec_doc_sidebar_v1"
    )
    
    st.session_state.dados['tecnico_registro'] = st.text_input(
        "Inscrição (CFT/CREA):", 
        value=st.session_state.dados.get('tecnico_registro', ''), 
        key="tec_reg_sidebar_v1"
    )
    
    st.markdown("---")
    

# --- FINAL DO APP: VALIDAÇÃO, ENVIO E LIMPEZA ---
    st.markdown("---")
    d = st.session_state.dados

    # 1. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS (Usando .get para não travar)
    if not d.get('nome') or not d.get('whatsapp'):
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp na Aba Cadastro)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
        # 2. MONTAGEM DA MENSAGEM (Protegida contra SyntaxError e KeyError)
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC*\n\n"
            f"👤 *CLIENTE:* {d.get('nome', '')}\n"
            f"📍 END: {d.get('endereco', '')}, {d.get('numero', '')}\n"
            f"🏙️ {d.get('cidade', '')}/{d.get('uf', '')} | CEP: {d.get('cep', '')}\n"
            f"📞 Contato: {d.get('whatsapp', '')}\n\n"
            f"⚙️ *EQUIPAMENTO:*\n"
            f"📌 TAG: {d.get('tag_id', '')} | Mod: {d.get('modelo', '')}\n"
            f"❄️ Fluido: {d.get('fluido', '')}\n\n"
            f"🩺 *DIAGNÓSTICO:*\n"
            f"{d.get('laudo_diag', 'Sem observações.')}\n\n"
            f"👨‍🔧 *TÉCNICO:* {d.get('tecnico_nome', '')}\n"
            f"📅 Data: {d.get('data', '')}"
        )

        # 3. GERAÇÃO DO LINK E BOTÃO DE ENVIO
        texto_url = urllib.parse.quote(msg_zap)
        link_final = f"https://wa.me/55{d.get('whatsapp', '')}?text={texto_url}"
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    st.markdown("---")

    # 4. LIMPAR FORMULÁRIO (DIRETRIZ: PROTEGENDO DADOS DO TÉCNICO)
    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        # Lista do que NÃO deve ser apagado
        chaves_preservadas = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        
        for chave in list(st.session_state.dados.keys()):
            if chave not in chaves_preservadas:
                st.session_state.dados[chave] = ""
        
        st.rerun()

# ==============================================================================
# 4. LÓGICA DE EXIBIÇÃO DAS ABAS (ATIVADA)
# ==============================================================================
# Use a seleção do sidebar para chamar a função correta
if aba_selecionada == "Home":
    # --- NOVA APRESENTAÇÃO DA ABA HOME (COM LOGO MPN SOLUÇÕES ) ---
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento superior

    # 1. CENTRALIZAÇÃO E EXIBIÇÃO DA LOGOMARCA
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2: 
        # NOME DO ARQUIVO DE IMAGEM QUE ESTÁ SENDO USADO
        NOME_ARQUIVO_LOGO = "logo.png"
        
        # VERIFICAÇÃO ADICIONAL DO ARQUIVO NO DISCO (PARA AJUDAR NO DIAGNÓSTICO)
        if os.path.exists(NOME_ARQUIVO_LOGO):
            try:
                # SE O ARQUIVO EXISTE, TENTA EXIBIR
                st.image(NOME_ARQUIVO_LOGO, use_container_width=True) 
            except Exception as e:
                st.error(f"⚠️ Erro ao tentar abrir a imagem '{NOME_ARQUIVO_LOGO}'. Verifique se o arquivo está corrompido.")
                st.write(f"Detalhes do erro do sistema: {e}")
        else:
            st.error(f"⚠️ Erro: Arquivo '{NOME_ARQUIVO_LOGO}' não encontrado na pasta raiz.")
            st.info("Verifique se o nome do arquivo salvo no computador é EXATAMENTE 'logo.png' (maiúsculas/minúsculas importam).")

    st.markdown("<br><br>", unsafe_allow_html=True) 

    # 2. TÍTULO E BOAS-VINDAS CENTRALIZADOS E ESTILIZADOS
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #0d47a1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                MPN Soluções
            </h1>
            <p style="color: #1976d2; font-size: 1.3em;">
                Soluções em Refrigeração e Climatização
            </p>
            <hr style="border: 1px solid #90caf9; width: 60%; margin: 20px auto;">
            <p style="color: #455a64; font-size: 1.1em; font-weight: bold;">
                Bem-vindo ao Sistema HVAC Pro de Gestão Inteligente.
            </p>
            <p style="color: #546e7a; font-size: 1.0em;">
                Selecione uma opção no Painel de Controle lateral para iniciar sua inspeção ou diagnóstico.
            </p>
        </div>
    """, unsafe_allow_html=True)
    # ------------------------------------------------

elif aba_selecionada == "1. Cadastro de Equipamentos":
    renderizar_aba_1() # Chama a função que contém todo o código da Aba 1

elif aba_selecionada == "2. Diagnósticos":
    renderizar_aba_diagnosticos() # Chama a função que contém o esqueleto da Aba 2

elif aba_selecionada == "Relatórios":
    st.header("Página de Relatórios (Em desenvolvimento)")
    st.write("Em breve: Visualização e exportação de relatórios.")
# [COLE AQUI - Logo após o fim da renderizar_aba_1]

def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    # Busca o fluido que você selecionou na Aba 1
    fluido_selecionado = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante em Análise: **{fluido_selecionado}**")
    st.markdown("---")

    # --- BLOCO 1: ENTRADA DE MEDIÇÕES ---
    st.subheader("1. Medições de Campo")
    col_suc, col_des = st.columns(2)
    
    with col_suc:
        st.markdown("### 🔵 Baixa Pressão")
        pres_suc = st.number_input("Pressão de Sucção (PSI):", min_value=0.0, step=1.0, key="p_suc_diag")
        temp_suc = st.number_input("Temp. Tubulação Sucção (°C):", step=0.1, key="t_suc_diag")

    with col_des:
        st.markdown("### 🔴 Alta Pressão")
        pres_des = st.number_input("Pressão de Descarga (PSI):", min_value=0.0, step=1.0, key="p_des_diag")
        temp_liq = st.number_input("Temp. Tubulação Líquido (°C):", step=0.1, key="t_liq_diag")

    st.markdown("---")
  

# --- BLOCO 2: PROCESSAMENTO (CÁLCULOS) ---
    # Nota: No próximo passo, inseriremos a tabela PT aqui
    t_sat_suc = 0.0  
    t_sat_des = 0.0  
    
    sh = temp_suc - t_sat_suc
    sc = t_sat_des - temp_liq

    # --- BLOCO 3: EXIBIÇÃO DE RESULTADOS ---
    st.subheader("2. Resultados Calculados")
    res1, res2 = st.columns(2)
    
    with res1:
        st.metric(label="Superaquecimento (SH)", value=f"{sh:.1f} K")
        if 5 <= sh <= 7: st.success("✅ SH dentro do padrão (5K a 7K)")
        elif sh < 5: st.error("⚠️ SH Baixo: Risco de retorno de líquido")
        else: st.warning("⚠️ SH Alto: Possível falta de fluido ou restrição")

    with res2:
        st.metric(label="Sub-resfriamento (SC)", value=f"{sc:.1f} K")
        if 4 <= sc <= 7: st.success("✅ SC dentro do padrão (4K a 7K)")
        else: st.info("ℹ️ SC fora do padrão: Verifique condensação")

    st.markdown("---")

    # --- BLOCO 4: CONCLUSÃO E LAUDO ---
    st.subheader("3. Parecer Técnico Final")
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        placeholder="Ex: Sistema operando com pressões estáveis, superaquecimento normal...",
        key="laudo_area_diag"
    )
