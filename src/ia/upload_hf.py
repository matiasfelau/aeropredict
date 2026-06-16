"""
Script para subir el modelo entrenado y sus metadatos a Hugging Face Hub.

Requiere un token con permisos de escritura de Hugging Face.
"""

import os
import argparse
from pathlib import Path
from huggingface_hub import HfApi

# Cargar variables de entorno desde el archivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "models" / "demand_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"

def subir_modelo(repo_id: str, token: str = None):
    """Sube el binario del modelo y su metadata JSON al repositorio de Hugging Face."""
    if token is None:
        token = os.environ.get("HF_TOKEN")
        
    if not token:
        print("Error: Se requiere un token de escritura de Hugging Face.")
        print("Puedes obtenerlo en https://huggingface.co/settings/tokens")
        print("Pasalo como argumento --token o setea la variable de entorno HF_TOKEN.")
        return
        
    api = HfApi()
    
    if not MODEL_PATH.exists():
        print(f"Error: No se encontro el archivo del modelo en {MODEL_PATH}")
        return
        
    print(f"Subiendo modelo a Hugging Face (repo: {repo_id})...")
    try:
        # Subir el modelo .joblib
        api.upload_file(
            path_or_fileobj=str(MODEL_PATH),
            path_in_repo="demand_model.joblib",
            repo_id=repo_id,
            token=token
        )
        print("Modelo demand_model.joblib subido con exito.")
        
        # Subir el archivo de metadatos .json
        if METADATA_PATH.exists():
            api.upload_file(
                path_or_fileobj=str(METADATA_PATH),
                path_in_repo="model_metadata.json",
                repo_id=repo_id,
                token=token
            )
            print("Metadatos model_metadata.json subidos con exito.")
            
        print("Proceso de subida finalizado.")
            
    except Exception as e:
        print(f"Error al subir los archivos: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subir modelo entrenado a Hugging Face Hub.")
    parser.add_argument(
        "--repo", 
        type=str, 
        default=os.environ.get("HF_MODEL_REPO_ID", "matiasfelau/aeropredict"), 
        help="ID del repositorio en Hugging Face (ej. usuario/nombre-repo)."
    )
    parser.add_argument(
        "--token", 
        type=str, 
        default=None, 
        help="Token con permisos de escritura de Hugging Face."
    )
    args = parser.parse_args()
    
    subir_modelo(args.repo, args.token)
