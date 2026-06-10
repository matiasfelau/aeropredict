"""Normalización de texto compartida.

CRÍTICO: la base principal y el archivo de aeropuertos deben normalizar
localidades/provincias con EXACTAMENTE el mismo criterio. Si no, los joins por
localidad (criterio de aceptación 5) pierden filas y los rankings de rutas se
duplican por una tilde o un espacio de más (regla 2 de limpieza).
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd

# Variantes conocidas -> forma canónica de salida.
# Se pobla DESPUÉS del EDA, cuando aparezcan los duplicados reales del portal
# (p. ej. {"capital federal": "Ciudad De Buenos Aires"}). La clave va en el
# formato de `clave_normalizada` (sin acentos, minúscula, espacios colapsados).
ALIASES: dict[str, str] = {}

_RE_ESPACIOS = re.compile(r"\s+")

# Conectores que en castellano van en minúscula dentro de un nombre propio
# ("Ciudad de Buenos Aires", no "Ciudad De Buenos Aires"). Solo se bajan si son
# palabras interiores (tienen espacio antes y después); la primera palabra
# siempre queda capitalizada.
_CONECTORES = ("de", "del", "la", "las", "los", "y", "e", "en")
_RE_CONECTORES = re.compile(
    r"(?<= )(" + "|".join(c.capitalize() for c in _CONECTORES) + r")(?= )"
)


def _bajar_conectores(texto: str) -> str:
    return _RE_CONECTORES.sub(lambda m: m.group(0).lower(), texto)


def quitar_acentos(texto: str) -> str:
    """Descompone y elimina marcas de acento (NFKD)."""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def clave_normalizada(valor) -> str | None:
    """Clave para comparar/deduplicar: sin acentos, minúscula, sin espacios
    redundantes. NO es para mostrar, solo para matchear variantes."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    s = quitar_acentos(str(valor)).lower().strip()
    s = _RE_ESPACIOS.sub(" ", s)
    return s or None


def normalizar_texto(valor, title_case: bool = True) -> str | None:
    """Normaliza un valor escalar para MOSTRAR: trim, colapsa espacios internos,
    aplica aliases conocidos y Title Case opcional. Devuelve None si queda vacío.
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    s = _RE_ESPACIOS.sub(" ", str(valor).strip())
    if not s:
        return None
    clave = clave_normalizada(s)
    if clave in ALIASES:
        return ALIASES[clave]
    return _bajar_conectores(s.title()) if title_case else s


def normalizar_serie(serie: pd.Series, modo: str = "title") -> pd.Series:
    """Versión vectorizada para columnas grandes.

    modo:
      - "title": Title Case (localidades, provincias, aeropuertos).
      - "lower": minúscula (categóricas: clasificacion/clase de vuelo).
      - "strip": solo trim + colapso de espacios (aerolínea).
    """
    base = (
        serie.astype("string")
        .str.strip()
        .str.replace(_RE_ESPACIOS, " ", regex=True)
    )
    base = base.mask(base.eq(""), pd.NA)

    if modo == "lower":
        resultado = base.str.lower()
    elif modo == "strip":
        resultado = base
    else:  # "title"
        resultado = base.str.title().str.replace(
            _RE_CONECTORES, lambda m: m.group(0).lower(), regex=True
        )

    # Aplicar aliases conocidos (si los hay) sobre la clave normalizada.
    if ALIASES:
        claves = base.map(clave_normalizada)
        alias = claves.map(ALIASES).astype("string")
        resultado = alias.fillna(resultado)

    return resultado
