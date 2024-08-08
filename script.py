import os
import pandas as pd
from config import API_KEY, BASE_ID, TABLE_ID, VIEW_ID
from utils import fetch_airtable_data, extract_cv_attachments, download_file, extract_text_from_pdf, extract_entities
import json

# Configuración
url = f'https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}?view={VIEW_ID}'

headers = {
    'Authorization': f'Bearer {API_KEY}'
}

# Fetch data from Airtable
records = fetch_airtable_data(url, headers)
cv_data = extract_cv_attachments(records)

# Convert to DataFrame
df = pd.DataFrame(cv_data)

# Guardar a CSV solo con datos de los CVs
df.to_csv('cv_attachments.csv', index=False)
print("CVs exported successfully!")

# Crear directorio para guardar la información extraída
os.makedirs('CVs', exist_ok=True)
os.makedirs('Extracted_Info', exist_ok=True)

# Diccionario para almacenar toda la información extraída
all_entities = {}

# Descargar y extraer texto de los CVs
for index, row in df.iterrows():
    file_path = f"CVs/{row['filename']}"
    download_file(row['url'], file_path)
    print(f"Downloaded {row['filename']}")
    
    # Extraer texto del PDF
    text = extract_text_from_pdf(file_path)
    
    # Extraer entidades del texto
    entities = extract_entities(text)
    
    # Añadir la información extraída al diccionario
    all_entities[row['filename']] = entities

# Guardar toda la información extraída en un solo archivo JSON
with open('Extracted_Info/all_entities.json', 'w', encoding='utf-8') as entities_file:
    json.dump(all_entities, entities_file, indent=4, ensure_ascii=False)
print("All extracted entities saved to all_entities.json")
