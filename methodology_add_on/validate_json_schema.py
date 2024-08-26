import json
from jsonschema import validate, ValidationError, SchemaError

# Definir las rutas de los archivos
schema_path = 'ruta/al/schema.json'  # Cambia esto por la ruta de tu archivo de esquema
json_path = 'ruta/al/data.json'      # Cambia esto por la ruta de tu archivo JSON

# Leer el esquema desde el archivo
with open(schema_path, 'r') as schema_file:
    schema = json.load(schema_file)

# Leer el JSON a validar desde el archivo
with open(json_path, 'r') as json_file:
    data = json.load(json_file)

# Validar el JSON contra el esquema
try:
    validate(instance=data, schema=schema)
    print("El JSON es válido según el esquema.")
except ValidationError as ve:
    print("Error de validación:", ve.message)
except SchemaError as se:
    print("Error en el esquema:", se.message)
except Exception as e:
    print("Otro error:", str(e))
