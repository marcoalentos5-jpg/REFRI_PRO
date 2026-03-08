import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import urllib.parse

try:
    import matplotlib.pyplot as plt
    grafico_ok=True
except:
    grafico_ok=False

st.set_page_config(page_title="MPN Engenharia HVAC PRO",layout="wide",page_icon="❄️")

st.title("MPN Engenharia – Sistema Profissional de Diagnóstico HVAC")

# ---------------------------------------
# BANCO DE REFRIGERANTES (APROXIMAÇÃO)
# ---------------------------------------

refrigerantes=pd.DataFrame({

"Refrigerante":["R410A","R22","R134a","R404A"],

"Pressão evap típica":[118,70,30,60],

"Pressão cond típica":[360,250,150,250]

})

# ---------------------------------------
# BANCO DE COMPRESSORES
# ---------------------------------------

compressores=pd.DataFrame({

"Capacidade":[9000,12000,18000,24000],

"Copeland":["ZP14K5E","ZP20K5E","ZP31K5E","ZP42K5E"],

"Danfoss":["SH090","SH120","SH180","SH240"],

"Embraco":["FFU80","FFU130","FFU160","FFU200"]

})

# ---------------------------------------
# FUNÇÃO PT
# ---------------------------------------

def calcular_tsat(psig,gas):

    if psig<=0:
        return None

    if gas=="R410A":
        return 0.231*psig-22.8

    if gas=="R22":
        return 0.285*psig-25.1

    if gas=="R134a":
        return 0.52*psig-38.5

    if gas=="R404A":
        return 0.21*psig-16.5

    return None

# ---------------------------------------
# EFICIÊNCIA
# ---------------------------------------

def calcular_cop(delta_t,corrente):

    if corrente<=0:
        return None

    cop=(delta_t*0.293)/corrente

    return round(cop,2)

def calcular_eer(cop):

    if cop:
        return round(cop*3.412,2)

    return None

# ---------------------------------------
# MOTOR DIAGNÓSTICO AVANÇADO
# ---------------------------------------

def diagnostico(sh,sc,dt):

    falhas=[]

    if sh is None or sc is None:
        falhas.append("Dados insuficientes para diagnóstico.")
        return falhas

    if sh>15 and sc<3:
        falhas.append("Baixa carga de refrigerante.")

    if sh<4 and sc>12:
        falhas.append("Excesso de refrigerante.")

    if sh>15 and sc>10:
        falhas.append("Restrição na linha líquida ou filtro secador.")

    if dt>14:
        falhas.append("Baixa vazão de ar na evaporadora.")

    if dt<8:
        falhas.append("Baixa troca térmica.")

    if sh<3:
        falhas.append("Possível retorno de líquido ao compressor.")

    if sc<2:
        falhas.append("Condensação insuficiente.")

    if not falhas:
        falhas.append("Sistema operando dentro dos parâmetros ideais.")

    return falhas

# ---------------------------------------
# RECOMENDAÇÕES AUTOMÁTICAS
# ---------------------------------------

def recomendacoes(falhas):

    texto=[]

    for f in falhas:

        if "Baixa carga" in f:
            texto.append("Verificar vazamentos e recarregar refrigerante.")

        if "Excesso" in f:
            texto.append("Remover excesso de refrigerante.")

        if "Restrição" in f:
            texto.append("Inspecionar filtro secador e válvula de expansão.")

        if "vazão de ar" in f:
            texto.append("Limpar filtros e verificar ventilador.")

        if "troca térmica" in f:
            texto.append("Verificar serpentinas e fluxo de ar.")

    return texto

# ---------------------------------------
# SIDEBAR
# ---------------------------------------

st.sidebar.header("Configuração")

refrigerante=st.sidebar.selectbox("Refrigerante",["","R410A","R22","R134a","R404A"])

equipamento=st.sidebar.selectbox("Equipamento",
["Split","Cassete","VRF","Chiller","Câmara Fria"])

# ---------------------------------------
# ABAS
# ---------------------------------------

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs([
"Identificação",
"Medições",
"Diagnóstico",
"Eficiência",
"Banco Técnico",
"Laudo"
])

# ---------------------------------------
# IDENTIFICAÇÃO
# ---------------------------------------

with tab1:

    c1,c2,c3=st.columns(3)

    cliente=c1.text_input("Cliente")
    tecnico=c2.text_input("Responsável técnico")
    serie=c3.text_input("Número de série")

    c4,c5,c6=st.columns(3)

    fabricante=c4.text_input("Fabricante")
    modelo=c5.text_input("Modelo")
    capacidade=c6.number_input("Capacidade BTU",0)

    rla=st.number_input("Corrente nominal RLA",0.0)
    corrente=st.number_input("Corrente medida",0.0)

# ---------------------------------------
# MEDIÇÕES
# ---------------------------------------

with tab2:

    c1,c2,c3,c4=st.columns(4)

    with c1:

        t_ret=st.number_input("Temp retorno °C",24.0)
        t_ins=st.number_input("Temp insuflação °C",12.0)

        delta_t=t_ret-t_ins

        st.metric("Delta T",round(delta_t,2))

    with c2:

        p_suc=st.number_input("Pressão sucção",120.0)

        tsat_evap=calcular_tsat(p_suc,refrigerante)

        if tsat_evap:
            st.metric("Temp evaporação",round(tsat_evap,2))

    with c3:

        t_suc=st.number_input("Temp linha sucção",12.0)

        sh=None

        if tsat_evap:
            sh=t_suc-tsat_evap

        if sh:
            st.metric("Superaquecimento",round(sh,2))

    with c4:

        p_desc=st.number_input("Pressão descarga",380.0)

        tsat_cond=calcular_tsat(p_desc,refrigerante)

        t_liq=st.number_input("Temp linha líquida",30.0)

        sc=None

        if tsat_cond:
            sc=tsat_cond-t_liq

        if sc:
            st.metric("Sub-resfriamento",round(sc,2))

# ---------------------------------------
# DIAGNÓSTICO
# ---------------------------------------

with tab3:

    falhas=diagnostico(sh,sc,delta_t)

    for f in falhas:

        if "ideal" in f.lower():
            st.success(f)
        else:
            st.warning(f)

    rec=recomendacoes(falhas)

    if rec:
        st.subheader("Recomendações técnicas")

        for r in rec:
            st.write("-",r)

# ---------------------------------------
# EFICIÊNCIA
# ---------------------------------------

with tab4:

    cop=calcular_cop(delta_t,corrente)
    eer=calcular_eer(cop)

    if cop:
        st.metric("COP estimado",cop)

    if eer:
        st.metric("EER estimado",eer)

    if grafico_ok and tsat_evap and tsat_cond:

        x=[1,2,3,4]
        y=[tsat_evap,t_suc,tsat_cond,t_liq]

        fig,ax=plt.subplots()

        ax.plot(x,y,marker="o")

        ax.set_xlabel("Etapas do ciclo")
        ax.set_ylabel("Temperatura")

        st.pyplot(fig)

# ---------------------------------------
# BANCO TÉCNICO
# ---------------------------------------

with tab5:

    st.subheader("Refrigerantes")

    st.dataframe(refrigerantes)

    st.subheader("Compressores")

    st.dataframe(compressores)

# ---------------------------------------
# LAUDO
# ---------------------------------------

with tab6:

    data=datetime.now().strftime("%d/%m/%Y")

    laudo=f"""
LAUDO TÉCNICO HVAC

Cliente: {cliente}
Responsável técnico: {tecnico}

Equipamento: {fabricante} {modelo}
Capacidade: {capacidade} BTU

Data: {data}

CONDIÇÕES OPERACIONAIS

Temp retorno: {t_ret}
Temp insuflação: {t_ins}
Delta T: {delta_t}

Pressão sucção: {p_suc}
Superaquecimento: {sh}

Pressão descarga: {p_desc}
Sub-resfriamento: {sc}

DIAGNÓSTICO

{", ".join(falhas)}

RECOMENDAÇÕES

{", ".join(rec)}

COP estimado: {cop}
EER estimado: {eer}

Conclusão:
Avaliação baseada em parâmetros técnicos
utilizados na engenharia de refrigeração
e climatização.
"""

    st.text_area("Laudo técnico",laudo,height=420)

    if st.button("Gerar PDF"):

        pdf=FPDF()
        pdf.add_page()
        pdf.set_font("Arial","",10)

        for linha in laudo.split("\n"):
            pdf.multi_cell(0,8,linha)

        pdf_bytes=pdf.output(dest="S").encode("latin-1","ignore")

        st.download_button("Baixar PDF",pdf_bytes,"laudo_hvac.pdf","application/pdf")

# ---------------------------------------
# WHATSAPP
# ---------------------------------------

resumo=f"""
MPN ENGENHARIA HVAC

Cliente: {cliente}

Equipamento: {fabricante} {modelo}

Diagnóstico:
{", ".join(falhas)}
"""

link=f"https://wa.me/?text={urllib.parse.quote(resumo)}"

st.link_button("Enviar diagnóstico WhatsApp",link)
