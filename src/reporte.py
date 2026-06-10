"""Generación del reporte de calidad (regla 11 / entregable 5.5)."""

from __future__ import annotations

from . import config
from .limpieza import ReporteCalidad


def generar_reporte_calidad(rep: ReporteCalidad, path=None) -> None:
    path = path or config.SALIDA_REPORTE
    config.asegurar_directorios()

    lineas: list[str] = []
    a = lineas.append

    a("# Reporte de calidad de datos — AeroPredict")
    a("")
    a("> Generado automáticamente por `python -m src.pipeline`.")
    a("")

    a("## Resumen")
    a("")
    a(f"- Filas iniciales (CSV crudo): **{rep.filas_iniciales:,}**")
    a(f"- Filas finales (base diaria limpia): **{rep.filas_finales:,}**")
    descartadas = rep.filas_iniciales - rep.filas_finales
    a(f"- Filas descartadas en total: **{descartadas:,}**")
    if rep.rango_fechas[0]:
        a(f"- Rango de fechas: **{rep.rango_fechas[0]} → {rep.rango_fechas[1]}**")
    a(f"- Rutas únicas: **{rep.n_rutas:,}**")
    a(f"- Aerolíneas únicas: **{rep.n_aerolineas:,}**")
    a(f"- Aeropuertos únicos: **{rep.n_aeropuertos:,}**")
    a("")

    a("## Filas descartadas por regla")
    a("")
    a("| Regla | Descripción | Antes | Después | Descartadas | Notas |")
    a("|---|---|---:|---:|---:|---|")
    for p in rep.pasos:
        a(f"| {p.regla} | {p.nombre} | {p.filas_antes:,} | {p.filas_despues:,} "
          f"| {p.descartadas:,} | {p.notas} |")
    a("")

    if rep.notas_extra:
        a("## Notas de calidad")
        a("")
        for n in rep.notas_extra:
            a(f"- {n}")
        a("")

    a("## % de nulos por columna (base diaria limpia)")
    a("")
    a("| Columna | % nulos |")
    a("|---|---:|")
    for col, pct in rep.nulos_por_columna.items():
        a(f"| `{col}` | {pct:.2f}% |")
    a("")

    path.write_text("\n".join(lineas), encoding="utf-8")
    print(f"[reporte] escrito {path}")
