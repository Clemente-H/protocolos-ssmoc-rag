#!/usr/bin/env python3
"""Parse todos los PDFs con Llama Cloud API y guardar chunks en JSON + Markdown."""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from llama_cloud import LlamaCloud

load_dotenv()

PDF_DIR = Path(__file__).parent.parent / "pdfs"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "parsed"
MD_DIR = OUTPUT_DIR / "markdown"
JSON_DIR = OUTPUT_DIR / "json"
BASE_URL = "https://ssmoc.redsalud.gob.cl/medicos/"

client = LlamaCloud()


def parse_pdf(pdf_path: Path) -> list[dict]:
    """Parse un PDF con Llama Cloud API y devuelve lista de chunks con metadata."""
    file = client.files.create(file=str(pdf_path), purpose="parse")

    result = client.parsing.parse(
        file_id=file.id,
        tier="agentic",
        version="latest",
        output_options={
            "markdown": {"tables": {"output_tables_as_markdown": True}},
        },
        processing_options={
            "ocr_parameters": {"languages": ["es"]},
        },
        expand=["markdown"],
    )

    chunks = []
    for page in result.markdown.pages:
        chunks.append({
            "text": page.markdown,
            "metadata": {
                "source_file": pdf_path.name,
                "original_url": f"{BASE_URL}{pdf_path.name}",
                "page": page.page_number,
            },
        })

    return chunks


def save_markdown(pdf_path: Path, chunks: list[dict]):
    """Guardar el contenido parseado de un PDF como archivo .md con separadores de página."""
    md_content = f"# {pdf_path.stem}\n\n"
    for chunk in chunks:
        md_content += (
            f"--- Página {chunk['metadata']['page']} ---\n\n"
            f"{chunk['text']}\n\n"
        )

    out = MD_DIR / f"{pdf_path.stem}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(md_content)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"Encontrados {len(pdf_files)} PDFs en {PDF_DIR}")

    all_chunks = []

    for i, pdf in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Parseando: {pdf.name}")
        chunks = parse_pdf(pdf)
        all_chunks.extend(chunks)
        print(f"  -> {len(chunks)} chunks de página")

        # Guardar markdown por documento
        save_markdown(pdf, chunks)

        # Guardar JSON por documento
        json_path = JSON_DIR / f"{pdf.stem}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

    # Guardar JSON consolidado
    output_path = OUTPUT_DIR / "parsed_documents.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"JSON consolidado: {output_path}")
    print(f"Markdowns: {MD_DIR}")
    print(f"JSON por documento: {JSON_DIR}")


if __name__ == "__main__":
    main()
