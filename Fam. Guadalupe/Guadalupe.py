# ============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA, IMPORTACIONES Y RUTAS DE CONTROL
# ============================================================================
import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64
import time

# Configuración inicial del lienzo responsivo de la aplicación
st.set_page_config(
    page_title="Catálogo de los productos a la venta", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Determinación dinámica y automática de la ruta raíz en servidores de producción
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mapeo unificado de archivos físicos de la base de datos local y estilos
RUTA_CSS = os.path.join(BASE_DIR, "estilos.css")
RUTA_JSON_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_JSON_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# --- MOTOR DE PRECARGA MULTIMEDIA OPTIMIZADO (EVITA LENTITUD EN BUCLE) ---
@st.cache_data(show_spinner=False)
def cargar_imagen_base64(ruta_archivo):
    """Carga y codifica una imagen local a Base64 una sola vez para rendimiento óptimo."""
    if os.path.exists(ruta_archivo):
        try:
            with open(ruta_archivo, "rb") as archivo:
                return f"data:image/png;base64,{base64.b64encode(archivo.read()).decode()}"
        except Exception:
            return ""
    return ""

# Precarga segura de recursos estáticos del sistema
ruta_foto_fisica = os.path.join(BASE_DIR, "establecimiento.png")
URL_BANNER_LOCAL = cargar_imagen_base64(ruta_foto_fisica)

ruta_logo_portada = os.path.join(BASE_DIR, "Logotipo.png")
URL_LOGO_PORTADA = cargar_imagen_base64(ruta_logo_portada)

ruta_qr_local = os.path.join(BASE_DIR, "mi_qr_yape de MELQUIADES.png")
URL_QR_YAPE = cargar_imagen_base64(ruta_qr_local)

# Inicialización por defecto de la variable de búsqueda global
busqueda = ""
# ============================================================================
# 2. MOTOR DE PERSISTENCIA FIJA (OPTIMIZADO: SIN HISTORIAL INNECESARIO)
# ============================================================================

def guardar_json(ruta, datos):
    """Función maestra genérica para escribir datos en archivos JSON de forma segura."""
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error al persistir base de datos: {e}")

def cargar_menu_desde_archivo():
    """Carga la carta de productos del JSON o inicializa el inventario por defecto."""
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
    """Carga las pestañas de navegación para evitar que las creadas por el admin se borren."""
    categorias_defecto = ["Todos", "Abarrotes", "Ferretería & Electricidad", "Tecnología", "Línea Ecuestre", "Útiles Escolares"]
    if os.path.exists(RUTA_JSON_CATEGORIAS):
        try:
            with open(RUTA_JSON_CATEGORIAS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, Exception):
            return categorias_defecto
    return categorias_defecto
# ============================================================================
# 3. INICIALIZACIÓN DE VARIABLES REACTIVAS DE SESIÓN (ESTADOS DEL SISTEMA)
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
if "mostrar_login_admin" not in st.session_state:
    st.session_state.mostrar_login_admin = False

# Anclaje y sincronización de reloj oficial para Perú (GMT-5)
zona_peru = timezone(timedelta(hours=-5))
ahora_peru = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

# ============================================================================
# 3.5 INYECCIÓN GLOBAL DEL MINI LOGOTIPO FLOTANTE GIRATORIO EN 3D (TIPO MONEDA)
# ============================================================================
if URL_LOGO_PORTADA:
    st.markdown(f"""
        <style>
        /* Contenedor fijo en la esquina superior derecha con profundidad de perspectiva */
        .mini-logo-flotante-master {{
            position: fixed !important;
            top: 60px !important;
            right: 25px !important;
            width: 65px !important;
            height: 65px !important;
            z-index: 999999 !important; /* Capa máxima por encima de todo */
            pointer-events: none !important;
            perspective: 1000px !important; /* Habilita el entorno tridimensional real */
        }}
        .mini-logo-imagen-circular {{
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            border-radius: 50% !important;
            border: 2px solid #d4af37 !important;
            background-color: #111424 !important;
            box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.6) !important;
            
            /* [!] CORRECCIÓN SUPREMA: Rota horizontalmente en 3D cada 4 segundos manteniéndose derecho */
            animation: rotarMiniLogo3DMoneda 4s linear infinite !important;
            transform-style: preserve-3d !important;
        }}
        
        /* Animación que simula una moneda girando de perfil de forma continua e infinita */
        @keyframes rotarMiniLogo3DMoneda {{
            0% {{ transform: rotateY(0deg); }}
            100% {{ transform: rotateY(360deg); }}
        }}
        
        /* Optimización responsiva para que en pantallas móviles no estorbe */
        @media (max-width: 480px) {{
            .mini-logo-flotante-master {{
                width: 50px !important;
                height: 50px !important;
                top: 70px !important;
                right: 15px !important;
            }}
        }}
        </style>
        <div class="mini-logo-flotante-master">
            <img src="{URL_LOGO_PORTADA}" class="mini-logo-imagen-circular">
        </div>
    """, unsafe_allow_html=True)

    
# ============================================================================
# 4. INYECCIÓN NATIVA MAESTRA DE ESTILOS Y CONTROL DE MARCA (BLINDAJE TOTAL)
# ============================================================================
st.markdown(f"""
    <style>
    /* 1. ELIMINACIÓN CORREGIDA: BORRAMOS EL MENÚ MAESTRO DERECHO Y CONTENEDORES TÉCNICOS */
    #MainMenu, .stAppDeployDropdown, [data-testid="stHeader"] > div:last-child {{
        display: none !important;
    }}
    
    /* BLINDAJE UNIVERSAL: Forzamos la aparición del botón izquierdo por posición estructural */
    header[data-testid="stHeader"] div:first-child,
    header[data-testid="stHeader"] button,
    [data-testid="stHeader"] [data-testid="stSidebarCollapseButton"],
    .stApp div[data-testid="stHeader"] button:first-of-type {{
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important; /* Capa máxima para que flote por encima de todo */
    }}

    /* 2. MOTOR DEL FONDO PANORÁMICO ANIMADO EN BUCLE GLOBAL INTEGRAL */
    [data-testid="stAppViewContainer"] {{
        background-color: #0a0a0f !important;
        background-image: linear-gradient(rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0.82)), url("{URL_BANNER_LOCAL}") !important;
        background-size: 140% auto !important; 
        background-position: 0% center !important;
        background-repeat: no-repeat !important;
        background-attachment: scroll !important;
        animation: recorridoPanoramicoEstablecimiento 25s ease-in-out infinite alternate !important;
    }}
    @keyframes recorridoPanoramicoEstablecimiento {{
        0% {{ 
            background-size: 140% auto !important;
            background-position: 0% center !important; 
        }}
        100% {{ 
            background-size: 140% auto !important;
            background-position: 100% center !important; 
        }}
    }}


    /* 3. TRANSPARENCIA RADICAL EN TODAS LAS CAPAS INTERMEDIAS */
    .stApp, [data-testid="stMainBlockContainer"], [data-testid="stVerticalBlock"], 
    [data-testid="stAppViewBlockContainer"], [data-testid="elementGrid"], 
    .element-container, div[role="radiogroup"], .bienvenida-transparente-master, 
    .catalogo-transparente-master, .carrito-transparente-master {{
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
    }}

    /* 4. CONFIGURACIÓN DEL SELLO DEL CREADOR */
    .sello-creador {{
        color: #2ecc71 !important;             
        font-size: 13.5px !important;
        font-weight: 800 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin: 20px 0 10px 10px !important;
        text-shadow: 0px 0px 8px rgba(46, 204, 113, 0.5) !important;
    }}
    </style>
""", unsafe_allow_html=True)

if os.path.exists(RUTA_CSS):
    with open(RUTA_CSS, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<div class='sello-creador'>Página desarrollada por: Jhohan Guadalupe</div>", unsafe_allow_html=True)



# ============================================================================
# 4.5 FUNCIÓN CENTRALIZADA DE PASARELA DE PAGO (ANTI-REDUNDANCIA COMPLETA)
# ============================================================================
def renderizar_informacion_pago(total_contexto=None):
    """Renderiza la pasarela oficial de datos financieros con bordes de luz interactivos."""
    st.markdown("### 💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO")
    st.caption("Selecciona el método de tu preferencia haciendo clic para desplegar los datos correspondientes:")

    # --- PORTADA DESPLEGABLE 1: DATOS DE CUENTA BANCARIA (BORDE AZUL CONTINUO) ---
    with st.expander("🏦 VER N° DE CUENTA DEL BANCO DE LA NACIÓN", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #2980b9; margin-bottom: 5px;">
                <p style="color: #2980b9; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🏦 BANCO DE LA NACION / BNP</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número de Cuenta:</b> 570-98421345-0-88</p>
                <hr style="border-color: #333; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 14px;"><b>Titular del Negocio:</b> Segundo Melquiades Guadalupe Sanchez</p>
            </div>
        """, unsafe_allow_html=True)

    # --- PORTADA DESPLEGABLE 2: PROCESAMIENTO ELECTRÓNICO CON YAPE Y QR (BORDE MORADO NEÓN) ---
    with st.expander("🟣 VER NÚMERO Y QR DE YAPE", expanded=False):
        if total_contexto is not None:
            st.markdown(f"<p style='color:#ffffff; font-weight:bold; font-size:15px; margin-bottom:10px;'>Monto exacto a transferir: <span style='color:#2ecc71;'>S/{total_contexto:.2f}</span></p>", unsafe_allow_html=True)
            
        src_qr = URL_QR_YAPE if URL_QR_YAPE else "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>"
        
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 5px auto; max-width: 450px; background-color: #1e1e24; padding: 20px; border-radius: 16px; border: 2px solid #8e44ad; text-align: center;">
                <p style="color: #aaaaaa; font-size: 13px; margin-bottom: 12px; font-weight: bold;">Escanee con la cámara del celular si desea pagar:</p>
                <img src="{src_qr}" style="width: 240px; height: 240px; object-fit: contain; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;" />
                <span style="color: #8e44ad; font-size: 14px; font-weight: bold; letter-spacing: 1px;">🟣 NÚMERO ASOCIADO: 950 239 350</span>
            </div>
        """, unsafe_allow_html=True)

    # --- PORTADA DESPLEGABLE 3: TELÉFONO DE CONTACTO DIRECTO (BORDE VERDE ESMERALDA) ---
    with st.expander("📞 VER TELÉFONO DE CONTACTO DIRECTO", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <p style="color: #27ae60; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🟢 WHATSAPP CORPORATIVO</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número Celular:</b> +51 950 239 350</p>
                <hr style="border-color: #333; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 13px;">Use este número para coordinar directamente el despacho de su mercadería o resolver consultas.</p>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# 5. BARRA LATERAL (SIDEBAR POS): GESTIÓN INTERNA Y AUTENTICACIÓN BLINDADA
# ============================================================================
# Inicializamos la variable de sesión para recordar si ya eres administrador
if "es_admin_autenticado" not in st.session_state:
    st.session_state.es_admin_autenticado = False

st.sidebar.markdown("<h2 style='text-align: center; color: #f39c12;'>Catálogo de Productos</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #aaa;'>Artículos de calidad a buen precio.</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### ⚙️ GESTIÓN DEL SISTEMA")

# Control interactivo de estados en el Sidebar para Login / Logout
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
    # Si ya está logueado, le damos un botón limpio para Salir de forma segura
    st.sidebar.success("✔ Modo Administrador Activo")
    if st.sidebar.button("🚪 CERRAR SESIÓN DE GESTIÓN", use_container_width=True, key="btn_cerrar_sesion_admin"):
        st.session_state.es_admin_autenticado = False
        st.rerun()

# Forzamos a que la variable global 'es_admin' lea el estado persistente de la sesión
es_admin = st.session_state.es_admin_autenticado

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕒 HORARIO DE ATENCIÓN")
st.sidebar.caption("Lunes a Domingo: 8:00 AM - 11:00 PM")

# --- INDICADOR VISUAL "EN LÍNEA" AUTOMÁTICO CON RADAR (SISTEMA INTELIGENTE) ---
hora_actual_int = ahora_peru.hour
if 8 <= hora_actual_int < 23:
    texto_radar = "🟢 EN LÍNEA - RECIBIENDO ÓRDENES"
    color_radar = "#2ecc71"
else:
    texto_radar = "🌙 CERRADO - SIMULADOR ACTIVO"
    color_radar = "#e67e22"

st.sidebar.markdown(f"""
    <style>
    .contenedor-radar {{
        display: flex;
        align-items: center;
        gap: 10px;
        background-color: #111424;
        padding: 8px 12px;
        border-radius: 8px;
        border: 1px solid #222538;
    }}
    .punto-radar {{
        width: 10px;
        height: 10px;
        background-color: {color_radar};
        border-radius: 50%;
        box-shadow: 0 0 0 0 {color_radar}88;
        animation: pulsoRadarEfecto 1.6s infinite ease-in-out;
    }}
    @keyframes pulsoRadarEfecto {{
        0% {{ box-shadow: 0 0 0 0 {color_radar}bb; }}
        70% {{ box-shadow: 0 0 0 10px {color_radar}00; }}
        100% {{ box-shadow: 0 0 0 0 {color_radar}00; }}
    }}
    .texto-radar {{
        font-size: 12.5px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }}
    </style>
    <div class="contenedor-radar">
        <div class="punto-radar"></div>
        <span class="texto-radar">{texto_radar}</span>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("#### 📍 NUESTRA UBICACIÓN")
st.sidebar.caption("Av. Principal El Gran Búfalo 742, Trujillo, Perú")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📞 ¿NECESITAS AYUDA?")

st.sidebar.link_button(
    "💬 Chatear con Soporte",
    "https://wa.me",
    use_container_width=True,
    key="link_whatsapp_soporte"
)

# ============================================================================
# 6. PANEL DE CONTROL DE ADMINISTRACIÓN - GESTOR DE SECCIONES (JSON)
# ============================================================================
if es_admin:
    st.markdown("<h1 class='titulo-principal'>📊 PANEL DE ADMINISTRACIÓN</h1>", unsafe_allow_html=True)
    st.info(f"📋 **Reporte Gerencial del Grupo 5** — Sincronizado en tiempo real: {fecha_actual}")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- TABLERO DE MÉTRICAS GERENCIALES EN TIEMPO REAL (CONTROL DE INVENTARIO) ---
    prod_registrados = len(st.session_state.menu_dinamico)
    prod_agotados = sum(1 for p in st.session_state.menu_dinamico.values() if p.get("stock", 0) <= 0)
    valor_total_capital = sum(p.get("stock", 0) * p.get("precio", 0.0) for p in st.session_state.menu_dinamico.values())

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="📦 TOTAL PRODUCTOS", value=f"{prod_registrados} ítems")
    with col_m2:
        st.metric(label="🚨 PRODUCTOS AGOTADOS", value=f"{prod_agotados} ítems")
    with col_m3:
        st.metric(label="💰 CAPITAL TOTAL EN STOCK", value=f"S/{valor_total_capital:,.2f}")
    st.markdown("<br>", unsafe_allow_html=True)

    # Bloque expandible de control de pestañas y categorías
    with st.expander("📁 ⚙️ CONFIGURACIÓN DE SECCIONES DE LOS PRODUCTOS", expanded=False):
        st.caption("Añada nuevas pestañas al menú horizontal o elimine las secciones que ya no utilice en la jornada.")
        st.markdown("<br>", unsafe_allow_html=True)

        col_cat1, col_cat2 = st.columns(2, gap="medium")
        
        with col_cat1:
            with st.container(border=True):
                st.markdown("##### ➕ Crear Nueva Sección")
                nueva_cat = st.text_input(
                    "Crear Sección", 
                    placeholder="Escribe aquí la nueva sección (Ej. Ferreteria)...", 
                    key="input_create_cat_name",
                    label_visibility="collapsed"
                ).strip().capitalize()
                
                if st.button("➕ CREAR NUEVA SECCIÓN", use_container_width=True, key="btn_create_cat"):
                    if nueva_cat and nueva_cat not in st.session_state.lista_categorias:
                        st.session_state.lista_categorias.append(nueva_cat)
                        guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                        st.success(f"✔ ¡Sección '{nueva_cat}' integrada con éxito!")
                        st.rerun()
                    elif nueva_cat in st.session_state.lista_categorias:
                        st.error("⚠️ Error: Esta categoría ya existe en el menú.")
                    else:
                        st.error("⚠️ Error: El nombre no puede estar vacío.")
        with col_cat2:
            with st.container(border=True):
                st.markdown("##### 🗑️ Eliminar Sección Seleccionada")
                cats_borrables = [c for c in st.session_state.lista_categorias if c != "Todos"]
                
                cat_a_borrar = st.selectbox(
                    "Eliminar Sección", 
                    options=cats_borrables, 
                    key="select_delete_cat_name",
                    label_visibility="collapsed"
                )
                
                if st.button("🗑️ ELIMINAR SECCIÓN SELECCIONADA", use_container_width=True, key="btn_delete_cat"):
                    if cat_a_borrar:
                        st.session_state.lista_categorias.remove(cat_a_borrar)
                        guardar_json(RUTA_JSON_CATEGORIAS, st.session_state.lista_categorias)
                        
                        if st.session_state.categoria_activa == cat_a_borrar:
                            st.session_state.categoria_activa = "Todos"
                            
                        st.warning(f"🗑️ Sección '{cat_a_borrar}' removida físicamente de la carta.")
                        st.rerun()

    # ============================================================================
    # 7. PANEL DE CONTROL DE ADMINISTRACIÓN - INSERCIÓN DE PRODUCTOS MULTIMEDIA
    # ============================================================================
    with st.expander("➕ 🛠️ AÑADIR NUEVO PRODUCTO CON FOTO", expanded=False):
        st.caption("Complete los datos para agregar un producto nuevo subiendo una imagen desde su dispositivo.")
        nuevo_nombre = st.text_input("Nombre del nuevo producto:", placeholder="Ej. Filtro de agua, Cables...").strip()
        
        col_new1, col_new2, col_new3, col_new4 = st.columns(4)
        with col_new1:
            nuevo_precio = st.number_input("Precio de venta (S/):", min_value=0.5, value=10.0, step=0.5)
        with col_new2:
            nuevo_icono = st.text_input("Icono (Emoji):", value="📦", max_chars=2).strip()
        with col_new3:
            nuevo_stock = st.number_input("Stock (Unidades):", min_value=0, value=15, step=1)
        with col_new4:
            cats_creadas = [c for c in st.session_state.lista_categorias if c != "Todos"]
            nueva_categoria_asociada = st.selectbox("Categoría asignada:", options=cats_creadas)
            
        archivo_foto = st.file_uploader("Selecciona la foto del producto:", type=["jpg", "jpeg", "png"], key="upload_nuevo_prod")
            
        if st.button("🚀 GUARDAR E INTEGRAR NUEVO PRODUCTO", use_container_width=True):
            if nuevo_nombre:
                if nuevo_nombre not in st.session_state.menu_dinamico:
                    if archivo_foto is not None:
                        bytes_foto = archivo_foto.getvalue()
                        encoded_foto = base64.b64encode(bytes_foto).decode()
                        src_final_foto = f"data:image/png;base64,{encoded_foto}"
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
                    st.success(f"✔ ¡{nuevo_icono} {nuevo_nombre} integrado con éxito en '{nueva_categoria_asociada}'!")
                    st.rerun()
                else:
                    st.error("⚠️ Error: Ese producto ya existe en la carta actual.")
            else:
                st.error("⚠️ Error: El nombre del producto no puede estar vacío.")

    # ============================================================================
    # 8. PANEL DE CONTROL DE ADMINISTRACIÓN - GESTIÓN DE PRECIOS, STOCK Y ELIMINACIÓN
    # ============================================================================
    st.markdown("### 📝 GESTIÓN DE PRECIOS, STOCK Y ELIMINACIÓN")
    st.caption(f"Filtro por pestaña activa: **{st.session_state.categoria_activa}**")
    productos_lista = list(st.session_state.menu_dinamico.keys())
    cambios_detectados = False

    # 1. FILTRADO PREVIO: Creamos una lista limpia solo con los productos de la pestaña activa
    productos_visibles_admin = []
    for prod in productos_lista:
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
            productos_visibles_admin.append(prod)

    # 2. ARQUITECTURA DE ENTORNO EN 2 COLUMNAS REALES PARA EL PANEL ADMINISTRATIVO
    col_admin1, col_admin2 = st.columns(2, gap="medium")
    
    # Iteramos con un contador limpio (pos) sobre la lista ya filtrada
    for pos, prod in enumerate(productos_visibles_admin):
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")
        
        # Distribución matemática exacta de vaivén entre la columna 1 y la columna 2
        target_col_admin = col_admin1 if pos % 2 == 0 else col_admin2
        
        with target_col_admin:
            with st.container(border=True):
                # Fila superior: Foto miniatura del producto y su Nombre/Sección
                col_det1, col_det2 = st.columns([1, 2])
                with col_det1:
                    foto_actual = info_prod.get("foto", "")
                    st.markdown(f'<img src="{foto_actual}" style="width:100%; height:75px; object-fit:cover; border-radius:6px; border:1px solid #d4af37;">', unsafe_allow_html=True)
                with col_det2:
                    st.markdown(f"**{info_prod['icono']} {prod}**")
                    st.caption(f"Sección: {cat_prod}")
                
                st.markdown("<hr style='margin:10px 0; border-color:#222538;'>", unsafe_allow_html=True)
                
                # Fila intermedia: Cajas de control para editar Precios y Stock
                col_inputs1, col_inputs2 = st.columns(2)
                with col_inputs1:
                    precio_edit = st.number_input(f"Precio (S/) de {prod}", min_value=0.1, value=float(info_prod["precio"]), step=0.1, key=f"edit_p_{prod}")
                with col_inputs2:
                    stock_edit = st.number_input(f"Stock de {prod}", min_value=0, value=int(info_prod["stock"]), step=1, key=f"edit_s_{prod}")
                
                # Cargador individual en caliente para cambiar la imagen del producto
                nueva_foto_individual = st.file_uploader(f"🔄 Cambiar foto de {prod}:", type=["jpg", "jpeg", "png"], key=f"foto_edit_{prod}")
                
                if nueva_foto_individual is not None:
                    bytes_foto_edit = nueva_foto_individual.getvalue()
                    encoded_foto_edit = base64.b64encode(bytes_foto_edit).decode()
                    st.session_state.menu_dinamico[prod]["foto"] = f"data:image/png;base64,{encoded_foto_edit}"
                    cambios_detectados = True
                
                # Fila inferior: Botón estructural de eliminación física
                if st.button("🗑️ ELIMINAR PRODUCTO", key=f"del_{prod}", use_container_width=True):
                    del st.session_state.menu_dinamico[prod]
                    guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                    st.warning(f"✔ Producto '{prod}' removido de la base de datos.")
                    st.rerun()
            
            # Verificación silenciosa de modificaciones numéricas para activar el guardado
            if precio_edit != info_prod["precio"] or stock_edit != info_prod["stock"]:
                st.session_state.menu_dinamico[prod]["precio"] = precio_edit
                st.session_state.menu_dinamico[prod]["stock"] = stock_edit
                st.session_state.menu_dinamico[prod]["disponible"] = stock_edit > 0
                cambios_detectados = True
                
        # Separador estético para evitar que los contenedores se peguen verticalmente
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    # 3. BOTÓN CONSOLIDADOR DE CAMBIOS GENERALES
    if cambios_detectados:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 CONFIRMAR Y GUARDAR CAMBIOS EN INVENTARIO", use_container_width=True, key="btn_guardar_cambios_admin"):
            guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
            st.success("✔ ¡Inventario y galería multimedia actualizados con éxito!")
            st.rerun()


else:
    # ============================================================================
    # 9. ENTORNO CLIENTE - PANTALLA 1: BIENVENIDA MULTIMEDIA PREMIUM
    # ============================================================================
    if st.session_state.pantalla_actual == "bienvenida":
        
        # --- PARCHE DE FUERZA BRUTA: Abrimos un contenedor HTML transparente global ---
        st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

        # 1. TÍTULOS PRINCIPALES CON MÁXIMA ALTURA SUPERIOR
        st.markdown("<h3 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px; margin-top: -10px; font-weight: bold; color: #d4af37;'>Bienvenidos al stock de productos disponibles y sus precios🔥</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # [!] SEGUNDO: INYECCIÓN MAESTRA DEL LOGOTIPO CON DESTELLO DE LUZ DIRECTO DE NAVEGADOR
        if URL_LOGO_PORTADA:
            st.markdown(f"""
                <style>
                .contenedor-logo-destello-fijo {{
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    width: 100% !important;
                    margin-top: -15px !important;
                    margin-bottom: 20px !important;
                }}
                .marco-escudo-brillante {{
                    position: relative !important;
                    width: 206px !important;
                    height: 206px !important;
                    border-radius: 50% !important;
                    overflow: hidden !important;
                    border: 3px solid #d4af37 !important;
                    box-shadow: 0px 0px 25px rgba(212, 175, 55, 0.45) !important;
                    background-color: #111424 !important;
                    
                    /* [!] BLINDAJE: Forzamos a que el logo central ignore cualquier rotación 3D y se quede de frente */
                    transform: none !important;
                    transform-style: flat !important;
                    perspective: none !important;
                }}
                .foto-logo-real {{
                    width: 100% !important;
                    height: 100% !important;
                    object-fit: cover !important;
                    /* Evitamos que la imagen herede giros o distorsiones */
                    transform: none !important;
                }}
                /* Capa física de luz real que cruza por encima obligatoriamente */
                .capa-luz-metalica {{
                    position: absolute !important;
                    top: 0 !important;
                    left: -100% !important;
                    width: 50% !important;
                    height: 100% !important;
                    background: linear-gradient(
                        90deg, 
                        rgba(255,255,255,0) 0%, 
                        rgba(255,255,255,0.6) 50%, 
                        rgba(255,255,255,0) 100%
                    ) !important;
                    transform: skewX(-25deg) !important;
                    animation: cruzarDestelloOro 3s ease-in-out infinite !important;
                }}
                @keyframes cruzarDestelloOro {{
                    0% {{ left: -100%; }}
                    30%, 100% {{ left: 150%; }}
                }}
                </style>
                <div class="contenedor-logo-destello-fijo">
                    <div class="marco-escudo-brillante">
                        <img src="{URL_LOGO_PORTADA}" class="foto-logo-real">
                        <div class="capa-luz-metalica"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)



        # 3. BOTÓN PRINCIPAL DE ACCIÓN DE LA BIENVENIDA
        cambiar_a_catalogo = st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_empezar_pedido_master")

        # 4. RENDERIZADO DE CUENTAS BANCARIAS CENTRALIZADAS TRANSPARENTES
        renderizar_informacion_pago()
            
        # 5. REDES SOCIALES: Footer estático
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class='social-footer'>
                <p style='margin-bottom: 10px; font-size: 14px; letter-spacing: 2px; color: #888; font-weight: bold;'>SÍGUENOS EN REDES SOCIALES</p>
                <a href='https://facebook.com' target='_blank' class='social-icon'>📘 Facebook</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://instagram.com' target='_blank' class='social-icon'>📸 Instagram</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://wa.me' target='_blank' class='social-icon'>🟢 WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # Cierre del contenedor maestro transparente

        if cambiar_a_catalogo:
            st.session_state.pantalla_actual = "catalogo"
            st.rerun()
    # ============================================================================
    # 10. ENTORNO CLIENTE - PANTALLA 2: CATÁLOGO DINÁMICO DE PRODUCTOS
    # ============================================================================
    elif st.session_state.pantalla_actual == "catalogo" and not st.session_state.pedido_guardado:
        st.markdown('<div class="catalogo-transparente-master">', unsafe_allow_html=True)
        st.markdown("\n<h2 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #aaa;'>Fecha y hora oficial de Perú (GMT-5): {fecha_actual}</h3>\n", unsafe_allow_html=True)
        
        # BARRA DE EXPLORACIÓN PREMIUM NETFLIX (DISEÑO AUTORESPONSIVO LAPTOP/MÓVIL)
        st.markdown("<div class='netflix-navbar-master'>", unsafe_allow_html=True)
        col_izq_tabs, col_der_search = st.columns([2.5, 1.5], gap="small")
        
        with col_izq_tabs:
            categoria_seleccionada = st.radio(
                "Categorías Navegación MASTER",
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
            busqueda = st.text_input(
                "🔍 Buscar", 
                placeholder="¿BUSQUE AQUÍ LO QUE NECESITA?", 
                label_visibility="collapsed", 
                key="search_bar_master_final_key"
            ).strip().lower()
            
        st.markdown("</div><br>", unsafe_allow_html=True)
        
        st.subheader(f"📍 SELECCIÓN DE {st.session_state.categoria_activa.upper()}")
        st.info("Ingrese las cantidades de los productos que desea llevar:")

        # FILTRADO INTEGRAL POR TEXTO Y CATEGORÍA SIMULTÁNEA
        productos_lista = list(st.session_state.menu_dinamico.keys())
        productos_filtrados = []

        for prod in productos_lista:
            if busqueda and busqueda not in prod.lower():
                continue
                
            info_prod = st.session_state.menu_dinamico[prod]
            cat_prod = info_prod.get("categoria", "Abarrotes")

            if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
                productos_filtrados.append(prod)

        # ARQUITECTURA EN COLUMNAS PARA ADAPTACIÓN MULTIDISPOSITIVO (MÓVIL/LAPTOP)
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
                    
                    # ALERTA DE STOCK CRÍTICO NEÓN CON EFECTO PARPADEO
                    if stock_actual <= 3:
                        st.markdown(f"<p class='mini-stock-alerta'>🔥 ¡Solo quedan {stock_actual} unidades! 🔥</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p class='mini-stock-normal'>📦 Stock disponible: {stock_actual} und.</p>", unsafe_allow_html=True)
                    
                    cantidades_ingresadas[prod] = st.number_input(
                        f"Cantidad de {prod}:", min_value=0, max_value=int(stock_actual), step=1, key=f"cat_{prod}", label_visibility="collapsed"
                    )
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
    # 11. ENTORNO CLIENTE - PANTALLA 3: SIMULACIÓN DE PEDIDO Y DATOS DE TRANSFERENCIA
    # ============================================================================
    else:
        st.markdown('<div class="carrito-transparente-master">', unsafe_allow_html=True)
        st.html("<div style='height: 15px;'></div>")
        st.subheader("📦 LISTA DE PRODUCTOS SELECCIONADOS")
        
        # Muestra la lista de productos elegidos manteniendo el estilo visual premium
        texto_proforma_whatsapp = "Hola Familia Guadalupe, deseo coordinar mi pedido desde el catálogo web:\n\n"
        for item in st.session_state.carrito:
            icono_p = st.session_state.menu_dinamico[item['producto']]['icono']
            st.markdown(f"""
                <div style="background-color: #1e1e24; border-left: 4px solid #f39c12; padding: 12px 16px; border-radius: 8px; color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);">
                    {icono_p} {item['producto']} x{item['cantidad']} &nbsp;|&nbsp; Subtotal: S/{item['subtotal']:.2f}
                </div>
            """, unsafe_allow_html=True)
            # Acumula la lista formateada para el mensaje directo de WhatsApp
            texto_proforma_whatsapp += f"• {icono_p} {item['producto']} x{item['cantidad']} (Subtotal: S/{item['subtotal']:.2f})\n"
        
        st.markdown("---")
        
        # Muestra el total acumulado en el cuadro verde brillante calibrado en CSS
        st.metric(label="Monto Total a Procesar", value=f"S/{st.session_state.total_acumulado:.2f}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Cierre del cuerpo del mensaje automatizado para concretar la venta
        texto_proforma_whatsapp += f"\n💰 *Monto Total Neto a Procesar: S/{st.session_state.total_acumulado:.2f}*\n📌 Generado el: {fecha_actual}\n\nQuedo a la espera para coordinar el despacho."
        texto_codificado_url = base64.b64encode(texto_proforma_whatsapp.encode('utf-8')).decode('utf-8')
        # Alternativa cruda limpia para compatibilidad directa con API de WhatsApp
        import urllib.parse
        mensaje_parseado_url = urllib.parse.quote(texto_proforma_whatsapp)

        # Renderizado unificado y consistente de cuentas oficiales (Previene datos cruzados)
        renderizar_informacion_pago(total_contexto=st.session_state.total_acumulado)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- [!] REQUERIMIENTO: NOTA ESTRATÉGICA DE RECOMENDACIÓN DE CAPTURA DE PANTALLA ---
        st.markdown("""
            <div style="background-color: rgba(212, 175, 55, 0.1); border: 2px dashed #d4af37; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 25px; box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.15);">
                <p style="color: #ffffff; font-size: 14.5px; font-weight: bold; margin: 0; line-height: 1.5;">
                    ⚠️ Recomendación: Tómale una captura de pantalla a esta lista para que no olvides los productos que quieres comprar antes de realizar tu transferencia bancaria.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ============================================================================
        # 12. CONFIRMACIÓN SIMULADA, DESPACHO WHATSAPP Y ENLACE DE CIERRE DE VENTA
        # ============================================================================
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💾 CONFIRMAR SIMULACIÓN EN SESIÓN", use_container_width=True):
                st.success("✔ Simulación procesada correctamente. Los productos han sido reservados en tu sesión.")
                st.balloons()
                
                # Descuenta temporalmente el stock disponible en el archivo persistente JSON
                for item in st.session_state.carrito:
                    prod_comprado = item["producto"]
                    cant_comprada = item["cantidad"]
                    stock_previo = st.session_state.menu_dinamico[prod_comprado].get("stock", 0)
                    st.session_state.menu_dinamico[prod_comprado]["stock"] = max(0, stock_previo - cant_comprada)
                    st.session_state.menu_dinamico[prod_comprado]["disponible"] = st.session_state.menu_dinamico[prod_comprado]["stock"] > 0
                
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.session_state.pedido_guardado = True
                
                # Pausa controlada para disfrutar la animación de los globos sin interrupción prematura
                time.sleep(2.5)
                st.rerun()
                
        with col_c2:
            # Botón maestro de cierre de venta: Envia la orden masticada y lista al WhatsApp del local
            st.link_button(
                "🟢 ENVIAR PEDIDO POR WHATSAPP",
                f"https://wa.me{mensaje_parseado_url}",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        # Botón estructural para regresar a la pantalla de bienvenida e iniciar un flujo nuevo
        if st.session_state.pedido_guardado or st.session_state.total_acumulado > 0:
            if st.button("🔄 Crear una nueva orden / Volver a Explorar", use_container_width=True, key="btn_nueva_orden_final"):
                st.session_state.carrito = []
                st.session_state.total_acumulado = 0.0
                st.session_state.pedido_guardado = False
                st.session_state.pantalla_actual = "bienvenida"
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
