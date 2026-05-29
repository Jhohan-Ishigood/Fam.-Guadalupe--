# CATÁLOGO PREMIUM FAM. GUADALUPE v5.0 — RENDER MASTER EDITION

## app.py

import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64
import mimetypes
import urllib.parse
import time

# =========================================================
# CONFIGURACIÓN GLOBAL
# =========================================================

st.set_page_config(
    page_title="CATÁLOGO PREMIUM FAM. GUADALUPE",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# =========================================================
# FUNCIONES
# =========================================================

@st.cache_data(show_spinner=False)
def convertir_base64(ruta_archivo):

    if not os.path.exists(ruta_archivo):
        return ""

    mime_type, _ = mimetypes.guess_type(ruta_archivo)

    if mime_type is None:
        mime_type = "image/png"

    with open(ruta_archivo, "rb") as archivo:
        encoded = base64.b64encode(archivo.read()).decode()

    return f"data:{mime_type};base64,{encoded}"


def guardar_json(ruta, datos):

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def cargar_menu():

    FOTO_DEFAULT = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><rect width='300' height='300' fill='%23222222'/></svg>"

    inventario = {
        "Arroz Costeño x1kg": {
            "precio": 4.50,
            "icono": "🌾",
            "stock": 120,
            "disponible": True,
            "categoria": "Abarrotes",
            "foto": FOTO_DEFAULT
        },

        "Parlante JBL Bluetooth": {
            "precio": 149.90,
            "icono": "🔊",
            "stock": 5,
            "disponible": True,
            "categoria": "Tecnología",
            "foto": FOTO_DEFAULT
        }
    }

    if os.path.exists(RUTA_MENU):

        try:

            with open(RUTA_MENU, "r", encoding="utf-8") as archivo:
                return json.load(archivo)

        except:
            return inventario

    return inventario


def cargar_categorias():

    categorias = [
        "Todos",
        "Abarrotes",
        "Tecnología"
    ]

    if os.path.exists(RUTA_CATEGORIAS):

        try:

            with open(RUTA_CATEGORIAS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)

        except:
            return categorias

    return categorias

# =========================================================
# SESSION STATE
# =========================================================

if "menu_dinamico" not in st.session_state:
    st.session_state.menu_dinamico = cargar_menu()

if "lista_categorias" not in st.session_state:
    st.session_state.lista_categorias = cargar_categorias()

if "pantalla" not in st.session_state:
    st.session_state.pantalla = "bienvenida"

if "categoria_activa" not in st.session_state:
    st.session_state.categoria_activa = "Todos"

if "carrito" not in st.session_state:
    st.session_state.carrito = []

if "total" not in st.session_state:
    st.session_state.total = 0

if "pedido_confirmado" not in st.session_state:
    st.session_state.pedido_confirmado = False

if "bloqueo_stock" not in st.session_state:
    st.session_state.bloqueo_stock = False

if "es_admin_autenticado" not in st.session_state:
    st.session_state.es_admin_autenticado = False

# =========================================================
# FECHA PERÚ
# =========================================================

zona_peru = timezone(timedelta(hours=-5))
ahora_peru = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

# =========================================================
# MULTIMEDIA
# =========================================================

URL_FONDO = convertir_base64(os.path.join(BASE_DIR, "establecimiento.png"))
URL_LOGO = convertir_base64(os.path.join(BASE_DIR, "Logotipo.png"))
URL_QR = convertir_base64(os.path.join(BASE_DIR, "miqr1.png"))

# VIDEO DIRECTO MP4 REAL
URL_VIDEO_PC = "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_MOVIL = "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_LOGO = "https://res.cloudinary.com/demo/video/upload/sample.mp4"

# =========================================================
# CSS MASTER ULTRA PREMIUM
# =========================================================

st.markdown(f'''

<style>

/* =========================================================
FONDO PANORÁMICO PREMIUM
========================================================= */

[data-testid="stAppViewContainer"]{{

    background:
    linear-gradient(
        rgba(0,0,0,.78),
        rgba(0,0,0,.78)
    ),
    url("{URL_FONDO}");

    background-size:130% auto;
    background-position:0% center;
    background-repeat:no-repeat;
    background-attachment:fixed;

    animation:fondoMaster 25s ease-in-out infinite alternate;
}}

@keyframes fondoMaster{{

    from{{
        background-position:0% center;
    }}

    to{{
        background-position:100% center;
    }}
}}

@media (max-width:768px){{

    [data-testid="stAppViewContainer"]{{

        background-size:auto 100% !important;

        animation:fondoMobile 30s linear infinite alternate;
    }}
}}

@keyframes fondoMobile{{

    from{{
        background-position:0% center;
    }}

    to{{
        background-position:100% center;
    }}
}}

/* =========================================================
TRANSPARENCIA
========================================================= */

.main,
.block-container,
section[data-testid="stSidebar"],
[data-testid="stHeader"],
[data-testid="stToolbar"]{{

    background:transparent !important;
}}

/* =========================================================
VIDEO BACKGROUND
========================================================= */

.video-background{{

    position:fixed;
    inset:0;

    width:100%;
    height:100%;

    overflow:hidden;

    z-index:-10;
}}

.video-background video{{

    width:100%;
    height:100%;

    object-fit:cover;
}}

/* =========================================================
MINI LOGO
========================================================= */

.mini-logo-master{{

    position:fixed;

    top:60px;
    right:25px;

    width:65px;
    height:65px;

    z-index:999999;

    animation:giroMoneda 4s linear infinite;
}}

.mini-logo-master video{{

    width:100%;
    height:100%;

    object-fit:cover;

    border-radius:50%;

    border:2px solid #d4af37;
}}

@keyframes giroMoneda{{

    from{{
        transform:rotateY(0deg);
    }}

    to{{
        transform:rotateY(360deg);
    }}
}}

@media (max-width:768px){{

    .mini-logo-master{{

        top:15px !important;
        left:15px !important;
        right:auto !important;

        width:45px;
        height:45px;
    }}
}}

/* =========================================================
LOGO CENTRAL
========================================================= */

.logo-central{{

    position:relative;

    width:206px;
    height:206px;

    margin:auto;

    border-radius:50%;

    overflow:hidden;

    border:3px solid #d4af37;

    box-shadow:
    0 0 25px rgba(212,175,55,.7),
    0 0 60px rgba(212,175,55,.4);

    animation:flotar 4s ease-in-out infinite;
}}

.logo-central video{{

    width:100%;
    height:100%;

    object-fit:cover;
}}

@keyframes flotar{{

    0%{{
        transform:translateY(0px);
    }}

    50%{{
        transform:translateY(-8px);
    }}

    100%{{
        transform:translateY(0px);
    }}
}}

.destello-fisico-linea{{

    position:absolute;

    top:-20%;
    left:-150%;

    width:80px;
    height:160%;

    background:linear-gradient(
        120deg,
        transparent,
        rgba(255,255,255,.85),
        transparent
    );

    transform:rotate(20deg);

    animation:destello 4s infinite;
}}

@keyframes destello{{

    0%{{
        left:-150%;
    }}

    20%{{
        left:150%;
    }}

    100%{{
        left:150%;
    }}
}}

/* =========================================================
TÍTULOS
========================================================= */

.titulo-principal{{

    text-align:center;

    color:#ffffff;

    font-size:52px;

    font-weight:900;

    text-shadow:
    0 0 25px rgba(212,175,55,.8);
}}

/* =========================================================
GRID
========================================================= */

.grid-productos{{

    display:grid;

    grid-template-columns:repeat(4,minmax(0,1fr));

    gap:22px;
}}

@media (max-width:768px){{

    .grid-productos{{

        grid-template-columns:repeat(2,minmax(0,1fr));

        gap:14px;
    }}
}}

/* =========================================================
TARJETAS
========================================================= */

.tarjeta-producto{{

    background:rgba(0,0,0,.58);

    backdrop-filter:blur(10px);

    border-radius:18px;

    overflow:hidden;

    transition:all .35s ease;

    animation:fadeUp .4s ease;
}}

.tarjeta-producto:hover{{

    transform:translateY(-5px);

    box-shadow:
    0 0 25px rgba(212,175,55,.45);
}}

.tarjeta-producto img{{

    width:100%;
    height:220px;

    object-fit:cover;

    transition:transform .35s ease;
}}

.tarjeta-producto:hover img{{

    transform:scale(1.05);
}}

.info-producto{{

    padding:16px;
}}

.nombre-producto{{

    color:white;

    font-weight:900;

    font-size:17px;
}}

.precio-producto{{

    color:#2ecc71;

    font-size:22px;

    font-weight:900;
}}

.stock-alerta{{

    color:#ff4b4b;

    font-weight:900;

    animation:parpadeo 1s infinite;
}}

@keyframes parpadeo{{

    0%{{opacity:1;}}
    50%{{opacity:.2;}}
    100%{{opacity:1;}}
}}

@keyframes fadeUp{{

    from{{
        opacity:0;
        transform:translateY(15px);
    }}

    to{{
        opacity:1;
        transform:translateY(0px);
    }}
}}

/* =========================================================
BOTÓN ESCÁNER
========================================================= */

div.stButton > button{{

    position:relative;

    overflow:hidden;

    border:none;

    border-radius:16px;

    height:60px;

    font-size:17px;

    font-weight:900;

    background:linear-gradient(90deg,#d4af37,#f1c40f);

    color:#000;

    box-shadow:
    0 0 20px rgba(212,175,55,.5);
}}

div.stButton > button::before{{

    content:"";

    position:absolute;

    top:0;
    left:-100%;

    width:40%;
    height:100%;

    background:linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,.7),
        transparent
    );

    animation:scanner 3s infinite;
}}

@keyframes scanner{{

    0%{{
        left:-100%;
    }}

    100%{{
        left:150%;
    }}
}}

/* =========================================================
TOTAL CARRITO
========================================================= */

.total-master{{

    text-align:center;

    color:#2ecc71;

    font-size:48px;

    font-weight:900;

    text-shadow:
    0 0 25px rgba(46,204,113,.8);
}}

</style>

''', unsafe_allow_html=True)

# =========================================================
# VIDEO FONDO
# =========================================================

st.markdown(f'''

<div class="video-background">

<video autoplay loop muted playsinline>

<source src="{URL_VIDEO_PC}" type="video/mp4">

</video>

</div>

<div class="mini-logo-master">

<video autoplay loop muted playsinline>

<source src="{URL_VIDEO_LOGO}" type="video/mp4">

</video>

</div>

''', unsafe_allow_html=True)

# =========================================================
# BIENVENIDA
# =========================================================

if st.session_state.pantalla == "bienvenida":

    st.markdown("<h1 class='titulo-principal'>FAMILIA GUADALUPE</h1>", unsafe_allow_html=True)

    st.markdown("<p style='text-align:center;color:#d4af37;font-size:24px;font-weight:bold;'>CATÁLOGO PREMIUM DE PRODUCTOS 🔥</p>", unsafe_allow_html=True)

    st.markdown(f'''

    <div class="logo-central">

        <div class="destello-fisico-linea"></div>

        <video autoplay loop muted playsinline>
            <source src="{URL_VIDEO_LOGO}" type="video/mp4">
        </video>

    </div>

    ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True):

        st.session_state.pantalla = "catalogo"
        st.rerun()

    with st.expander("🏦 BANCO DE LA NACIÓN"):

        st.markdown("""
        ### DATOS BANCARIOS

        Número: 04-762-855629

        Titular: Segundo Melquiades Guadalupe Sanchez
        """)

    with st.expander("🟣 YAPE"):

        st.image(URL_QR, width=240)

        st.markdown("""
        ### YAPE

        +51 950 239 350
        """)

    with st.expander("🟢 WHATSAPP"):

        st.markdown("""
        ### CONTACTO

        +51 950 239 350
        """)

# =========================================================
# CATÁLOGO
# =========================================================

elif st.session_state.pantalla == "catalogo":

    st.markdown("<h1 class='titulo-principal'>CATÁLOGO</h1>", unsafe_allow_html=True)

    busqueda = st.text_input("Buscar producto")

    categoria = st.radio(
        "Categorías",
        options=st.session_state.lista_categorias,
        horizontal=True
    )

    cantidades = {}

    productos_filtrados = []

    for producto, info in st.session_state.menu_dinamico.items():

        if busqueda.lower() not in producto.lower():
            continue

        if categoria != "Todos":

            if info["categoria"] != categoria:
                continue

        productos_filtrados.append(producto)

    st.markdown('<div class="grid-productos">', unsafe_allow_html=True)

    for producto in productos_filtrados:

        info = st.session_state.menu_dinamico[producto]

        stock = info["stock"]

        st.markdown(f'''

        <div class="tarjeta-producto">

            <img src="{info['foto']}">

            <div class="info-producto">

                <div class="nombre-producto">
                    {info['icono']} {producto}
                </div>

                <div class="precio-producto">
                    S/{info['precio']:.2f}
                </div>

        ''', unsafe_allow_html=True)

        if stock <= 3:

            st.markdown(f'''
            <div class="stock-alerta">
                🔥 SOLO QUEDAN {stock} UNIDADES
            </div>
            ''', unsafe_allow_html=True)

        else:

            st.markdown(f'''
            <div style="color:#cccccc;">
                📦 Stock disponible: {stock}
            </div>
            ''', unsafe_allow_html=True)

        cantidades[producto] = st.number_input(
            producto,
            min_value=0,
            max_value=int(stock),
            key=producto
        )

        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    if st.button("🛒 SIMULAR MONTO FINAL", use_container_width=True):

        st.session_state.carrito = []
        st.session_state.total = 0

        for producto, cantidad in cantidades.items():

            if cantidad > 0:

                subtotal = cantidad * st.session_state.menu_dinamico[producto]["precio"]

                st.session_state.carrito.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "subtotal": subtotal
                })

                st.session_state.total += subtotal

        if st.session_state.total > 0:

            st.session_state.pantalla = "carrito"
            st.rerun()

# =========================================================
# CARRITO
# =========================================================

elif st.session_state.pantalla == "carrito":

    st.markdown("<h1 class='titulo-principal'>CARRITO</h1>", unsafe_allow_html=True)

    mensaje = "Hola Familia Guadalupe, deseo coordinar mi pedido:%0A%0A"

    for item in st.session_state.carrito:

        producto = item["producto"]
        cantidad = item["cantidad"]
        subtotal = item["subtotal"]

        st.markdown(f'''

        <div style="
            background:rgba(0,0,0,.55);
            padding:18px;
            border-radius:16px;
            margin-bottom:12px;
            color:white;
            border-left:4px solid #d4af37;
        ">

            {producto} x{cantidad}

            <br>

            <b>S/{subtotal:.2f}</b>

        </div>

        ''', unsafe_allow_html=True)

        mensaje += f"{producto} x{cantidad} - S/{subtotal:.2f}%0A"

    st.markdown(f'''

    <div class="total-master">
        TOTAL: S/{st.session_state.total:.2f}
    </div>

    ''', unsafe_allow_html=True)

    mensaje += f"%0A💰 TOTAL: S/{st.session_state.total:.2f}"

    url_whatsapp = f"https://wa.me/51950239350?text={mensaje}"

    st.markdown("<br>", unsafe_allow_html=True)

    st.info("⚠️ Recomendación: Tómale una captura antes de transferir.")

    col1, col2 = st.columns(2)

    with col1:

        if st.button("💾 CONFIRMAR SIMULACIÓN", use_container_width=True):

            if not st.session_state.bloqueo_stock:

                st.session_state.bloqueo_stock = True

                for item in st.session_state.carrito:

                    producto = item["producto"]
                    cantidad = item["cantidad"]

                    stock_actual = st.session_state.menu_dinamico[producto]["stock"]

                    nuevo_stock = max(0, stock_actual - cantidad)

                    st.session_state.menu_dinamico[producto]["stock"] = nuevo_stock

                    st.session_state.menu_dinamico[producto]["disponible"] = nuevo_stock > 0

                guardar_json(RUTA_MENU, st.session_state.menu_dinamico)

                st.success("✔ Pedido procesado correctamente")

                st.balloons()

                time.sleep(1)

                st.rerun()

    with col2:

        st.link_button(
            "🟢 ENVIAR PEDIDO POR WHATSAPP",
            url_whatsapp,
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 NUEVA ORDEN", use_container_width=True):

        st.session_state.carrito = []
        st.session_state.total = 0
        st.session_state.pantalla = "bienvenida"
        st.session_state.bloqueo_stock = False

        st.rerun()