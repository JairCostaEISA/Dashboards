import streamlit as st
import smtplib
from paginas import reports  # Importa a página de reports

# Função para validar o login
def validar_email_sender(sender_email, password):
    """Valida se o sender_email existe e a senha é válida."""
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()  # Inicia a criptografia
            server.login(sender_email, password)  # Testa o login com o sender_email e a senha
            return True
    except smtplib.SMTPAuthenticationError:
        return False
    except Exception as e:
        st.error(f"Erro ao validar o e-mail: {e}")
        return False

# Gerencia o estado da aplicação
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "login"  # Define a página inicial como login

def tela_login():
    
    # Cria três colunas para centralizar os campos
    col1, col2, col3 = st.columns([1, 2, 1])  # Centraliza na coluna do meio
    with col2:
        st.subheader("Acesse sua conta")

    # Cria três colunas para centralizar os campos
    col4, col5, col6 = st.columns([1, 2, 1])  # Centraliza na coluna do meio
    with col5:  # Campos na coluna central
        username = st.text_input("Usuário", placeholder="Digite seu nome de usuário", key="username")
        password = st.text_input("Senha", type="password", placeholder="Digite sua senha de 'E-MAIL'", key="password")

        # Botão de login
        if st.button("Entrar"):
            if username and password:
                sender_email = f"{username}@ericssoninovacao.com.br"
                if validar_email_sender(sender_email, password):
                    st.success("Login realizado com sucesso! 🎉")
                    st.session_state.logged_in = True
                    st.session_state.current_page = "reports"  # Altera para a página de reports
                    st.rerun()  # Recarrega a interface para ir para a próxima tela
                else:
                    st.error("Usuário ou senha inválidos. Por favor, tente novamente.")
            else:
                st.warning("Preencha todos os campos antes de prosseguir.") 

def tela_principal():
    """Tela de reports."""
    # Redireciona para a página de reports
    reports.exibir_tela_reports()

# Lógica para decidir qual tela exibir
if st.session_state.current_page == "login":
    tela_login()
elif st.session_state.current_page == "reports":
    tela_principal()
