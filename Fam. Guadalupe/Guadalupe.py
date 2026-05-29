import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64
import mimetypes
import urllib.parse
import hashlib

# ------ CONFIGURACIÓN GLOBAL ------
st.set_page_config(
    page_title="Catálogo FAM. GUADALUPE - Productos de Calidad",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

RUTA_CSS = os.path.join(BASE_DIR, "estilos.css")
RUTA_JSON_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_JSON_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# ------ FUNCIONES AUXILIARES ------
@st.cache_data(show_spinner=False)
def cargar_recurso_base64(ruta_archivo, tipo_recurso="imagen"):
    if os.path.exists(ruta_archivo):
        try:
            mime_type, _ = mimetypes.guess_type(ruta_archivo)
            if not mime_type:
                mime_type = "video/mp4" if tipo_recurso == "video" else "image/png"
            with open(ruta_archivo, "rb") as fichero:
                encoded = base64.b64encode(fichero.read()).decode()
                return f"data:{mime_type};base64,{encoded}"
        except Exception:
            return ""
    return ""

def guardar_json(ruta, datos):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando datos: {e}")

def cargar_menu_desde_archivo():
    FOTO_DEFECTO = ("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' "
                    "viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' "
                    "stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' "
                    "height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/>"
                    "<polyline points='21 15 16 10 5 21'/></svg>")
    inventario_defecto = {
        "Arroz Costeño x 1kg": {"precio": 4.50, "icono": "🌾", "disponible": True, "foto": FOTO_DEFECTO, "stock": 120, "categoria": "Abarrotes"},
        "Parlante Bluetooth JBL": {"precio": 140.00, "icono": "🔊", "disponible": True, "foto": FOTO_DEFECTO, "stock": 5, "categoria": "Tecnología"},
        "Montura de Cuero Fina": {"precio": 420.00, "icono": "🐎", "disponible": True, "foto": FOTO_DEFECTO, "stock": 2, "categoria": "Línea Ecuestre"},
        "Tubo PVC de Construcción 1/2": {"precio": 8.50, "icono": "🛠️", "disponible": True, "foto": FOTO_DEFECTO, "stock": 0, "categoria": "Ferretería & Electricidad"},
        "Cuaderno Standford A4 Liso": {"precio": 6.50, "icono": "📚", "disponible": True, "foto": FOTO_DEFECTO, "stock": 60, "categoria": "Útiles Escolares"}
    }
    if os.path.exists(RUTA_JSON_MENU):
        try:
            with open(RUTA_JSON_MENU, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return inventario_defecto
    return inventario_defecto

def cargar_categorias_desde_archivo():
    categorias_defecto = ["Todos", "Abarrotes", "Ferretería & Electricidad", "Tecnología", "Línea Ecuestre", "Útiles Escolares"]
    if os.path.exists(RUTA_JSON_CATEGORIAS):
        try:
            with open(RUTA_JSON_CATEGORIAS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return categorias_defecto
    return categorias_defecto

def renderizar_informacion_pago(total_contexto=None):
    st.markdown("### 💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO")
    st.caption("Selecciona tu método de pago haciendo clic para desplegar los datos bancarios:")

    with st.expander("🏦 VER N° DE CUENTA DEL BANCO DE LA NACIÓN", expanded=False):
        st.markdown("""
        <div style="background-color: #111424; padding: 15px; border-radius: 8px; border-left: 4px solid #2980b9; margin-bottom: 5px;">
        <p style="color: #2980b9; font-weight: bold; font-size: 16px;">🏦 BANCO DE LA NACIÓN / BNP</p>
        <p style="color: #fff; font-size: 14px;"><b>Número de Cuenta:</b> 04-762-855629</p>
        <hr style="border-color: #222538; margin: 10px 0;">
        <p style="color: #aaa; font-size: 14px;"><b>Titular:</b> Segundo Melquiades Guadalupe Sanchez</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🟣 VER NÚMERO Y QR DE YAPE", expanded=False):
        if total_contexto is not None:
            st.markdown(f"<p style='color:#fff; font-weight:bold; font-size:15px; margin-bottom:10px; text-align:center;'>Monto exacto a transferir: <span style='color:#2ecc71;'>S/{total_contexto:.2f}</span></p>", unsafe_allow_html=True)
        src_qr = URL_QR_YAPE if URL_QR_YAPE else ""
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 5px auto; max-width: 450px; background-color: #1e1e24; padding: 20px; border-radius: 16px; border: 2px solid #8e44ad; text-align: center;">
        <p style="color: #aaa; font-size: 13px; margin-bottom: 12px; font-weight: bold;">Escanee con la cámara de su celular para pagar:</p>
        <img src="{src_qr}" style="width: 240px; height: 240px; object-fit: contain; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;" />
        <span style="color: #8e44ad; font-size: 15px; font-weight: 900;">🟣 +51 950 239 350</span>
        <p style="color:#888; font-size:12px; margin-top:5px; margin-bottom:0;">Titular: Jhohan Antoni Guadalupe Cusquipoma</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📞 VER TELÉFONO DE CONTACTO DIRECTO", expanded=False):
        st.markdown("""
        <div style="background-color: #111424; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
        <p style="color: #27ae60; font-weight: bold; font-size: 16px;">🟢 WHATSAPP Y LLAMADAS DIRECTAS</p>
        <p style="color: #fff; font-size: 14px;"><b>Número Celular:</b> +51 950 239 350</p>
        <hr style="border-color: #222538; margin: 10px 0;">
        <p style="color: #aaa; font-size: 13px;">Use este canal directo para coordinar despachos inmediatos o resolver consultas.</p>
        </div>
        """, unsafe_allow_html=True)

# ------ VARIABLES GLOBALES Y SESIÓN ------
zona_peru = timezone(timedelta(hours=-5))
ahora_peru = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

URL_FOTO_TIENDA = cargar_recurso_base64(os.path.join(BASE_DIR, "establecimiento.png"), "imagen")
URL_QR_YAPE = cargar_recurso_base64(os.path.join(BASE_DIR, "miqr1.png"), "imagen")
URL_LOGOTIPO = cargar_recurso_base64(os.path.join(BASE_DIR, "Logotipo.png"), "imagen")

URL_VIDEO_PC = "https://streamable.com/hovyqm"
URL_VIDEO_MOVIL = "https://streamable.com/6oo3z9"
URL_VIDEO_LOGO = "https://streamable.com/4gffqo"

if os.path.exists(RUTA_CSS):
    try:
        with open(RUTA_CSS, "r", encoding="utf-8") as f:
            custom_css = f.read()
            st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    except:
        pass

# Fondo panorámico y animación vaivén
st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    position: relative;
    overflow: hidden;
    background-image: url("establecimiento.png");
    background-repeat: no-repeat;
    background-size: 130% auto;
    background-position: 0% center;
    animation: barridoHorizontal 25s ease-in-out infinite alternate;
}}
@keyframes barridoHorizontal {{
    0% {{ background-position: 0% center; }}
    100% {{ background-position: 100% center; }}
}}
@media (max-width: 768px) {{
    [data-testid="stAppViewContainer"] {{
        background-size: auto 100% !important;
        animation: barridoVertical 30s ease-in-out infinite alternate;
    }}
    @keyframes barridoVertical {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 100% center; }}
    }}
}}
</style>
""", unsafe_allow_html=True)

# Mini-logo flotante rotando 3D adaptable a PC y móvil
st.markdown(f"""
<style>
.mini-logo-flotante-master {{
    position: fixed !important;
    top: 60px !important;
    right: 25px !important;
    width: 65px !important;
    height: 65px !important;
    z-index: 999999 !important;
    perspective: 1000px !important;
    pointer-events: none !important;
    animation: rotarMiniLogo3D 4s linear infinite;
}}
@media (max-width: 768px) {{
    .mini-logo-flotante-master {{
        top: 15px !important;
        left: 15px !important;
        right: auto !important;
        width: 45px !important;
        height: 45px !important;
        animation: rotarMiniLogo3D 4s linear infinite;
        transform:none !important;
    }}
}}
@keyframes rotarMiniLogo3D {{
    0% {{ transform: rotateY(0deg); }}
    100% {{ transform: rotateY(360deg); }}
}}
</style>
<div class="mini-logo-flotante-master">
    <video autoplay loop muted playsinline style="width: 100%; height: 100%; border-radius: 50%; border: 2px solid #d4af37; box-shadow: 0 0 15px rgba(212,175,55,0.6); object-fit: cover;">
        <source src="{URL_VIDEO_LOGO}" type="video/mp4" />
    </video>
</div>
""", unsafe_allow_html=True)

# --- Inicialización variables sesión ---
for key, default in {
    "menu_dinamico": cargar_menu_desde_archivo(),
    "lista_categorias": cargar_categorias_desde_archivo(),
    "carrito": [],
    "total_acumulado": 0.0,
    "pedido_guardado": False,
    "pantalla_actual": "bienvenida",
    "categoria_activa": "Todos",
    "es_admin_autenticado": False,
    "mostrar_login_admin": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Resto del código, panel admin, cliente, carrito y más ---
# (Si quieres, te puedo enviar en la siguiente parte para no extender mucho esta.)

# --- Botón con luz corrediza (ejemplo estilo) ---
st.markdown("""
<style>
.btn-luz-escaner > button {
position: relative;
overflow: hidden;
background: linear-gradient(135deg, #d4af37 0%, #aa8416 100%);
color: #0a0a0f;
font-weight: 900;
font-family: 'Arial Black', Gadget, sans-serif;
border: 1px solid #f1c40f;
text-transform: uppercase;
box-shadow: 0 4px 12px rgba(212,175,55,0.35);
}
.btn-luz-escaner > button::before {
Content: "";
position: absolute;
top: 0; left: -100%;
width: 200%;
height: 100%;
background: linear-gradient(90deg, transparent, rgba(255,255,255,0.75), transparent);
animation: luzCorrediza 3s linear infinite;
pointer-events: none;
}
@keyframes luzCorrediza {
0% { left: -100%; }
100% { left: 100%; }
}
</style>
""", unsafe_allow_html=True)
# --- Comienzo de pantallas según estado ---
def pantalla_bienvenida():
    st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

    st.markdown("<h3 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; margin-top: -10px; font-weight: bold; color: #d4af37;'>Bienvenidos al stock de productos disponibles y sus precios 🔥</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Logo grande con animación flotante y destello
    st.markdown(f"""
    <div style="position: relative; width: 206px; height: 206px; margin: 0 auto; border: 3px solid #d4af37; border-radius: 50%; box-shadow: 0 0 25px #d4af37;">
        <video autoplay loop muted playsinline style="width: 100%; height: 100%; border-radius: 50%; animation: flotacionVertical 3s ease-in-out infinite;">
            <source src="{URL_VIDEO_LOGO}" type="video/mp4" />
        </video>
        <div style="
            position: absolute;
            top: 0; left: -50%;
            width: 50%;
            height: 100%;
            background: linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent);
            animation: destello 4s linear infinite;
            border-radius: 50%;
            pointer-events: none;
        "></div>
    </div>

    <style>
    @keyframes flotacionVertical {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-8px); }}
    }}

    @keyframes destello {{
        0% {{ left: -50%; opacity: 0; }}
        50% {{ left: 100%; opacity: 1; }}
        100% {{ left: 100%; opacity: 0; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="btn-luz-escaner">', unsafe_allow_html=True)
    if st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_empezar"):
        st.session_state.pantalla_actual = "catalogo"
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    renderizar_informacion_pago()

    st.markdown("""
    <div class='social-footer'>
        <p style='margin-bottom: 10px; font-size: 14px; letter-spacing: 2px; color: #888; font-weight: bold;'>SÍGUENOS EN REDES SOCIALES</p>
        <a href='https://facebook.com' target='_blank' class='social-icon'>📘 Facebook</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href='https://instagram.com' target='_blank' class='social-icon'>📸 Instagram</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
        <a href='https://wa.me' target='_blank' class='social-icon'>🟢 WhatsApp</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def pantalla_catalogo():
    st.markdown('<div class="catalogo-transparente-master">', unsafe_allow_html=True)
    st.markdown(f"<h2 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #aaa;'>Fecha y hora Perú (GMT-5): {fecha_actual}</h3>\n", unsafe_allow_html=True)

    st.markdown("<div class='netflix-navbar-master'>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([2.5, 1.5], gap="small")
    with col_izq:
        categoria = st.radio(
            "Categorías",
            options=st.session_state.lista_categorias,
            index=st.session_state.lista_categorias.index(st.session_state.categoria_activa),
            horizontal=True,
            label_visibility="collapsed",
            key="catalogo_categorias"
        )
        if categoria != st.session_state.categoria_activa:
            st.session_state.categoria_activa = categoria
            st.experimental_rerun()
    with col_der:
        busqueda = st.text_input("Buscar", placeholder="Buscar aquí...", label_visibility="collapsed", key="catalogo_busqueda").strip().lower()
    st.markdown("</div><br>", unsafe_allow_html=True)

    st.subheader(f"📍 SELECCIÓN DE {st.session_state.categoria_activa.upper()}")
    st.info("Ingrese las cantidades de los productos que desea llevar:")

    productos_filtrados = []
    for prod, info in st.session_state.menu_dinamico.items():
        if busqueda and busqueda not in prod.lower():
            continue
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == info.get("categoria",""):
            productos_filtrados.append(prod)

    st.markdown('<div class="grid-productos-responsivo">', unsafe_allow_html=True)

    cantidades = {}
    for prod in productos_filtrados:
        info = st.session_state.menu_dinamico[prod]
        stock = info.get("stock", 0)
        disponible = info.get("disponible", True) and stock > 0

        st.markdown(f'<div class="tarjeta-producto-individual">', unsafe_allow_html=True)
        with st.container():
            if disponible:
                st.markdown(f"""<img src="{info.get("foto","")}" style="width:100%; height:220px; object-fit:cover; border-radius:12px 12px 0 0;">""", unsafe_allow_html=True)
                st.markdown(f"""
                <div class='product-card-bottom'>
                    <span class='product-title'>{info.get("icono","")} {prod}</span>
                    <span class='product-price'>S/{info.get("precio",0):.2f}</span>
                </div>
                """, unsafe_allow_html=True)
                if stock <=3:
                    st.markdown(f"<p class='mini-stock-alerta'>🔥 ¡Solo quedan {stock} unidades! 🔥</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p class='mini-stock-normal'>📦 Stock disponible: {stock} und.</p>", unsafe_allow_html=True)

                key_cantidad = f"cantidad_{hashlib.md5(prod.encode()).hexdigest()}"
                cantidades[prod] = st.number_input(f"Cantidad de {prod}:", min_value=0, max_value=stock, step=1, key=key_cantidad, label_visibility="collapsed")
            else:
                st.markdown(f"""<div style="width:100%; height:200px; background:#222; border-radius:12px 12px 0 0; display:flex; align-items:center; justify-content:center;">
                <span style="font-size:50px; filter:grayscale(100%)">{info.get("icono","")}</span></div>""", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#1c1c1c; padding:20px; border-radius:0 0 12px 12px; border:2px solid #ff4b4b; text-align:center; margin-bottom:25px;'>"
                            f"<p style='color:#ff4b4b; font-weight:bold; font-size:18px; margin:0;'>❌ {prod}<br>(AGOTADO)</p></div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🛒 SIMULAR MONTO FINAL", use_container_width=True):
        carrito = []
        total = 0.0
        for prod, cant in cantidades.items():
            if cant > 0:
                subtotal = cant * st.session_state.menu_dinamico[prod]["precio"]
                carrito.append({"producto": prod, "cantidad": cant, "subtotal": subtotal})
                total += subtotal
        if total > 0:
            st.session_state.carrito = carrito            st.session_state.total_acumulado = total
            st.session_state.pedido_guardado = True
            st.experimental_rerun()
        else:
            st.error("⚠️ Selecciona al menos un producto.")

    st.markdown('</div>', unsafe_allow_html=True)

def pantalla_carrito():
    st.markdown('<div class="carrito-transparente-master">', unsafe_allow_html=True)
    st.subheader("📦 LISTA DE PRODUCTOS SELECCIONADOS")

    texto_ws = "Hola Familia Guadalupe, deseo coordinar mi pedido:\n\n"
    for item in st.session_state.carrito:
        icono = st.session_state.menu_dinamico[item["producto"]]["icono"]
        st.markdown(f"""
        <div style="background:#1e1e24; border-left:4px solid #f39c12; padding:12px 16px; border-radius:8px; color:#fff; font-weight:700; font-size:16px; margin-bottom:10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
            {icono} {item['producto']} x{item['cantidad']} &nbsp;|&nbsp; S/{item['subtotal']:.2f}
        </div>
        """, unsafe_allow_html=True)
        texto_ws += f"• {icono} {item['producto']} x{item['cantidad']} (S/{item['subtotal']:.2f})\n"

    st.markdown("---")
    st.metric("Monto Total", f"S/{st.session_state.total_acumulado:.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    texto_ws += f"\n💰 Total: S/{st.session_state.total_acumulado:.2f}\n📌 {fecha_actual}"
    mensaje_url = urllib.parse.quote(texto_ws)
    url_whatsapp = f"https://wa.me/?text={mensaje_url}"

    renderizar_informacion_pago(st.session_state.total_acumulado)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='nota-captura-estrategica'>
        <p>⚠️ Recomendación: Tómale una captura de pantalla a esta lista para que no olvides los productos que quieres comprar antes de realizar tu transferencia bancaria.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 CONFIRMAR SIMULACIÓN", use_container_width=True):
            st.session_state.pedido_guardado = True
            for item in st.session_state.carrito:
                producto = item["producto"]
                cantidad = item["cantidad"]
                stock_previo = st.session_state.menu_dinamico[producto]["stock"]
                st.session_state.menu_dinamico[producto]["stock"] = max(0, stock_previo - cantidad)
                st.session_state.menu_dinamico[producto]["disponible"] = st.session_state.menu_dinamico[producto]["stock"] > 0
            guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
            st.success("✔ Simulación procesada correctamente!")
            st.balloons()
            st.experimental_rerun()

        st.link_button("🟢 ENVIAR PEDIDO POR WHATSAPP", url_whatsapp, use_container_width=True)

    with c2:
        if st.button("🔄 Crear Nueva Orden", use_container_width=True):
            st.session_state.carrito = []
            st.session_state.total_acumulado = 0.0
            st.session_state.pedido_guardado = False
            st.session_state.pantalla_actual = "bienvenida"
            st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def panel_administrador():
    st.markdown("<h1 class='titulo-principal'>📊 PANEL DE ADMINISTRACIÓN</h1>", unsafe_allow_html=True)
    st.info(f"📋 Sincronizado en tiempo real: {fecha_actual}")
    st.markdown("<br>", unsafe_allow_html=True)

    inventario = st.session_state.menu_dinamico
    prod_registrados = len(inventario)
    prod_agotados = sum(1 for v in inventario.values() if v.get("stock", 0) <= 0)
    valor_total = sum(v.get("stock",0)*v.get("precio",0) for v in inventario.values())

    c1, c2, c3 = st.columns(3)
    c1.metric("📦 TOTAL PRODUCTOS", f"{prod_registrados} ítems")
    c2.metric("🚨 AGOTADOS", f"{prod_agotados} ítems")
    c3.metric("💰 CAPITAL EN STOCK", f"S/{valor_total:,.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📁 ⚙️ CONFIGURACIÓN DE SECCIONES", expanded=False):
        nueva_cat = st.text_input("Crear Nueva Sección:", placeholder="Ej. Ferretería...", key="admin_nueva_categoria").strip().capitalize()
        if st.button("➕ CREAR", key="btn_crear_cat"):
            if nueva_cat and nueva_cat not in st.session_state.lista_categorias:
                st.session_state.lista_categorias.append(nueva_cat)
                guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                st.success(f"✔ Sección '{nueva_cat}' creada!")
                st.experimental_rerun()
            elif nueva_cat in st.session_state.lista_categorias:
                st.error("⚠️ La categoría ya existe")

        cats_borrables = [c for c in st.session_state.lista_categorias if c != "Todos"]
        cat_a_borrar = st.selectbox("Eliminar Sección:", options=cats_borrables, key="admin_borrar_categoria")

        if st.button("🗑️ ELIMINAR", key="btn_borrar_cat"):
            if cat_a_borrar:
                st.session_state.lista_categorias.remove(cat_a_borrar)
                guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                st.warning(f"🗑️ Sección '{cat_a_borrar}' eliminada")
                st.experimental_rerun()

    with st.expander("➕ 🛠️ AÑADIR NUEVO PRODUCTO", expanded=False):
        nuevo_nom = st.text_input("Nombre:", placeholder="Ej. Filtro de agua...", key="admin_nuevo_nombre").strip()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nuevo_pr = st.number_input("Precio (S/):", min_value=0.5, value=10.0, step=0.5, key="admin_nuevo_precio")
        with col2:
            nuevo_ic = st.text_input("Icono:", value="📦", max_chars=2, key="admin_nuevo_icono")
        with col3:
            nuevo_stk = st.number_input("Stock:", min_value=0, value=15, step=1, key="admin_nuevo_stock")
        with col4:
            cats_disp = [c for c in st.session_state.lista_categorias if c != "Todos"]
            nueva_cat_asoc = st.selectbox("Categoría:", options=cats_disp, key="admin_nuevo_categoria")

        foto_nueva = st.file_uploader("Foto:", type=["jpg", "jpeg", "png"], key="admin_nuevo_foto")

        if st.button("🚀 GUARDAR PRODUCTO", key="btn_guardar_nuevo_prod"):
            if nuevo_nom and nuevo_nom not in st.session_state.menu_dinamico:
                if foto_nueva:
                    bytes_foto = foto_nueva.getvalue()
                    mime_type = foto_nueva.type or "image/png"
                    encoded = base64.b64encode(bytes_foto).decode()
                    src_foto = f"data:{mime_type};base64,{encoded}"
                else:
                    src_foto = "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>"
                st.session_state.menu_dinamico[nuevo_nom] = {
                    "precio": nuevo_pr,
                    "icono": nuevo_ic,
                    "disponible": True,
                    "foto": src_foto,
                    "stock": int(nuevo_stk),
                    "categoria": nueva_cat_asoc
                }
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.success(f"✔ Producto '{nuevo_nom}' agregado.")
                st.experimental_rerun()
            else:
                st.error("⚠️ Nombre inválido o producto ya existe.")

    st.markdown("### 📝 GESTIÓN DE PRODUCTOS")
    st.caption(f"Filtro por sección activo: **{st.session_state.categoria_activa}**")

    productos_visibles = []
    for p, v in st.session_state.menu_dinamico.items():
        cat = v.get("categoria", "Abarrotes")
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat:
            productos_visibles.append(p)

    st.markdown('<div class="admin-grid-2col">', unsafe_allow_html=True)
    cambios = False
    for p in productos_visibles:
        v = st.session_state.menu_dinamico[p]
        st.markdown('<div class="admin-tarjeta">', unsafe_allow_html=True)
        with st.container():
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f'<img src="{v.get("foto","")}" style="width:100%; height:75px; object-fit:cover; border-radius:6px; border:1px solid #d4af37;">', unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{v.get('icono','')} {p}**")
                st.caption(f"Sección: {v.get('categoria','')}")

            st.markdown("<hr style='margin:10px 0; border-color:#222538;'>", unsafe_allow_html=True)

            key_prec = f"edit_p_{hashlib.md5(p.encode()).hexdigest()}"
            key_stk = f"edit_s_{hashlib.md5(p.encode()).hexdigest()}"
            precio_nuevo = st.number_input(f"Precio (S/) {p}:", min_value=0.1, value=float(v.get("precio")), step=0.1, key=key_prec)
            stock_nuevo = st.number_input(f"Stock {p}:", min_value=0, value=int(v.get("stock")), step=1, key=key_stk)

            key_foto = f"foto_edit_{hashlib.md5(p.encode()).hexdigest()}"
            foto_cambio = st.file_uploader(f"Cambiar Foto {p}:", type=["jpg","jpeg","png"], key=key_foto)
            if foto_cambio is not None:
                bytes_foto = foto_cambio.getvalue()
                mime_type = foto_cambio.type or "image/png"
                encoded = base64.b64encode(bytes_foto).decode()
                st.session_state.menu_dinamico[p]["foto"] = f"data:{mime_type};base64,{encoded}"
                cambios = True

            if st.button("🗑️ ELIMINAR ARTÍCULO", key=f"del_{hashlib.md5(p.encode()).hexdigest()}", use_container_width=True):
                del st.session_state.menu_dinamico[p]
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.warning(f"✔ '{p}' eliminado.")
                st.experimental_rerun()

            if precio_nuevo != v.get("precio") or stock_nuevo != v.get("stock"):
                st.session_state.menu_dinamico[p]["precio"] = precio_nuevo
                st.session_state.menu_dinamico[p]["stock"] = stock_nuevo
                st.session_state.menu_dinamico[p]["disponible"] = stock_nuevo > 0
                cambios = True
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if cambios and st.button("💾 GUARDAR CAMBIOS", use_container_width=True, key="btn_guardar_cambios"):
        guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
        st.success("✔ Cambios guardados correctamente.")
        st.experimental_rerun()

# =========== CONTROL DE FLUJO =============
if not st.session_state.es_admin_autenticado:
    st.sidebar.markdown("<h2 style='color:#f39c12; text-align:center;'>Catálogo FAM. GUADALUPE</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    if st.sidebar.button("INGRESAR COMO ADMINISTRADOR 🤵‍♂️"):
        st.session_state.mostrar_login_admin = True

    if st.session_state.mostrar_login_admin:
        usuario = st.sidebar.text_input("Usuario:", key="login_user")
        clave = st.sidebar.text_input("Contraseña:", type="password", key="login_pass")
        if st.sidebar.button("🔓 ENTRAR"):
            USER_PROD = st.secrets["admin_user"] if "admin_user" in st.secrets else "Los Guadalupe"
            PASS_PROD = st.secrets["admin_password"] if "admin_password" in st.secrets else "18987915"
            if usuario == USER_PROD and clave == PASS_PROD:
                st.session_state.es_admin_autenticado = True
                st.session_state.mostrar_login_admin = False
                st.experimental_rerun()
            else:
                st.sidebar.error("❌ Credenciales incorrectas")
else:
    st.sidebar.success("✔ Modo Administrador Activo")
    if st.sidebar.button("🚪 CERRAR SESIÓN"):
        st.session_state.es_admin_autenticado = False
        st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕒 HORARIO DE ATENCIÓN")
st.sidebar.caption("Lunes a Domingo: 8:00 AM - 11:00 PM")
st.sidebar.markdown("---")
st.sidebar.markdown("#### 📞 ¿NECESITAS AYUDA?")
st.sidebar.link_button("💬 Chatear con Soporte", "https://wa.me", use_container_width=True)

# --- Renderizado principal según estado ---
if st.session_state.es_admin_autenticado:
    panel_administrador()
else:
    if st.session_state.pantalla_actual == "bienvenida":
        pantalla_bienvenida()
    elif st.session_state.pantalla_actual == "catalogo" and not st.session_state.pedido_guardado:
        pantalla_catalogo()
    else:
        pantalla_carrito()
