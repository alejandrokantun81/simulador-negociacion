import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Negociación - COBAY",
    page_icon="🤝",
    layout="wide"
)

# --- 2. LÓGICA DE ESTILOS Y PERSONALIDAD ---
def obtener_personalidad_bot(estilo_usuario):
    mapa_estilos = {
        "Competitivo": {
            "rol": "Evasivo y Pasivo-Agresivo",
            "instruccion": "Tu oponente es agresivo. Tu objetivo es frustrarlo. No digas que no directamente, pero desvía el tema, posterga decisiones y hazte la víctima. Nunca cierres el trato rápido."
        },
        "Colaborativo": {
            "rol": "Competitivo y Despiadado",
            "instruccion": "Tu oponente quiere colaborar. Aprovecha esto como debilidad. Exige concesiones unilaterales. Sé frío, cortante y solo acepta acuerdos donde tú ganes el 90% del valor."
        },
        "Cediendo / Suave": {
            "rol": "Insaciable y Explotador",
            "instruccion": "Tu oponente es débil. Cada vez que ceda algo, pide más. Nunca te muestres satisfecho. Sube tus exigencias constantemente."
        },
        "Analítico / Lógico": {
            "rol": "Emocional y Caótico",
            "instruccion": "Tu oponente usa datos. Tú usa emociones irracionales, cambia de opinión sin lógica y quéjate de que 'no se siente bien' el trato. Ignora sus números."
        }
    }
    perfil = mapa_estilos.get(estilo_usuario, mapa_estilos["Competitivo"])
    return f"""
    ACTÚA COMO: Un negociador experto con un estilo {perfil['rol']}.
    CONTEXTO: Estás negociando un contrato comercial importante.
    REGLA DE ORO: {perfil['instruccion']}
    CONDICIONES DE CIERRE: Solo acepta el trato si el usuario ofrece un beneficio extraordinario. Si sus argumentos son débiles, recházalos.
    """

# --- 3. INTERFAZ LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Registro del Alumno
    nombre_alumno = st.text_input("Nombre del Alumno")
    estilo_alumno = st.selectbox(
        "¿Cuál es tu estilo de negociación predominante?",
        ["Competitivo", "Colaborativo", "Cediendo / Suave", "Analítico / Lógico"]
    )
    
    # Botón de Inicio
    if st.button("Iniciar Simulación ⏱️", type="primary"):
        try:
            # --- CAMBIO CLAVE: LEER LA LLAVE OCULTA ---
            api_key = st.secrets["GOOGLE_API_KEY"]
            
            st.session_state.start_time = time.time()
            st.session_state.active = True
            st.session_state.messages = []
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash') # Usamos el modelo rápido y nuevo
            
            prompt_oculto = obtener_personalidad_bot(estilo_alumno)
            historial_inyeccion = [
                {"role": "user", "parts": [f"INSTRUCCIÓN SISTEMA: {prompt_oculto}"]},
                {"role": "model", "parts": ["Entendido."]}
            ]
            
            st.session_state.chat = model.start_chat(history=historial_inyeccion)
            
            initial_msg = "He revisado su propuesta. Estamos lejos de un acuerdo. ¿Qué ofrece?"
            st.session_state.messages.append({"role": "model", "content": initial_msg})
            st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
            st.rerun()
            
        except Exception as e:
            st.error(f"Error técnico: {e}")

# --- 4. ZONA PRINCIPAL ---
st.title("Simulador de Negociación Avanzada")

if "active" not in st.session_state:
    st.session_state.active = False

if st.session_state.active:
    elapsed = time.time() - st.session_state.start_time
    remaining = 600 - elapsed
    
    col1, col2 = st.columns([3, 1])
    with col1: st.progress(max(0, remaining / 600), text="Tiempo Restante")
    with col2: st.metric("Tiempo", f"{int(remaining)//60:02d}:{int(remaining)%60:02d}")

    if remaining <= 0:
        st.session_state.active = False
        st.error("⌛ TIEMPO AGOTADO. SIN ACUERDO.")
        st.stop()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu argumento..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            resp = st.session_state.chat.send_message(prompt)
            with st.chat_message("model"): st.markdown(resp.text)
            st.session_state.messages.append({"role": "model", "content": resp.text})
            st.rerun()
        except: st.error("Error de conexión.")

else:
    st.info("👈 Ingresa tu nombre y estilo en el menú lateral para comenzar.")