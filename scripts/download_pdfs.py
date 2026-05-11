#!/usr/bin/env python3
"""Descarga todos los PDF de protocolos desde ssmoc.redsalud.gob.cl."""

import urllib.request
from pathlib import Path

BASE_URL = "https://ssmoc.redsalud.gob.cl"
PDF_DIR = Path(__file__).parent.parent / "pdfs"

PDF_PATHS = [
    "/wp-content/uploads/2025/10/CRITERIOS-DE-REFERENCIA-DIABETES-2017.-ord.pdf",
    "/wp-content/uploads/2025/10/MANUAL-CONSOLIDADO-PATOLOGIAS-GES-V.1-2025.-firmas.pdf",
    "/wp-content/uploads/2025/10/MANUAL-CONSOLIDADO-PATOLOGIAS-GES-V.1-2025.-res.pdf",
    "/wp-content/uploads/2025/10/PROT-PACIENTE-CON-OBESIDAD-CANDIDATO-A-CIRUGIA-BARIATRICA-V.1-2024.pdf",
    "/wp-content/uploads/2025/10/PROT-ALTO-RIESGO-OBSTETRICO-V.1-2025-2.pdf",
    "/wp-content/uploads/2025/10/PROT-AMENORREA-2017.pdf",
    "/wp-content/uploads/2025/10/PROT-ATENCION-DE-VICTIMAS-DE-VIOLENCIA-SEXUAL-2024.pdf",
    "/wp-content/uploads/2025/10/PROT-CARDIOLOGIA-ADULTO-V.2-2021-2.pdf",
    "/wp-content/uploads/2025/10/PROT-CATEGORIZACION-DE-PACIENTES-EN-UNIDADES-DE-EMERGENCIA-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-ENDOCRINO-ADULTO-V.2-2019-2.pdf",
    "/wp-content/uploads/2025/10/PROT-GASTRO-ADULTO-V.2-2019-2.pdf",
    "/wp-content/uploads/2025/10/PROT-GENERACION-DE-LA-MACULA-DEL-OJO-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-GLAUCOMA-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-HEMATOLOGIA-ADULTO-V.1-2023-2.pdf",
    "/wp-content/uploads/2025/10/PROT-HIPERTIROIDISMO-2017.pdf",
    "/wp-content/uploads/2025/10/PROT-HOMBRO-DOLOROSO-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-NEFROLOGIA-ADULTO-V.1-2023-2.pdf",
    "/wp-content/uploads/2025/10/PROT-NEUROLOGIA-ADULTO-V.1-2018-2.pdf",
    "/wp-content/uploads/2025/10/PROT-OFTALMOLOGIA-V.1-2019-2.pdf",
    "/wp-content/uploads/2025/11/PROTOCOLO-REFCON-2024-res.pdf",
    "/wp-content/uploads/2025/10/PROT-REHABILITACION-AVE-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-REHABILITACION-INTEGRAL-V.1-2025.res_.pdf",
    "/wp-content/uploads/2025/10/PROT-SOSPECHA-DE-INTOXICACION-POR-ORGANOFOSFORADOS-2018.pdf",
    "/wp-content/uploads/2025/10/PROT-TRASTORNO-DE-CONDUCTA-2017.pdf",
    "/wp-content/uploads/2025/10/PROT-UROLOGIA-PEDIATRICA-V.1.res-2025.pdf",
    "/wp-content/uploads/2025/10/MANUAL-CONSOLIDADO-PATOLOGIAS-GES-2025.-firmas-1.pdf",
    "/wp-content/uploads/2025/10/MANUAL-CONSOLIDADO-PATOLOGIAS-GES-2025.-res-1.pdf",
    "/wp-content/uploads/2025/10/PROT-ALTO-RIESGO-OBSTETRICO-V.1-2025-1.pdf",
    "/wp-content/uploads/2025/10/PROT-CARDIOLOGIA-ADULTO-V.2-2021-1.pdf",
    "/wp-content/uploads/2025/10/PROT-ENDOCRINO-ADULTO-V.2-2019-1.pdf",
    "/wp-content/uploads/2025/10/PROT-GASTRO-ADULTO-V.2-2019-1.pdf",
    "/wp-content/uploads/2025/10/PROT-HEMATOLOGIA-ADULTO-V.1-2023-1.pdf",
    "/wp-content/uploads/2025/10/PROT-NEFROLOGIA-ADULTO-V.1-2023-1.pdf",
    "/wp-content/uploads/2025/10/PROT-NEUROLOGIA-ADULTO-V.1-2018-1.pdf",
    "/wp-content/uploads/2025/10/PROT-OFTALMOLOGIA-V.1-2019-1.pdf",
    "/wp-content/uploads/2025/10/PROT-REFCON-V.2-2024-1.pdf",
    "/wp-content/uploads/2025/10/PROT-REHABILITACION-INTEGRAL-2025.res_-1.pdf",
    "/wp-content/uploads/2025/10/PROTOCOLO-PACIENTE-CON-OBESIDAD-CANDIDATO-A-CIRUGIA-BARIATRICA-V.1-2024-1.pdf",
    "/wp-content/uploads/2025/11/PROTOCOLO-GESTION-DE-TIEMPO-DE-ESPERA-MINSAL-2025-res.pdf",
    "/wp-content/uploads/2025/11/PROT-OTORRINO-2025.pdf",
]


def main():
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    for path in PDF_PATHS:
        url = BASE_URL + path
        fname = Path(path).name
        dest = PDF_DIR / fname
        if dest.exists():
            print(f"Ya existe: {fname}")
            continue
        print(f"Descargando: {fname}")
        urllib.request.urlretrieve(url, str(dest))

    count = len(list(PDF_DIR.glob("*.pdf")))
    print(f"\nTotal PDFs en {PDF_DIR}: {count}")


if __name__ == "__main__":
    main()
