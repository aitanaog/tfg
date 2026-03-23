umbrales_polen = {
    # Muy Alergénicos
    'Poaceae': {'bajo': 25, 'moderado': 50},
    'Olea': {'bajo': 50, 'moderado': 200},
    'Urticaceae': {'bajo': 15, 'moderado': 30},
    'Plantago': {'bajo': 25, 'moderado': 50},
    'Chenopo/Amarant': {'bajo': 25, 'moderado': 50},
    
    # Árboles con síntomas claros
    'Platanus': {'bajo': 50, 'moderado': 200},
    'Cupress/Taxaceae': {'bajo': 50, 'moderado': 200},
    'Betula': {'bajo': 30, 'moderado': 50},
    'Alnus': {'bajo': 30, 'moderado': 50},
    'Fraxinus': {'bajo': 50, 'moderado': 200},
    'Corylus': {'bajo': 30, 'moderado': 50},
    'Quercus': {'bajo': 50, 'moderado': 200},
    'Ulmus': {'bajo': 30, 'moderado': 50},
    'Populus': {'bajo': 50, 'moderado': 200},
    'Salix': {'bajo': 50, 'moderado': 200},
    'Castanea': {'bajo': 30, 'moderado': 50},
    'Ligustrum': {'bajo': 30, 'moderado': 50},
    
    # Especiales y otros con síntomas
    'Pinus': {'bajo': 50, 'moderado': 200},
    'Alternaria': {'bajo': 15, 'moderado': 30}
}

sintomas_polen = {
    # --- Tus búsquedas anteriores ---
    'Platanus': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Picor_de_garganta', 'Tos', 'Asma'],
    'Corylus': ['Rinitis', 'Conjuntivitis', 'Asma'],
    'Cupress/Taxaceae': ['Rinitis', 'Conjuntivitis', 'Asma'],
    'Alnus': ['Estornudos', 'Rinitis', 'Picor_de_garganta', 'Conjuntivitis', 'Asma'],
    'Ulmus': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Picor_de_garganta', 'Asma'],
    'Populus': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Tos', 'Dolor _de_cabeza', 'Picor_de_garganta'],
    'Betula': ['Conjuntivitis', 'Asma', 'Rinitis'],
    'Quercus': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Picor_de_garganta', 'Asma'],
    'Olea': ['Picor_de_garganta', 'Estornudos', 'Rinitis', 'Tos', 'Asma'],
    'Poaceae': ['Rinitis', 'Asma', 'Estornudos', 'Picor_nasal', 'Tos', 'Opresión_torácica'],
    'Urticaceae': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Asma'],
    'Plantago': ['Tos', 'Estornudos', 'Rinitis', 'Dolor_de_cabeza', 'Picor_de_garganta'],
    'Castanea': ['Rinitis', 'Tos', 'Estornudos', 'Picor_de_garganta', 'Conjuntivitis', 'Erupción', 'Asma'],
    'Alternaria': ['Estornudos', 'Rinitis', 'Picor_de_garganta', 'Erupción', 'Conjuntivitis', 'Tos'],
    'Pinus': ['Irritación_ocular', 'Rinitis', 'Mucosidad'],
    'Fraxinus': ['Estornudos', 'Rinitis', 'Conjuntivitis', 'Asma'], 
    'Salix': ['Estornudos', 'Rinitis', 'Conjuntivitis'],
    'Ligustrum': ['Picor_de_garganta', 'Estornudos', 'Rinitis', 'Conjuntivitis'],
    'Chenopo/Amarant': ['Rinitis', 'Asma', 'Conjuntivitis', 'Estornudos']
}

# Mapeo de IDs de Municipios de la API de Euskadi
MUNICIPIOS = {
    'Bilbao': '020',
    'Donostia': '069',
    'Vitoria': '059'
}

# Mapeo de IDs de la API a nombres de columnas del CSV
# La API usa minúsculas y algunos guiones, lo estandarizamos
MAPEO_ESPECIES = {
    'poaceae': 'Poaceae',
    'platanus': 'Platanus',
    'betula': 'Betula',
    'cupress_taxaceae': 'Cupress/Taxaceae',
    'olea': 'Olea',
    'quercus': 'Quercus',
    'alnus': 'Alnus',
    'corylus': 'Corylus',
    'fraxinus': 'Fraxinus',
    'urticaceae': 'Urticaceae',
    'pinus': 'Pinus',
    'plantago': 'Plantago',
    'castanea': 'Castanea',
    'ulmus': 'Ulmus',
    'populus': 'Populus',
    'salix': 'Salix',
    'ligustrum': 'Ligustrum',
    'chenopo_amarant': 'Chenopo/Amarant'
}