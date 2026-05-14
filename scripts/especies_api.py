import requests

def listar_especies_api():
    # URL oficial de la API de Euskadi para listar 
    url = "https://api.euskadi.eus/pollen-quality/species"
    
    try:
        print("Conectando con la API de Open Data Euskadi...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            especies = response.json()
            print("\n LISTA DE ESPECIES ENCONTRADAS:")
            print("-" * 40)
            for esp in especies:
                # Mostramos el ID y el nombre en castellano
                print(f"ID: {esp.get('id')} | Nombre: {esp.get('nameEs')}")
            print("-" * 40)

        else:
            print(f"❌ Error: La API respondió con código {response.status_code}")
            
    except Exception as e:
        print(f"❌ No se pudo conectar: {e}")

if __name__ == "__main__":
    listar_especies_api()