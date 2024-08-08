import requests
import spacy
import re
import pdfplumber
import os

# Cargar el modelo de spaCy en español
nlp = spacy.load("es_core_news_sm")

def fetch_airtable_data(url, headers):
    """Obtiene datos de Airtable"""
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('records', [])

def extract_cv_attachments(records):
    """Extrae los datos de los CVs desde los registros de Airtable"""
    cv_data = []
    for record in records:
        if 'fields' in record and 'CV' in record['fields']:
            for attachment in record['fields']['CV']:
                if attachment['type'] == 'application/pdf':
                    cv_data.append({
                        'filename': attachment['filename'],
                        'url': attachment['url']
                    })
    return cv_data

def download_file(url, local_filename):
    """Descarga un archivo desde una URL y lo guarda localmente"""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF usando pdfplumber"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_entities(text):
    """Extrae entidades del texto usando spaCy"""
    doc = nlp(text)
    entities = {'PERSON': [], 'ORG': [], 'DATE': [], 'EMAIL': [], 'SKILLS': [], 'EXPERIENCE': [], 'NAME': []}
    
    # Extraer entidades predefinidas
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)
    
    # Buscar correos electrónicos con regex
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    entities['EMAIL'].extend(emails)
    
    # Ejemplo de patrones para habilidades y experiencia
    skills_pattern = re.compile(r'\b(?:habilidades|competencias|conocimientos)\b.*?:\s*(.*)', re.IGNORECASE)
    experience_pattern = re.compile(r'\b(?:experiencia|historial laboral|experiencia profesional)\b.*?:\s*(.*)', re.IGNORECASE)
    
    # Buscar habilidades
    skills_matches = skills_pattern.findall(text)
    entities['SKILLS'].extend([item.strip() for sublist in skills_matches for item in sublist.split(',')])
    
    # Buscar experiencia
    experience_matches = experience_pattern.findall(text)
    entities['EXPERIENCE'].extend([item.strip() for sublist in experience_matches for item in sublist.split(',')])
    
    # Buscar nombres completos usando un patrón regex simple
    name_pattern = re.compile(r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?: [A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b')
    name_matches = name_pattern.findall(text)
    entities['NAME'].extend(name_matches)
    
    return entities
