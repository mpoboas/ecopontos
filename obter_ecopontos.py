import math
import requests
import json
import time
import concurrent.futures
from tqdm import tqdm
from pathlib import Path

# Configurações
LAYER_ID = "6aa81fe2-7f17-45ff-ab50-aaf980951856"
LAYERGROUP_ID = "ersar@96e5548e@7020d702b2897cde83e09e46e0a28682:1711979554305"
ZOOM = 17

# URL do mapa
TILE_TEMPLATE = f"https://a.gusc.cartocdn.com/ersar/api/v1/map/{LAYERGROUP_ID}/{LAYER_ID}/{{z}}/{{x}}/{{y}}.grid.json"

# Regiões de Portugal
REGIONS = {
    #"portugal": {"north": 42.2, "south": 36.8, "west": -9.6, "east": -6.0},
    #"porto": {"north": 41.4000, "south": 41.0000, "west": -8.7700, "east": -8.2500}
    #"lisboa": {"north": 38.8, "south": 38.6, "west": -9.2, "east": -9.1},
}

def lng2tile_x(lon, zoom):
    return int((lon + 180.0) / 360.0 * (2 ** zoom))

def lat2tile_y(lat, zoom):
    lat_rad = math.radians(lat)
    return int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * (2 ** zoom))

def tile2lng(x, z):
    return x / (2.0 ** z) * 360.0 - 180.0

def tile2lat(y, z):
    n = math.pi - 2.0 * math.pi * y / (2.0 ** z)
    return math.degrees(math.atan(math.sinh(n)))

def get_tiles_for_region(bounds):
    """Calcula os tiles necessários para uma região"""
    min_x = lng2tile_x(bounds["west"], ZOOM)
    max_x = lng2tile_x(bounds["east"], ZOOM)
    min_y = lat2tile_y(bounds["north"], ZOOM)
    max_y = lat2tile_y(bounds["south"], ZOOM)
    return [(x, y) for x in range(min_x, max_x + 1) for y in range(min_y, max_y + 1)]

def fetch_tile(x, y, retries=3, delay=1):
    """Busca um tile com retry e delay"""
    url = TILE_TEMPLATE.format(z=ZOOM, x=x, y=y)
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                tile = response.json()
                points = []
                for key, value in tile.get("data", {}).items():
                    # Calcular coordenadas do centro do tile
                    lng = tile2lng(x + 0.5, ZOOM)
                    lat = tile2lat(y + 0.5, ZOOM)
                    value["coordinates"] = {
                        "lat": lat,
                        "lng": lng
                    }
                    points.append(value)
                return points
            time.sleep(delay * (attempt + 1))
        except Exception as e:
            if attempt == retries - 1:
                print(f"\n⚠️ Erro no tile ({x},{y}): {e}")
            time.sleep(delay * (attempt + 1))
    return []

def process_region(region_name, bounds):
    """Processa uma região inteira"""
    tiles = get_tiles_for_region(bounds)
    region_data = []
    
    print(f"\n🔄 Processando região: {region_name}")
    print(f"📍 Tiles a processar: {len(tiles)}")

    # Processa tiles em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_tile = {
            executor.submit(fetch_tile, x, y): (x, y) 
            for x, y in tiles
        }
        
        for future in tqdm(concurrent.futures.as_completed(future_to_tile), total=len(tiles)):
            tile_data = future.result()
            region_data.extend(tile_data)

    # Salva checkpoint da região
    save_checkpoint(region_data, region_name)
    return region_data

def save_checkpoint(data, region_name):
    """Salva dados de uma região"""
    checkpoint_dir = Path("checkpoints")
    checkpoint_dir.mkdir(exist_ok=True)
    
    with open(checkpoint_dir / f"{region_name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def merge_checkpoints():
    """Combina todos os checkpoints em um arquivo final"""
    checkpoint_dir = Path("checkpoints")
    all_data = []
    
    for checkpoint_file in checkpoint_dir.glob("*.json"):
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            region_data = json.load(f)
            all_data.extend(region_data)
    
    # Remove duplicatas baseado no cartodb_id
    unique_data = {item["cartodb_id"]: item for item in all_data}.values()
    
    with open("ecopontos_dados.json", "w", encoding="utf-8") as f:
        json.dump(list(unique_data), f, ensure_ascii=False, indent=2)

def main():
    print("🚀 Iniciando coleta de dados dos ecopontos...")
    
    all_data = []
    for region_name, bounds in REGIONS.items():
        region_data = process_region(region_name, bounds)
        all_data.extend(region_data)
        
        # Pequeno delay entre regiões para evitar sobrecarga
        time.sleep(2)
    
    # Combina todos os dados
    merge_checkpoints()
    
    print(f"\n✅ Processo concluído! {len(all_data)} ecopontos coletados.")

if __name__ == "__main__":
    main() 