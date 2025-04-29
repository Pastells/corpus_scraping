Recull d'eines per creació de corpus a partir de scraping. Explicat a `eines.pdf`.

# Twitter

La carpeta conté un notebook de guia i 3 projectes d'exemple.

# audio_subs

Corpus de parells àudio - transcripció a partir de vídeos amb subtítols amb un exemple per crear un
corpus d'ASR a partir de tv3.

## Exemple 3cat

Tot i que la URL ha canviat de ccma.cat/3cat a 3cat.cat/3cat, yt-dlp falla amb l'adreça nova i funciona
amb la vella, deu ser per com està indexat el vídeo o ves a saber, a data de 25/04/25.

1. Obtenir l'índex de contingut amb `python utils/index_tv3.py` (modificar pel contingut que es vol)
2. Descarregar fitxers amb `./scripts/tv3.sh` (modificar pels índex que es volen)
3. Podem separar els talls d'àudio a partir dels temps dels subtítols amb `./scripts/process_split.sh`
   (per defecte en talls de 30 segons, per veure com funciona vegeu `utils/srt-audio-split.py`).
