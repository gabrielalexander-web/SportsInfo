"""
Ilustraciones propias en SVG para cada deporte (estilo de línea, minimalista,
sin depender de fotos de internet por temas de derechos de autor). Cada
ícono es dibujado a mano con formas simples para mantener consistencia
visual con la identidad de SportsInfo.
"""

# Trazo interno de cada ícono (sin la etiqueta <svg> exterior), en un
# lienzo de 64x64. Usa currentColor para heredar el color que se le pase.
TRAZOS_POR_DEPORTE = {
    "fútbol": '<circle cx="32" cy="32" r="21"/><path d="M32 14 L39 23 L32 32 L25 23 Z"/><path d="M32 32 L20 40 M32 32 L44 40 M20 40 L16 52 M44 40 L48 52"/>',
    "básquetbol": '<circle cx="32" cy="32" r="21"/><path d="M32 11 V53 M11 32 H53 M17 17 Q32 32 17 47 M47 17 Q32 32 47 47"/>',
    "vóley": '<circle cx="32" cy="32" r="21"/><path d="M32 11 Q41 32 32 53 M15 21 Q32 29 49 21 M15 43 Q32 35 49 43"/>',
    "natación": '<circle cx="32" cy="16" r="6"/><path d="M9 30 Q17 24 25 30 T41 30 T57 30"/><path d="M9 42 Q17 36 25 42 T41 42 T57 42"/>',
    "running": '<circle cx="38" cy="12" r="6"/><path d="M38 18 L29 33 L17 29 M29 33 L35 47 L27 59 M29 33 L41 39 L49 31"/>',
    "ciclismo": '<circle cx="15" cy="46" r="10"/><circle cx="49" cy="46" r="10"/><path d="M15 46 L27 25 L39 25 L49 46 M27 25 L21 46 M27 25 L33 13 L40 17"/>',
    "boxeo": '<path d="M19 30 Q19 15 34 15 Q49 15 49 30 V42 Q49 55 34 55 Q21 55 19 44 Z"/><path d="M19 34 Q11 34 11 26 Q11 19 18 19"/>',
    "tenis": '<ellipse cx="23" cy="25" rx="12" ry="16" transform="rotate(-25 23 25)"/><line x1="31" y1="36" x2="46" y2="53"/><circle cx="47" cy="13" r="5"/>',
    "yoga": '<circle cx="32" cy="13" r="6"/><path d="M32 19 V33 M19 45 Q32 34 45 45 M19 45 L13 40 M45 45 L51 40 M19 45 L25 54 M45 45 L39 54"/>',
    "artes marciales": '<path d="M20 27 V21 Q20 15 26 15 Q30 15 30 21 V25 Q34 23 34 29 V25 Q38 23 38 29 V25 Q42 25 42 31 V39 Q42 50 31 50 Q19 50 17 39 Z"/>',
}

# Colores de marca asignados por deporte para dar variedad visual
COLOR_POR_DEPORTE = {
    "fútbol": "var(--turf)", "básquetbol": "var(--amber)", "vóley": "var(--sky)",
    "natación": "var(--sky)", "running": "var(--amber)", "ciclismo": "var(--violet)",
    "boxeo": "var(--coral)", "tenis": "var(--turf)", "yoga": "var(--pink)",
    "artes marciales": "var(--coral)",
}

# Ícono de respaldo por categoría, para deportes agregados por el usuario
# que no están en la lista curada de arriba.
TRAZOS_POR_CATEGORIA = {
    "Equipo": TRAZOS_POR_DEPORTE["fútbol"],
    "Individual": TRAZOS_POR_DEPORTE["running"],
    "Acuático": TRAZOS_POR_DEPORTE["natación"],
    "Combate": TRAZOS_POR_DEPORTE["boxeo"],
}


def icono_svg(nombre_deporte: str, categoria: str = "", tamano: int = 40) -> str:
    """Devuelve el marcado SVG completo (como string) para un deporte dado."""
    clave = (nombre_deporte or "").strip().lower()
    trazo = TRAZOS_POR_DEPORTE.get(clave) or TRAZOS_POR_CATEGORIA.get(categoria) or TRAZOS_POR_DEPORTE["running"]
    color = COLOR_POR_DEPORTE.get(clave, "var(--amber)")
    return (
        f'<svg width="{tamano}" height="{tamano}" viewBox="0 0 64 64" fill="none" '
        f'stroke="{color}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">{trazo}</svg>'
    )
