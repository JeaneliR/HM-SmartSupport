"""Interfaz Streamlit de HM Smart Support."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter

import streamlit as st

from config import settings
from services.audio_service import transcribe_uploaded_audio
from services.chat_service import generate_reply
from services.classifier_service import QueryClassification, classify_query
from services.exceptions import SmartSupportError


st.set_page_config(
    page_title="HM Smart Support",
    layout="centered",
)

# Tema oscuro por defecto.
if "light_mode" not in st.session_state:
    st.session_state.light_mode = False


# =========================================================
# ESTILO BASE: MODO OSCURO
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --hm-black: #090909;
        --hm-surface: #151515;
        --hm-surface-2: #1d1d1d;
        --hm-border: #343434;
        --hm-orange: #ff6b00;
        --hm-orange-soft: #ff8a35;
        --hm-text: #f5f5f5;
        --hm-muted: #a7a7a7;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 88% 3%,
                rgba(255, 107, 0, .10),
                transparent 27rem
            ),
            linear-gradient(180deg, #111111 0%, #0d0d0d 100%);
        color: var(--hm-text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stDecoration"] {
        background: var(--hm-orange);
    }

    .block-container {
        max-width: 960px;
        padding-top: 2.4rem;
        padding-bottom: 5rem;
    }

    [data-testid="stSidebar"] {
        background: #080808;
        border-right: 1px solid #2d2d2d;
    }

    [data-testid="stSidebar"] hr {
        border-color: #2c2c2c;
    }

    [data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {
        color: #8f8f8f;
    }

    h1, h2, h3, p, label, .stMarkdown {
        color: var(--hm-text);
    }

    [data-testid="stCaptionContainer"] {
        color: var(--hm-muted);
    }

    hr {
        border-color: #303030 !important;
    }

    .hm-side-brand {
        padding: .35rem 0 1.35rem;
        font-size: 1.05rem;
        font-weight: 800;
        letter-spacing: .08em;
        color: #f5f5f5;
    }

    .hm-side-brand span {
        color: var(--hm-orange);
    }

    .hm-hero {
        position: relative;
        overflow: hidden;
        padding: 2.1rem 2.2rem;
        margin-bottom: 1.8rem;
        border: 1px solid #353535;
        border-radius: 22px;
        background:
            linear-gradient(135deg, #1c1c1c 0%, #111111 72%);
        box-shadow: 0 22px 55px rgba(0, 0, 0, .28);
    }

    .hm-hero::after {
        content: "";
        position: absolute;
        right: -55px;
        top: -75px;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: rgba(255, 107, 0, .13);
    }

    .hm-kicker {
        color: var(--hm-orange-soft);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .18em;
        text-transform: uppercase;
    }

    .hm-title {
        margin: .45rem 0 .55rem;
        color: #ffffff;
        font-size: clamp(2rem, 5vw, 3.25rem);
        font-weight: 850;
        line-height: 1.02;
        letter-spacing: -.035em;
    }

    .hm-title span {
        color: var(--hm-orange);
    }

    .hm-subtitle {
        max-width: 650px;
        margin: 0;
        color: #b9b9b9;
        font-size: 1rem;
        line-height: 1.6;
    }

    .hm-section-title {
        display: flex;
        align-items: center;
        gap: .7rem;
        margin: 2rem 0 .35rem;
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 750;
    }

    .hm-section-title::before {
        content: "";
        width: 5px;
        height: 25px;
        border-radius: 99px;
        background: var(--hm-orange);
    }

    .hm-composer-copy {
        margin: .2rem 0 .75rem;
        color: var(--hm-muted);
        font-size: .92rem;
    }

    .hm-badge {
        display: inline-block;
        padding: .28rem .68rem;
        margin: .25rem .35rem .3rem 0;
        border: 1px solid rgba(255, 107, 0, .38);
        border-radius: 999px;
        background: rgba(255, 107, 0, .10);
        color: #ff9b57;
        font-size: .8rem;
        font-weight: 700;
    }

    .hm-api-status {
        display: flex;
        align-items: center;
        gap: .65rem;
        padding: .8rem .9rem;
        border: 1px solid #343434;
        border-radius: 12px;
        background: #161616;
        color: #d8d8d8;
        font-size: .9rem;
        font-weight: 650;
    }

    .hm-api-status .dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: var(--hm-orange);
        box-shadow: 0 0 0 4px rgba(255, 107, 0, .13);
    }

    .hm-api-status.missing .dot {
        background: #8d8d8d;
        box-shadow: none;
    }

    [data-baseweb="select"] > div,
    [data-testid="stTextArea"] textarea,
    [data-testid="stChatInput"] {
        background: #1b1b1b !important;
        border-color: #3a3a3a !important;
        color: #f5f5f5 !important;
    }

    [data-baseweb="select"] * {
        color: #f5f5f5 !important;
    }

    [data-testid="stTextArea"] textarea:focus,
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--hm-orange) !important;
        box-shadow: 0 0 0 1px var(--hm-orange) !important;
    }

    [data-testid="stChatInput"] {
        min-height: 3.25rem;
        border-radius: 16px !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #f5f5f5 !important;
    }

    [data-testid="stChatInput"] button {
        color: var(--hm-orange) !important;
    }

    [data-testid="stAudioInput"] {
        margin: 0;
    }

    [data-testid="stAudioInput"] > div:last-child {
        min-height: 3.25rem;
        margin-bottom: 0;
        border: 1px solid #3a3a3a;
        border-radius: 16px;
        background: #1b1b1b;
    }

    [data-testid="stAudioInput"]:focus-within > div:last-child {
        border-color: var(--hm-orange);
        box-shadow: 0 0 0 1px var(--hm-orange);
    }

    [data-testid="stAudioInputActionButton"] {
        color: var(--hm-orange) !important;
    }

    [data-testid="stAudioInputActionButton"]:hover {
        color: #ff9a52 !important;
        background: rgba(255, 107, 0, .12) !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #171717;
        border: 1px dashed #4a4a4a;
        border-radius: 16px;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--hm-orange);
    }

    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        color: #c6c6c6 !important;
    }

    .stButton > button {
        min-height: 2.75rem;
        border: 1px solid #484848;
        border-radius: 11px;
        background: #1c1c1c;
        color: #f4f4f4;
        font-weight: 700;
        transition: all .18s ease;
    }

    .stButton > button:hover {
        border-color: var(--hm-orange);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 7px 20px rgba(255, 107, 0, .12);
    }

    .stButton > button[kind="primary"] {
        border-color: var(--hm-orange);
        background: var(--hm-orange);
        color: #111111;
    }

    .stButton > button[kind="primary"]:hover {
        border-color: #ff8124;
        background: #ff8124;
        color: #080808;
    }

    [data-testid="stChatMessage"] {
        margin-bottom: .8rem;
        border: 1px solid #303030;
        border-radius: 16px;
        background: rgba(27, 27, 27, .88);
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="chatAvatarIcon-user"]
    ) {
        border-left: 3px solid var(--hm-orange);
    }

    [data-testid="stExpander"] {
        margin-top: .5rem;
        border: 1px solid #343434;
        border-radius: 11px;
        background: #171717;
    }

    [data-testid="stCode"] {
        border: 1px solid #343434;
        border-radius: 10px;
    }

    [data-testid="stAlert"] {
        border-radius: 13px;
        border-width: 1px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1.2rem;
        }

        .hm-hero {
            padding: 1.5rem 1.3rem;
            border-radius: 17px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# ESTADO DE LA APLICACIÓN
# =========================================================
def initialize_state() -> None:
    defaults = {
        "messages": [],
        "transcription": "",
        "transcription_filename": "",
        "last_recording_signature": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def show_classification(
    classification: QueryClassification,
) -> None:
    urgency = (
        "🔴"
        if classification.prioridad == "Crítica"
        else "🟠"
        if classification.prioridad == "Alta"
        else "🔵"
    )

    st.markdown(
        f'<span class="hm-badge">'
        f"{classification.categoria}</span>"
        f'<span class="hm-badge">'
        f"{urgency} {classification.prioridad}</span>",
        unsafe_allow_html=True,
    )

    with st.expander("Ver clasificación estructurada"):
        st.code(
            json.dumps(
                classification.to_dict(),
                ensure_ascii=False,
                indent=2,
            ),
            language="json",
        )


def handle_query(
    query: str,
    prompt_version: str,
) -> None:
    previous_history = list(st.session_state.messages)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Analizando la consulta..."):
            try:
                started = perf_counter()

                chat_result = generate_reply(
                    query,
                    previous_history,
                    prompt_version,
                )

                classification = classify_query(
                    query,
                    previous_history,
                )

                total_elapsed = round(
                    perf_counter() - started,
                    3,
                )

            except SmartSupportError as error:
                st.error(str(error))
                st.session_state.messages.pop()
                return

        st.markdown(chat_result.answer)
        show_classification(classification)

        st.caption(
            f"Modelo: {chat_result.model} · "
            f"Tiempo de respuesta: {total_elapsed:.2f} s · "
            f"Clasificación: {classification.fuente}"
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": chat_result.answer,
                "classification": classification.to_dict(),
                "elapsed_seconds": total_elapsed,
            }
        )


initialize_state()


# =========================================================
# BARRA LATERAL
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="hm-side-brand">
            HM <span>SMART</span> SUPPORT
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Configuración")

    st.toggle(
        "☀️ Modo claro",
        key="light_mode",
        help="Activa o desactiva el tema claro.",
    )

    prompt_version = st.selectbox(
        "Versión del prompt",
        ("V3", "V2", "V1"),
        help=(
            "V3 es la versión final recomendada. "
            "V1 y V2 permiten demostrar la evolución."
        ),
    )

    st.caption(f"Chat: {settings.chat_model}")
    st.caption(f"Audio: {settings.transcription_model}")

    if st.button(
        "Reiniciar conversación",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.transcription = ""
        st.session_state.transcription_filename = ""
        st.session_state.last_recording_signature = ""

        st.session_state.pop(
            "transcription_editor",
            None,
        )
        st.session_state.pop(
            "voice_recorder",
            None,
        )

        st.rerun()

    st.divider()

    api_is_configured = (
        settings.api_key
        and settings.api_key
        != "sk-reemplaza_con_tu_clave"
    )

    if api_is_configured:
        st.markdown(
            """
            <div class="hm-api-status">
                <span class="dot"></span>
                API configurada
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="hm-api-status missing">
                <span class="dot"></span>
                Configura la API en el archivo .env
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# SOBRESCRITURA DEL MODO CLARO
# =========================================================
if st.session_state.light_mode:
    st.markdown(
        """
        <style>
        :root {
            --hm-surface: #ffffff;
            --hm-surface-2: #f4f4f4;
            --hm-border: #dedede;
            --hm-text: #171717;
            --hm-muted: #666666;
        }

        .stApp {
            background: #ffffff;
            color: #171717;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, .94);
        }

        [data-testid="stSidebar"] {
            background: #eeeeee;
            border-right: 1px solid #d4d4d4;
        }

        [data-testid="stSidebar"] hr,
        hr {
            border-color: #dddddd !important;
        }

        [data-testid="stSidebar"]
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] {
            color: #696969;
        }

        h1, h2, h3, p, label, .stMarkdown {
            color: #171717;
        }

        .hm-side-brand {
            color: #171717;
        }

        .hm-hero {
            border-color: #dedede;
            background:
                linear-gradient(
                    135deg,
                    #ffffff 0%,
                    #f5f5f5 100%
                );
            box-shadow:
                0 18px 45px rgba(0, 0, 0, .08);
        }

        .hm-title,
        .hm-section-title {
            color: #151515;
        }

        .hm-subtitle,
        .hm-composer-copy {
            color: #646464;
        }

        .hm-api-status {
            border-color: #d5d5d5;
            background: #ffffff;
            color: #303030;
        }

        [data-baseweb="select"] > div,
        [data-testid="stTextArea"] textarea,
        [data-testid="stChatInput"] {
            background: #ffffff !important;
            border-color: #d8d8d8 !important;
            color: #171717 !important;
        }

        [data-baseweb="select"] * {
            color: #171717 !important;
        }

        [data-testid="stChatInput"] textarea,
        [data-testid="stTextArea"] textarea {
            color: #171717 !important;
        }

        [data-testid="stChatInput"]
        textarea::placeholder,
        [data-testid="stTextArea"]
        textarea::placeholder {
            color: #858585 !important;
        }

        [data-testid="stAudioInput"]
        > div:last-child {
            border-color: #d8d8d8;
            background: #ffffff;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: #f7f7f7;
            border-color: #c9c9c9;
        }

        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] small {
            color: #444444 !important;
        }

        .stButton > button {
            border-color: #d1d1d1;
            background: #ffffff;
            color: #202020;
        }

        .stButton > button[kind="primary"] {
            border-color: var(--hm-orange);
            background: var(--hm-orange);
            color: #111111;
        }

        [data-testid="stChatMessage"] {
            border-color: #dedede;
            background: #ffffff;
            box-shadow:
                0 5px 18px rgba(0, 0, 0, .045);
        }

        [data-testid="stChatMessage"]:has(
            [data-testid="chatAvatarIcon-user"]
        ) {
            background: #fff8f3;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li {
            color: #202020;
        }

        [data-testid="stExpander"] {
            border-color: #dddddd;
            background: #ffffff;
        }

        [data-testid="stCode"] {
            border-color: #dddddd;
            background: #f6f6f6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ENCABEZADO
# =========================================================
st.markdown(
    """
<section class="hm-hero">
    <div class="hm-title">HM Smart <span>Support</span></div>
    <p class="hm-subtitle">Asistencia multimodal para resolver consultas sobre configuración, mantenimiento, repuestos, garantía, fallas y servicio técnico.</p>
</section>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HISTORIAL DE CONVERSACIÓN
# =========================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("classification")
        ):
            show_classification(
                QueryClassification(
                    **message["classification"]
                )
            )

            if message.get("elapsed_seconds") is not None:
                st.caption(
                    "Tiempo de respuesta: "
                    f"{message['elapsed_seconds']:.2f} s"
                )


# =========================================================
# CAMPO DE TEXTO Y MICRÓFONO
# =========================================================
st.divider()

st.markdown(
    """
    <div class="hm-section-title">
        ¿En qué podemos ayudarte?
    </div>

    <div class="hm-composer-copy">
        Escribe tu consulta o pulsa el micrófono para hablar.
    </div>
    """,
    unsafe_allow_html=True,
)

text_column, microphone_column = st.columns(
    [9, 1],
    gap="small",
    vertical_alignment="bottom",
)

with text_column:
    text_query = st.chat_input(
        "Escribe tu consulta de postventa...",
        key="main_chat_input",
    )

with microphone_column:
    recorded_audio = st.audio_input(
        "Grabar consulta",
        key="voice_recorder",
        label_visibility="collapsed",
    )


# Procesar automáticamente la grabación del micrófono.
voice_query = None

if recorded_audio is not None:
    recording_signature = hashlib.sha256(
        recorded_audio.getvalue()
    ).hexdigest()

    is_new_recording = (
        recording_signature
        != st.session_state.last_recording_signature
    )

    if is_new_recording:
        st.session_state.last_recording_signature = (
            recording_signature
        )

        with st.spinner(
            "Escuchando y transcribiendo tu consulta..."
        ):
            try:
                voice_result = transcribe_uploaded_audio(
                    recorded_audio
                )

                voice_query = voice_result.text.strip()

                if voice_query:
                    st.toast(
                        "Voz transcrita. Preparando respuesta...",
                        icon="🎙️",
                    )

            except SmartSupportError as error:
                st.error(str(error))


# =========================================================
# CARGA DE ARCHIVOS DE AUDIO
# =========================================================
audio_query = None

with st.expander(
    "Adjuntar un audio MP3, WAV o M4A"
):
    st.caption(
        "También puedes cargar una grabación guardada "
        "y corregir su texto antes de enviarla."
    )

    uploaded_audio = st.file_uploader(
        "Selecciona el archivo",
        type=["mp3", "wav", "m4a"],
        accept_multiple_files=False,
    )

    if uploaded_audio is not None:
        st.write(
            f"Archivo: **{uploaded_audio.name}**"
        )

        st.audio(uploaded_audio)

        if st.button(
            "Transcribir archivo",
            type="secondary",
        ):
            with st.spinner("Transcribiendo..."):
                try:
                    result = transcribe_uploaded_audio(
                        uploaded_audio
                    )

                    st.session_state.transcription = (
                        result.text
                    )

                    st.session_state.transcription_filename = (
                        result.filename
                    )

                    st.session_state.transcription_editor = (
                        result.text
                    )

                    st.success(
                        "Audio transcrito correctamente."
                    )

                except SmartSupportError as error:
                    st.error(str(error))

    if st.session_state.transcription:
        transcription = st.text_area(
            "Transcripción "
            "(puedes corregirla antes de enviarla)",
            value=st.session_state.transcription,
            height=110,
            key="transcription_editor",
        )

        if st.button(
            "Usar transcripción como consulta",
            type="primary",
        ):
            audio_query = transcription.strip()


# =========================================================
# ENVIAR CONSULTA
# =========================================================
query_to_process = (
    voice_query
    or audio_query
    or text_query
)

if query_to_process:
    handle_query(
        query_to_process,
        prompt_version,
    )