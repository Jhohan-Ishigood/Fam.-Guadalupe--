# ============================================================================
# CATÁLOGO PREMIUM FAM. GUADALUPE v2.0 - INGENIERÍA SENIOR EN PYTHON/STREAMLIT
# Reescritura completa con arquitectura visual avanzada, animaciones 3D y 
# diseño responsivo integral (Laptop/PC/Celular)
# ============================================================================

import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64
import time
import mimetypes
import urllib.parse

# ============================================================================
# 1. CONFIGURACIÓN GLOBAL DEL SISTEMA
# ============================================================================
st.set_page_config(
    page_title="Catálogo FAM. GUADALUPE - Productos de Calidad",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"Get Help": None, "Report a bug": None, "About": None}
)

# Determinación de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSS = os.path.join(BASE_DIR, "estilos.css")
RUTA_JSON_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_JSON_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# ============================================================================
# 2. FUNCIONES DE UTILIDAD - PRECARGA MULTIMEDIA Y PERSISTENCIA JSON
# ============================================================================
@st.cache_data(show_spinner=False)
def cargar_imagen_base64(ruta_archivo):
    """Carga y codifica imagen local a Base64 - Optimizado para caché"""
    if os.path.exists(ruta_archivo):
        try:
            mime_type, _ = mimetypes.guess_type(ruta_archivo)
            if not mime_type:
                mime_type = "image/png"
            with open(ruta_archivo, "rb") as archivo:
                return f"data:{mime_type};base64,{base64.b64encode(archivo.read()).decode()}"
        except Exception:
            return ""
    return ""

def guardar_json(ruta, datos):
    """Escritura segura de datos JSON"""
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error crítico al persistir datos: {e}")

def cargar_menu_desde_archivo():
    """Carga inventario desde JSON o usa plantilla por defecto"""
    FOTO_DEFECTO = "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>"
    
    inventario_defecto = {
        "Arroz Costeño x 1kg": {"precio": 4.50, "icono": "🌾", "disponible": True, "foto": FOTO_DEFECTO, "stock": 120, "categoria": "Abarrotes"},
        "Parlante Bluetooth JBL": {"precio": 140.00, "icono": "🔊", "disponible": True, "foto": FOTO_DEFECTO, "stock": 5, "categoria": "Tecnología"},
        "Montura de Cuero Fina": {"precio": 420.00, "icono": "🐎", "disponible": True, "foto": FOTO_DEFECTO, "stock": 2, "categoria": "Línea Ecuestre"},
        "Tubo PVC de Construcción 1/2": {"precio": 8.50, "icono": "🛠️", "disponible": True, "foto": FOTO_DEFECTO, "stock": 0, "categoria": "Ferretería & Electricidad"},
        "Cuaderno Standford A4 Liso": {"precio": 6.50, "icono": "📚", "disponible": True, "foto": FOTO_DEFECTO, "stock": 60, "categoria": "Útiles Escolares"}
    }

    if os.path.exists(RUTA_JSON_MENU):
        try:
            with open(RUTA_JSON_MENU, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, Exception):
            return inventario_defecto
    return inventario_defecto

def cargar_categorias_desde_archivo():
    """Carga categorías desde JSON"""
    categorias_defecto = ["Todos", "Abarrotes", "Ferretería & Electricidad", "Tecnología", "Línea Ecuestre", "Útiles Escolares"]
    if os.path.exists(RUTA_JSON_CATEGORIAS):
        try:
            with open(RUTA_JSON_CATEGORIAS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, Exception):
            return categorias_defecto
    return categorias_defecto

# ============================================================================
# 3. INICIALIZACIÓN DE VARIABLES DE SESIÓN
# ============================================================================
if "menu_dinamico" not in st.session_state:
    st.session_state.menu_dinamico = cargar_menu_desde_archivo()
if "lista_categorias" not in st.session_state:
    st.session_state.lista_categorias = cargar_categorias_desde_archivo()
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "total_acumulado" not in st.session_state:
    st.session_state.total_acumulado = 0.0
if "pedido_guardado" not in st.session_state:
    st.session_state.pedido_guardado = False
if "pantalla_actual" not in st.session_state:
    st.session_state.pantalla_actual = "bienvenida"
if "categoria_activa" not in st.session_state:
    st.session_state.categoria_activa = "Todos"
if "es_admin_autenticado" not in st.session_state:
    st.session_state.es_admin_autenticado = False
if "mostrar_login_admin" not in st.session_state:
    st.session_state.mostrar_login_admin = False

# Reloj de Perú GMT-5
zona_peru = timezone(timedelta(hours=-5))
ahora_peru = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

# ============================================================================
# 4. PRECARGA DE IMÁGENES Y RECURSOS MULTIMEDIA
# ============================================================================
ruta_foto_fisica = os.path.join(BASE_DIR, "establecimiento.png")
URL_BANNER_LOCAL = cargar_imagen_base64(ruta_foto_fisica)

ruta_logo_portada = os.path.join(BASE_DIR, "Logotipo.png")
URL_LOGO_PORTADA = cargar_imagen_base64(ruta_logo_portada)

ruta_qr_local = os.path.join(BASE_DIR, "miqr1.png")
URL_QR_YAPE = cargar_imagen_base64(ruta_qr_local)

# Cargar CSS externo si existe
if os.path.exists(RUTA_CSS):
    try:
        with open(RUTA_CSS, "r", encoding="utf-8") as f:
            custom_css = f.read()
            st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    except Exception:
        pass

# Inyección maestra de estilos y elementos físicos requeridos (mini-logo, destello, animaciones, admin-grid)
st.markdown(f"""
    <style>
    /* Ajustes de visibilidad para barra lateral y menú - LADO IZQUIERDO CON FONDO OSCURO */
    /* En PC y móvil: barra lateral en la izquierda */
    section[data-testid='stSidebar'], div[data-testid='stSidebar'] {{
        display:block !important;
        position:fixed !important;
        top:0 !important;
        left:0 !important;
        height:100% !important;
        z-index:999998 !important;
        background-color: rgba(10, 15, 35, 0.92) !important;
        pointer-events:auto !important;
    }}
    /* Asegurar que el contenedor principal quede por debajo de la sidebar en z-order */
    [data-testid="stAppViewContainer"] {{ position:relative !important; z-index:1 !important; }}

    /* Fondo panorámico - colocar arriba para evitar mostrar logo central duplicado */
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), url("{URL_BANNER_LOCAL}") !important;
        background-size: cover !important;
        background-position: top center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    /* Mini-logo flotante: PC y móvil derecha. Animación rotateY coin-like */
    .mini-logo-flotante-master {{ z-index:999999 !important; pointer-events:none !important; position:fixed !important; perspective:1000px !important; }}
    @media (min-width:769px) {{ .mini-logo-flotante-master {{ top:80px !important; right:25px !important; left:auto !important; width:65px !important; height:65px !important; }} .mini-logo-imagen-circular {{ width:100% !important; height:100% !important; object-fit:cover !important; border-radius:50% !important; border:2px solid #d4af37 !important; box-shadow:0 0 15px rgba(212,175,55,0.6) !important; transform-style:preserve-3d !important; animation:rotarMiniLogo3D 4s linear infinite !important; }} }}
    @media (max-width:768px) {{ .mini-logo-flotante-master {{ top:120px !important; right:15px !important; left:auto !important; width:45px !important; height:45px !important; }} .mini-logo-imagen-circular {{ width:100% !important; height:100% !important; object-fit:cover !important; border-radius:50% !important; border:2px solid #d4af37 !important; box-shadow:0 0 10px rgba(212,175,55,0.5) !important; animation:rotarMiniLogo3D 4s linear infinite !important; }} }}
    @keyframes rotarMiniLogo3D {{ 0% {{ transform:rotateY(0deg); }} 100% {{ transform:rotateY(360deg); }} }}

    /* Logo central con destello físico - EFECTO FLOTANTE + DESTELLO ESCÁNER CON REPOSO */
    .contenedor-logo-destello-fijo {{ display:flex !important; justify-content:center !important; align-items:center !important; width:100% !important; margin:20px auto !important; }}
    .marco-escudo-brillante {{ position:relative !important; width:206px !important; height:206px !important; border-radius:50% !important; overflow:hidden !important; border:3px solid #d4af37 !important; box-shadow:0 0 30px rgba(212,175,55,0.8) !important; background-color:#111424 !important; transform:none !important; animation:flotarLogoSuave 3s ease-in-out infinite !important; }}
    .foto-logo-real {{ width:100% !important; height:100% !important; object-fit:cover !important; display:block !important; border-radius:50% !important; }}
    .destello-fisico-linea {{ position:absolute !important; top:-50% !important; left:-50% !important; width:200% !important; height:200% !important; background:linear-gradient(45deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0) 15%, rgba(255,255,255,1) 30%, rgba(255,220,100,1) 50%, rgba(255,255,255,1) 70%, rgba(255,255,255,0) 85%, rgba(255,255,255,0) 100%) !important; transform:skewX(-20deg) !important; animation:destelloEscanerConReposo 6s ease-in-out infinite !important; pointer-events:none !important; z-index:2 !important; }}
    @keyframes flotarLogoSuave {{ 0% {{ transform:translateY(0px); }} 50% {{ transform:translateY(-8px); }} 100% {{ transform:translateY(0px); }} }}
    @keyframes destelloEscanerConReposo {{ 0% {{ left:-100%; opacity:0; }} 1% {{ left:-50%; opacity:1; }} 15% {{ left:120%; opacity:1; }} 16% {{ left:150%; opacity:0; }} 100% {{ left:150%; opacity:0; }} }}




    /* Fade-in en pestañas */
    .bienvenida-transparente-master, .catalogo-transparente-master, .carrito-transparente-master {{ animation: aparicionSuave 0.4s cubic-bezier(0.25,0.46,0.45,0.94) both !important; }}
    @keyframes aparicionSuave {{ 0% {{ transform:translateY(15px); opacity:0; }} 100% {{ transform:translateY(0); opacity:1; }} }}

    /* Hover elevación + micro-zoom + hilo dorado */
    div[data-testid="stColumn"] {{ transition:transform 0.28s cubic-bezier(0.25,0.8,0.25,1) !important; border-radius:12px !important; }}
    div[data-testid="stColumn"]:hover, div[data-testid="stColumn"].tapped-mobile {{ transform:translateY(-5px) !important; }}
    div[data-testid="stColumn"] img {{ transition:transform 0.35s ease !important; border-radius:12px 12px 0 0 !important; }}
    div[data-testid="stColumn"]:hover img, div[data-testid="stColumn"].tapped-mobile img {{ transform:scale(1.05) !important; }}
    div[data-testid="stColumn"]:hover .product-card-bottom, div[data-testid="stColumn"].tapped-mobile .product-card-bottom {{ border-left:4px solid #d4af37 !important; border-right:4px solid #d4af37 !important; box-shadow:0 6px 18px rgba(212,175,55,0.25) !important; }}

    /* Botón con franja escáner */
    .btn-luz-escaner {{ position:relative !important; overflow:hidden !important; display:inline-block !important; }}
    .btn-luz-escaner::after {{ content:"" !important; position:absolute !important; top:0 !important; left:-120% !important; width:60% !important; height:100% !important; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent) !important; transform:skewX(-20deg) !important; animation:luzBoton 3s linear infinite !important; z-index:1 !important; }}
    @keyframes luzBoton {{ 0% {{ left:-120%; }} 100% {{ left:220%; }} }}

    /* Pulso neón en contadores */
    div[data-testid="stNumberInput"] input:focus, div[data-testid="stNumberInput"] input:active {{ animation: pulsoNeon 0.28s ease !important; box-shadow:0 0 12px rgba(46,204,113,0.45) !important; }}
    @keyframes pulsoNeon {{ 0% {{ transform:scale(1); }} 50% {{ transform:scale(1.08); }} 100% {{ transform:scale(1); }} }}

    /* Admin grid */
    .admin-grid-2col {{ display:flex !important; flex-wrap:wrap !important; gap:15px !important; width:100% !important; }}
    .admin-tarjeta {{ flex:0 0 calc(50% - 8px) !important; min-width:calc(50% - 8px) !important; max-width:calc(50% - 8px) !important; }}
    @media (max-width:768px) {{ .admin-tarjeta {{ flex:0 0 100% !important; min-width:100% !important; max-width:100% !important; }} }}

    /* Nota captura */
    .nota-captura-estrategica {{ background-color: rgba(212,175,55,0.1) !important; border:2px dashed #d4af37 !important; padding:15px !important; border-radius:10px !important; text-align:center !important; margin-bottom:25px !important; box-shadow:0 4px 15px rgba(212,175,55,0.12) !important; }}
    .nota-captura-estrategica p {{ color:#ffffff !important; font-weight:700 !important; margin:0 !important; }}

    </style>

    <!-- elemento físico mini-logo -->
    <div class="mini-logo-flotante-master">
      <img src="{URL_LOGO_PORTADA}" class="mini-logo-imagen-circular" alt="Mini Logo">
    </div>

""", unsafe_allow_html=True)


# ============================================================================
# 7. FUNCIÓN CENTRALIZADA DE PASARELA DE PAGO
# ============================================================================
def renderizar_informacion_pago(total_contexto=None):
    """Renderiza información oficial de pago con acordeones estilizados"""
    st.markdown("### 💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO")
    st.caption("Selecciona el método de tu preferencia haciendo clic para desplegar los datos correspondientes:")

    with st.expander("🏦 VER N° DE CUENTA DEL BANCO DE LA NACIÓN", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #2980b9; margin-bottom: 5px;">
                <p style="color: #2980b9; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🏦 BANCO DE LA NACION / BNP</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número de Cuenta:</b> 04-762-855629 </p>
                <hr style="border-color: #333; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 14px;"><b>Titular:</b> Segundo Melquiades Guadalupe Sanchez</p>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("🟣 VER NÚMERO Y QR DE YAPE", expanded=False):
        if total_contexto is not None:
            st.markdown(f"<p style='color:#ffffff; font-weight:bold; font-size:15px; margin-bottom:10px;'>Monto exacto: <span style='color:#2ecc71;'>S/{total_contexto:.2f}</span></p>", unsafe_allow_html=True)        
        src_qr = URL_QR_YAPE if URL_QR_YAPE else ""
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 5px auto; max-width: 450px; background-color: #1e1e24; padding: 20px; border-radius: 16px; border: 2px solid #8e44ad; text-align: center;">
                <p style="color: #aaaaaa; font-size: 13px; margin-bottom: 12px; font-weight: bold;">Escanee con cámara si desea pagar:</p>
                <img src="{src_qr}" style="width: 240px; height: 240px; object-fit: contain; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;" />
                <span style="color: #8e44ad; font-size: 14px; font-weight: bold; letter-spacing: 1px;">🟣 +51 950 239 350</span>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("📞 VER TELÉFONO DE CONTACTO DIRECTO", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <p style="color: #27ae60; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🟢 WHATSAPP Y LLAMADAS </p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número Celular:</b> +51 950 239 350</p>
                <hr style="border-color: #333; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 13px;">Use este número para coordinar despacho o resolver consultas.</p>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# 8. BARRA LATERAL (SIDEBAR) - GESTIÓN ADMIN Y INFO
# ============================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #f39c12;'>Catálogo FAM. GUADALUPE</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #aaa;'>Productos de calidad a buen precio.</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### ⚙️ GESTIÓN DEL SISTEMA")

# Control de Login Admin
if not st.session_state.es_admin_autenticado:
    if st.sidebar.button("INGRESAR COMO ADMINISTRADOR 🤵‍♂️", use_container_width=True, key="btn_toggle_admin_login"):
        st.session_state.mostrar_login_admin = not st.session_state.mostrar_login_admin

    if st.session_state.mostrar_login_admin:
        with st.sidebar.container():
            usuario_input = st.text_input("Nombre de Usuario:", key="user_login").strip()
            clave_input = st.text_input("Contraseña:", type="password", key="pass_login").strip()
            
            USER_PROD = st.secrets.get("admin_user", "Los Guadalupe")
            PASS_PROD = st.secrets.get("admin_password", "18987915")
            
            if st.button("🔓 ENTRAR AL SISTEMA", use_container_width=True, key="btn_ejecutar_login_pos"):
                if usuario_input == USER_PROD and clave_input == PASS_PROD:
                    st.session_state.es_admin_autenticado = True
                    st.session_state.mostrar_login_admin = False
                    st.rerun()
                else:
                    st.sidebar.error("❌ Credenciales incorrectas")
else:
    st.sidebar.success("✔ Modo Administrador Activo")
    if st.sidebar.button("🚪 CERRAR SESIÓN", use_container_width=True, key="btn_cerrar_sesion_admin"):
        st.session_state.es_admin_autenticado = False
        st.rerun()

es_admin = st.session_state.es_admin_autenticado

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕒 HORARIO DE ATENCIÓN")
st.sidebar.caption("Lunes a Domingo: 8:00 AM - 11:00 PM")

hora_actual_int = ahora_peru.hour
if 8 <= hora_actual_int < 23:
    texto_radar = "🟢 EN LÍNEA"
    color_radar = "#2ecc71"
else:
    texto_radar = "🌙 CERRADO"
    color_radar = "#e67e22"

st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; background-color: #111424; padding: 8px 12px; border-radius: 8px; border: 1px solid #222538;">
        <div style="width: 10px; height: 10px; background-color: {color_radar}; border-radius: 50%; box-shadow: 0 0 0 0 {color_radar}88; animation: pulsoRadar 1.6s infinite ease-in-out;"></div>
        <span style="font-size: 12.5px; font-weight: bold; color: #ffffff;">{texto_radar}</span>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("#### 📍 UBICACIÓN")
st.sidebar.caption("Av. Principal El Gran Búfalo 742, Trujillo, Perú")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📞 ¿NECESITAS AYUDA?")
st.sidebar.link_button("💬 Chatear con Soporte", "https://wa.me/51950239350", use_container_width=True, key="link_whatsapp_soporte")

# ============================================================================
# 9. PANEL DE ADMINISTRACIÓN
# ============================================================================
if es_admin:
    st.markdown("<h1 class='titulo-principal'>📊 PANEL DE ADMINISTRACIÓN</h1>", unsafe_allow_html=True)
    st.info(f"📋 Sincronizado en tiempo real: {fecha_actual}")
    st.markdown("<br>", unsafe_allow_html=True)

    prod_registrados = len(st.session_state.menu_dinamico)
    prod_agotados = sum(1 for p in st.session_state.menu_dinamico.values() if p.get("stock", 0) <= 0)
    valor_total_capital = sum(p.get("stock", 0) * p.get("precio", 0.0) for p in st.session_state.menu_dinamico.values())

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="📦 TOTAL PRODUCTOS", value=f"{prod_registrados} ítems")
    with col_m2:
        st.metric(label="🚨 AGOTADOS", value=f"{prod_agotados} ítems")
    with col_m3:
        st.metric(label="💰 CAPITAL EN STOCK", value=f"S/{valor_total_capital:,.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    # Configuración de categorías
    with st.expander("📁 ⚙️ CONFIGURACIÓN DE SECCIONES", expanded=False):
        st.caption("Añada nuevas pestañas o elimine secciones existentes")
        st.markdown("<br>", unsafe_allow_html=True)

        col_cat1, col_cat2 = st.columns(2, gap="medium")
        
        with col_cat1:
            with st.container(border=True):
                st.markdown("##### ➕ Crear Nueva Sección")
                nueva_cat = st.text_input("Crear Sección", placeholder="Ej. Ferreteria...", key="input_create_cat_name", label_visibility="collapsed").strip().capitalize()
                
                if st.button("➕ CREAR", use_container_width=True, key="btn_create_cat"):
                    if nueva_cat and nueva_cat not in st.session_state.lista_categorias:
                        st.session_state.lista_categorias.append(nueva_cat)
                        guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                        st.success(f"✔ Sección '{nueva_cat}' creada!")
                        st.rerun()
                    elif nueva_cat in st.session_state.lista_categorias:
                        st.error("⚠️ Categoría ya existe")
        
        with col_cat2:
            with st.container(border=True):
                st.markdown("##### 🗑️ Eliminar Sección")
                cats_borrables = [c for c in st.session_state.lista_categorias if c != "Todos"]
                cat_a_borrar = st.selectbox("Eliminar", options=cats_borrables, key="select_delete_cat_name", label_visibility="collapsed")
                
                if st.button("🗑️ ELIMINAR", use_container_width=True, key="btn_delete_cat"):
                    if cat_a_borrar:
                        st.session_state.lista_categorias.remove(cat_a_borrar)
                        guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                        st.warning(f"🗑️ Sección '{cat_a_borrar}' removida")
                        st.rerun()

    # Agregar nuevo producto
    with st.expander("➕ 🛠️ AÑADIR NUEVO PRODUCTO", expanded=False):
        st.caption("Complete los datos para agregar un producto nuevo")
        nuevo_nombre = st.text_input("Nombre:", placeholder="Ej. Filtro de agua...").strip()
        
        col_new1, col_new2, col_new3, col_new4 = st.columns(4)
        with col_new1:
            nuevo_precio = st.number_input("Precio (S/):", min_value=0.5, value=10.0, step=0.5)
        with col_new2:
            nuevo_icono = st.text_input("Icono:", value="📦", max_chars=2).strip()
        with col_new3:
            nuevo_stock = st.number_input("Stock:", min_value=0, value=15, step=1)
        with col_new4:
            cats_creadas = [c for c in st.session_state.lista_categorias if c != "Todos"]
            nueva_categoria_asociada = st.selectbox("Categoría:", options=cats_creadas)
            
        archivo_foto = st.file_uploader("Foto:", type=["jpg", "jpeg", "png"], key="upload_nuevo_prod")
            
        if st.button("🚀 GUARDAR PRODUCTO", use_container_width=True):
            if nuevo_nombre:
                if nuevo_nombre not in st.session_state.menu_dinamico:
                    if archivo_foto is not None:
                        bytes_foto = archivo_foto.getvalue()
                        mime_type = archivo_foto.type or "image/png"
                        encoded_foto = base64.b64encode(bytes_foto).decode()
                        src_final_foto = f"data:{mime_type};base64,{encoded_foto}"
                    else:
                        src_final_foto = "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>"

                    st.session_state.menu_dinamico[nuevo_nombre] = {
                        "precio": nuevo_precio,
                        "icono": nuevo_icono,
                        "disponible": True,
                        "foto": src_final_foto,
                        "stock": int(nuevo_stock),
                        "categoria": nueva_categoria_asociada
                    }
                    guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                    st.success(f"✔ {nuevo_icono} {nuevo_nombre} agregado!")
                    st.rerun()
                else:
                    st.error("⚠️ Producto ya existe")

    # ============================================================================
    # GESTIÓN DE PRODUCTOS EN 2 COLUMNAS ESTRICTAS
    # ============================================================================
    st.markdown("### 📝 GESTIÓN DE PRECIOS, STOCK Y ELIMINACIÓN")
    st.caption(f"Filtro activo: **{st.session_state.categoria_activa}**")
    
    productos_lista = list(st.session_state.menu_dinamico.keys())
    cambios_detectados = False

    productos_visibles_admin = []
    for prod in productos_lista:
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
            productos_visibles_admin.append(prod)

    # Renderizar el grid administrativo usando un wrapper HTML (2 columnas estrictas)
    st.markdown('<div class="admin-grid-2col">', unsafe_allow_html=True)

    for pos, prod in enumerate(productos_visibles_admin):
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")

        # cada tarjeta física controla su 50% de ancho
        st.markdown(f'<div class="admin-tarjeta">', unsafe_allow_html=True)
        with st.container(border=True):
            col_det1, col_det2 = st.columns([1, 2])
            with col_det1:
                foto_actual = info_prod.get("foto", "")
                st.markdown(f'<img src="{foto_actual}" style="width:100%; height:75px; object-fit:cover; border-radius:6px; border:1px solid #d4af37;">', unsafe_allow_html=True)
            with col_det2:
                st.markdown(f"**{info_prod['icono']} {prod}**")
                st.caption(f"Sección: {cat_prod}")

            st.markdown("<hr style='margin:10px 0; border-color:#222538;'>", unsafe_allow_html=True)

            col_inputs1, col_inputs2 = st.columns(2)
            with col_inputs1:
                precio_edit = st.number_input(f"Precio (S/) {prod}", min_value=0.1, value=float(info_prod["precio"]), step=0.1, key=f"edit_p_{prod}")
            with col_inputs2:
                stock_edit = st.number_input(f"Stock {prod}", min_value=0, value=int(info_prod["stock"]), step=1, key=f"edit_s_{prod}")

            # file_uploader por ítem (actualiza la foto en caliente)
            nueva_foto_individual = st.file_uploader(f"🔄 Foto de {prod}:", type=["jpg", "jpeg", "png"], key=f"foto_edit_{prod}")
            if nueva_foto_individual is not None:
                bytes_foto_edit = nueva_foto_individual.getvalue()
                mime_type_edit = nueva_foto_individual.type or "image/png"
                encoded_foto_edit = base64.b64encode(bytes_foto_edit).decode()
                st.session_state.menu_dinamico[prod]["foto"] = f"data:{mime_type_edit};base64,{encoded_foto_edit}"
                cambios_detectados = True

            st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)

            if st.button("🗑️ ELIMINAR", key=f"del_{prod}", use_container_width=True):
                del st.session_state.menu_dinamico[prod]
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.warning(f"✔ '{prod}' removido")
                st.rerun()

            # aplicar cambios detectados en precio/stock
            if precio_edit != info_prod["precio"] or stock_edit != info_prod["stock"]:
                st.session_state.menu_dinamico[prod]["precio"] = precio_edit
                st.session_state.menu_dinamico[prod]["stock"] = stock_edit
                st.session_state.menu_dinamico[prod]["disponible"] = stock_edit > 0
                cambios_detectados = True

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

    if cambios_detectados:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 CONFIRMAR Y GUARDAR CAMBIOS", use_container_width=True, key="btn_guardar_cambios_admin"):
            guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
            st.success("✔ Inventario actualizado!")
            st.rerun()

# ============================================================================
# 10. ENTORNO CLIENTE - PANTALLA 1: BIENVENIDA
# ============================================================================
else:
    if st.session_state.pantalla_actual == "bienvenida":
        st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

        st.markdown("<h3 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px; margin-top: -10px; font-weight: bold; color: #d4af37;'>Bienvenidos al stock de productos disponibles y sus precios 🔥</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Logotipo con destello metálico forzado inline
        if URL_LOGO_PORTADA:
            st.markdown(f"""
                <div class="contenedor-logo-destello-fijo">
                    <div class="marco-escudo-brillante">
                        <img src="{URL_LOGO_PORTADA}" class="foto-logo-real" alt="Logo FAM. GUADALUPE">
                        <!-- Inyectamos el destello físico (usa keyframes global cruzarDestello) -->
                        <div class="destello-fisico-linea"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="btn-luz-escaner">', unsafe_allow_html=True)
        cambiar_a_catalogo = st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_empezar_pedido_master")
        st.markdown('</div>', unsafe_allow_html=True)

        renderizar_informacion_pago()
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class='social-footer'>
                <p style='margin-bottom: 10px; font-size: 14px; letter-spacing: 2px; color: #888; font-weight: bold;'>SÍGUENOS EN REDES SOCIALES</p>
                <a href='https://facebook.com' target='_blank' class='social-icon'>📘 Facebook</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://instagram.com' target='_blank' class='social-icon'>📸 Instagram</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://wa.me' target='_blank' class='social-icon'>🟢 WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        if cambiar_a_catalogo:
            st.session_state.pantalla_actual = "catalogo"
            st.rerun()

    # ============================================================================
    # 11. ENTORNO CLIENTE - PANTALLA 2: CATÁLOGO DE PRODUCTOS
    # ============================================================================
    elif st.session_state.pantalla_actual == "catalogo" and not st.session_state.pedido_guardado:
        st.markdown('<div class="catalogo-transparente-master">', unsafe_allow_html=True)
        st.markdown("\n<h2 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #aaa;'>Fecha y hora Perú (GMT-5): {fecha_actual}</h3>\n", unsafe_allow_html=True)
        
        st.markdown("<div class='netflix-navbar-master'>", unsafe_allow_html=True)
        col_izq_tabs, col_der_search = st.columns([2.5, 1.5], gap="small")
        
        with col_izq_tabs:
            categoria_seleccionada = st.radio(
                "Categorías",
                options=st.session_state.lista_categorias,
                index=st.session_state.lista_categorias.index(st.session_state.categoria_activa),
                horizontal=True,
                label_visibility="collapsed",
                key="tabs_netflix_master_final_key"
            )
            if categoria_seleccionada != st.session_state.categoria_activa:
                st.session_state.categoria_activa = categoria_seleccionada
                st.rerun()
                
        with col_der_search:
            busqueda = st.text_input("🔍 Buscar", placeholder="¿BUSQUE AQUÍ?", label_visibility="collapsed", key="search_bar_master_final_key").strip().lower()
            
        st.markdown("</div><br>", unsafe_allow_html=True)
        
        st.subheader(f"📍 SELECCIÓN DE {st.session_state.categoria_activa.upper()}")
        st.info("Ingrese las cantidades de los productos que desea llevar:")

        productos_lista = list(st.session_state.menu_dinamico.keys())
        productos_filtrados = []

        for prod in productos_lista:
            if busqueda and busqueda not in prod.lower():
                continue
                
            info_prod = st.session_state.menu_dinamico[prod]
            cat_prod = info_prod.get("categoria", "Abarrotes")

            if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
                productos_filtrados.append(prod)

        col1, col2 = st.columns(2, gap="medium")
        cantidades_ingresadas = {}
        
        for i in range(len(productos_filtrados)):
            prod = productos_filtrados[i]
            info = st.session_state.menu_dinamico[prod]
            target_col = col1 if i % 2 == 0 else col2
            
            stock_actual = info.get("stock", 0)
            esta_disponible = info["disponible"] and stock_actual > 0
            
            with target_col:
                if esta_disponible:
                    url_imagen_plato = info.get("foto", "")
                    st.markdown(f"""<img src="{url_imagen_plato}" style="width:100%; height:220px; object-fit:cover; border-radius:12px 12px 0px 0px; box-shadow: 0px 4px 12px rgba(0,0,0,0.6); display:block; margin:0; padding:0;">""", unsafe_allow_html=True)
                    
                    texto_precio = f"S/{info['precio']:.2f}"
                    st.markdown(f"""
                        <div class='product-card-bottom'>
                            <span class='product-title'>{info['icono']} {prod}</span>
                            <span class='product-price'>{texto_precio}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if stock_actual <= 3:
                        st.markdown(f"<p class='mini-stock-alerta'>🔥 ¡Solo quedan {stock_actual} unidades! 🔥</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p class='mini-stock-normal'>📦 Stock disponible: {stock_actual} und.</p>", unsafe_allow_html=True)
                    
                    cantidades_ingresadas[prod] = st.number_input(f"Cantidad de {prod}:", min_value=0, max_value=int(stock_actual), step=1, key=f"cat_{prod}", label_visibility="collapsed")
                    st.markdown("<br>", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="width:100%; height:200px; background-color:#222; border-radius:12px 12px 0px 0px; display:flex; align-items:center; justify-content:center;"><span style="font-size:50px; filter:grayscale(100%);">{info['icono']}</span></div>""", unsafe_allow_html=True)
                    st.markdown(f"<div style='background-color:#1c1c1c; padding:20px; border-radius:0px 0px 12px 12px; border:2px solid #ff4b4b; text-align:center; margin-bottom:25px;'><p style='color: #ff4b4b; font-size:18px; font-weight: bold; margin:0;'>❌ {prod}<br>(AGOTADO)</p></div>", unsafe_allow_html=True)
                    
        st.markdown("---")
        if st.button("🛒 SIMULAR MONTO FINAL", use_container_width=True):
            st.session_state.carrito = []
            st.session_state.total_acumulado = 0.0
            for prod, cant in cantidades_ingresadas.items():
                if cant > 0:
                    sub = cant * st.session_state.menu_dinamico[prod]["precio"]
                    st.session_state.carrito.append({"producto": prod, "cantidad": cant, "subtotal": sub})
                    st.session_state.total_acumulado += sub
            
            if st.session_state.total_acumulado > 0:
                st.session_state.pedido_guardado = True
                st.rerun()
            else:
                st.error("⚠️ Error: Debe seleccionar al menos 1 producto.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================================
    # 12. ENTORNO CLIENTE - PANTALLA 3: CARRITO Y FINALIZACIÓN
    # ============================================================================
    else:
        st.markdown('<div class="carrito-transparente-master">', unsafe_allow_html=True)
        st.html("<div style='height: 15px;'></div>")
        st.subheader("📦 LISTA DE PRODUCTOS SELECCIONADOS")
        
        texto_proforma_whatsapp = "Hola Familia Guadalupe, deseo coordinar mi pedido:\n\n"
        for item in st.session_state.carrito:
            icono_p = st.session_state.menu_dinamico[item['producto']]['icono']
            st.markdown(f"""
                <div style="background-color: #1e1e24; border-left: 4px solid #f39c12; padding: 12px 16px; border-radius: 8px; color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);">
                    {icono_p} {item['producto']} x{item['cantidad']} &nbsp;|&nbsp; S/{item['subtotal']:.2f}
                </div>
            """, unsafe_allow_html=True)
            texto_proforma_whatsapp += f"• {icono_p} {item['producto']} x{item['cantidad']} (S/{item['subtotal']:.2f})\n"
        
        st.markdown("---")
        st.metric(label="Monto Total", value=f"S/{st.session_state.total_acumulado:.2f}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        texto_proforma_whatsapp += f"\n💰 Total: S/{st.session_state.total_acumulado:.2f}\n📌 {fecha_actual}"
        mensaje_parseado_url = urllib.parse.quote(texto_proforma_whatsapp)
        url_whatsapp = f"https://api.whatsapp.com/send?phone=51950239350&text={mensaje_parseado_url}"

        renderizar_informacion_pago(total_contexto=st.session_state.total_acumulado)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # NOTA ESTRATÉGICA DE CAPTURA
        st.markdown("""
            <div class='nota-captura-estrategica'>
                <p>⚠️ Recomendación: Tómale una captura de pantalla a esta lista para que no olvides los productos que quieres comprar antes de realizar tu transferencia bancaria.</p>
            </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💾 CONFIRMAR SIMULACIÓN", use_container_width=True):
                # Marcar la bandera ANTES de persistir y hacer rerun para evitar doble descuento por refresh
                st.session_state.pedido_guardado = True

                # aplicar reserva / descuento de stock localmente
                for item in st.session_state.carrito:
                    prod_comprado = item["producto"]
                    cant_comprada = item["cantidad"]
                    stock_previo = st.session_state.menu_dinamico[prod_comprado].get("stock", 0)
                    st.session_state.menu_dinamico[prod_comprado]["stock"] = max(0, stock_previo - cant_comprada)
                    st.session_state.menu_dinamico[prod_comprado]["disponible"] = st.session_state.menu_dinamico[prod_comprado]["stock"] > 0

                # persistir cambios de inventario y confirmar al usuario
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.success("✔ Simulación procesada correctamente!")
                st.balloons()
                time.sleep(1.0)
                st.rerun()

            st.link_button("🟢 ENVIAR PEDIDO POR WHATSAPP", url_whatsapp, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Crear Nueva Orden", use_container_width=True, key="btn_nueva_orden_final"):
            st.session_state.carrito = []
            st.session_state.total_acumulado = 0.0
            st.session_state.pedido_guardado = False
            st.session_state.pantalla_actual = "bienvenida"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
