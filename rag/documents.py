"""
Registry de documentos disponibles.

Cada entrada agrupa uno o más archivos del mismo protocolo (e.g. parte 1 y parte 2
del mismo PDF escaneado) bajo un único identificador con nombre legible.
"""

from dataclasses import dataclass, field
from pathlib import Path

BASE_URL = "https://ssmoc.redsalud.gob.cl/medicos/"
MD_DIR = Path(__file__).parent.parent / "data" / "parsed" / "markdown"


@dataclass
class Documento:
    id: str
    label: str
    especialidad: str
    filenames: list[str]  # uno o más archivos que conforman este protocolo
    url: str = ""

    @property
    def md_paths(self) -> list[Path]:
        return [MD_DIR / f.replace(".pdf", ".md") for f in self.filenames]

    @property
    def display_url(self) -> str:
        return self.url or (BASE_URL + self.filenames[0])


DOCUMENTOS: list[Documento] = [
    # ── Cardiología ──────────────────────────────────────────────────────────
    Documento(
        id="cardiologia_adulto",
        label="Cardiología Adulto",
        especialidad="Cardiología",
        filenames=[
            "PROT-CARDIOLOGIA-ADULTO-V.2-2021-1.pdf",
            "PROT-CARDIOLOGIA-ADULTO-V.2-2021-2.pdf",
        ],
    ),
    # ── Endocrinología ───────────────────────────────────────────────────────
    Documento(
        id="endocrino_adulto",
        label="Endocrinología Adulto",
        especialidad="Endocrinología",
        filenames=[
            "PROT-ENDOCRINO-ADULTO-V.2-2019-1.pdf",
            "PROT-ENDOCRINO-ADULTO-V.2-2019-2.pdf",
        ],
    ),
    Documento(
        id="diabetes_criterios",
        label="Criterios de Derivación: Diabetes Tipo 2",
        especialidad="Endocrinología",
        filenames=["CRITERIOS-DE-REFERENCIA-DIABETES-2017.-ord.pdf"],
    ),
    Documento(
        id="hipertiroidismo",
        label="Hipertiroidismo",
        especialidad="Endocrinología",
        filenames=["PROT-HIPERTIROIDISMO-2017.pdf"],
    ),
    # ── Gastroenterología ────────────────────────────────────────────────────
    Documento(
        id="gastro_adulto",
        label="Gastroenterología Adulto",
        especialidad="Gastroenterología",
        filenames=[
            "PROT-GASTRO-ADULTO-V.2-2019-1.pdf",
            "PROT-GASTRO-ADULTO-V.2-2019-2.pdf",
        ],
    ),
    # ── Hematología ──────────────────────────────────────────────────────────
    Documento(
        id="hematologia_adulto",
        label="Hematología Adulto",
        especialidad="Hematología",
        filenames=[
            "PROT-HEMATOLOGIA-ADULTO-V.1-2023-1.pdf",
            "PROT-HEMATOLOGIA-ADULTO-V.1-2023-2.pdf",
        ],
    ),
    # ── Nefrología ───────────────────────────────────────────────────────────
    Documento(
        id="nefrologia_adulto",
        label="Nefrología Adulto",
        especialidad="Nefrología",
        filenames=[
            "PROT-NEFROLOGIA-ADULTO-V.1-2023-1.pdf",
            "PROT-NEFROLOGIA-ADULTO-V.1-2023-2.pdf",
        ],
    ),
    # ── Neurología ───────────────────────────────────────────────────────────
    Documento(
        id="neurologia_adulto",
        label="Neurología Adulto",
        especialidad="Neurología",
        filenames=[
            "PROT-NEUROLOGIA-ADULTO-V.1-2018-1.pdf",
            "PROT-NEUROLOGIA-ADULTO-V.1-2018-2.pdf",
        ],
    ),
    Documento(
        id="rehabilitacion_ave",
        label="Rehabilitación AVE",
        especialidad="Neurología",
        filenames=["PROT-REHABILITACION-AVE-2018.pdf"],
    ),
    # ── Oftalmología ─────────────────────────────────────────────────────────
    Documento(
        id="oftalmologia",
        label="Oftalmología",
        especialidad="Oftalmología",
        filenames=[
            "PROT-OFTALMOLOGIA-V.1-2019-1.pdf",
            "PROT-OFTALMOLOGIA-V.1-2019-2.pdf",
        ],
    ),
    Documento(
        id="macula_ojo",
        label="Degeneración Macular",
        especialidad="Oftalmología",
        filenames=["PROT-GENERACION-DE-LA-MACULA-DEL-OJO-2018.pdf"],
    ),
    Documento(
        id="glaucoma",
        label="Glaucoma",
        especialidad="Oftalmología",
        filenames=["PROT-GLAUCOMA-2018.pdf"],
    ),
    # ── Otorrinolaringología ─────────────────────────────────────────────────
    Documento(
        id="otorrino",
        label="Otorrinolaringología",
        especialidad="Otorrinolaringología",
        filenames=["PROT-OTORRINO-2025.pdf"],
    ),
    # ── Obstetricia ──────────────────────────────────────────────────────────
    Documento(
        id="alto_riesgo_obstetrico",
        label="Alto Riesgo Obstétrico",
        especialidad="Obstetricia",
        filenames=[
            "PROT-ALTO-RIESGO-OBSTETRICO-V.1-2025-1.pdf",
            "PROT-ALTO-RIESGO-OBSTETRICO-V.1-2025-2.pdf",
        ],
    ),
    Documento(
        id="amenorrea",
        label="Amenorrea",
        especialidad="Obstetricia",
        filenames=["PROT-AMENORREA-2017.pdf"],
    ),
    # ── Traumatología / Rehabilitación ───────────────────────────────────────
    Documento(
        id="hombro_doloroso",
        label="Hombro Doloroso",
        especialidad="Traumatología",
        filenames=["PROT-HOMBRO-DOLOROSO-2018.pdf"],
    ),
    Documento(
        id="rehabilitacion_integral",
        label="Rehabilitación Integral",
        especialidad="Rehabilitación",
        filenames=[
            "PROT-REHABILITACION-INTEGRAL-2025.res_-1.pdf",
            "PROT-REHABILITACION-INTEGRAL-V.1-2025.res_.pdf",
        ],
    ),
    # ── Urología ─────────────────────────────────────────────────────────────
    Documento(
        id="urologia_pediatrica",
        label="Urología Pediátrica",
        especialidad="Urología",
        filenames=["PROT-UROLOGIA-PEDIATRICA-V.1.res-2025.pdf"],
    ),
    # ── Salud Mental ─────────────────────────────────────────────────────────
    Documento(
        id="trastorno_conducta",
        label="Trastorno de Conducta",
        especialidad="Salud Mental",
        filenames=["PROT-TRASTORNO-DE-CONDUCTA-2017.pdf"],
    ),
    # ── Cirugía ──────────────────────────────────────────────────────────────
    Documento(
        id="cirugia_bariatrica",
        label="Cirugía Bariátrica (Obesidad)",
        especialidad="Cirugía",
        filenames=[
            "PROT-PACIENTE-CON-OBESIDAD-CANDIDATO-A-CIRUGIA-BARIATRICA-V.1-2024.pdf",
            "PROTOCOLO-PACIENTE-CON-OBESIDAD-CANDIDATO-A-CIRUGIA-BARIATRICA-V.1-2024-1.pdf",
        ],
    ),
    # ── Urgencias ────────────────────────────────────────────────────────────
    Documento(
        id="categorizacion_urgencias",
        label="Categorización Pacientes en Urgencias",
        especialidad="Urgencias",
        filenames=["PROT-CATEGORIZACION-DE-PACIENTES-EN-UNIDADES-DE-EMERGENCIA-2018.pdf"],
    ),
    Documento(
        id="intoxicacion_organofosforados",
        label="Intoxicación por Organofosforados",
        especialidad="Urgencias",
        filenames=["PROT-SOSPECHA-DE-INTOXICACION-POR-ORGANOFOSFORADOS-2018.pdf"],
    ),
    # ── Violencia / Social ───────────────────────────────────────────────────
    Documento(
        id="violencia_sexual",
        label="Atención Víctimas de Violencia Sexual",
        especialidad="Salud Pública",
        filenames=["PROT-ATENCION-DE-VICTIMAS-DE-VIOLENCIA-SEXUAL-2024.pdf"],
    ),
    # ── Gestión / Administrativo ─────────────────────────────────────────────
    Documento(
        id="refcon",
        label="Referencia y Contrarreferencia (REFCON)",
        especialidad="Gestión",
        filenames=[
            "PROT-REFCON-V.2-2024-1.pdf",
            "PROTOCOLO-REFCON-2024-res.pdf",
        ],
    ),
    Documento(
        id="tiempos_espera",
        label="Gestión de Tiempos de Espera MINSAL",
        especialidad="Gestión",
        filenames=["PROTOCOLO-GESTION-DE-TIEMPO-DE-ESPERA-MINSAL-2025-res.pdf"],
    ),
    Documento(
        id="ges_manual",
        label="Manual Consolidado Patologías GES",
        especialidad="Gestión",
        filenames=[
            "MANUAL-CONSOLIDADO-PATOLOGIAS-GES-2025.-res-1.pdf",
            "MANUAL-CONSOLIDADO-PATOLOGIAS-GES-2025.-firmas-1.pdf",
            "MANUAL-CONSOLIDADO-PATOLOGIAS-GES-V.1-2025.-res.pdf",
            "MANUAL-CONSOLIDADO-PATOLOGIAS-GES-V.1-2025.-firmas.pdf",
        ],
    ),
]

# ── Helpers ──────────────────────────────────────────────────────────────────

_by_id: dict[str, Documento] = {d.id: d for d in DOCUMENTOS}
_by_filename: dict[str, Documento] = {
    fname: doc for doc in DOCUMENTOS for fname in doc.filenames
}


def get_by_id(doc_id: str) -> Documento | None:
    return _by_id.get(doc_id)


def get_by_filename(filename: str) -> Documento | None:
    return _by_filename.get(filename)


def especialidades() -> list[str]:
    seen = []
    for d in DOCUMENTOS:
        if d.especialidad not in seen:
            seen.append(d.especialidad)
    return seen


def documentos_por_especialidad() -> dict[str, list[Documento]]:
    result: dict[str, list[Documento]] = {}
    for d in DOCUMENTOS:
        result.setdefault(d.especialidad, []).append(d)
    return result
