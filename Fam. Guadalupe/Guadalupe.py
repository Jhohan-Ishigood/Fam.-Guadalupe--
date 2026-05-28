# ============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA, IMPORTACIONES Y RUTAS DE CONTROL
# ============================================================================
import streamlit as st
from datetime import datetime, timedelta, timezone
import os
import json
import base64

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
ruta_foto_fisica = os.path.join(BASE_DIR, "Foto del establecimiento.png")
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
    categorias_defecto = ["Todos", "Ferretería & Electricidad", "Parlantes", "Celulares", "Útiles Escolares"]
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
fecha_actual = datetime.now(zona_peru).strftime("%d/%m/%Y %H:%M:%S")


# ============================================================================
# 4. INYECCIÓN EXTERNA DE MARCA Y REGLAS DE DISEÑO DE AUTORÍA
# ============================================================================
if os.path.exists(RUTA_CSS):
    with open(RUTA_CSS, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inyección limpia del sello de creador adaptado al flujo estructural
st.markdown("<div class='sello-creador'>Página desarrollada por: Jhohan Guadalupe</div>", unsafe_allow_html=True)


# ============================================================================
# 4.5 FUNCIONES AUXILIARES INTERFACES COMPARTIDAS (ANTI-REDUNDANCIA)
# ============================================================================
def renderizar_informacion_pago(total_contexto=None):
    """Renderiza los expanders oficiales de pago centralizados para evitar código duplicado."""
    st.markdown("### 💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO")
    st.caption("Selecciona el método de tu preferencia haciendo clic para desplegar los datos correspondientes:")

    # --- PORTADA DESPLEGABLE 1: DATOS DE CUENTA BANCARIA ---
    with st.expander("📐 VER N° DE CUENTA OFICIAL", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #2980b9; margin-bottom: 10px;">
                <p style="color: #2980b9; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🏦 BANCO DE LA NACION / BNP</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número de Cuenta:</b> 570-98421345-0-88</p>
                <p style="color: #aaaaaa; margin: 0; font-size: 14px;"><b>Titular del Negocio:</b> Segundo Melquiades Guadalupe Sanchez</p>
            </div>
        """, unsafe_allow_html=True)

    # --- PORTADA DESPLEGABLE 2: PROCESAMIENTO ELECTRÓNICO CON YAPE Y QR ---
    with st.expander("📱 VER NÚMERO Y QR DE YAPE", expanded=False):
        if total_contexto is not None:
            st.markdown(f"**Monto exacto a transferir:** S/{total_contexto:.2f}")
            
        src_qr = URL_QR_YAPE if URL_QR_YAPE else "data:image/svg+xml;utf8,<svg xmlns='http://w3.org' width='100' height='100' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>"
        
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 15px auto; max-width: 450px; background-color: #1e1e24; padding: 20px; border-radius: 16px; border: 2px solid #8e44ad; text-align: center;">
                <p style="color: #aaaaaa; font-size: 13px; margin-bottom: 12px; font-weight: bold;">Escanee con la cámara del celular si desea pagar:</p>
                <img src="{src_qr}" style="width: 240px; height: 240px; object-fit: contain; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;" />
                <span style="color: #8e44ad; font-size: 14px; font-weight: bold; letter-spacing: 1px;">🟣 NÚMERO ASOCIADO: 950 239 350</span>
            </div>
        """, unsafe_allow_html=True)

    # --- PORTADA DESPLEGABLE 3: TELEFONO DE CONTACTO ---
    with st.expander("📞 VER TELÉFONO DE CONTACTO DIRECTO", expanded=False):
        st.markdown("""
            <div style="background-color: #1c1c1c; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <p style="color: #27ae60; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🟢 WHATSAPP CORPORATIVO</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número Celular:</b> +51 950 239 350</p>
                <p style="color: #aaaaaa; margin: 0; font-size: 13px;">Use este número para coordinar directamente o reportar consultas.</p>
            </div>
        """, unsafe_allow_html=True)
# ============================================================================
# 5. BARRA LATERAL (SIDEBAR POS): GESTIÓN INTERNA Y AUTENTICACIÓN
# ============================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #f39c12;'>Catálogo de Productos</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #aaa;'>Artículos de calidad a buen precio.</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### ⚙️ SOLO PARA ADMINISTRADORES")
if st.sidebar.button("INGRESAR COMO ADMINISTRADOR🤵‍♂️", use_container_width=True, key="btn_toggle_admin_login"):
    st.session_state.mostrar_login_admin = not st.session_state.mostrar_login_admin

# Inicialización limpia de variables de control de acceso
usuario_input = ""
clave_input = ""
es_admin = False

# Renderizado condicional del bloque de autenticación administrativa
if st.session_state.mostrar_login_admin:
    with st.sidebar.container():
        usuario_input = st.text_input("Nombre de Usuario:", key="user_login").strip()
        clave_input = st.text_input("Contraseña:", type="password", key="pass_login").strip()

# Validación de credenciales blindada (Usa Streamlit Secrets o respaldo local)
USER_PROD = st.secrets.get("admin_user", "Los Guadalupe")
PASS_PROD = st.secrets.get("admin_password", "18987915")

es_admin = (usuario_input == USER_PROD and clave_input == PASS_PROD)

# Retroalimentación interactiva del estado del usuario
if es_admin:
    st.sidebar.success("✔ Modo Administrador Activo")
elif usuario_input or clave_input:
    st.sidebar.error("❌ Credenciales incorrectas")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 🕒 HORARIO DE ATENCIÓN")
st.sidebar.caption("Lunes a Domingo: 8:00 AM - 11:00 PM")

st.sidebar.markdown("#### 📍 NUESTRA UBICACIÓN")
st.sidebar.caption("Av. Principal El Gran Búfalo 742, Trujillo, Perú")

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📞 ¿NECESITAS AYUDA?")

# Enlace de soporte por WhatsApp optimizado con el número y prefijo del catálogo
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
        
        col_new1, col_new2, col_new3, col_new4 = st.columns([1, 1, 1, 1])
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
    # 8. PANEL DE CONTROL DE ADMINISTRACIÓN - FILTRADO INTELIGENTE Y EDICIÓN (REFINADO)
    # ============================================================================
    st.markdown("### 📝 GESTIÓN DE PRECIOS, STOCK Y ELIMINACIÓN")
    st.caption(f"Filtro actual: **{st.session_state.categoria_activa}**")
    productos_lista = list(st.session_state.menu_dinamico.keys())
    cambios_detectados = False

    # Renderizado y procesamiento de edición en bloque para el administrador
    for prod in productos_lista:
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Ferretería & Electricidad")
        
        # Filtra correctamente para que el administrador gestione el catálogo según la pestaña
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
            with st.container(border=True):
                col_e1, col_e2, col_e3, col_e4 = st.columns([2, 1, 1, 1])
                with col_e1:
                    st.markdown(f"**{info_prod['icono']} {prod}** ({cat_prod})")
                with col_e2:
                    precio_edit = st.number_input(f"Precio (S/) de {prod}", min_value=0.1, value=float(info_prod["precio"]), step=0.1, key=f"edit_p_{prod}")
                with col_e3:
                    stock_edit = st.number_input(f"Stock de {prod}", min_value=0, value=int(info_prod["stock"]), step=1, key=f"edit_s_{prod}")
                with col_e4:
                    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ ELIMINAR", key=f"del_{prod}", use_container_width=True):
                        del st.session_state.menu_dinamico[prod]
                        guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                        st.warning(f"Producto '{prod}' removido del sistema.")
                        st.rerun()
                
                # Evalúa de forma silenciosa si existen cambios en caliente para guardar
                if precio_edit != info_prod["precio"] or stock_edit != info_prod["stock"]:
                    st.session_state.menu_dinamico[prod]["precio"] = precio_edit
                    st.session_state.menu_dinamico[prod]["stock"] = stock_edit
                    st.session_state.menu_dinamico[prod]["disponible"] = stock_edit > 0
                    cambios_detectados = True

    if cambios_detectados:
        if st.button("💾 GUARDAR CAMBIOS DE PRECIO / STOCK", use_container_width=True, key="btn_guardar_cambios_admin"):
            guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
            st.success("✔ ¡Cambios de inventario guardados exitosamente!")
            st.rerun()

else:
    # ============================================================================
    # 9. ENTORNO CLIENTE - PANTALLA 1: BIENVENIDA MULTIMEDIA PREMIUM
    # ============================================================================
    if st.session_state.pantalla_actual == "bienvenida":
        # Aplicamos el fondo premium en la app
        if URL_BANNER_LOCAL:
            st.markdown(f"""
                <style>
                .stApp {{
                    background-image: linear-gradient(rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0.82)), url("{URL_BANNER_LOCAL}");
                    background-size: cover !important;
                    background-position: center !important;
                    background-repeat: no-repeat !important;
                    background-attachment: fixed !important;
                }}
                </style>
            """, unsafe_allow_html=True)

        # --- PARCHE DE FUERZA BRUTA: Abrimos un contenedor HTML transparente ---
        st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

        # [!] PRIMERO: TÍTULOS PRINCIPALES (QUEDAN DEBAJO DEL AUTOR VERDE NATIIVO Y ARRIBA DEL LOGO)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 class='titulo-principal'>BIENVENIDOS AL CATÁLOGO DE PRODUCTOS DISPONIBLES</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # [!] SEGUNDO: INYECCIÓN MAESTRA DEL LOGOTIPO (AHORA QUEDA ABAJO DEL TÍTULO)
        if URL_LOGO_PORTADA:
            st.markdown(f'<div class="contenedor-logo-portada"><img src="{URL_LOGO_PORTADA}" class="logo-portada-circular"></div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="contenedor-logo-portada">
                    <div class="logo-portada-circular" style="display:flex; align-items:center; justify-content:center; background-color:#111424;">
                        <span style="color:#d4af37; font-size:12px; font-weight:bold; text-align:center;">CARGANDO LOGO...</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br><p style='text-align: left; font-size: 20px; margin-top: -54px; font-weight: bold; color: #d4af37;'>Bienvenidos al stock de productos disponibles y sus precios🔥</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 1. BOTÓN PRINCIPAL DE ACCIÓN
        cambiar_a_catalogo = st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_empezar_pedido_master")

        # 2. DESPLEGABLES CENTRALIZADOS (Muestra la info de pago sin duplicar código en el archivo)
        renderizar_informacion_pago()
            
        # 3. REDES SOCIALES: Footer estático
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div class='social-footer'>
                <p style='margin-bottom: 10px; font-size: 14px; letter-spacing: 2px; color: #888; font-weight: bold;'>SÍGUENOS EN REDES SOCIALES</p>
                <a href='https://facebook.com' target='_blank' class='social-icon'>📘 Facebook</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://instagram.com' target='_blank' class='social-icon'>📸 Instagram</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <a href='https://wa.me' target='_blank' class='social-icon'>🟢 WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

        if cambiar_a_catalogo:
            st.session_state.pantalla_actual = "catalogo"
            st.rerun()
    # ============================================================================
    # 10. ENTORNO CLIENTE - PANTALLA 2: CATÁLOGO DINÁMICO DE PRODUCTOS
    # ============================================================================
    elif st.session_state.pantalla_actual == "catalogo" and not st.session_state.pedido_guardado:
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
            cat_prod = info_prod.get("categoria", "Ferretería & Electricidad")

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
                    st.markdown(f"""<img src="{url_imagen_plato}" style="width:100%; height:200px; object-fit:cover; border-radius:12px 12px 0px 0px; box-shadow: 0px 4px 12px rgba(0,0,0,0.6); display:block; margin:0; padding:0;">""", unsafe_allow_html=True)
                    
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
    # ============================================================================
    # 11. ENTORNO CLIENTE - PANTALLA 3: SIMULACIÓN DE PEDIDO Y DATOS DE TRANSFERENCIA
    # ============================================================================
    else:
        st.html("<div style='height: 15px;'></div>")
        st.subheader("📦 LISTA DE PRODUCTOS SELECCIONADOS")
        
        # Muestra la lista de productos elegidos manteniendo el estilo visual premium
        for item in st.session_state.carrito:
            icono_p = st.session_state.menu_dinamico[item['producto']]['icono']
            st.markdown(f"""
                <div style="background-color: #1e1e24; border-left: 4px solid #f39c12; padding: 12px 16px; border-radius: 8px; color: #ffffff; font-size: 16px; font-weight: 700; margin-bottom: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);">
                    {icono_p} {item['producto']} x{item['cantidad']} &nbsp;|&nbsp; Subtotal: S/{item['subtotal']:.2f}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Muestra el total acumulado en el cuadro verde brillante calibrado en CSS
        st.metric(label="Monto Total a Procesar", value=f"S/{st.session_state.total_acumulado:.2f}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Renderizado unificado y consistente de cuentas oficiales (Previene datos cruzados)
        renderizar_informacion_pago(total_contexto=st.session_state.total_acumulado)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # ============================================================================
        # 12. CONFIRMACIÓN SIMULADA Y ACTUALIZACIÓN TEMPORAL DE STOCK
        # ============================================================================
        if st.button("💾 CONFIRMAR SIMULACIÓN DE PEDIDO", use_container_width=True):
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
            
            # Pequeña pausa de cortesía para que el usuario disfrute la animación de los globos antes de recargar
            import time
            time.sleep(2.5)
            st.rerun()

        # Botón estructural para regresar a la pantalla de bienvenida e iniciar un flujo nuevo
        if st.session_state.pedido_guardado:
            if st.button("🔄 Crear una nueva orden / Volver a Explorar", use_container_width=True, key="btn_nueva_orden_final"):
                st.session_state.carrito = []
                st.session_state.total_acumulado = 0.0
                st.session_state.pedido_guardado = False
                st.session_state.pantalla_actual = "bienvenida"
                st.rerun()
