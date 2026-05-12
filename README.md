# Protocolos Médicos SSMOC — RAG

Asistente para búsqueda y consulta de protocolos de referencia y contrarreferencia del
Servicio de Salud Metropolitano Occidente (SSMOC). Dirigido a médicos de APS que necesitan
navegar criterios de derivación sin tener que leer documentos escaneados completos.

## Problema que resuelve

Los protocolos son PDFs escaneados con muchas páginas de encabezado burocrático.
El médico no puede hacer Ctrl+F, no puede citar la fuente, y pierde tiempo llegando
al criterio clínico relevante. Este sistema parsea los documentos, los hace buscables
por contenido, y permite hacer preguntas en lenguaje natural obteniendo respuestas
con cita de página.

## Diseño de la app

Layout de 3 columnas:

```
┌──────────────┬──────────────────────────────┬────────────────────┐
│   Buscar...  │                              │  Asistente         │
│              │   # Cardiología Adulto       │                    │
│  Resultados: │   v2 · 2021                  │  > ¿cuáles son     │
│              │   ─────────────────────────  │    los criterios   │
│  · Cardio    │                              │    de derivación   │
│    pág 5     │   --- Página 1 ---           │    para ICC?       │
│    ...texto  │   contenido...               │                    │
│              │                              │  Los criterios     │
│  · GES 2025  │   --- Página 2 ---           │  son... (pág. 7)   │
│    pág 12    │   contenido...               │                    │
│    ...texto  │                              │  [escribe aquí...] │
└──────────────┴──────────────────────────────┴────────────────────┘
```

**Sidebar izquierdo** — búsqueda de contenido (BM25) sobre todos los documentos.
Muestra chunks con extracto, nombre del protocolo y página. Click en un resultado
carga ese documento en el centro, scrolleado a esa sección.
Los médicos ya conocen los documentos: no necesitan un árbol de archivos,
necesitan encontrar rápido el contenido relevante.

**Panel central** — markdown del documento activo, scrollable, con separadores de página.
Ctrl+F del browser funciona sobre el texto renderizado.

**Panel derecho** — chat multi-turn. El contexto es el documento activo: el LLM
responde solo con información de ese protocolo y cita la página.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI |
| Frontend | HTML + CSS + JS vanilla (sin frameworks, sin build steps) |
| LLM | Mistral (`mistral-small-latest`) |
| Embeddings | `BAAI/bge-m3` vía HuggingFace Inference API |
| Vector Store | ChromaDB (cosine distance) |
| Búsqueda sidebar | BM25 (`rank-bm25`) sobre contenido de todos los docs |
| Deploy | Railway |

## Estructura

```
├── main.py                         # FastAPI: API endpoints + sirve el frontend
├── static/
│   └── index.html                  # Frontend completo (HTML + CSS + JS inline)
├── rag/
│   ├── documents.py                # Registry: 40 archivos → 26 documentos lógicos agrupados
│   ├── embed.py                    # Embeddings HuggingFace + ChromaDB (cosine)
│   ├── retriever.py                # Búsqueda semántica con filtro opcional por documento
│   └── generator.py                # Respuesta con Mistral + citas de página
├── scripts/
│   ├── download_pdfs.py            # Descarga PDFs desde ssmoc.redsalud.gob.cl
│   ├── parse_pdfs.py               # Llama Cloud → JSON + Markdown por página
│   └── build_index.py              # Genera embeddings y almacena en ChromaDB
└── data/
    ├── parsed/
    │   └── markdown/               # Un .md por PDF (40 archivos, ya generados)
    └── chroma_db/                  # Vector store (ya indexado, 1010 chunks, cosine)
```

## Setup local

```bash
# 1. Dependencias
uv sync

# 2. Variables de entorno
cp .env.example .env
# Editar .env con MISTRAL_API_KEY y HUGGING_FACE_API_KEY

# 3. Correr
uv run python main.py
# → http://localhost:8000
```

El índice ChromaDB y los markdowns ya están generados en `data/`.
Solo hay que re-indexar si se agregan documentos nuevos:
```bash
uv run python scripts/build_index.py
```

## Deploy en Railway

1. Push al repo (incluye `data/chroma_db/` y `data/parsed/markdown/`)
2. New project → Deploy from GitHub
3. Variables de entorno: `MISTRAL_API_KEY`, `HUGGING_FACE_API_KEY`
4. Railway detecta `railway.toml` automáticamente

## API Keys requeridas

| Key | Servicio |
|---|---|
| `MISTRAL_API_KEY` | Mistral (generación de respuestas) |
| `HUGGING_FACE_API_KEY` | HuggingFace Inference API (embeddings BAAI/bge-m3) |
