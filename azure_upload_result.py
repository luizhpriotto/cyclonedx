import os
import sys
import json
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient

# ============================================================================
# CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE
# ============================================================================
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
app_name = os.getenv("SBOM_APP_NAME")

if not connection_string:
    print("❌ Erro: AZURE_STORAGE_CONNECTION_STRING não definida.")
    sys.exit(1)

if not container_name:
    print("❌ Erro: AZURE_STORAGE_CONTAINER_NAME não definida.")
    sys.exit(1)

if not app_name:
    print("❌ Erro: SBOM_APP_NAME não definida.")
    sys.exit(1)

local_file = sys.argv[1] if len(sys.argv) > 1 else "grype.json"

# ============================================================================
# VALIDA ARQUIVO
# ============================================================================
if not os.path.exists(local_file):
    print(f"❌ Erro: Arquivo '{local_file}' não encontrado.")
    sys.exit(1)

try:
    with open(local_file, encoding="utf-8") as f:
        json.load(f)
except json.JSONDecodeError as e:
    print(f"❌ Erro: '{local_file}' não é um JSON válido: {e}")
    sys.exit(1)

file_size = os.path.getsize(local_file)
print(f"✅ Arquivo '{local_file}' validado ({file_size} bytes)")

# ============================================================================
# GERA NOME DO BLOB COM DATA+HORA
# ============================================================================
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
blob_name = f"{app_name}/{timestamp}.json"

# ============================================================================
# UPLOAD
# ============================================================================
try:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
except Exception as e:
    print(f"❌ Erro ao conectar ao Azure Storage: {e}")
    sys.exit(1)

print(f"\n📤 Enviando arquivo...")
print(f"   Arquivo local : {local_file}")
print(f"   Blob remoto   : {blob_name}")
print(f"   Container     : {container_name}")

try:
    with open(local_file, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    print(f"\n✅ Upload concluído!")
    print(f"   App      : {app_name}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Path     : {container_name}/{blob_name}")

except Exception as e:
    print(f"❌ Erro ao enviar arquivo: {e}")
    sys.exit(1)
