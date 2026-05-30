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

# Cargar CSS externo
with open(os.path.join(BASE_DIR, "estilos.css"), "r", encoding="utf-8") as f:
    css_externo = f.read()
st.markdown(f"<style>{css_externo}</style>", unsafe_allow_html=True)

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
            "categoria_principal": "🌾 Abarrotes",
            "categoria": "Arroz",
            "foto": FOTO_DEFAULT
        },
        "Parlante JBL Bluetooth": {
            "precio": 149.90,
            "icono": "🔊",
            "stock": 2,
            "disponible": True,
            "categoria_principal": "🔊 Tecnología",
            "categoria": "Parlantes",
            "foto": FOTO_DEFAULT
        }
    }
    menu = inventario
    if os.path.exists(RUTA_MENU):
        try:
            with open(RUTA_MENU, "r", encoding="utf-8") as archivo:
                menu = json.load(archivo)
        except:
            menu = inventario

    # Migración de productos anteriores
    for prod, info in menu.items():
        if "categoria_principal" not in info:
            old_cat = info.get("categoria", "🌾 Abarrotes")
            info["categoria_principal"] = "🌾 Abarrotes"
            info["categoria"] = "Todos"
            if "Abarrotes" in old_cat or "abarrotes" in old_cat.lower():
                info["categoria_principal"] = "🌾 Abarrotes"
            elif "Tecnología" in old_cat or "tecnologia" in old_cat.lower():
                info["categoria_principal"] = "🔊 Tecnología"
            elif "Útiles" in old_cat or "utiles" in old_cat.lower():
                info["categoria_principal"] = "✏️ Útiles escolares"
            elif "Ferretería" in old_cat or "ferreteria" in old_cat.lower():
                info["categoria_principal"] = "🛠️ Ferretería"
    return menu


def cargar_categorias():
    categorias_default = {
        "🌾 Abarrotes": ["Todos", "Arroz", "Fideos", "Aceites"],
        "🔊 Tecnología": ["Todos", "Parlantes", "Audífonos"],
        "✏️ Útiles escolares": ["Todos", "Cuadernos", "Plumones", "Lapiceros"],
        "🛠️ Ferretería": ["Todos", "Herramientas", "Pinturas"]
    }
    if os.path.exists(RUTA_CATEGORIAS):
        try:
            with open(RUTA_CATEGORIAS, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                if isinstance(datos, dict):
                    return datos
                else:
                    datos_nuevos = {}
                    for cat in datos:
                        if cat != "Todos":
                            datos_nuevos[cat] = ["Todos"]
                    if not datos_nuevos:
                        return categorias_default
                    return datos_nuevos
        except:
            return categorias_default
    return categorias_default


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
  @media print {{
    .no-print {{ display: none !important; }}
    body {{ background: #fff !important; color: #000 !important; padding: 20px !important; }}
    th {{ background: #d4af37 !important; color: #000 !important; }}
    tr td {{ border-bottom: 1px solid #ddd !important; color: #000 !important; }}
    .total-row td {{ font-size: 22px; font-weight: 900; color: #27ae60 !important; padding: 16px 10px; border-top: 2px solid #d4af37 !important; }}
    .advertencia {{ background: #fdfaf2 !important; border: 1px solid #d4af37 !important; color: #d4af37 !important; }}
    .footer {{ color: #555 !important; }}
  }}
</style>
</head>
<body>
<div class="no-print" style="text-align: center; margin-bottom: 30px;">
  <button onclick="window.print()" style="background: #d4af37; color: #000; font-weight: 900; padding: 14px 28px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; box-shadow: 0 4px 15px rgba(212,175,55,0.4); font-family: sans-serif; transition: transform 0.2s;">
    🖨️ IMPRIMIR / GUARDAR COMO PDF
  </button>
</div>
<div class="logo">🏪 ALMACÉN FAMILIA GUADALUPE</div>
<div class="subtitulo">PROFORMA DE PEDIDO — {fecha}</div>
<table>
  <thead><tr><th>Producto</th><th style="text-align:center;">Cant.</th><th style="text-align:right;">Subtotal</th></tr></thead>
  <tbody>{filas}</tbody>
  <tfoot><tr class="total-row"><td colspan="2">SU TOTAL A PAGAR SERIA:</td><td style="text-align:right;">S/{total:.2f}</td></tr></tfoot>
</table>
<div class="advertencia">Recomendación: Tómale una captura a esta para recordar su lista de compras.</div>
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
if "categoria_principal_activa" not in st.session_state:
    st.session_state.categoria_principal_activa = list(st.session_state.lista_categorias.keys())[0] if st.session_state.lista_categorias else ""
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

# URLs de video — usando static local si está disponible o Cloudinary de respaldo
URL_VIDEO_PC    = "/app/static/videofondopc.mp4" if os.path.exists(os.path.join(BASE_DIR, "static", "videofondopc.mp4")) else "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_MOVIL = "/app/static/videofondocelular.mp4" if os.path.exists(os.path.join(BASE_DIR, "static", "videofondocelular.mp4")) else "https://res.cloudinary.com/demo/video/upload/sample.mp4"
URL_VIDEO_LOGO  = "/app/static/logovideo.mp4" if os.path.exists(os.path.join(BASE_DIR, "static", "logovideo.mp4")) else "https://res.cloudinary.com/demo/video/upload/sample.mp4"

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
logo_flotante_html = f'<img src="{URL_LOGO}" class="mini-logo-imagen-circular" alt="Logo Guadalupe">' \
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

<!-- MINI LOGO FLOTANTE RESPONSIVO -->
<div class="mini-logo-flotante-master">
    {logo_flotante_html}
</div>

<!-- DOM OBSERVER PARA ACORDEONES Y GRILLAS -->
<script>
const observer = new MutationObserver((mutations) => {{
    // 1. Expanders
    const summaries = document.querySelectorAll('div[data-testid="stExpander"] summary');
    summaries.forEach(summary => {{
        const text = summary.textContent.toUpperCase();
        const expander = summary.closest('div[data-testid="stExpander"]');
        if (expander) {{
            if (text.includes("BANCO")) {{
                expander.classList.add("expander-banco");
            }} else if (text.includes("YAPE")) {{
                expander.classList.add("expander-yape");
            }} else if (text.includes("CONTACTO")) {{
                expander.classList.add("expander-contacto");
            }}
        }}
    }});

    // 2. Grilla Catalog
    const cards = document.querySelectorAll('.tarjeta-producto-individual');
    cards.forEach(card => {{
        const horizontalBlock = card.closest('[data-testid="stHorizontalBlock"]');
        if (horizontalBlock) {{
            horizontalBlock.classList.add('grilla-cuatro-dos');
        }}
    }});

    // 3. Admin Grilla Inventory
    const adminUploaders = document.querySelectorAll('div[data-testid="stFileUploader"]');
    adminUploaders.forEach(uploader => {{
        const horizontalBlock = uploader.closest('[data-testid="stHorizontalBlock"]');
        if (horizontalBlock) {{
            horizontalBlock.classList.add('grilla-cuatro-dos');
        }}
    }});

    // 4. Grilla Categorías Principales
    const catCards = document.querySelectorAll('.tarjeta-categoria-principal');
    catCards.forEach(card => {{
        const horizontalBlock = card.closest('[data-testid="stHorizontalBlock"]');
        if (horizontalBlock) {{
            horizontalBlock.classList.add('grilla-cuatro-dos');
        }}
    }});
}});
observer.observe(document.body, {{ childList: true, subtree: true }});
</script>

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
        st.session_state.pantalla = "seleccion_categorias"
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
    if URL_VIDEO_LOGO:
        contenido_logo = f'<video autoplay loop muted playsinline style="width:100%;height:100%;object-fit:cover;border-radius:50%;"><source src="{URL_VIDEO_LOGO}" type="video/mp4"></video>'
    elif URL_LOGO:
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
        st.session_state.pantalla = "seleccion_categorias"
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

# =========================================================
# ██████  PANTALLA: SELECCIÓN DE CATEGORÍAS  ██████████████
# =========================================================

elif st.session_state.pantalla == "seleccion_categorias":

    st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)
    st.markdown("<h1 class='titulo-principal'>¿Qué está buscando?</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#aaa;font-size:16px;margin-bottom:30px;'>Selecciona una sección para explorar nuestros productos</p>", unsafe_allow_html=True)

    categorias_principales = list(st.session_state.lista_categorias.keys())
    
    # Grilla de categorías principales: 4 columnas PC / 2 columnas móvil
    for idx in range(0, len(categorias_principales), 4):
        grupo = categorias_principales[idx:idx+4]
        cols = st.columns(4, gap="large")
        for j, cat in enumerate(grupo):
            with cols[j]:
                partes = cat.split(" ", 1)
                icono = partes[0] if len(partes) > 1 else "📦"
                nombre = partes[1] if len(partes) > 1 else cat
                
                st.markdown(f'''
                <div class="tarjeta-categoria-principal">
                    <div class="categoria-icono">{icono}</div>
                    <div class="categoria-titulo">{nombre}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Entrar a {nombre}", use_container_width=True, key=f"cat_btn_{cat}"):
                    st.session_state.categoria_principal_activa = cat
                    st.session_state.categoria_activa = "Todos"
                    st.session_state.pantalla = "catalogo"
                    st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("⬅ Volver al inicio", use_container_width=True, key="btn_volver_bienvenida"):
        st.session_state.pantalla = "bienvenida"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# ██████████████  PANTALLA: CATÁLOGO  ████████████████████
# =========================================================

elif st.session_state.pantalla == "catalogo":

    st.markdown('<div class="catalogo-transparente-master">', unsafe_allow_html=True)
    
    # Botón Volver a las categorías en la parte superior
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅ Categorías", use_container_width=True, key="btn_volver_seleccion"):
            st.session_state.pantalla = "seleccion_categorias"
            st.rerun()
    with col_title:
        st.markdown(f"<h1 class='titulo-principal' style='text-align:left;margin-top:0px !important;'>🛍️ {st.session_state.categoria_principal_activa}</h1>", unsafe_allow_html=True)

    # ── BUSCADOR ──
    busqueda = st.text_input(
        "🔍 Buscar producto...",
        key="search_bar_catalogo",
        placeholder="Escribe el nombre del producto"
    )

    # ── PESTAÑAS NETFLIX ──
    cat_principal = st.session_state.categoria_principal_activa
    subcategorias = st.session_state.lista_categorias.get(cat_principal, ["Todos"])
    if "Todos" not in subcategorias:
        subcategorias = ["Todos"] + subcategorias
        
    cols_tabs = st.columns(len(subcategorias))
    for i, subcat in enumerate(subcategorias):
        with cols_tabs[i]:
            activo = "✅ " if subcat == st.session_state.categoria_activa else ""
            if st.button(
                f"{activo}{subcat}",
                use_container_width=True,
                key=f"tabs_netflix_master_{i}"
            ):
                st.session_state.categoria_activa = subcat
                st.rerun()

    categoria_sel = st.session_state.categoria_activa

    # ── FILTRADO ──
    productos_filtrados = []
    for producto, info in st.session_state.menu_dinamico.items():
        if info.get("categoria_principal", "🌾 Abarrotes") != cat_principal:
            continue
        if busqueda.lower() not in producto.lower():
            continue
        if categoria_sel != "Todos" and info.get("categoria") != categoria_sel:
            continue
        if not info.get("disponible", True):
            continue
        productos_filtrados.append((producto, info))

    if not productos_filtrados:
        st.warning("No se encontraron productos en esta sección.")
    else:
        # ── GRILLA DE PRODUCTOS — 4 cols PC / 2 cols móvil ──
        st.markdown('<div class="grid-productos-responsivo">', unsafe_allow_html=True)

        for idx in range(0, len(productos_filtrados), 4):
            grupo = productos_filtrados[idx:idx+4]
            columnas_par = st.columns(4, gap="medium")

            for j, (producto, info) in enumerate(grupo):
                stock = int(info.get("stock", 0))
                with columnas_par[j]:
                    foto_url = info.get('foto', '')
                    is_video = foto_url.startswith("data:video/") or foto_url.endswith((".mp4", ".webm", ".ogg", ".mov"))
                    
                    if is_video:
                        media_html = f'<video class="video-producto" autoplay loop muted playsinline style="width:100%;height:200px;object-fit:cover;border-radius:12px 12px 0 0;"><source src="{foto_url}" type="video/mp4"></video>'
                    else:
                        media_html = f'<img src="{foto_url}" alt="{producto}" style="width:100%;height:200px;object-fit:cover;border-radius:12px 12px 0 0;">'

                    st.markdown(f'''
                    <div class="tarjeta-producto-individual">
                        {media_html}
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
            Recomendación:Tómele una <b>captura a la lista que seleccionó para que no se le olvide</b>.
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
            if st.button("💾 CONFIRMAR PEDIDO", use_container_width=True, key="btn_confirmar", disabled=st.session_state.bloqueo_stock):
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

                    # Subir nueva foto o video
                    nueva_foto = st.file_uploader(
                        "📷 Cambiar foto o video",
                        type=["png", "jpg", "jpeg", "webp", "mp4", "webm", "ogg", "mov"],
                        key=f"foto_upload_{nombre}"
                    )
                    if nueva_foto:
                        mime = nueva_foto.type
                        b64  = base64.b64encode(nueva_foto.read()).decode()
                        nueva_media_url = f"data:{mime};base64,{b64}"
                        if st.session_state.menu_dinamico[nombre].get("foto") != nueva_media_url:
                            st.session_state.menu_dinamico[nombre]["foto"] = nueva_media_url
                            guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                            st.success("✔ Archivo multimedia actualizado")
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

                    # Editar Categorías
                    lista_cat_principales = list(st.session_state.lista_categorias.keys())
                    cat_p_actual = datos.get("categoria_principal", lista_cat_principales[0] if lista_cat_principales else "")
                    if cat_p_actual not in lista_cat_principales:
                        lista_cat_principales.append(cat_p_actual)
                        
                    nuevo_cat_principal = st.selectbox(
                        "Categoría Principal",
                        lista_cat_principales,
                        index=lista_cat_principales.index(cat_p_actual),
                        key=f"cat_p_{nombre}"
                    )
                    
                    subcats_disponibles = st.session_state.lista_categorias.get(nuevo_cat_principal, ["Todos"])
                    if "Todos" not in subcats_disponibles:
                        subcats_disponibles = ["Todos"] + subcats_disponibles
                    cat_sub_actual = datos.get("categoria", "Todos")
                    if cat_sub_actual not in subcats_disponibles:
                        subcats_disponibles.append(cat_sub_actual)
                        
                    nuevo_cat_sub = st.selectbox(
                        "Sub-Categoría",
                        subcats_disponibles,
                        index=subcats_disponibles.index(cat_sub_actual),
                        key=f"cat_sub_{nombre}"
                    )

                    if st.button("💾 Guardar cambios", use_container_width=True, key=f"guardar_{nombre}"):
                        st.session_state.menu_dinamico[nombre]["precio"]              = nuevo_precio
                        st.session_state.menu_dinamico[nombre]["stock"]               = nuevo_stock
                        st.session_state.menu_dinamico[nombre]["disponible"]          = disponible
                        st.session_state.menu_dinamico[nombre]["categoria_principal"] = nuevo_cat_principal
                        st.session_state.menu_dinamico[nombre]["categoria"]           = nuevo_cat_sub
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

        lista_cat_principales = list(st.session_state.lista_categorias.keys())
        np_cat_principal = st.selectbox("Categoría Principal", lista_cat_principales, key="np_cat_principal")
        
        subcats_disponibles = st.session_state.lista_categorias.get(np_cat_principal, ["Todos"])
        if "Todos" not in subcats_disponibles:
            subcats_disponibles = ["Todos"] + subcats_disponibles
        np_cat_sub = st.selectbox("Sub-Categoría", subcats_disponibles, key="np_cat_sub")
        
        np_foto   = st.file_uploader("Foto o video del producto", type=["png","jpg","jpeg","webp","mp4","webm","ogg","mov"], key="np_foto")

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
                    "precio":              np_precio,
                    "icono":               np_icono,
                    "stock":               np_stock,
                    "disponible":          True,
                    "categoria_principal": np_cat_principal,
                    "categoria":           np_cat_sub,
                    "foto":                foto_nueva
                }
                guardar_json(RUTA_MENU, st.session_state.menu_dinamico)
                st.success(f"✔ Producto '{np_nombre}' agregado")
                st.rerun()
            else:
                st.error("Escribe un nombre para el producto.")

    st.markdown("---")

    # ── GESTIÓN DE CATEGORÍAS ──
    st.markdown("### 🏷️ Gestionar Categorías")

    with st.expander("Agregar o eliminar Categorías Principales"):
        np_cat_princ_nombre = st.text_input("Nombre de Categoría Principal (ej: ✏️ Útiles escolares)", key="np_cat_princ_nombre")
        if st.button("➕ Agregar Categoría Principal", use_container_width=True, key="btn_add_cat_princ"):
            if np_cat_princ_nombre.strip() and np_cat_princ_nombre.strip() not in st.session_state.lista_categorias:
                st.session_state.lista_categorias[np_cat_princ_nombre.strip()] = ["Todos"]
                guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
                st.success(f"✔ Categoría principal '{np_cat_princ_nombre}' agregada")
                st.rerun()
        
        cats_princ_eliminables = list(st.session_state.lista_categorias.keys())
        cat_princ_eliminar = st.selectbox("Eliminar Categoría Principal", cats_princ_eliminables, key="cat_princ_eliminar_sel")
        if st.button("🗑️ Eliminar Categoría Principal", use_container_width=True, key="btn_del_cat_princ"):
            if cat_princ_eliminar:
                del st.session_state.lista_categorias[cat_princ_eliminar]
                guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
                st.success(f"✔ Categoría principal '{cat_princ_eliminar}' eliminada")
                st.rerun()

    with st.expander("Agregar o eliminar Sub-Categorías"):
        cats_princ_existentes = list(st.session_state.lista_categorias.keys())
        if cats_princ_existentes:
            cat_princ_seleccionada = st.selectbox("Selecciona Categoría Principal", cats_princ_existentes, key="cat_princ_sel_sub")
            nueva_subcat = st.text_input("Nueva Sub-Categoría (ej: Cuadernos)", key="nueva_subcat_input")
            if st.button("➕ Agregar Sub-Categoría", use_container_width=True, key="btn_add_subcat"):
                if nueva_subcat.strip():
                    if nueva_subcat.strip() not in st.session_state.lista_categorias[cat_princ_seleccionada]:
                        st.session_state.lista_categorias[cat_princ_seleccionada].append(nueva_subcat.strip())
                        guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
                        st.success(f"✔ Sub-categoría '{nueva_subcat}' agregada a '{cat_princ_seleccionada}'")
                        st.rerun()
            
            subcats_eliminables = [s for s in st.session_state.lista_categorias[cat_princ_seleccionada] if s != "Todos"]
            subcat_eliminar = st.selectbox("Eliminar Sub-Categoría", subcats_eliminables, key="subcat_eliminar_sel")
            if st.button("🗑️ Eliminar Sub-Categoría", use_container_width=True, key="btn_del_subcat"):
                if subcat_eliminar:
                    st.session_state.lista_categorias[cat_princ_seleccionada].remove(subcat_eliminar)
                    guardar_json(RUTA_CATEGORIAS, st.session_state.lista_categorias)
                    st.success(f"✔ Sub-categoría '{subcat_eliminar}' eliminada de '{cat_princ_seleccionada}'")
                    st.rerun()
        else:
            st.info("Crea una categoría principal primero.")

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
<p class="sello-creador">⚡ Plataforma Desarrollada — Jhohan Guadalupe</p>
''', unsafe_allow_html=True)
