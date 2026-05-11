# Protocolos Médicos — RAG

Asistente RAG para búsqueda de protocolos y guías clínicas del SESAM CENIA (Red Salud Chile). Los médicos pueden consultar preguntas sobre derivaciones, contrarreferencias y protocolos, y el sistema responde citando las fuentes originales.

## Stack

| Capa | Tecnología |
|---|---|
| UI | Streamlit |
| OCR / Parse | Llama Parse |
| LLM | Mistral (`mistral-small-latest`) |
| Embeddings | `mistral-embed` |
| Vector Store | ChromaDB |
| Deploy | Railway |

## Estructura

```
├── app.py                          # Streamlit app
├── rag/
│   ├── embed.py                    # Construye/carga índice ChromaDB con embeddings Mistral
│   ├── retriever.py                # Recupera chunks relevantes para una consulta
│   └── generator.py                # Genera respuesta con Mistral + citas
├── scripts/
│   ├── download_pdfs.py            # Descarga todos los PDFs desde ssmoc.redsalud.gob.cl
│   ├── parse_pdfs.py               # Pasa los PDFs por Llama Parse → JSON con metadata
│   └── build_index.py              # Crea embeddings y almacena en ChromaDB
├── pdfs/                           # PDFs descargados (gitignored)
└── data/
    ├── parsed/                     # Documentos parseados (gitignored)
    └── chroma_db/                  # Vector store (gitignored)
```

## Uso local

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API keys
cp .env.example .env
# Editar .env con LLAMA_CLOUD_API_KEY y MISTRAL_API_KEY

# 3. Descargar PDFs (si no están)
python scripts/download_pdfs.py

# 4. Parsear con Llama Parse
python scripts/parse_pdfs.py

# 5. Construir índice de embeddings
python scripts/build_index.py

# 6. Correr app
streamlit run app.py
```

## Flujo de datos

1. **Descarga** → `scripts/download_pdfs.py` baja 40 PDFs desde `ssmoc.redsalud.gob.cl/medicos/`
2. **Parseo** → `scripts/parse_pdfs.py` pasa cada PDF por Llama Parse, guarda chunks con metadata (nombre del protocolo, página, URL original) en `data/parsed/parsed_documents.json`
3. **Indexación** → `scripts/build_index.py` genera embeddings con `mistral-embed` y almacena en ChromaDB
4. **Consulta** → Streamlit app recibe pregunta → retriever busca chunks relevantes → generator llama a Mistral con contexto + citas → respuesta al médico

## API Keys requeridas

| Key | Servicio | Archivo |
|---|---|---|
| `LLAMA_CLOUD_API_KEY` | Llama Parse (OCR) | `.env` |
| `MISTRAL_API_KEY` | Mistral (LLM + Embeddings) | `.env` |
