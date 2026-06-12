"""
Data loader: integra el pipeline ETL con la DB PostgreSQL.

Lee CSVs desde data/processed/ y carga/actualiza la base de datos.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Ruta, RutaAerolinea, Aeropuerto, ReporteCalidad


def cargar_datos_desde_pipeline(db: Session) -> Dict[str, Any]:
    """
    Carga datos desde los CSVs generados por el pipeline ETL.

    Lee los siguientes archivos:
    - data/processed/base_mensual_ruta.csv
    - data/processed/base_mensual_ruta_aerolinea.csv
    - data/processed/aeropuertos_limpio.csv

    Args:
        db: Sesión de SQLAlchemy

    Returns:
        Dict con estadísticas de carga:
        - rutas_nuevas: int
        - rutas_actualizadas: int
        - aeropuertos_nuevos: int
        - aeropuertos_actualizados: int
        - errores: list[str]
    """
    resultado = {
        "rutas_nuevas": 0,
        "rutas_actualizadas": 0,
        "aeropuertos_nuevos": 0,
        "aeropuertos_actualizados": 0,
        "errores": [],
    }

    try:
        # Cargar CSVs
        print("📂 Leyendo archivos CSV del pipeline...")

        rutas_csv = settings.DATA_PROCESSED_PATH / "base_mensual_ruta.csv"
        rutas_aerolinea_csv = (
            settings.DATA_PROCESSED_PATH / "base_mensual_ruta_aerolinea.csv"
        )
        aeropuertos_csv = settings.DATA_PROCESSED_PATH / "aeropuertos_limpio.csv"

        if not rutas_csv.exists():
            raise FileNotFoundError(f"No encontrado: {rutas_csv}")
        if not aeropuertos_csv.exists():
            raise FileNotFoundError(f"No encontrado: {aeropuertos_csv}")

        # Cargar rutas
        print("📥 Cargando rutas...")
        df_rutas = pd.read_csv(rutas_csv)
        resultado["rutas_nuevas"], resultado["rutas_actualizadas"] = _cargar_rutas(
            db, df_rutas
        )

        # Cargar rutas por aerolínea (si existe)
        if rutas_aerolinea_csv.exists():
            print("📥 Cargando rutas por aerolínea...")
            df_rutas_aero = pd.read_csv(rutas_aerolinea_csv)
            _cargar_rutas_aerolinea(db, df_rutas_aero)

        # Cargar aeropuertos
        print("📥 Cargando aeropuertos...")
        df_aeropuertos = pd.read_csv(aeropuertos_csv)
        (
            resultado["aeropuertos_nuevos"],
            resultado["aeropuertos_actualizados"],
        ) = _cargar_aeropuertos(db, df_aeropuertos)

        # Crear reporte de calidad
        print("📝 Generando reporte de calidad...")
        _crear_reporte_calidad(db, df_rutas)

        db.commit()
        print("✅ Carga completada exitosamente")

    except Exception as e:
        db.rollback()
        resultado["errores"].append(str(e))
        print(f"❌ Error durante carga: {e}")

    return resultado


def _cargar_rutas(db: Session, df: pd.DataFrame) -> tuple[int, int]:
    """
    Carga o actualiza rutas en la DB.

    Returns:
        (nuevas, actualizadas)
    """
    nuevas = 0
    actualizadas = 0

    for _, row in df.iterrows():
        try:
            # Clave única: (anio, mes, ruta, clasificacion_vuelo)
            ruta_existente = (
                db.query(Ruta)
                .filter(
                    (Ruta.anio == row["anio"])
                    & (Ruta.mes == row["mes"])
                    & (Ruta.ruta == row["ruta"])
                    & (Ruta.clasificacion_vuelo == row["clasificacion_vuelo"])
                )
                .first()
            )

            if ruta_existente:
                # Actualizar
                ruta_existente.pasajeros = row.get("pasajeros", 0)
                ruta_existente.asientos = row.get("asientos", 0)
                ruta_existente.vuelos = row.get("vuelos", 0)
                ruta_existente.factor_ocupacion = row.get("factor_ocupacion", 0)
                actualizadas += 1
            else:
                # Crear nueva
                nueva_ruta = Ruta(
                    anio=row["anio"],
                    mes=row["mes"],
                    ruta=row["ruta"],
                    clasificacion_vuelo=row["clasificacion_vuelo"],
                    origen_localidad=row["origen_localidad"],
                    origen_provincia=row["origen_provincia"],
                    destino_localidad=row["destino_localidad"],
                    destino_provincia=row["destino_provincia"],
                    pasajeros=row.get("pasajeros", 0),
                    asientos=row.get("asientos", 0),
                    vuelos=row.get("vuelos", 0),
                    factor_ocupacion=row.get("factor_ocupacion", 0),
                )
                db.add(nueva_ruta)
                nuevas += 1
        except Exception as e:
            print(f"⚠️ Error cargando ruta: {e}")

    return nuevas, actualizadas


def _cargar_rutas_aerolinea(db: Session, df: pd.DataFrame) -> None:
    """
    Carga rutas desglosadas por aerolínea.
    """
    # Este loader es opcional; ajustar según disponibilidad de datos
    for _, row in df.iterrows():
        try:
            # Buscar ruta padre
            ruta_padre = (
                db.query(Ruta)
                .filter(
                    (Ruta.anio == row.get("anio"))
                    & (Ruta.mes == row.get("mes"))
                    & (Ruta.ruta == row.get("ruta"))
                    & (Ruta.clasificacion_vuelo == row.get("clasificacion_vuelo"))
                )
                .first()
            )

            if not ruta_padre:
                continue

            # Verificar si ya existe
            ruta_aero_existente = (
                db.query(RutaAerolinea)
                .filter(
                    (RutaAerolinea.ruta_id == ruta_padre.id)
                    & (RutaAerolinea.aerolinea == row.get("aerolinea"))
                )
                .first()
            )

            if not ruta_aero_existente:
                nueva_ruta_aero = RutaAerolinea(
                    ruta_id=ruta_padre.id,
                    aerolinea=row.get("aerolinea"),
                    pasajeros=row.get("pasajeros", 0),
                    asientos=row.get("asientos", 0),
                    vuelos=row.get("vuelos", 0),
                    factor_ocupacion=row.get("factor_ocupacion", 0),
                )
                db.add(nueva_ruta_aero)
        except Exception as e:
            print(f"⚠️ Error cargando ruta aerolínea: {e}")


def _cargar_aeropuertos(db: Session, df: pd.DataFrame) -> tuple[int, int]:
    """
    Carga o actualiza aeropuertos en la DB.

    Returns:
        (nuevos, actualizados)
    """
    nuevos = 0
    actualizados = 0

    for _, row in df.iterrows():
        try:
            codigo_oaci = str(row.get("codigo", "")).upper()
            if not codigo_oaci or len(codigo_oaci) < 4:
                continue

            aeropuerto_existente = (
                db.query(Aeropuerto)
                .filter(Aeropuerto.codigo_oaci == codigo_oaci)
                .first()
            )

            latitud = _parse_float(row.get("latitud"))
            longitud = _parse_float(row.get("longitud"))

            if aeropuerto_existente:
                # Actualizar
                aeropuerto_existente.nombre = row.get("nombre", "")
                aeropuerto_existente.localidad = row.get("localidad", "")
                aeropuerto_existente.provincia = row.get("provincia", "")
                aeropuerto_existente.latitud = latitud
                aeropuerto_existente.longitud = longitud
                actualizados += 1
            else:
                # Crear nuevo
                nuevo_aeropuerto = Aeropuerto(
                    codigo_oaci=codigo_oaci,
                    nombre=row.get("nombre", ""),
                    localidad=row.get("localidad", ""),
                    provincia=row.get("provincia", ""),
                    pais=row.get("pais", "Argentina"),
                    latitud=latitud,
                    longitud=longitud,
                )
                db.add(nuevo_aeropuerto)
                nuevos += 1
        except Exception as e:
            print(f"⚠️ Error cargando aeropuerto: {e}")

    return nuevos, actualizados


def _crear_reporte_calidad(db: Session, df_rutas: pd.DataFrame) -> None:
    """
    Crea un reporte de calidad basado en los datos cargados.
    """
    try:
        total_registros = len(df_rutas)
        rutas_unicas = df_rutas["ruta"].nunique()
        aerolineas = db.query(RutaAerolinea).count()

        reporte = ReporteCalidad(
            fecha_generacion=datetime.utcnow(),
            total_registros=total_registros,
            total_descartados=0,  # Ya están descartes en el pipeline
            rutas_unicas=int(rutas_unicas),
            aerolineas_unicas=aerolineas,
            periodo_inicio=None,
            periodo_fin=None,
        )
        db.add(reporte)
    except Exception as e:
        print(f"⚠️ Error creando reporte de calidad: {e}")


def _parse_float(value: Any) -> Optional[float]:
    """Convierte un valor a float de forma segura."""
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
