"""Descarga de los CSV de origen con caché local.

El archivo principal pesa cientos de MB: se baja UNA sola vez a data/raw/
(gitignored). Si ya existe, no se vuelve a descargar salvo `forzar=True`.
"""

from __future__ import annotations

from pathlib import Path

import requests

from . import config

_CHUNK = 1024 * 1024  # 1 MB


def descargar(url: str, destino: Path, forzar: bool = False) -> Path:
    """Descarga `url` a `destino` por streaming. Devuelve la ruta local.

    Si el archivo ya existe y no está vacío, no lo vuelve a bajar (salvo forzar).
    """
    config.asegurar_directorios()

    if destino.exists() and destino.stat().st_size > 0 and not forzar:
        mb = destino.stat().st_size / 1_048_576
        print(f"[descarga] ya existe {destino.name} ({mb:,.1f} MB), se omite.")
        return destino

    print(f"[descarga] bajando {destino.name} desde {url}")
    tmp = destino.with_suffix(destino.suffix + ".part")
    bajado = 0
    siguiente_aviso = 50  # MB

    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))
        with open(tmp, "wb") as fh:
            for bloque in resp.iter_content(chunk_size=_CHUNK):
                if not bloque:
                    continue
                fh.write(bloque)
                bajado += len(bloque)
                mb = bajado / 1_048_576
                if mb >= siguiente_aviso:
                    if total:
                        print(f"[descarga]   {mb:,.0f} MB de {total/1_048_576:,.0f} MB")
                    else:
                        print(f"[descarga]   {mb:,.0f} MB")
                    siguiente_aviso += 50

    tmp.replace(destino)
    mb = destino.stat().st_size / 1_048_576
    print(f"[descarga] listo {destino.name} ({mb:,.1f} MB)")
    return destino


def asegurar_datos(forzar: bool = False) -> None:
    """Garantiza que ambos CSV de origen estén en data/raw/."""
    descargar(config.URL_MICRODATOS, config.ARCHIVO_MICRODATOS, forzar=forzar)
    descargar(config.URL_AEROPUERTOS, config.ARCHIVO_AEROPUERTOS, forzar=forzar)


if __name__ == "__main__":
    asegurar_datos()
