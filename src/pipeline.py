"""Pipeline de punta a punta del módulo de datos.

    python -m src.pipeline            # corre todo (descarga si falta + procesa)
    python -m src.pipeline --no-descarga   # asume los CSV ya en data/raw/

Genera los entregables 5.1–5.5 en data/processed/ y reports/.
"""

from __future__ import annotations

import argparse

import pandas as pd

from . import agregacion, config, descarga, limpieza, reporte


def _validar_mensual(m: pd.DataFrame) -> None:
    """Codifica como asserts los criterios de aceptación del entregable 5.2."""
    clave = [
        config.COL_ANIO, config.COL_MES, config.COL_RUTA, config.COL_CLASIFICACION,
        "pasajeros", "asientos", "vuelos", config.COL_FACTOR,
    ]
    n_nulos = int(m[clave].isna().sum().sum())
    assert n_nulos == 0, f"5.2: {n_nulos} nulos en columnas clave"
    assert m[config.COL_FACTOR].between(0, config.FACTOR_MAX_VALIDO).all(), \
        "5.2: factor_ocupacion fuera de [0, 1.05]"
    assert m[config.COL_MES].between(1, 12).all(), "5.2: mes fuera de 1-12"
    assert (m[["pasajeros", "asientos", "vuelos"]] >= 0).to_numpy().all(), \
        "5.2: conteos negativos"


def main(descargar_datos: bool = True) -> None:
    config.asegurar_directorios()

    # --- 0. Descarga (caché local) ---------------------------------------
    if descargar_datos:
        descarga.asegurar_datos()

    # --- 1. Carga + validación de esquema --------------------------------
    print("[pipeline] cargando microdatos...")
    df = limpieza.cargar_microdatos()
    limpieza.validar_esquema(df)

    # --- 2. Limpieza (reglas 1–10) ---------------------------------------
    df_limpio, rep = limpieza.limpiar(df)

    # --- 3. Entregable 5.1: base diaria limpia (Parquet) -----------------
    df_limpio.to_parquet(config.SALIDA_BASE_DIARIA, index=False)
    print(f"[pipeline] 5.1 escrito {config.SALIDA_BASE_DIARIA.name} "
          f"({len(df_limpio):,} filas)")

    # --- 4. Entregable 5.2: base mensual por ruta (PRINCIPAL) ------------
    mensual = agregacion.agregar_mensual_ruta(df_limpio)
    mensual.to_csv(config.SALIDA_MENSUAL_RUTA, index=False, encoding="utf-8")
    print(f"[pipeline] 5.2 escrito {config.SALIDA_MENSUAL_RUTA.name} "
          f"({len(mensual):,} filas)")

    # --- 5. Entregable 5.3: base mensual por ruta+aerolínea (opcional) ---
    mensual_aero = agregacion.agregar_mensual_ruta_aerolinea(df_limpio)
    mensual_aero.to_csv(config.SALIDA_MENSUAL_RUTA_AEROLINEA, index=False, encoding="utf-8")
    print(f"[pipeline] 5.3 escrito {config.SALIDA_MENSUAL_RUTA_AEROLINEA.name} "
          f"({len(mensual_aero):,} filas)")

    # --- 6. Entregable 5.4: aeropuertos limpios --------------------------
    if config.ARCHIVO_AEROPUERTOS.exists():
        df_aero = pd.read_csv(config.ARCHIVO_AEROPUERTOS, dtype=str)
        aeropuertos = agregacion.limpiar_aeropuertos(df_aero)
        aeropuertos.to_csv(config.SALIDA_AEROPUERTOS, index=False, encoding="utf-8")
        print(f"[pipeline] 5.4 escrito {config.SALIDA_AEROPUERTOS.name} "
              f"({len(aeropuertos):,} filas)")
    else:
        print("[pipeline] AVISO: no está aeropuertos.csv, se omite 5.4")

    # --- 7. Entregable 5.5: reporte de calidad ---------------------------
    reporte.generar_reporte_calidad(rep)

    # --- Validación de criterios de aceptación (5.2) ---------------------
    _validar_mensual(mensual)

    # --- Control: suma de pasajeros antes vs. después de agregar ----------
    total_diario = int(df_limpio[config.COL_PASAJEROS].sum())
    total_mensual = int(mensual["pasajeros"].sum())
    assert total_mensual <= total_diario, \
        f"5.2 suma más pasajeros ({total_mensual:,}) que la base diaria ({total_diario:,})"
    print(f"[pipeline] control pasajeros — diario(post-limpieza): {total_diario:,} | "
          f"mensual 5.2: {total_mensual:,} | "
          f"dif: {total_diario - total_mensual:,}")
    print("[pipeline] validación OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de datos AeroPredict")
    parser.add_argument(
        "--no-descarga", action="store_true",
        help="No descargar; asumir los CSV ya en data/raw/",
    )
    args = parser.parse_args()
    main(descargar_datos=not args.no_descarga)
