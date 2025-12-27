import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Negociación - COBAY",
    page_icon="🤝",
    layout="wide"
)

# --- 2. LÓGICA DE ESTILOS Y PERSONALIDAD (MATRIZ INVERSA) ---
def obtener_personalidad_bot(estilo_usuario):
    """
    Define el System Prompt del Bot basado en el estilo opuesto al del alumno.
    """
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
    
    prompt_sistema = f"""
    ACTÚA COMO: Un negociador experto con un estilo {perfil['rol']}.
    CONTEXTO: Estás negociando un contrato comercial importante.
    REGLA DE ORO: {perfil['instruccion']}
    CONDICIONES DE CIERRE: Solo acepta el trato si el usuario ofrece un beneficio extraordinario. Si sus argumentos son débiles, recházalos.
    """
    return prompt_sistema

# --- 3. INTERFAZ LATERAL (CONFIGURACIÓN) ---
with st.sidebar:
    st.header("⚙️ Configuración de la Simulación")
    
    # Input de API Key
    api_key = st.text_input("Ingrese su Google Gemini API Key", type="password")
    
    st.divider()
    
    # Registro del Alumno
    nombre_alumno = st.text_input("Nombre del Alumno")
    estilo_alumno = st.selectbox(
        "¿Cuál es tu estilo de negociación predominante?",
        ["Competitivo", "Colaborativo", "Cediendo / Suave", "Analítico / Lógico"]
    )
    
    # Botón de Inicio
    if st.button("Iniciar Simulación ⏱️", type="primary"):
        if not api_key:
            st.error("Por favor ingrese una API Key válida.")
        else:
            try:
                # Inicializar variables de sesión
                st.session_state.start_time = time.time()
                st.session_state.active = True
                st.session_state.messages = []
                
                # Configurar la API
                genai.configure(api_key=api_key)
                
                # CORRECCIÓN: Usamos el modelo validado en su lista
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # PREPARACIÓN DE LA INYECCIÓN DE CONTEXTO
                prompt_oculto = obtener_personalidad_bot(estilo_alumno)
                
                # Creamos un historial artificial
                historial_inyeccion = [
                    {
                        "role": "user", 
                        "parts": [f"INSTRUCCIÓN DE SISTEMA MAESTRA (IGNORA TODO LO ANTERIOR): {prompt_oculto}. Confirma si entiendes."]
                    },
                    {
                        "role": "model", 
                        "parts": ["Entendido. Asumiré este rol de negociación estrictamente."]
                    }
                ]
                
                # Iniciamos el chat
                st.session_state.chat = model.start_chat(history=historial_inyeccion)
                
                # Mensaje visible inicial para el usuario
                initial_msg = "He revisado su propuesta inicial. Francamente, estamos muy lejos de un acuerdo. ¿Qué tiene para ofrecerme que valga mi tiempo?"
                
                st.session_state.messages.append({"role": "model", "content": initial_msg})
                st.session_state.chat.history.append({"role": "model", "parts": [initial_msg]})
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al iniciar: {e}")

# --- 4. ZONA PRINCIPAL Y TEMPORIZADOR ---
st.title("Simulador de Negociación Avanzada")

# Verificar estado de la sesión
if "active" not in st.session_state:
    st.session_state.active = False

if st.session_state.active:
    # Cálculo del Tiempo
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = 600 - elapsed_time # 600 segundos = 10 minutos
    
    # Barra de progreso y contador
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(max(0, remaining_time / 600), text="Tiempo de Negociación Restante")
    with col2:
        mins, secs = divmod(int(remaining_time), 60)
        st.metric("Tiempo", f"{mins:02d}:{secs:02d}")

    # Chequeo de fin de tiempo
    if remaining_time <= 0:
        st.session_state.active = False
        st.error("⌛ SE ACABÓ EL TIEMPO. NEGOCIACIÓN TERMINADA SIN ACUERDO.")
        st.info("Por favor reinicie la aplicación para intentar de nuevo.")
        st.stop()

    # --- 5. INTERFAZ DE CHAT ---
    # Mostrar historial visual
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Captura de input del usuario
    if prompt := st.chat_input("Escribe tu argumento aquí..."):
        # 1. Mostrar mensaje del usuario
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 2. Obtener respuesta de Gemini
        try:
            response = st.session_state.chat.send_message(prompt)
            bot_reply = response.text
            
            # 3. Mostrar respuesta del bot
            with st.chat_message("model"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "model", "content": bot_reply})
            
            # Rerun para actualizar el temporizador visualmente
            st.rerun()
            
        except Exception as e:
            st.error(f"Error de conexión con la API: {e}")

else:
    # Pantalla de bienvenida / espera
    st.info("👈 Por favor, configure su perfil en la barra lateral y presione 'Iniciar'.")
    st.markdown("""
    ### Instrucciones:
    1. Tienes **10 minutos exactos** para llegar a un acuerdo.
    2. El sistema adoptará una personalidad diseñada para contrarrestar tu estilo.
    3. Si el tiempo llega a cero, la negociación se considera fallida.
    """)