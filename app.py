# ==============================================================================
# 0. CONFIGURAÇÕES INICIAIS E IMPORTAÇÕES (CONGELADO)
# ==============================================================================
import streamlit as st
from datetime import datetime
import requests
import urllib.parse
import os # Biblioteca para verificar arquivos no sistema
import numpy as np


# 1. CONFIGURAÇÃO INICIAL (TESTADA)

st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

# CSS: Estilização (CONGELADO)
st.markdown("""
    <style>
    .stTextInput>div>div>input[aria-label="Data da Visita:"] {
        background-color: #e0f2f1 !important;
        color: #004d40 !important;
        font-weight: bold;
        border: 1px solid #b2dfdb !important;
    }
    div.stLinkButton > a {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1.1. MOTOR DE SESSÃO (CHAVES VERIFICADAS)

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'data': datetime.now().strftime("%d/%m/%Y"),
        'cep': '', 'endereco': '', 'bairro': '', 'cidade': '', 'uf': '', 'numero': '', 'complemento': '',
        'fabricante': 'Carrier', 'modelo': '', 'capacidade': '12.000', 'linha': 'Residencial',
        'serie_evap': '', 'serie_cond': '', 'fluido': 'R410A', 'local_cond': '', 'local_evap': '',
        'tipo_servico': 'Manutenção Preventiva', 'tag_id': 'TAG-01',
        'tecnico_nome': 'Marcos Alexandre', 'tecnico_documento': '', 'tecnico_registro': '',
        'status_maquina': '🟢 Operacional'
    }

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados['endereco'] = d.get('logradouro', '')
                    st.session_state.dados['bairro'] = d.get('bairro', '')
                    st.session_state.dados['cidade'] = d.get('localidade', '')
                    st.session_state.dados['uf'] = d.get('uf', '')
                    return True
        except: pass
    return False

# ==============================================================================
# 1.2 FUNÇÃO DA ABA 1: Identificação e Equipamento (VERSÃO COM LAYOUT E MÁSCARAS)
# ==============================================================================
def renderizar_aba_1():
    tabs = st.tabs(["📋 Identificação e Equipamento"])
    tab1 = tabs[0]

    with tab1:
        with st.expander("👤 Dados do Cliente e Endereço", expanded=True):
            # --- CAMPOS COM FORMATAÇÃO (Máscaras sugeridas via placeholder) ---
            c1, c2, c3 = st.columns([2, 1, 1])
            st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'], key="cli_nome_v2")
            
            # Formatação CPF/CNPJ
            st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF (000.000.000-00)", value=st.session_state.dados['cpf_cnpj'], key="cli_doc_v2")
            
            # Formatação WhatsApp
            st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (XX-X-XXXX-XXXX) *", value=st.session_state.dados['whatsapp'], key="cli_zap_v2")

            cx1, cx2, cx3 = st.columns([1, 1, 2])
            st.session_state.dados['celular'] = cx1.text_input("Cel. (XX-X-XXXX-XXXX):", value=st.session_state.dados['celular'], key="cli_cel_v2")
            st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo (XX-XXXX-XXXX):", value=st.session_state.dados['tel_fixo'], key="cli_tel_v2")
            st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'], key="cli_email_v2")

            st.markdown("---")
            
            # --- SEÇÃO ENDEREÇO (LINHA 1) ---
            ce1, ce2, ce3 = st.columns([1, 2, 1])
            cep_input = ce1.text_input("CEP *", value=st.session_state.dados['cep'], key="cli_cep_v2")
            if cep_input != st.session_state.dados['cep']:
                st.session_state.dados['cep'] = cep_input
                if buscar_cep(cep_input): st.rerun()

            st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'], key="cli_end_v2")
            st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'], key="cli_num_v2")

            # --- SEÇÃO ENDEREÇO (LINHA 2 - TUDO JUNTO) ---
            # Dividindo em 4 colunas para caber Complemento, Bairro, Cidade e UF
            ce4, ce5, ce6, ce7 = st.columns([1.2, 1.2, 1.2, 0.4]) 
            
            st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'], key="cli_comp_v2")
            st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'], key="cli_bairro_v2")
            st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'], key="cli_cid_v2")
            
            # UF com limite de 2 caracteres e alinhado na mesma linha
            st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2, key="cli_uf_v2")

        # --- SEÇÃO EQUIPAMENTO ---
        col_titulo, col_data = st.columns([3, 1])
        with col_titulo: st.subheader("⚙️ Especificações do Equipamento")
        with col_data: st.session_state.dados['data'] = st.text_input("Data da Visita:", value=st.session_state.dados['data'])

        with st.expander("Detalhes Técnicos do Ativo", expanded=True):
            e1, e2, e3 = st.columns(3)
            with e1:
                fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
                fab_val = st.session_state.dados.get('fabricante', 'Carrier')
                fab_idx = fab_list.index(fab_val) if fab_val in fab_list else 0
                st.session_state.dados['fabricante'] = st.selectbox("Fabricante:", fab_list, index=fab_idx)
                st.session_state.dados['modelo'] = st.text_input("Modelo:", value=st.session_state.dados['modelo'])
                st.session_state.dados['linha'] = st.selectbox("Linha:", ["Residencial", "Comercial", "Industrial"], index=0)
                st.session_state.dados['status_maquina'] = st.radio("Status:", ["🟢 Operacional", "🟡 Requer Atenção", "🔴 Parado"], horizontal=True)

            with e2:
                st.session_state.dados['serie_evap'] = st.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
                st.session_state.dados['serie_cond'] = st.text_input("Nº Série (COND)", value=st.session_state.dados['serie_cond'])
                st.session_state.dados['local_evap'] = st.text_input("Local da Evaporadora:", value=st.session_state.dados['local_evap'])
                st.session_state.dados['local_cond'] = st.text_input("Local da Condensadora:", value=st.session_state.dados['local_cond'])

            with e3:
                st.session_state.dados['capacidade'] = st.selectbox("Capacidade:", ["9.000", "12.000", "18.000", "24.000", "30.000", "36.000", "48.000", "60.000"], index=1)
                st.session_state.dados['fluido'] = st.selectbox("Fluido:", ["R410A", "R134a", "R22", "R32", "R290"], index=0)
                st.session_state.dados['tipo_servico'] = st.selectbox("Tipo de Serviço:", ["Manutenção Preventiva", "Manutenção Corretiva", "Instalação", "Infraestrutura"], index=0)
                st.session_state.dados['tag_id'] = st.text_input("TAG:", value=st.session_state.dados['tag_id'])

# ==============================================================================
# 2. FUNÇÃO DA ABA DE DIAGNÓSTICOS (VERSÃO CALIBRADA - MOTOR V.20)
# ==============================================================================
def renderizar_aba_diagnosticos():
    st.header("🔍 Central de Diagnóstico Técnico")
    
    # Resgate do Fluido da Aba 1
    fluido = st.session_state.dados.get('fluido', 'R410A')
    st.info(f"❄️ Fluido Refrigerante: **{fluido}** | Motor de Precisão Auditado")
    
    # --- CSS PARA ALERTAS TÉCNICOS ---
    st.markdown("""
        <style>
        .sh-critico { background-color: #ff1744; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; }
        .sobrecarga { color: #d32f2f; font-weight: bold; font-size: 14px; }
        .alerta-pressao { padding: 10px; border-radius: 5px; margin-bottom: 10px; text-align: center; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # --- 1. MEDIÇÕES DE CAMPO (5 COLUNAS) ---
    st.subheader("1. Medições de Campo")
    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown("🔵 **EVAPORADORA**")
        p_suc = st.number_input("P. Sucção (PSI)", format="%.2f", step=0.1, key="ps_final")
        t_suc = st.number_input("T. Tubo Suc. (°C)", format="%.2f", step=0.1, key="ts_final")
        t_ret = st.number_input("T. Retorno (°C)", format="%.2f", step=0.1, key="tr_final")
        t_ins = st.number_input("T. Insufla. (°C)", format="%.2f", step=0.1, key="ti_final")

    with c2:
        st.markdown("🔴 **CONDENSADORA**")
        p_des = st.number_input("P. Desc. (PSI)", format="%.2f", step=0.1, key="pd_final")
        t_liq = st.number_input("T. Tubo Líq. (°C)", format="%.2f", step=0.1, key="tl_final")

    with c3:
        st.markdown("⚡ **TENSÃO**")
        v_lin = st.number_input("Tens. Linha (V)", format="%.2f", step=1.0, key="vl_final")
        v_med = st.number_input("Tens. Medida (V)", format="%.2f", step=1.0, key="vm_final")

    with c4:
        st.markdown("🔌 **CORRENTE**")
        rla = st.number_input("RLA (A)", format="%.2f", step=0.1, key="rla_final")
        lra = st.number_input("LRA (A)", format="%.2f", step=0.1, key="lra_final")
        i_med = st.number_input("Corr. Medida (A)", format="%.2f", step=0.1, key="im_final")

    with c5:
        st.markdown("🔋 **CAPACIT.**")
        cn_c = st.number_input("C. Nom. Comp", format="%.2f", key="cnc_final")
        cn_f = st.number_input("C. Nom. Fan", format="%.2f", key="cnf_final")
        cm_c = st.number_input("C. Med. Comp", format="%.2f", key="cmc_final")
        cm_f = st.number_input("C. Med. Fan", format="%.2f", key="cmf_final")

    # --- 2. MOTOR DE CÁLCULO (INTERPOLAÇÃO REAL) ---
    def f_sat_precisao(p, g):
        if p <= 5: return -50.0
        if g == "R410A":
            # TABELA RECALCULADA 90-150 (Conforme seus dados de campo)
            
            pressões = [90.0, 100.0, 105.0, 110.0, 115.0, 120.0, 122.7, 130.9, 141.7, 150.0]
            saturações = [-3.50, -0.29, 1.06, 2.36, 3.62, 4.84, 5.50, 7.40, 9.80, 11.50]
            
           # --- 2. MOTOR DE PRECISÃO (SISTEMA DE BUSCA DIRETA - SEM ERRO) ---
    def f_sat_precisao(p, g):
        if p <= 5: return -50.0
        
        # TABELA R410A (Seus pontos auditados)
        if g == "R410A":
            xp = [90.0, 100.0, 105.0, 110.0, 115.0, 120.0, 122.7, 130.9, 141.7, 150.0]
            fp = [-3.50, -0.29, 1.06, 2.36, 3.62, 4.84, 5.50, 7.40, 9.80, 11.50]
        elif g == "R32":
            xp = [90.0, 100.0, 115.0, 140.0, 170.0]
            fp = [-3.66, -0.87, 3.00, 8.50, 14.80]
        else:
            return 0.0

        for i in range(len(xp) - 1):
            if xp[i] <= p <= xp[i+1]:
                return fp[i] + (p - xp[i]) * (fp[i+1] - fp[i]) / (xp[i+1] - xp[i])
        return fp[0] if p < xp[0] else fp[-1]

    # --- INICIALIZAÇÃO DE VARIÁVEIS (EVITA O ERRO NA LINHA 236) ---
    t_sat_s = f_sat_precisao(p_suc, fluido)
    t_sat_d = f_sat_precisao(p_des, fluido)
    sh = (t_suc - t_sat_s) if p_suc > 0 else 0.0
    sc = (t_sat_d - t_liq) if p_des > 0 else 0.0
    dt_ar = (t_ret - t_ins) if (t_ret > 0 and t_ins > 0) else 0.0
    dif_v = v_lin - v_med
    dif_i = (rla - i_med) if rla > 0 else 0.0
   
      # --- 3. ALERTAS DE EXTREMOS (CALIBRADOS: 110-130 PSI) ---
    if p_suc > 0:
                texto_base = f"TEMP. SATURAÇÃO = {t_sat_s:.2f}ºC"
        
       # --- 3. ALERTAS DE EXTREMOS (LINHA 233 CORRIGIDA) ---
    if p_suc > 0:
        texto_base = f"TEMP. SATURAÇÃO = {t_sat_s:.2f}ºC"
        
        if p_suc < 110:
            st.markdown(f'<div class="alerta-pressao" style="background-color: #ffc107; color: black; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">{texto_base}  -  ⚠️ SUBPRESSÃO: ABAIXO DE 110 PSI</div>', unsafe_allow_html=True)
        elif 110 <= p_suc <= 130:
            st.markdown(f'<div class="alerta-pressao" style="background-color: #4caf50; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">{texto_base}  -  ✅ PRESSÃO IDEAL: 110 A 130 PSI</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alerta-pressao" style="background-color: #f44336; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;">{texto_base}  -  🚨 SOBREPRESSÃO: ACIMA DE 130 PSI</div>', unsafe_allow_html=True)

    
    with l1_c2:
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div class="sh-critico">SH TOTAL: {sh:.2f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH TOTAL", f"{sh:.2f} K")
    with l1_c3:
        st.metric("SC Final", f"{sc:.2f} K")
    with l1_c4:
        st.metric("COP", "0.00")
    with l1_c5:
        st.metric("Queda Tens.", f"{dif_v:.2f} V")

    # Linha 2
    l2_c1, l2_c2, l2_c3, l2_c4, l2_c5 = st.columns(5)
    with l2_c1:
        st.metric("Sat. Baixa", f"{t_sat_s:.2f} °C")
    with l2_c2:
        st.metric("Sat. Alta", f"{t_sat_d:.2f} °C")
    with l2_c3:
        st.metric("Dif. RLA", f"{dif_i:.2f} A")
    with l2_c4:
        d_fan = cm_f - cn_f if (cm_f > 0 and cn_f > 0) else 0.0
        st.metric("Δ Fan", f"{d_fan:.2f} µF")
    with l2_c5:
        d_comp = cm_c - cn_c if (cm_c > 0 and cn_c > 0) else 0.0
        st.metric("Δ Comp.", f"{d_comp:.2f} µF")
        
   # ==============================================================================
    # 2.1. RESULTADOS CALCULADOS (ORGANIZAÇÃO 5x2 CONFORME O PAPEL)
    # ==============================================================================
    st.markdown("---")
    st.subheader("2. Resultados Calculados")
    
    # Estilo para números Verdes e Grandes
    st.markdown('<style>div[data-testid="stMetricValue"] > div { font-size: 1.8rem !important; color: #00e676; }</style>', unsafe_allow_html=True)

    # LINHA 1: SH TOTAL | Sat. Baixa | Δ Tensão | Δ T | Δ Comp.
    l1_c1, l1_c2, l1_c3, l1_c4, l1_c5 = st.columns(5)
    with l1_c1:
        if sh < 5 and p_suc > 0:
            st.markdown(f'<div style="color:#ff4b4b; font-weight:bold; font-size:14px;">SH TOTAL: {sh:.2f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else:
            st.metric("SH TOTAL", f"{sh:.2f} K")
    with l1_c2: st.metric("Sat. Baixa", f"{t_sat_s:.2f} °C")
    with l1_c3: st.metric("Δ Tensão", f"{dif_v:.2f} V")
    with l1_c4: st.metric("Δ T", f"{dt_ar:.2f} °C")
    with l1_c5: st.metric("Δ Comp.", f"{(cm_c - cn_c):.2f} µF")

    # LINHA 2: SC FINAL | Sat. Alta | Δ Corrente | COP | Δ Fan
    l2_c1, l2_c2, l2_c3, l2_c4, l2_c5 = st.columns(5)
    with l2_c1: st.metric("SC FINAL", f"{sc:.2f} K")
    with l2_c2: st.metric("Sat. Alta", f"{t_sat_d:.2f} °C")
    with l2_c3:
        st.metric("Δ Corrente", f"{dif_i:.2f} A")
        if i_med > rla and rla > 0: st.markdown('<div style="color:#ff4b4b; font-size:12px; font-weight:bold;">⚠️ SOBRECARGA</div>', unsafe_allow_html=True)
    with l2_c4: st.metric("COP", "0.00")
    with l2_c5: st.metric("Δ Fan", f"{(cm_f - cn_f):.2f} µF")

    # ==============================================================================
    # 2.2. PARECER TÉCNICO (ÚNICO E FINAL)
    # ==============================================================================
    st.markdown("---")
    st.subheader("3. Parecer Técnico")
    st.session_state.dados['laudo_diag'] = st.text_area(
        label="Notas e Diagnóstico Final:", 
        value=st.session_state.dados.get('laudo_diag', ''),
        key="laudo_final_v4"
    )

# ==============================================================================
# 3. SIDEBAR - DADOS DO TÉCNICO E ENVIO WHATSAPP
# ==============================================================================
with st.sidebar:
    st.title("🚀 Painel de Controle")
    opcoes_abas = ["Home", "1. Cadastro de Equipamentos", "2. Diagnósticos", "Relatórios"]
    aba_selecionada = st.sidebar.radio("Selecione a Aba:", opcoes_abas)
    
    st.markdown("---")
    st.subheader("👤 Técnico Responsável")
    st.session_state.dados['tecnico_nome'] = st.text_input("Nome:", value=st.session_state.dados['tecnico_nome'])
    st.session_state.dados['tecnico_documento'] = st.text_input("CPF/CNPJ Técnico:", value=st.session_state.dados['tecnico_documento'])
    st.session_state.dados['tecnico_registro'] = st.text_input("Inscrição (CFT/CREA):", value=st.session_state.dados['tecnico_registro'])
    
    st.markdown("---")
    
    if not st.session_state.dados['nome'] or not st.session_state.dados['whatsapp']:
        st.error("📋 STATUS: PENDENTE (Preencha Cliente e WhatsApp)")
    else:
        st.success("📋 STATUS: PRONTO PARA ENVIO")
        
        # MENSAGEM WHATSAPP ATUALIZADA COM DADOS DO DIAGNÓSTICO
        msg_zap = (
            f"*LAUDO TÉCNICO HVAC - MPN SOLUÇÕES*\n\n"
            f"👤 *CLIENTE:* {st.session_state.dados['nome']}\n"
            f"📞 Contato: {st.session_state.dados['whatsapp']}\n\n"
            f"⚙️ *EQUIPAMENTO:*\n"
            f"📌 TAG: {st.session_state.dados['tag_id']} | Mod: {st.session_state.dados['modelo']}\n"
            f"❄️ Cap: {st.session_state.dados['capacidade']} BTU | Fluido: {st.session_state.dados['fluido']}\n\n"
            f"🩺 *DIAGNÓSTICO TÉCNICO:*\n"
            f"✅ SH TOTAL: {sh:.2f} K\n"
            f"✅ SC FINAL: {sc:.2f} K\n"
            f"✅ Δ TENSÃO: {dif_v:.2f} V\n"
            f"✅ Δ TEMP: {dt_ar:.2f} °C\n\n"
            f"📝 *PARECER FINAL:*\n"
            f"{st.session_state.dados.get('laudo_diag', 'Nenhum parecer informado.')}\n\n"
            f"👨‍🔧 *TÉCNICO:* {st.session_state.dados['tecnico_nome']}\n"
            f"📅 Data: {st.session_state.dados['data']}"
        )
        
        # Correção do link com urllib
        import urllib.parse
        link_final = f"https://wa.me/55{st.session_state.dados['whatsapp'].replace(' ', '').replace('-', '')}?text={urllib.parse.quote(msg_zap)}"
        st.link_button("📲 Enviar Laudo via WhatsApp", link_final, use_container_width=True)

    if st.button("🗑️ Limpar Formulário", use_container_width=True):
        chaves_tecnico = ['tecnico_nome', 'tecnico_documento', 'tecnico_registro', 'data']
        for key in st.session_state.dados.keys():
            if key not in chaves_tecnico: st.session_state.dados[key] = ""
        st.rerun()
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

  # ... (Bloco de Resultados 5x2 que arrumamos antes) ...

    # --- BLOCO 4: CONCLUSÃO E LAUDO (MANTENHA APENAS ESTE) ---
    st.markdown("---")
    st.subheader("3. Parecer Técnico Final")
    st.session_state.dados['laudo_diag'] = st.text_area(
        "Descreva o diagnóstico ou anomalias encontradas:",
        value=st.session_state.dados.get('laudo_diag', ''), # Importante para não apagar o texto ao trocar de aba
        placeholder="Ex: Sistema operando com pressões estáveis...",
        key="laudo_area_diag"
    )

elif aba_selecionada == "1. Cadastro de Equipamentos":
    # Seu código do cadastro aqui...
