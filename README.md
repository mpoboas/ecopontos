# 🗺️ Mapa de Ecopontos Portugal

Uma aplicação web para visualizar ecopontos em Portugal, com dados obtidos do mapa público da ERSAR.

## 📋 Descrição

Este projeto consiste em:
- Um site interativo para visualizar ecopontos no mapa
- Um script para recolher dados de ecopontos
- Sistema de filtragem por concelho e entidade
- Visualização otimizada com agrupamento de pontos

## 🌐 Site

O site (`index.html`) disponibiliza:
- Mapa interativo utilizando Leaflet
- Agrupamento automático de pontos próximos
- Filtros por concelho e entidade
- Contadores de pontos visíveis/totais
- Design responsivo com Tailwind CSS e DaisyUI

### Funcionalidades
- Zoom in/out para ver mais detalhes
- Clique nos pontos para ver informações detalhadas
- Filtros para localizar ecopontos específicos
- Agrupamento automático de pontos para melhor desempenho

## 🤖 Script de Recolha

O script (`script_optimized.py`) permite recolher dados de ecopontos do mapa da ERSAR.

### Configuração
```python
ZOOM = 17  # Nível de zoom (mais alto = mais preciso, mais lento)
REGIONS = {
    "porto": {
        "north": 41.2, 
        "south": 41.1, 
        "west": -8.7, 
        "east": -8.5
    },
    # Adiciona mais regiões conforme necessário
}
```

### Como usar
1. Instala as dependências:
```bash
pip install requests tqdm
```

2. Configura a região desejada no script:
- Define as coordenadas no dicionário `REGIONS`
- Ajusta o `ZOOM` conforme necessário
  - Zoom 14-15: Boa precisão, mais rápido
  - Zoom 16-17: Alta precisão, muito mais lento

3. Executa o script:
```bash
python script_optimized.py
```

### ⚠️ Considerações
- Zoom alto (17) é muito preciso mas extremamente lento
- O script usa processamento paralelo e checkpoints
- Recomendado testar com áreas pequenas primeiro
- Considera dividir áreas grandes em regiões menores

### 📊 Precisão vs Performance
- Zoom 14: ~100m precisão, processamento rápido
- Zoom 15: ~50m precisão, processamento médio
- Zoom 16: ~25m precisão, processamento lento
- Zoom 17: ~5m precisão, processamento muito lento

## ⚖️ Licença

Este projeto é open source, usa-o à vontade.
