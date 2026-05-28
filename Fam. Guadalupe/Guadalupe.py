import streamlit as st
import os
import json
import base64

# ==============================================================================
# 1. CONFIGURACIÓN DINÁMICA DE RUTAS (Compatibilidad Local y Producción)
# ==============================================================================
# Detecta automáticamente la raíz del proyecto sin importar el sistema operativo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mapeo unificado de archivos físicos de configuración y estilos
RUTA_CSS = os.path.join(BASE_DIR, "estilos.css")
RUTA_JSON_MENU = os.path.join(BASE_DIR, "menu_config.json")
RUTA_JSON_CATEGORIAS = os.path.join(BASE_DIR, "categorias_config.json")

# Ubicaciones de los archivos de imágenes locales
RUTA_FOTO_ESTABLECIMIENTO = os.path.join(BASE_DIR, "Foto del establecimiento.png")
RUTA_LOGO_OFICIAL = os.path.join(BASE_DIR, "tu_imagen_del_logo.png")  # Cambia esto por el nombre real de tu archivo de logo si varía

# ==============================================================================
# 2. FUNCIONES DE OPTIMIZACIÓN DE MEDIOS (Incrustación Segura Base64)
# ==============================================================================
@st.cache_data(show_spinner=False)
def optimizar_y_cargar_base64(ruta_archivo):
    """
    Lee una imagen local, la comprime en memoria y la transforma en código Base64.
    Esto garantiza que se muestre en celulares y PCs sin depender del sistema de archivos.
    """
    try:
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "rb") as archivo:
                datos = archivo.read()
            codificado = base64.b64encode(datos).decode()
            # Detecta la extensión automáticamente para generar la cabecera correcta
            extension = ruta_archivo.split(".")[-1].lower()
            return f"data:image/{extension};base64,{codificado}"
        return ""
    except Exception:
        return ""

# Procesamiento de imágenes a cadenas de texto web web-ready
URL_BANNER_LOCAL = optimizar_y_cargar_base64(RUTA_FOTO_ESTABLECIMIENTO)
URL_LOGO_LOCAL = optimizar_y_cargar_base64(RUTA_LOGO_OFICIAL)
# ==============================================================================
# 3. CONFIGURACIÓN GLOBAL DE LA PÁGINA (Layout y Responsive)
# ==============================================================================
st.set_page_config(
    page_title="Catálogo de Productos - Almacén Guadalupe",
    page_icon="🛍️",
    layout="centered",  # Centrado para mantener una estructura limpia y elegante
    initial_sidebar_state="collapsed"  # Mantiene el menú lateral oculto en celulares para ganar espacio
)

# ==============================================================================
# 4. INYECCIÓN AUTOMÁTICA DE ESTILOS CSS
# ==============================================================================
def cargar_estilos_custom(ruta_css):
    """
    Lee el archivo estilos.css e inyecta las reglas en el HTML de la aplicación.
    Incluye un respaldo visual en caso de que el archivo CSS local no sea accesible.
    """
    if os.path.exists(ruta_css):
        with open(ruta_css, "r", encoding="utf-8") as f:
            css_contenido = f.read()
        st.markdown(f"<style>{css_contenido}</style>", unsafe_allow_html=True)
    else:
        # Respaldo de seguridad: Estilos base responsivos incrustados directamente
        st.markdown(
            """
            <style>
            .header-container { display: flex; flex-direction: column; align-items: center; text-align: center; width: 100%; padding: 10px; }
            .autor-text { font-size: clamp(0.7rem, 2vw, 1rem); margin-bottom: 20px; color: #4CAF50; font-weight: bold; letter-spacing: 1px; }
            .logo-title-wrapper { position: relative; display: flex; flex-direction: column; align-items: center; width: 100%; margin-bottom: 30px; }
            .logo-img { width: clamp(150px, 40vw, 260px); height: auto; z-index: 1; }
            .titulo-catalogo { position: absolute; bottom: -15px; z-index: 2; font-size: clamp(1.1rem, 4vw, 2.2rem); background-color: rgba(0, 0, 0, 0.85); color: #FFFFFF; padding: 6px 16px; border-radius: 6px; border: 2px solid #FFD700; width: 90%; max-width: 550px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
            </style>
            """,
            unsafe_allow_html=True
        )

# Ejecutamos la carga de estilos de inmediato
cargar_estilos_custom(RUTA_CSS)
# ==============================================================================
# 5. CARGA Y CONTROL DE DATOS (Manejo Seguro de Archivos JSON)
# ==============================================================================
@st.cache_data(show_spinner="Cargando catálogo disponible...")
def cargar_base_datos_json(ruta_json, tipo_archivo="menu"):
    """
    Lee los archivos de configuración JSON. Si no existen o están dañados,
    devuelve una estructura limpia por defecto para evitar caídas del sistema.
    """
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            st.error(f"⚠️ El archivo {tipo_archivo} tiene un error de formato.")
    
    # Datos de respaldo automáticos si los archivos fallan o no existen
    if tipo_archivo == "menu":
        return {
            "productos": [
                {"id": 1, "nombre": "Producto de Muestra", "categoria": "General", "precio": 0.0, "disponible": True}
            ]
        }
    else:
        return {"categorias": ["General"]}

# Inicialización y carga de los datos del catálogo en memoria
DATOS_MENU = cargar_base_datos_json(RUTA_JSON_MENU, "menu")
DATOS_CATEGORIAS = cargar_base_datos_json(RUTA_JSON_CATEGORIAS, "categorias")

# Extraemos las listas limpias listas para usar en la interfaz
LISTA_PRODUCTOS = DATOS_MENU.get("productos", [])
LISTA_CATEGORIAS = DATOS_CATEGORIAS.get("categorias", ["Todas"])
# ==============================================================================
# 6. CONSTRUCCIÓN DEL ENCABEZADO RESPONSIVO (Logo y Título Flotante)
# ==============================================================================

# Si la imagen en Base64 falló por completo, usamos un enlace de respaldo genérico para el logo
URL_LOGO_FINAL = URL_LOGO_LOCAL if URL_LOGO_LOCAL else "https://unsplash.com"

st.markdown(
    f"""
    <!-- Añadimos translate="no" para bloquear traducciones automáticas destructivas de Chrome -->
    <div class="header-container" translate="no">
        <!-- 1. Nombre del autor en la parte superior con separación controlada -->
        <div class="autor-text">
            PÁGINA DESARROLLADA POR: JHOHAN GUADALUPE
        </div>
        
        <!-- 2. Envoltura del Logo y el Título para permitir la superposición (z-index) -->
        <div class="logo-title-wrapper">
            <img src="{URL_LOGO_FINAL}" class="logo-img" alt="Logo Almacén Guadalupe">
            <h1 class="titulo-catalogo">
                CATÁLOGO DE PRODUCTOS DISPONIBLES
            </h1>
        </div>
        
        <!-- 3. Mensaje de bienvenida flotante debajo del conjunto central -->
        <p class="texto-bienvenida" style="color: #FFD700; font-weight: 500; margin-top: 25px; margin-bottom: 5px;">
            Bienvenidos al stock de productos disponibles y sus precios 🔥
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# Separador estético sutil para dar paso a la botonera de navegación
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
# ==============================================================================
# 7. MÓDULO DE INFORMACIÓN OFICIAL DE PAGO Y CONTACTO (Responsive Accordions)
# ==============================================================================

# Encabezado del bloque informativo utilizando clases responsivas
st.markdown(
    """
    <div style="text-align: center; width: 100%; margin-top: 15px; margin-bottom: 5px;">
        <h2 style="font-size: clamp(1.1rem, 3.5vw, 1.6rem); color: #FFFFFF; font-weight: bold; margin-bottom: 5px;">
            💳 INFORMACIÓN OFICIAL DE PAGO Y CONTACTO
        </h2>
        <p style="font-size: clamp(0.75rem, 2.2vw, 0.95rem); color: #B0B0B0; margin-bottom: 15px;">
            Selecciona el método de tu preferencia haciendo clic para desplegar los datos correspondientes:
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Estructura de pestañas expandibles seguras para pantallas táctiles y escritorios
with st.expander("▶  📄 VER Nº DE CUENTA OFICIAL"):
    st.markdown(
        """
        <div class="boton-desplegable-info">
            <p><strong>Banco:</strong> Banco de Crédito del Perú (BCP)</p>
            <p><strong>Número de Cuenta:</strong> <code style="color: #FFD700; font-size: 1.1rem;">191-XXXXXX-X-XX</code></p>
            <p><strong>Titular:</strong> Almacén Guadalupe E.I.R.L.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with st.expander("▶  📱 VER NÚMERO Y QR DE YAPE"):
    st.markdown(
        """
        <div class="boton-desplegable-info" style="text-align: center;">
            <p><strong>Número Yape:</strong> <strong style="color: #FFD700; font-size: 1.1rem;">987-XXX-XXX</strong></p>
            <p style="font-size: 0.85rem; color: #B0B0B0;">(A nombre de Jhohan Guadalupe)</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    # Ejemplo de cómo insertar el QR de forma responsiva si lo tienes localmente
    # URL_QR = optimizar_y_cargar_base64(os.path.join(BASE_DIR, "qr_yape.png"))
    # if URL_QR: st.markdown(f'<img src="{URL_QR}" style="width: 180px; max-width: 50%; height: auto; display: block; margin: 10px auto; border-radius: 8px;">', unsafe_allow_html=True)

with st.expander("▶  📞 VER TELÉFONO DE CONTACTO DIRECTO"):
    st.markdown(
        """
        <div class="boton-desplegable-info">
            <p><strong>Atención al Cliente:</strong> 📞 +51 987 XXX XXX</p>
            <p><strong>Horario de atención:</strong> Lunes a Sábado de 8:00 AM a 8:00 PM</p>
            <p style="margin-top: 10px; text-align: center;"><a href="https://wa.me" target="_blank" style="background-color: #25D366; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 0.85rem;">Escríbenos por WhatsApp</a></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Separador para dar inicio al buscador y catálogo de stock
st.markdown("<hr style='border: 0; height: 1px; background: #333; margin: 35px 0 25px 0;'>", unsafe_allow_html=True)
# ==============================================================================
# 8. SISTEMA DE BÚSQUEDA Y FILTRADO DE PRODUCTOS (Lógica de Inventario)
# ==============================================================================

st.markdown(
    """
    <div style="text-align: left; width: 100%; margin-bottom: 10px;">
        <h3 style="font-size: clamp(1.0rem, 3vw, 1.4rem); color: #FFD700; font-weight: bold;">
            📦 BUSCADOR DE PRODUCTOS EN TIEMPO REAL
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Diseño en columnas adaptativo para los controles de búsqueda
col_busqueda, col_categoria = st.columns([2, 1])

with col_busqueda:
    # Barra de texto para buscar productos por coincidencia de nombre
    texto_buscado = st.text_input(
        label="Buscar por nombre del artículo:",
        placeholder="Ej. Arroz, Aceite, Leche...",
        label_visibility="visible"
    ).strip().lower()

with col_categoria:
    # Selector desplegable con la lista dinámica de categorías cargadas del JSON
    # Se asegura de incluir una opción global "Todas" al inicio
    opciones_combo = ["Todas"] + [c for c in LISTA_CATEGORIAS if c != "Todas"]
    categoria_seleccionada = st.selectbox(
        label="Filtrar por categoría:",
        options=opciones_combo
    )

# ==============================================================================
# 9. PROCESAMIENTO MATEMÁTICO DE FILTROS (Algoritmo de Selección)
# ==============================================================================
productos_filtrados = []

for prod in LISTA_PRODUCTOS:
    # 1. Validación de existencia de llaves críticas para evitar caídas
    nombre_prod = str(prod.get("nombre", "")).lower()
    cat_prod = str(prod.get("categoria", ""))
    esta_disponible = prod.get("disponible", True)
    
    # 2. Evaluación del filtro de categoría
    cumple_categoria = (categoria_seleccionada == "Todas" or cat_prod == categoria_seleccionada)
    
    # 3. Evaluación del filtro por texto escrito
    cumple_texto = (not texto_buscado or texto_buscado in nombre_prod)
    
    # Si cumple ambas condiciones y está en stock, se añade a la vista final
    if cumple_categoria and cumple_texto and esta_disponible:
        productos_filtrados.append(prod)
# ==============================================================================
# 10. RENDERIZADO DEL CATÁLOGO (Tarjetas de Productos Responsivas)
# ==============================================================================
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

if not productos_filtrados:
    st.info("🔍 No se encontraron productos disponibles que coincidan con tu búsqueda.")
else:
    # Abrimos el contenedor general con soporte CSS Grid nativo para celulares/PCs
    html_tarjetas = '<div class="contenedor-productos">'
    
    for prod in productos_filtrados:
        # Extracción segura de valores
        nombre = prod.get("nombre", "Producto sin nombre")
        precio = prod.get("precio", 0.0)
        categoria = prod.get("categoria", "General")
        
        # Generación de la tarjeta individual adaptable
        html_tarjetas += f"""
        <div class="tarjeta-producto">
            <span class="etiqueta-categoria">{categoria}</span>
            <h4 class="nombre-producto">{nombre}</h4>
            <div class="divisor-tarjeta"></div>
            <p class="precio-producto">S/. {precio:.2f}</p>
        </div>
        """
    
    html_tarjetas += '</div>'
    st.markdown(html_tarjetas, unsafe_allow_html=True)

# ==============================================================================
# 11. PIE DE PÁGINA (Footer institucional fijo)
# ==============================================================================
st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; padding: 20px 0; border-top: 1px solid #222;">
        <p style="font-size: 0.8rem; color: #666; margin: 0;">
            © 2026 Almacén Guadalupe - Todos los derechos reservados.
        </p>
        <p style="font-size: 0.75rem; color: #444; margin-top: 5px;">
            Precios y disponibilidad sujetos a cambios sin previo aviso.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
