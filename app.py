def check_password():
    def password_entered():
        if st.session_state["password"] == "MPN2024": # Sua senha aqui
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("Senha de Acesso MPN", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

if not check_password(): st.stop()
