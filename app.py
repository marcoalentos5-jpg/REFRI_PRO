import streamlit as st
import os
from datetime import datetime
import numpy as np
import requests
import urllib.parse

# ==============================================================================
# 1. CONFIGURAÇÃO E ESTILO (LAYOUT ORIGINAL)
# ==============================================================================
st.set_page_config(page_title="HVAC Pro - MPN Soluções", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stMetricValue"] > div { font-size: 1.8rem !important; color: #00e676 !important; font-weight: bold; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 5px; }
    .sh-alerta { background-color: #ff1744; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. MOTOR DE SESSÃO (PERSISTÊNCIA TOTAL)
# ==============================================================================
if 'dados' not in st.session_state:
    st.session_state.dados = {
        'nome': '', 'cpf_cnpj': '', 'whatsapp': '', 'celular': '', 'tel_fixo': '', 'email': '',
        'cep': '', 'endereco': '', 'numero': '', 'complemento': '', 'bairro': '', 'cidade': '', 'uf': '',
        'fabricante': 'Carrier', 'modelo': '', 'linha': 'Residencial', 'status_maquina': '🟢 Operacional',
        'serie_evap': '', 'serie_cond': '', 'local_evap': '', 'local_cond': '',
        'capacidade': '12.000', 'fluido': 'R410A', 'tipo_servico': 'Manutenção Preventiva', 'tag_id': '',
        'laudo_diag': '', 'data': datetime.now().strftime("%d/%m/%Y"),
        'p_suc': 0.0, 't_suc': 0.0, 'p_des': 0.0, 't_liq': 0.0
    }

# ==============================================================================
# 3. FUNÇÕES TÉCNICAS (PRECISÃO DANFOSS)
# ==============================================================================
def f_sat_precisao(p, g):
    if p <= 5: return -50.0
    tabelas = {
        "R410A": {"xp": [90.0, 110.0, 122.7, 150.0, 200.0], "fp": [-3.50, 2.36, 5.50, 11.50, 21.00]},
        "R32":   {"xp": [90.0, 115.0, 140.0, 170.0, 210.0], "fp": [-3.66, 3.00, 8.50, 14.80, 22.00]},
        "R22":   {"xp": [50.0, 70.0, 80.0, 200.0],          "fp": [-3.00, 5.80, 9.70, 38.50]}
    }
    tab = tabelas.get(g, tabelas["R410A"])
    return float(np.interp(p, tab["xp"], tab["fp"]))

def buscar_cep(cep):
    cep_limpo = "".join(filter(str.isdigit, cep))
    if len(cep_limpo) == 8:
        try:
            r = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
            if r.status_code == 200:
                d = r.json()
                if "erro" not in d:
                    st.session_state.dados.update({
                        'endereco': d.get('logradouro', ''), 'bairro': d.get('bairro', ''),
                        'cidade': d.get('localidade', ''), 'uf': d.get('uf', '')
                    })
                    return True
        except: pass
    return False

# ==============================================================================
# 4. INTERFACES (CADASTRO, CHECKLIST E DIAGNÓSTICO)
# ==============================================================================

def renderizar_cadastro():
    with st.expander("👤 Identificação do Cliente", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        st.session_state.dados['nome'] = c1.text_input("Nome / Razão Social *", value=st.session_state.dados['nome'])
        st.session_state.dados['cpf_cnpj'] = c2.text_input("CPF/CNPJ", value=st.session_state.dados['cpf_cnpj'])
        st.session_state.dados['whatsapp'] = c3.text_input("WhatsApp (DDD+Número) *", value=st.session_state.dados['whatsapp'])

        cx1, cx2, cx3 = st.columns([1, 1, 2])
        st.session_state.dados['celular'] = cx1.text_input("Celular:", value=st.session_state.dados['celular'])
        st.session_state.dados['tel_fixo'] = cx2.text_input("Fixo:", value=st.session_state.dados['tel_fixo'])
        st.session_state.dados['email'] = cx3.text_input("E-mail:", value=st.session_state.dados['email'])

    with st.expander("📍 Endereço da Instalação", expanded=True):
        ce1, ce2, ce3 = st.columns([1, 2, 1])
        cep_in = ce1.text_input("CEP *", value=st.session_state.dados['cep'])
        if cep_in != st.session_state.dados['cep']:
            st.session_state.dados['cep'] = cep_in
            if buscar_cep(cep_in): st.rerun()
        st.session_state.dados['endereco'] = ce2.text_input("Logradouro:", value=st.session_state.dados['endereco'])
        st.session_state.dados['numero'] = ce3.text_input("Nº/Apto:", value=st.session_state.dados['numero'])

        ce4, ce5, ce6, ce7 = st.columns([1, 1, 1, 0.5])
        st.session_state.dados['complemento'] = ce4.text_input("Complemento:", value=st.session_state.dados['complemento'])
        st.session_state.dados['bairro'] = ce5.text_input("Bairro:", value=st.session_state.dados['bairro'])
        st.session_state.dados['cidade'] = ce6.text_input("Cidade:", value=st.session_state.dados['cidade'])
        st.session_state.dados['uf'] = ce7.text_input("UF:", value=st.session_state.dados['uf'], max_chars=2)

    with st.expander("⚙️ Detalhes do Equipamento", expanded=True):
        e1, e2, e3 = st.columns(3)
        fab_list = sorted(["Carrier", "Daikin", "Fujitsu", "LG", "Samsung", "Trane", "York", "Elgin", "Gree", "Midea"])
        st.session_state.dados['fabricante'] = e1.selectbox("Fabricante:", fab_list, index=fab_list.index(st.session_state.dados['fabricante']) if st.session_state.dados['fabricante'] in fab_list else 0)
        st.session_state.dados['modelo'] = e1.text_input("Modelo:", value=st.session_state.dados['modelo'])
        st.session_state.dados['serie_evap'] = e2.text_input("Nº Série (EVAP) *", value=st.session_state.dados['serie_evap'])
        st.session_state.dados['local_evap'] = e2.text_input("Localização:", value=st.session_state.dados['local_evap'])
        st.session_state.dados['capacidade'] = e3.selectbox("Capacidade (BTU):", ["9.000", "12.000", "18.000", "24.000", "36.000", "60.000"], index=1)
        st.session_state.dados['fluido'] = e3.selectbox("Fluido:", ["R410A", "R32", "R22", "R134a"], index=0)

def renderizar_diagnostico():
    st.header("🔍 Central de Diagnóstico")
    f = st.session_state.dados['fluido']
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔵 Sucção")
        p_s = st.number_input("Pressão (PSI)", value=st.session_state.dados['p_suc'], key="ps_final")
        t_s = st.number_input("Temp. Tubo (°C)", value=st.session_state.dados['t_suc'], key="ts_final")
    with c2:
        st.markdown("### 🔴 Descarga")
        p_d = st.number_input("Pressão (PSI)", value=st.session_state.dados['p_des'], key="pd_final")
        t_l = st.number_input("Temp. Tubo Líq (°C)", value=st.session_state.dados['t_liq'], key="tl_final")
    
    st.session_state.dados.update({'p_suc': p_s, 't_suc': t_s, 'p_des': p_d, 't_liq': t_l})

    tsat_s = f_sat_precisao(p_s, f)
    tsat_d = f_sat_precisao(p_d, f)
    sh = t_s - tsat_s
    sc = tsat_d - t_l

    st.markdown("---")
    res1, res2 = st.columns(2)
    with res1:
        if sh < 5 and p_s > 0: st.markdown(f'<div class="sh-alerta">SH: {sh:.1f} K<br>⚠️ RISCO LÍQUIDO</div>', unsafe_allow_html=True)
        else: st.metric("Superaquecimento (SH)", f"{sh:.1f} K")
    res2.metric("Sub-resfriamento (SC)", f"{sc:.1f} K")

    st.session_state.dados['laudo_diag'] = st.text_area("Parecer Técnico:", value=st.session_state.dados['laudo_diag'], height=150)
    
    if st.button("🚀 Gerar Relatório WhatsApp"):
        msg = f"*RELATÓRIO HVAC - {st.session_state.dados['data']}*\n\n*Cliente:* {st.session_state.dados['nome']}\n*Equipamento:* {st.session_state.dados['fabricante']} ({f})\n*SH/SC:* {sh:.1f}K / {sc:.1f}K\n*Parecer:* {st.session_state.dados['laudo_diag']}"
        st.link_button("Abrir WhatsApp", f"https://wa.me/55{st.session_state.dados['whatsapp']}?text={urllib.parse.quote(msg)}")

# ==============================================================================
# 5. MENU PRINCIPAL
# ==============================================================================
aba = st.sidebar.radio("Navegação", ["Home", "1. Cadastro", "2. Diagnóstico"])

if aba == "Home":
    st.title("MPN Soluções - HVAC Pro")
    st.info("Sistema de Gestão Técnica Ativo. Selecione uma aba lateral.")
    if os.path.exists("logo.png"): st.image("logo.png", width=300)
elif aba == "1. Cadastro":
    renderizar_cadastro()
elif aba == "2. Diagnóstico":
    renderizar_diagnostico()
