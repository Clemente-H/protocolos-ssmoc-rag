#!/usr/bin/env python3
"""Construye el índice de embeddings a partir de los documentos parseados."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.embed import build_index


def main():
    print("Construyendo índice de embeddings...")
    build_index()
    print("Indice listo. Puedes ejecutar streamlit app.py")


if __name__ == "__main__":
    main()
