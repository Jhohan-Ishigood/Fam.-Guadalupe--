# CATÁLOGO PREMIUM FAM. GUADALUPE v6.0 — RENDER MASTER EDITION
# app.py

import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64
import mimetypes
import urllib.parse
import time
# Cargar CSS externo
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "estilos.css"), "r", encoding="utf-8") as f:
    css_externo = f.read()

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
st.markdown(f"<style>{css_externo}</style>", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_MENU       = os.path.join(BASE_DIR, "menu_config.json")
RUTA_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# =========================================================
# FUNCIONES UTILITARIAS
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
    FOTO_DEFAULT = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
        "<rect width='300' height='300' fill='%23222222'/>"
        "</svg>"
    )
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
            "stock": 2,
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
    categorias = ["Todos", "Abarrotes", "Tecnología"]
    if os.path.exists(RUTA_CATEGORIAS):
        try:
            with open(RUTA_CATEGORIAS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except:
            return categorias
    return categorias


def generar_proforma_html(carrito, total, fecha):
    """Genera el HTML de la proforma para descarga como archivo."""
    filas = ""
    for item in carrito:
        filas += f"""
        <tr>
            <td style="padding:10px;border-bottom:1px solid #333;">{item['producto']}</td>
            <td style="padding:10px;border-bottom:1px solid #333;text-align:center;">{item['cantidad']}</td>
            <td style="padding:10px;border-bottom:1px solid #333;text-align:right;">S/{item['subtotal']:.2f}</td>
        </tr>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Proforma - Familia Guadalupe</title>
<style>
  body {{ font-family: Arial, sans-serif; background: #0a0a0f; color: #fff; padding: 40px; }}
  .logo {{ text-align: center; color: #d4af37; font-size: 28px; font-weight: 900; margin-bottom: 5px; }}
  .subtitulo {{ text-align: center; color: #aaa; font-size: 14px; margin-bottom: 30px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ background: #d4af37; color: #000; padding: 12px; text-align: left; }}
  tr:hover td {{ background: rgba(212,175,55,0.05); }}
  .total-row td {{ font-size: 22px; font-weight: 900; color: #2ecc71; padding: 16px 10px; border-top: 2px solid #d4af37; }}
  .footer {{ text-align: center; margin-top: 40px; color: #888; font-size: 12px; }}
  .advertencia {{ background: rgba(212,175,55,0.1); border: 1px solid #d4af37; border-radius: 8px;
                  padding: 12px 16px; margin-top: 25px; color: #d4af37; font-weight: bold; text-align: center; }}
</style>
</head>
<body>
<div class="logo">🏪 ALMACÉN FAMILIA GUADALUPE</div>
<div class="subtitulo">PROFORMA DE PEDIDO — {fecha}</div>
<table>
  <thead><tr><th>Producto</th><th style="text-align:center;">Cant.</th><th style="text-align:right;">Subtotal</th></tr></thead>
  <tbody>{filas}</tbody>
  <tfoot><tr class="total-row"><td colspan="2">💰 TOTAL A PAGAR</td><td style="text-align:right;">S/{total:.2f}</td></tr></tfoot>
</table>
<div class="advertencia">⚠️ Recomendación: Tómale una captura a esta proforma antes de realizar tu transferencia.</div>
<div class="footer">Almacén Familia Guadalupe · +51 950 239 350 · Generado el {fecha}</div>
</body>
</html>"""

# =========================================================
# SESSION STATE
# =========================================================

if "menu_dinamico"          not in st.session_state:
    st.session_state.menu_dinamico      = cargar_menu()
if "lista_categorias"       not in st.session_state:
    st.session_state.lista_categorias   = cargar_categorias()
if "pantalla"               not in st.session_state:
    st.session_state.pantalla           = "bienvenida"
if "categoria_activa"       not in st.session_state:
    st.session_state.categoria_activa   = "Todos"
if "carrito"                not in st.session_state:
    st.session_state.carrito            = []
if "total"                  not in st.session_state:
    st.session_state.total              = 0.0
if "pedido_confirmado"      not in st.session_state:
    st.session_state.pedido_confirmado  = False
if "bloqueo_stock"          not in st.session_state:
    st.session_state.bloqueo_stock      = False
if "es_admin_autenticado"   not in st.session_state:
    st.session_state.es_admin_autenticado = False
if "admin_pass_input"       not in st.session_state:
    st.session_state.admin_pass_input   = ""

# =========================================================
# FECHA PERÚ
# =========================================================

zona_peru   = timezone(timedelta(hours=-5))
ahora_peru  = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

# =========================================================
# MULTIMEDIA
# =========================================================

URL_FONDO = convertir_base64(os.path.join(BASE_DIR, "establecimiento.png"))
URL_LOGO  = convertir_base64(os.path.join(BASE_DIR, "Logotipo.png"))
URL_QR    = convertir_base64(os.path.join(BASE_DIR, "miqr1.png"))

# URLs de video — reemplaza con tus propios videos en Cloudinary o similar
URL_VIDEO_PC    = "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_MOVIL = "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_LOGO  = "https://res.cloudinary.com/demo/video/upload/sample.mp4"

# =========================================================
# CSS MAESTRO — Solo variables Python aquí, resto en style.css externo
# REGLA DE ORO: todas las llaves CSS van como {{ }} en f-strings
# =========================================================

st.markdown(f'''
<style>

/* ── FONDO PANORÁMICO (necesita URL_FONDO de Python) ── */
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(0,0,0,.78), rgba(0,0,0,.78)),
        url("{URL_FONDO}");
    background-size: 130% auto;
    background-position: 0% center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    animation: fondoMaster 25s ease-in-out infinite alternate;
}}

@keyframes fondoMaster {{
    from {{ background-position: 0% center; }}
    to   {{ background-position: 100% center; }}
}}

@media (max-width: 768px) {{
    [data-testid="stAppViewContainer"] {{
        background-size: auto 100% !important;
        animation: fondoMobile 30s linear infinite alternate !important;
    }}
}}

@keyframes fondoMobile {{
    from {{ background-position: 0% center; }}
    to   {{ background-position: 100% center; }}
}}

/* ── TRANSPARENCIA RADICAL DE BLOQUES NATIVOS ── */
.main,
.block-container,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stAppViewBlockContainer"],
[data-testid="elementGrid"],
.element-container,
div[role="radiogroup"] {{
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
}}

</style>
''', unsafe_allow_html=True)

# =========================================================
# VIDEO DE FONDO + MINI LOGO FLOTANTE
# =========================================================

# Decide qué mostrar en el logo flotante: video si existe URL, imagen si no
logo_flotante_html = f'<img src="{URL_LOGO}" class="mini-logo-imagen-circular" alt="Logo">' \
    if URL_LOGO else '<span style="color:#d4af37;font-size:28px;">🏪</span>'

st.markdown(f'''

<!-- VIDEO DE FONDO -->
<div class="video-background-container pc-only">
    <video class="video-fondo-maestro" autoplay loop muted playsinline>
        <source src="{URL_VIDEO_PC}" type="video/mp4">
    </video>
</div>
<div class="video-background-container movil-only">
    <video class="video-fondo-maestro" autoplay loop muted playsinline>
        <source src="{URL_VIDEO_MOVIL}" type="video/mp4">
    </video>
</div>

<!-- MINI LOGO FLOTANTE — estilos inline para garantizar posición fija -->
<style>
@keyframes rotarMiniLogo3D {{
    0%   {{ transform: rotateY(0deg); }}
    100% {{ transform: rotateY(360deg); }}
}}
</style>

<div style="
    position: fixed !important;
    top: 20px !important;
    right: 20px !important;
    left: auto !important;
    width: 65px !important;
    height: 65px !important;
    z-index: 999999 !important;
    pointer-events: none !important;
    perspective: 1000px !important;
">
    <img src="{URL_LOGO}"
         style="
             width: 65px !important;
             height: 65px !important;
             object-fit: cover !important;
             border-radius: 50% !important;
             border: 2px solid #d4af37 !important;
             box-shadow: 0 0 15px rgba(212,175,55,0.6) !important;
             transform-style: preserve-3d !important;
             animation: rotarMiniLogo3D 4s linear infinite !important;
             display: block !important;
         "
         alt="Logo Guadalupe">
</div>

''', unsafe_allow_html=True)

# =========================================================
# SIDEBAR — NAVEGACIÓN Y ADMIN ACCESS
# =========================================================

with st.sidebar:
    st.markdown("### 🏪 Familia Guadalupe")
    st.markdown("---")

    if st.button("🏠 Inicio", use_container_width=True, key="nav_inicio"):
        st.session_state.pantalla = "bienvenida"
        st.rerun()

    if st.button("🛍️ Catálogo", use_container_width=True, key="nav_catalogo"):
        st.session_state.pantalla = "catalogo"
        st.rerun()

    if st.session_state.carrito:
        if st.button(f"🛒 Carrito ({len(st.session_state.carrito)})", use_container_width=True, key="nav_carrito"):
            st.session_state.pantalla = "carrito"
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🔐 Panel Admin")

    if not st.session_state.es_admin_autenticado:
        clave = st.text_input("Contraseña", type="password", key="sidebar_pass", label_visibility="collapsed")
        if st.button("Ingresar", use_container_width=True, key="btn_login_admin"):
            if clave == "guadalupe2024":   # ← CAMBIA ESTA CLAVE
                st.session_state.es_admin_autenticado = True
                st.session_state.pantalla = "admin"
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.success("✔ Admin activo")
        if st.button("⚙️ Panel Admin", use_container_width=True, key="btn_ir_admin"):
            st.session_state.pantalla = "admin"
            st.rerun()
        if st.button("🚪 Cerrar sesión", use_container_width=True, key="btn_logout"):
            st.session_state.es_admin_autenticado = False
            st.session_state.pantalla = "bienvenida"
            st.rerun()

    st.markdown("---")
    st.markdown(f"<p style='color:#888;font-size:11px;text-align:center;'>📅 {fecha_actual}</p>", unsafe_allow_html=True)
    st.link_button("💬 Soporte WhatsApp", "https://wa.me/51950239350", use_container_width=True)

# =========================================================
# ██████████████  PANTALLA: BIENVENIDA  ██████████████████
# =========================================================

if st.session_state.pantalla == "bienvenida":

    st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

    # Títulos principales
    st.markdown("<h1 class='titulo-principal'>FAMILIA GUADALUPE</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#d4af37;font-size:22px;font-weight:bold;"
        "text-shadow:0 0 15px rgba(212,175,55,0.6);margin-bottom:0;'>"
        "CATÁLOGO PREMIUM DE PRODUCTOS 🔥</p>",
        unsafe_allow_html=True
    )

    # ── LOGO CENTRAL CON DESTELLO METÁLICO ──
    # Usa video si está disponible, sino imagen con fallback emoji
    if URL_LOGO:
        contenido_logo = f'<img src="{URL_LOGO}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="Logo Guadalupe">'
    else:
        contenido_logo = '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:80px;">🏪</div>'

    st.markdown(f'''
    <div style="display:flex;justify-content:center;margin:25px 0 30px 0;">
        <div class="logo-central-escudo">
            <div class="destello-fisico-linea"></div>
            {contenido_logo}
        </div>
    </div>

    <style>
    .logo-central-escudo {{
        position: relative;
        width: 206px;
        height: 206px;
        border-radius: 50%;
        overflow: hidden;
        border: 3px solid #d4af37;
        box-shadow: 0 0 25px rgba(212,175,55,.7), 0 0 60px rgba(212,175,55,.4);
        animation: flotarEscudo 4s ease-in-out infinite;
    }}
    @keyframes flotarEscudo {{
        0%   {{ transform: translateY(0px); }}
        50%  {{ transform: translateY(-8px); }}
        100% {{ transform: translateY(0px); }}
    }}
    .destello-fisico-linea {{
        position: absolute;
        top: -20%;
        left: -150%;
        width: 80px;
        height: 160%;
        background: linear-gradient(120deg, transparent, rgba(255,255,255,.85), transparent);
        transform: rotate(20deg);
        animation: destelloOro 4s infinite;
        z-index: 10;
        pointer-events: none;
    }}
    @keyframes destelloOro {{
        0%  {{ left: -150%; }}
        20% {{ left: 150%;  }}
        100%{{ left: 150%;  }}
    }}
    </style>
    ''', unsafe_allow_html=True)

    # ── BOTÓN PRINCIPAL CON ESCÁNER DE LUZ ──
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🛍️ EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_navegar"):
        st.session_state.pantalla = "catalogo"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ACORDEONES DE PAGO ──
    with st.expander("🏦 BANCO DE LA NACIÓN"):
        st.markdown("""
        #### DATOS BANCARIOS
        **Número de cuenta:** 04-762-855629

        **Titular:** Segundo Melquiades Guadalupe Sanchez

        > Realiza tu depósito y envíanos el comprobante por WhatsApp.
        """)

    with st.expander("🟣 YAPE — +51 950 239 350"):
        if URL_QR:
            col_qr1, col_qr2, col_qr3 = st.columns([1, 2, 1])
            with col_qr2:
                st.image(URL_QR, width=220)
        st.markdown("""
        #### YAPE
        **Número:** +51 950 239 350

        **Titular:** Segundo Guadalupe

        > Escanea el QR o yapea al número directamente.
        """)

    with st.expander("🟢 CONTACTO DIRECTO — WHATSAPP"):
        st.markdown("""
        #### WHATSAPP
        **Número:** +51 950 239 350

        > Escríbenos por WhatsApp para coordinar tu pedido y entrega.
        """)
        st.link_button("💬 Abrir WhatsApp", "https://wa.me/51950239350", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ██████████████  PANTALLA: CATÁLOGO  ████████████████████
# =========================================================

elif st.session_state.pantalla == "catalogo":

    st.markdown('<div class="catalogo-transparente-master">', unsafe_allow_html=True)
    st.markdown("<h1 class='titulo-principal'>🛍️ CATÁLOGO</h1>", unsafe_allow_html=True)

    # ── BUSCADOR ──
    busqueda = st.text_input(
        "🔍 Buscar producto...",
        key="search_bar_catalogo",
        placeholder="Escribe el nombre del producto"
    )

    # ── PESTAÑAS NETFLIX ──
    categorias = st.session_state.lista_categorias
    cols_tabs = st.columns(len(categorias))
    for i, cat in enumerate(categorias):
        with cols_tabs[i]:
            activo = "✅ " if cat == st.session_state.categoria_activa else ""
            if st.button(
                f"{activo}{cat}",
                use_container_width=True,
                key=f"tabs_netflix_master_{i}"
            ):
                st.session_state.categoria_activa = cat
                st.rerun()

    categoria_sel = st.session_state.categoria_activa

    # ── FILTRADO ──
    productos_filtrados = []
    for producto, info in st.session_state.menu_dinamico.items():
        if busqueda.lower() not in producto.lower():
            continue
        if categoria_sel != "Todos" and info.get("categoria") != categoria_sel:
            continue
        if not info.get("disponible", True):
            continue
        productos_filtrados.append((producto, info))

    if not productos_filtrados:
        st.warning("No se encontraron productos con ese filtro.")
    else:
        # ── GRILLA DE PRODUCTOS — 4 cols PC / 2 cols móvil ──
        # Se usan st.columns en pares para respetar widgets nativos dentro del HTML
        st.markdown('<div class="grid-productos-responsivo">', unsafe_allow_html=True)

        # Agrupamos en filas de 2 para compatibilidad con widgets Streamlit
        for idx in range(0, len(productos_filtrados), 2):
            par = productos_filtrados[idx:idx+2]
            col_izq, col_der = st.columns(2, gap="medium")
            columnas_par = [col_izq, col_der]

            for j, (producto, info) in enumerate(par):
                stock = int(info.get("stock", 0))
                with columnas_par[j]:
                    # Cabecera de tarjeta (HTML puro)
                    st.markdown(f'''
                    <div class="tarjeta-producto-individual">
                        <img src="{info.get('foto', '')}"
                             alt="{producto}"
                             style="width:100%;height:200px;object-fit:cover;border-radius:12px 12px 0 0;">
                        <div class="product-card-bottom">
                            <div>
                                <div class="product-title">{info.get('icono','📦')} {producto}</div>
                    ''', unsafe_allow_html=True)

                    if stock <= 3:
                        st.markdown(
                            f'<div class="mini-stock-alerta">🔥 ¡SOLO QUEDAN {stock}!</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div class="mini-stock-normal">📦 Stock: {stock}</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(f'''
                            </div>
                            <div class="product-price">S/{info.get('precio', 0):.2f}</div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Widget nativo fuera del bloque HTML
                    st.number_input(
                        f"Cantidad — {producto}",
                        min_value=0,
                        max_value=stock,
                        value=0,
                        key=f"qty_{producto}",
                        label_visibility="collapsed"
                    )

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🛒 SIMULAR MONTO FINAL", use_container_width=True, key="btn_simular"):
        st.session_state.carrito = []
        st.session_state.total   = 0.0

        for producto, info in st.session_state.menu_dinamico.items():
            key_qty = f"qty_{producto}"
            cantidad = st.session_state.get(key_qty, 0)
            if cantidad and cantidad > 0:
                subtotal = cantidad * info["precio"]
                st.session_state.carrito.append({
                    "producto": producto,
                    "cantidad": cantidad,
                    "subtotal": subtotal
                })
                st.session_state.total += subtotal

        if st.session_state.total > 0:
            st.session_state.bloqueo_stock = False
            st.session_state.pantalla = "carrito"
            st.rerun()
        else:
            st.warning("Agrega al menos un producto antes de continuar.")

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ██████████████  PANTALLA: CARRITO  █████████████████████
# =========================================================

elif st.session_state.pantalla == "carrito":

    st.markdown('<div class="carrito-transparente-master">', unsafe_allow_html=True)
    st.markdown("<h1 class='titulo-principal'>🛒 CARRITO</h1>", unsafe_allow_html=True)

    if not st.session_state.carrito:
        st.warning("Tu carrito está vacío.")
        if st.button("← Volver al catálogo", use_container_width=True):
            st.session_state.pantalla = "catalogo"
            st.rerun()
    else:
        # ── ITEMS DEL CARRITO ──
        for item in st.session_state.carrito:
            st.markdown(f'''
            <div style="
                background: rgba(0,0,0,.6);
                backdrop-filter: blur(10px);
                padding: 16px 20px;
                border-radius: 14px;
                margin-bottom: 10px;
                color: white;
                border-left: 4px solid #d4af37;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span style="font-size:16px;font-weight:700;">
                    {item["producto"]}
                    <span style="color:#aaa;font-weight:400;"> x{item["cantidad"]}</span>
                </span>
                <span style="color:#2ecc71;font-size:20px;font-weight:900;">
                    S/{item["subtotal"]:.2f}
                </span>
            </div>
            ''', unsafe_allow_html=True)

        # ── TOTAL NEÓN ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric(label="💰 TOTAL A PAGAR", value=f"S/{st.session_state.total:.2f}")

        # ── NOTA ESTRATÉGICA DORADA ──
        st.markdown('''
        <div style="
            background: rgba(212,175,55,0.12);
            border: 1px solid #d4af37;
            border-radius: 10px;
            padding: 14px 18px;
            margin: 18px 0;
            text-align: center;
            color: #d4af37;
            font-weight: 700;
            font-size: 15px;
        ">
            ⚠️ Recomendación: Tómale una <b>captura a esta proforma</b> antes de realizar tu transferencia.
        </div>
        ''', unsafe_allow_html=True)

        # ── PROFORMA DESCARGABLE ──
        proforma_html = generar_proforma_html(
            st.session_state.carrito,
            st.session_state.total,
            fecha_actual
        )
        st.download_button(
            label="📄 DESCARGAR PROFORMA",
            data=proforma_html.encode("utf-8"),
            file_name=f"proforma_guadalupe_{ahora_peru.strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
            key="btn_proforma"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── MENSAJE WHATSAPP AUTOMÁTICO ──
        lineas_wa = "%0A".join([
            urllib.parse.quote(f"{i['producto']} x{i['cantidad']} — S/{i['subtotal']:.2f}")
            for i in st.session_state.carrito
        ])
        total_wa = urllib.parse.quote(f"💰 TOTAL: S/{st.session_state.total:.2f}")
        encabezado_wa = urllib.parse.quote("Hola Familia Guadalupe 👋, quiero coordinar mi pedido:\n\n")
        url_whatsapp = f"https://wa.me/51950239350?text={encabezado_wa}{lineas_wa}%0A%0A{total_wa}"

        # ── BOTONES DE ACCIÓN ──
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            if st.button("💾 CONFIRMAR PEDIDO", use_container_width=True, key="btn_confirmar"):
                if not st.session_state.bloqueo_stock:
                    st.session_state.bloqueo_stock = True
                    for item in st.session_state.carrito:
                        prod     = item["producto"]
                        cantidad = item["cantidad"]
                        stock_actual = st.session_state.menu_dinamico[prod]["stock"]
                        nuevo_stock  = max(0, stock_actual - cantidad)
                        st.session_state.menu_dinamico[prod]["stock"]      = nuevo_stock
                        st.session_state.menu_dinamico[prod]["disponible"] = nuevo_stock > 0
                    guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                    st.success("✔ Pedido confirmado correctamente")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.info("Este pedido ya fue procesado.")

        with col2:
            st.link_button(
                "🟢 ENVIAR POR WHATSAPP",
                url_whatsapp,
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄 NUEVA ORDEN", use_container_width=True, key="btn_nueva_orden"):
            st.session_state.carrito       = []
            st.session_state.total         = 0.0
            st.session_state.pantalla      = "bienvenida"
            st.session_state.bloqueo_stock = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ██████████████  PANTALLA: ADMIN  ███████████████████████
# =========================================================

elif st.session_state.pantalla == "admin":

    if not st.session_state.es_admin_autenticado:
        st.error("⛔ Acceso denegado. Inicia sesión desde el menú lateral.")
        st.stop()

    st.markdown("<h1 class='titulo-principal'>⚙️ PANEL ADMINISTRADOR</h1>", unsafe_allow_html=True)

    menu = st.session_state.menu_dinamico

    # ── MÉTRICAS DE CAPITAL ──
    total_productos   = len(menu)
    total_stock       = sum(p.get("stock", 0) for p in menu.values())
    capital_estimado  = sum(p.get("precio", 0) * p.get("stock", 0) for p in menu.values())
    productos_criticos = sum(1 for p in menu.values() if p.get("stock", 0) <= 3)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Productos",    total_productos)
    c2.metric("🗃️ Stock Total",  total_stock)
    c3.metric("💰 Capital Est.", f"S/{capital_estimado:.2f}")
    c4.metric("🔥 Stock Crítico", productos_criticos)

    st.markdown("---")

    # ── GESTIÓN DE INVENTARIO ──
    st.markdown("### 🗂️ Inventario — Edición en Caliente")

    productos_lista = list(menu.items())
    for idx in range(0, len(productos_lista), 2):
        par = productos_lista[idx:idx+2]
        col_a, col_b = st.columns(2, gap="large")
        columnas_admin = [col_a, col_b]

        for j, (nombre, datos) in enumerate(par):
            with columnas_admin[j]:
                with st.expander(f"{datos.get('icono','📦')} {nombre}", expanded=False):

                    # Foto actual
                    if datos.get("foto") and datos["foto"].startswith("data:image"):
                        st.image(datos["foto"], width=160)

                    # Subir nueva foto
                    nueva_foto = st.file_uploader(
                        "📷 Cambiar foto",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=f"foto_upload_{nombre}"
                    )
                    if nueva_foto:
                        mime = nueva_foto.type
                        b64  = base64.b64encode(nueva_foto.read()).decode()
                        st.session_state.menu_dinamico[nombre]["foto"] = f"data:{mime};base64,{b64}"
                        guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                        st.success("✔ Foto actualizada")
                        st.rerun()

                    # Editar precio
                    nuevo_precio = st.number_input(
                        "💲 Precio (S/)",
                        min_value=0.0,
                        value=float(datos.get("precio", 0)),
                        step=0.5,
                        key=f"precio_{nombre}"
                    )

                    # Editar stock
                    nuevo_stock = st.number_input(
                        "📦 Stock",
                        min_value=0,
                        value=int(datos.get("stock", 0)),
                        step=1,
                        key=f"stock_{nombre}"
                    )

                    # Disponibilidad
                    disponible = st.toggle(
                        "✅ Disponible",
                        value=bool(datos.get("disponible", True)),
                        key=f"disp_{nombre}"
                    )

                    if st.button("💾 Guardar cambios", use_container_width=True, key=f"guardar_{nombre}"):
                        st.session_state.menu_dinamico[nombre]["precio"]     = nuevo_precio
                        st.session_state.menu_dinamico[nombre]["stock"]      = nuevo_stock
                        st.session_state.menu_dinamico[nombre]["disponible"] = disponible
                        guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                        st.success(f"✔ {nombre} actualizado")
                        st.rerun()

    st.markdown("---")

    # ── AGREGAR NUEVO PRODUCTO ──
    st.markdown("### ➕ Agregar Nuevo Producto")

    with st.expander("Formulario nuevo producto"):
        np_nombre = st.text_input("Nombre del producto", key="np_nombre")
        np_icono  = st.text_input("Icono (emoji)", value="📦", key="np_icono")
        np_precio = st.number_input("Precio (S/)", min_value=0.0, step=0.5, key="np_precio")
        np_stock  = st.number_input("Stock inicial", min_value=0, step=1, key="np_stock")

        categorias_disponibles = st.session_state.lista_categorias[1:]  # Quita "Todos"
        np_cat    = st.selectbox("Categoría", categorias_disponibles, key="np_cat")
        np_foto   = st.file_uploader("Foto del producto", type=["png","jpg","jpeg","webp"], key="np_foto")

        if st.button("✅ AGREGAR PRODUCTO", use_container_width=True, key="btn_agregar_prod"):
            if np_nombre.strip():
                FOTO_DEFAULT = (
                    "data:image/svg+xml;utf8,"
                    "<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
                    "<rect width='300' height='300' fill='%23222222'/>"
                    "</svg>"
                )
                foto_nueva = FOTO_DEFAULT
                if np_foto:
                    mime = np_foto.type
                    b64  = base64.b64encode(np_foto.read()).decode()
                    foto_nueva = f"data:{mime};base64,{b64}"

                st.session_state.menu_dinamico[np_nombre.strip()] = {
                    "precio":     np_precio,
                    "icono":      np_icono,
                    "stock":      np_stock,
                    "disponible": True,
                    "categoria":  np_cat,
                    "foto":       foto_nueva
                }
                guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                st.success(f"✔ Producto '{np_nombre}' agregado")
                st.rerun()
            else:
                st.error("Escribe un nombre para el producto.")

    st.markdown("---")

    # ── GESTIÓN DE CATEGORÍAS ──
    st.markdown("### 🏷️ Gestionar Categorías")

    with st.expander("Agregar o eliminar categorías"):
        nueva_cat = st.text_input("Nueva categoría", key="nueva_cat_input")
        if st.button("➕ Agregar categoría", use_container_width=True, key="btn_add_cat"):
            if nueva_cat.strip() and nueva_cat not in st.session_state.lista_categorias:
                st.session_state.lista_categorias.append(nueva_cat.strip())
                guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
                st.success(f"✔ Categoría '{nueva_cat}' agregada")
                st.rerun()

        cats_eliminables = [c for c in st.session_state.lista_categorias if c != "Todos"]
        cat_eliminar = st.selectbox("Eliminar categoría", cats_eliminables, key="cat_eliminar_sel")
        if st.button("🗑️ Eliminar categoría", use_container_width=True, key="btn_del_cat"):
            st.session_state.lista_categorias.remove(cat_eliminar)
            guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
            st.success(f"✔ Categoría '{cat_eliminar}' eliminada")
            st.rerun()

    st.markdown("---")

    # ── ELIMINAR PRODUCTO ──
    st.markdown("### 🗑️ Eliminar Producto")
    with st.expander("Selecciona el producto a eliminar"):
        prod_eliminar = st.selectbox(
            "Producto",
            list(st.session_state.menu_dinamico.keys()),
            key="prod_eliminar_sel"
        )
        if st.button("⛔ ELIMINAR PRODUCTO", use_container_width=True, key="btn_del_prod"):
            del st.session_state.menu_dinamico[prod_eliminar]
            guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
            st.success(f"✔ Producto '{prod_eliminar}' eliminado")
            st.rerun()

# =========================================================
# PIE DE PÁGINA
# =========================================================

st.markdown('''
<div class="social-footer">
    <p style="color:#d4af37;font-weight:900;font-size:16px;margin:0;">
        🏪 ALMACÉN FAMILIA GUADALUPE
    </p>
    <p style="color:#aaa;font-size:13px;margin:5px 0;">
        📍 Tu tienda de confianza &nbsp;|&nbsp;
        <a href="https://wa.me/51950239350" style="color:#2ecc71;">💬 +51 950 239 350</a>
    </p>
</div>
<p class="sello-creador">⚡ Plataforma Desarrollada — Edición Render Master v6.0</p>
''', unsafe_allow_html=True)