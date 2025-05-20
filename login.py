import streamlit as st
import os
import json
import random
import hashlib
from dotenv import load_dotenv
from email_utils import send_email

load_dotenv()

USERS_FILE = "users.json"
CODE_EXPIRY_MINUTES = 10

# Utilidades para usuarios

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Registro y login

def register():
    st.title("Registro de usuario")
    email = st.text_input("Email")
    if st.button("Enviar código de verificación"):
        code = str(random.randint(100000, 999999))
        st.session_state["pending_email"] = email
        st.session_state["pending_code"] = code
        st.session_state["code_sent"] = send_email(email, "Tu código de verificación para EbalQuiz", f"Tu código de verificación es: {code}")
        st.session_state["register_step"] = 2
        st.success("Código enviado. Revisa tu correo.")

    if st.session_state.get("register_step") == 2:
        code_input = st.text_input("Código de verificación")
        password = st.text_input("Elige una contraseña", type="password")
        if st.button("Crear cuenta"):
            if code_input == st.session_state.get("pending_code"):
                users = load_users()
                users[email] = {"password": hash_password(password)}
                save_users(users)
                st.success("Usuario creado. Ya puedes iniciar sesión.")
                st.session_state["register_step"] = 0
            else:
                st.error("Código incorrecto.")

def login():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        users = load_users()
        if email in users and users[email]["password"] == hash_password(password):
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.success("¡Login exitoso!")
            st.rerun()
        else:
            st.error("Email o contraseña incorrectos.")

def check_auth():
    if not st.session_state.get("authenticated", False):
        mode = st.radio("¿Tienes cuenta?", ("Iniciar sesión", "Registrarse"))
        if mode == "Iniciar sesión":
            login()
        else:
            register()
        st.stop() 