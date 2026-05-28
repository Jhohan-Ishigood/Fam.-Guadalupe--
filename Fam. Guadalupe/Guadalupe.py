# ============================================================================
# CATÁLOGO PREMIUM FAM. GUADALUPE v3.0 - INGENIERÍA EN PYTHON/STREAMLIT
# Rediseño Máster: Arquitectura Adaptativa (PC 4 Columnas / Celular 2 Columnas)
# Sistema de Fondo de Video en Bucle Infinito y Bienvenida Multi-Capa POS
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

# Determinación física de rutas en el servidor local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CSS = os.path.join(BASE_DIR, "estilos.css")
RUTA_JSON_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_JSON_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# ============================================================================
# 2. MOTOR DE PRECARGA MULTIMEDIA (OPTIMIZADO PARA CACHÉ BINARIA)
# ============================================================================
@st.cache_data(show_spinner=False)
def cargar_recurso_base64(ruta_archivo, tipo_recurso="imagen"):
    """Lee un archivo físico (imagen/video) y lo convierte en URI Base64"""
    if os.path.exists(ruta_archivo):
        try:
            mime_type, _ = mimetypes.guess_type(ruta_archivo)
            if not mime_type:
                if tipo_recurso == "video":
                    mime_type = "video/mp4"
                else:
                    mime_type = "image/png"
            with open(ruta_archivo, "rb") as archivo:
                encoded = base64.b64encode(archivo.read()).decode()
                return f"data:{mime_type};base64,{encoded}"
        except Exception:
            return ""
    return ""
def guardar_json(ruta, datos):
    """Escritura segura y atómica de datos en formato JSON"""
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error crítico al persistir datos: {e}")

def cargar_menu_desde_archivo():
    """Carga el inventario desde JSON o inicializa la plantilla por defecto"""
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
    """Carga la lista oficial de secciones desde el almacenamiento JSON"""
    categorias_defecto = ["Todos", "Abarrotes", "Ferretería & Electricidad", "Tecnología", "Línea Ecuestre", "Útiles Escolares"]
    if os.path.exists(RUTA_JSON_CATEGORIAS):
        try:
            with open(RUTA_JSON_CATEGORIAS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, Exception):
            return categorias_defecto
    return categorias_defecto

# ============================================================================
# 3. INICIALIZACIÓN DE VARIABLES DE SESIÓN (ESTADOS DEL SISTEMA)
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

# ============================================================================
# 4. CONTROL HORARIO Y ENLACES DIRECTOS MULTIMEDIA (OPTIMIZADO ANTI-SATURACIÓN)
# ============================================================================
zona_peru = timezone(timedelta(hours=-5))
ahora_peru = datetime.now(zona_peru)
fecha_actual = ahora_peru.strftime("%d/%m/%Y %H:%M:%S")

# Las imágenes locales se quedan igual en Base64 porque no pesan casi nada
URL_FOTO_TIENDA = cargar_recurso_base64(os.path.join(BASE_DIR, "establecimiento.png"), "imagen")
URL_QR_YAPE = cargar_recurso_base64(os.path.join(BASE_DIR, "miqr1.png"), "imagen")

# Enlaces directos en la nube para que el servidor de Streamlit no se sature
URL_VIDEO_PC = "https://githubusercontent.com"
URL_VIDEO_MOVIL = "https://githubusercontent.com"
URL_VIDEO_LOGO = "https://githubusercontent.com"


if os.path.exists(RUTA_CSS):
    try:
        with open(RUTA_CSS, "r", encoding="utf-8") as f:
            custom_css = f.read()
            st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    except Exception:
        pass

# ============================================================================
# 5. INYECCIÓN DEL MOTOR DE FONDO DE VIDEO Y ELEMENTOS DE NAVEGACIÓN CAPA-Z
# ============================================================================
st.markdown(f"""
    <!-- Bloque de Reproducción Multimedia en Bucle Infinito de Fondo -->
    <div class="video-background-container pc-only">
        <video autoplay loop muted playsinline class="video-fondo-maestro">
            <source src="{URL_VIDEO_PC}" type="video/mp4">
        </video>
    </div>

    <div class="video-background-container movil-only">
        <video autoplay loop muted playsinline class="video-fondo-maestro">
            <source src="{URL_VIDEO_MOVIL}" type="video/mp4">
        </video>
    </div>

    <!-- Sello de Identidad de Marca: Mini-Logo Flotante con Rotación Coin-3D -->
    <div class="mini-logo-flotante-master">
        <video autoplay loop muted playsinline class="mini-logo-imagen-circular">
            <source src="{URL_VIDEO_LOGO}" type="video/mp4">
        </video>
    </div>
""", unsafe_allow_html=True)

# ============================================================================
# 6. FUNCIÓN CENTRALIZADA DE PASARELA DE COMPROBACIÓN DE PAGO (POS)
# ============================================================================
def renderizar_informacion_pago(total_contexto=None):
    """Renderiza información oficial de pago con acordeones responsivos de alta gama"""
    st.markdown("### 💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO")
    st.caption("Selecciona tu método de pago haciendo clic para desplegar los datos bancarios:")

    with st.expander("🏦 VER N° DE CUENTA DEL BANCO DE LA NACIÓN", expanded=False):
        st.markdown("""
            <div style="background-color: #111424; padding: 15px; border-radius: 8px; border-left: 4px solid #2980b9; margin-bottom: 5px;">
                <p style="color: #2980b9; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🏦 BANCO DE LA NACIÓN / BNP</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número de Cuenta:</b> 04-762-855629 </p>
                <hr style="border-color: #222538; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 14px;"><b>Titular:</b> Segundo Melquiades Guadalupe Sanchez</p>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("🟣 VER NÚMERO Y QR DE YAPE", expanded=False):
        if total_contexto is not None:
            st.markdown(f"<p style='color:#ffffff; font-weight:bold; font-size:15px; margin-bottom:10px; text-align:center;'>Monto exacto a transferir: <span style='color:#2ecc71;'>S/{total_contexto:.2f}</span></p>", unsafe_allow_html=True)        
        src_qr = URL_QR_YAPE if URL_QR_YAPE else ""
        st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 5px auto; max-width: 450px; background-color: #1e1e24; padding: 20px; border-radius: 16px; border: 2px solid #8e44ad; text-align: center;">
                <p style="color: #aaaaaa; font-size: 13px; margin-bottom: 12px; font-weight: bold;">Escanee con la cámara de su celular para pagar:</p>
                <img src="{src_qr}" style="width: 240px; height: 240px; object-fit: contain; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); margin-bottom: 12px;" />
                <span style="color: #8e44ad; font-size: 15px; font-weight: 900; letter-spacing: 1px;">🟣 +51 950 239 350</span>
                <p style="color:#888; font-size:12px; margin-top:5px; margin-bottom:0;">Titular: Jhohan Antoni Guadalupe Cusquipoma</p>
            </div>
        """, unsafe_allow_html=True)
    with st.expander("📞 VER TELÉFONO DE CONTACTO DIRECTO", expanded=False):
        st.markdown("""
            <div style="background-color: #111424; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60;">
                <p style="color: #27ae60; font-weight: bold; margin: 0 0 5px 0; font-size: 16px;">🟢 WHATSAPP Y LLAMADAS DIRECTAS</p>
                <p style="color: #ffffff; margin: 0 0 3px 0; font-size: 14px;"><b>Número Celular:</b> +51 950 239 350</p>
                <hr style="border-color: #222538; margin: 10px 0;">
                <p style="color: #aaaaaa; margin: 0; font-size: 13px;">Use este canal directo para coordinar despachos inmediatos o resolver consultas.</p>
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# 7. CONTROL DE LA BARRA LATERAL (SIDEBAR DE CONTROL ADMISTRATIVO)
# ============================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #f39c12;'>Catálogo FAM. GUADALUPE</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #aaa;'>Productos de calidad a buen precio.</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### ⚙️ GESTIÓN DEL SISTEMA")

# Lógica del panel de inicio de sesión de administración
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

# Automatización de la disponibilidad del radar según la hora de Perú
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
st.sidebar.link_button("💬 Chatear con Soporte", "https://wa.me", use_container_width=True, key="link_whatsapp_soporte")

# ============================================================================
# 8. PANEL DE CONTROL EXCLUSIVO DEL ADMINISTRADOR (VISTA INTERNA)
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

    # Configuración avanzada de secciones / categorías
    with st.expander("📁 ⚙️ CONFIGURACIÓN DE SECCIONES", expanded=False):
        st.caption("Añada nuevas pestañas o elimine secciones existentes en caliente")
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
    # Sección para agregar un nuevo producto al inventario
    with st.expander("➕ 🛠️ AÑADIR NUEVO PRODUCTO", expanded=False):
        st.caption("Complete los datos requeridos para registrar un producto nuevo:")
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
                    st.error("⚠️ El producto ya se encuentra registrado.")

    # ============================================================================
    # GESTIÓN EN CALIENTE DE PRODUCTOS (EDICIÓN Y ELIMINACIÓN)
    # ============================================================================
    st.markdown("### 📝 GESTIÓN DE PRECIOS, STOCK Y ELIMINACIÓN")
    st.caption(f"Filtro por sección activo: **{st.session_state.categoria_activa}**")
    
    productos_lista = list(st.session_state.menu_dinamico.keys())
    cambios_detectados = False

    productos_visibles_admin = []
    for prod in productos_lista:
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")
        if st.session_state.categoria_activa == "Todos" or st.session_state.categoria_activa == cat_prod:
            productos_visibles_admin.append(prod)

    # Renderizado estricto del grid de administración en 2 columnas fijas
    st.markdown('<div class="admin-grid-2col">', unsafe_allow_html=True)

    for pos, prod in enumerate(productos_visibles_admin):
        info_prod = st.session_state.menu_dinamico[prod]
        cat_prod = info_prod.get("categoria", "Abarrotes")

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

            nueva_foto_individual = st.file_uploader(f"🔄 Cambiar Foto {prod}:", type=["jpg", "jpeg", "png"], key=f"foto_edit_{prod}")
            if nueva_foto_individual is not None:
                bytes_foto_edit = nueva_foto_individual.getvalue()
                mime_type_edit = nueva_foto_individual.type or "image/png"
                encoded_foto_edit = base64.b64encode(bytes_foto_edit).decode()
                st.session_state.menu_dinamico[prod]["foto"] = f"data:{mime_type_edit};base64,{encoded_foto_edit}"
                cambios_detectados = True

            st.markdown("<div style='height:5px;'></div>", unsafe_allow_html=True)

            if st.button("🗑️ ELIMINAR ARTÍCULO", key=f"del_{prod}", use_container_width=True):
                del st.session_state.menu_dinamico[prod]
                guardar_json(RUTA_JSON_MENU, st.session_state.menu_dinamico)
                st.warning(f"✔ '{prod}' removido correctamente")
                st.rerun()

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
            st.success("✔ ¡Inventario actualizado en el servidor!")
            st.rerun()
# ============================================================================
# 9. ENTORNO CLIENTE - PANTALLA 1: BIENVENIDA MULTI-CAPA ADAPTATIVA
# ============================================================================
else:
    if st.session_state.pantalla_actual == "bienvenida":
        st.markdown('<div class="bienvenida-transparente-master">', unsafe_allow_html=True)

        st.markdown("<h3 class='titulo-principal'>CATÁLOGO DE PRODUCTOS DISPONIBLES</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px; margin-top: -10px; font-weight: bold; color: #d4af37;'>Bienvenidos al stock de productos disponibles y sus precios 🔥</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Inyección Maestra de la Tarjeta Central Estilo Yape con Elementos Alineados
        st.markdown(f"""
            <div class="tarjeta-bienvenida-yape">
                <div class="contenedor-tienda-estatica">
                    <img src="{URL_FOTO_TIENDA}" class="foto-tienda-yape" alt="Fachada Familiar Guadalupe">
                </div>
                <div class="contenedor-logo-por-debajo">
                    <video autoplay loop muted playsinline class="video-logo-yape-base">
                        <source src="{URL_VIDEO_LOGO}" type="video/mp4">
                    </video>
                </div>
            </div>
            <br>
        """, unsafe_allow_html=True)

        st.markdown('<div class="btn-luz-escaner">', unsafe_allow_html=True)
        cambiar_a_catalogo = st.button("EMPEZAR A NAVEGAR EN LOS PRODUCTOS DISPONIBLES", use_container_width=True, key="btn_empezar_pedido_master")
        st.markdown('</div>', unsafe_allow_html=True)

        # Renderizar la información de cuentas oficiales debajo del botón de ingreso
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
    # 10. ENTORNO CLIENTE - PANTALLA 2: CATÁLOGO DE PRODUCTOS (GRID DE PRODUCTOS)
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

        # Inyección del contenedor flexible que delega las columnas (4 en PC / 2 en Móvil) al CSS
        st.markdown('<div class="grid-productos-responsivo">', unsafe_allow_html=True)
        cantidades_ingresadas = {}
        
        for i in range(len(productos_filtrados)):
            prod = productos_filtrados[i]
            info = st.session_state.menu_dinamico[prod]
            
            stock_actual = info.get("stock", 0)
            esta_disponible = info["disponible"] and stock_actual > 0
            
            # Cada tarjeta se inyecta en una caja div aislada que el CSS ordenará automáticamente
            st.markdown(f'<div class="tarjeta-producto-individual">', unsafe_allow_html=True)
            with st.container(border=True):
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
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True) # Cierre del div grid-productos-responsivo
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
    # 11. ENTORNO CLIENTE - PANTALLA 3: CARRITO DE COMPRAS Y DESPACHO WHATSAPP
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
        url_whatsapp = f"https://whatsapp.com{mensaje_parseado_url}"

        # Renderizar la información física de pagos vinculando el total acumulado
        renderizar_informacion_pago(total_contexto=st.session_state.total_acumulado)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # NOTA ESTRATÉGICA DE CAPTURA VISUAL
        st.markdown("""
            <div class='nota-captura-estrategica'>
                <p>⚠️ Recomendación: Tómale una captura de pantalla a esta lista para que no olvides los productos que quieres comprar antes de realizar tu transferencia bancaria.</p>
            </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("💾 CONFIRMAR SIMULACIÓN", use_container_width=True):
                # Forzar bandera de seguridad antes de persistir cambios
                st.session_state.pedido_guardado = True

                # Descuento atómico de stock local por ítem comprado
                for item in st.session_state.carrito:
                    prod_comprado = item["producto"]
                    cant_comprada = item["cantidad"]
                    stock_previo = st.session_state.menu_dinamico[prod_comprado].get("stock", 0)
                    st.session_state.menu_dinamico[prod_comprado]["stock"] = max(0, stock_previo - cant_comprada)
                    st.session_state.menu_dinamico[prod_comprado]["disponible"] = st.session_state.menu_dinamico[prod_comprado]["stock"] > 0

                # Persistencia atómica definitiva en archivo local JSON
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
