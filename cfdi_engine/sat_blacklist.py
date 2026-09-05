"""
SAT Article 69-B Sentinel (EFOS - Empresas que Facturan Operaciones Simuladas).
Maintains an in-memory hash set and lookup engine for high-speed O(1) risk assessment.
"""

import csv
from pathlib import Path
from typing import Dict, Any, Optional

# Sample confirmed EFOS from official Diario Oficial de la Federación for local testing
SAMPLE_EFOS_DB = {
    "XEF980101XYZ": {
        "nombre": "DISTRIBUIDORA COMERCIAL FANTASMA SA DE CV",
        "situacion": "Definitivo",
        "oficio_publicacion": "500-05-2023-14523",
        "fecha_dof": "2023-04-15"
    },
    "FFS101010ABC": {
        "nombre": "SERVICIOS LOGISTICOS SIMULADOS SA DE CV",
        "situacion": "Definitivo",
        "oficio_publicacion": "500-05-2024-00124",
        "fecha_dof": "2024-01-18"
    },
    "PRE050505123": {
        "nombre": "CONSTRUCTORA BAJO INVESTIGACION SA DE CV",
        "situacion": "Presunto",
        "oficio_publicacion": "500-05-2025-08912",
        "fecha_dof": "2025-08-20"
    },
    "DES121212789": {
        "nombre": "COMERCIALIZADORA ACLARADA SA DE CV",
        "situacion": "Desvirtuado",
        "oficio_publicacion": "500-05-2022-04512",
        "fecha_dof": "2022-11-03"
    }
}

class EFOSSentinel:
    def __init__(self, csv_path: Optional[Path] = None):
        self.blacklist: Dict[str, Dict[str, Any]] = dict(SAMPLE_EFOS_DB)
        if csv_path and csv_path.exists():
            self.load_from_sat_csv(csv_path)

    def load_from_sat_csv(self, csv_path: Path):
        """
        Parses official SAT 69-B CSV format.
        Expected columns: No, RFC, Nombre del Contribuyente, Situación del contribuyente, ...
        """
        try:
            with open(csv_path, mode="r", encoding="latin-1") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 4:
                        rfc = row[1].strip().upper()
                        nombre = row[2].strip()
                        situacion = row[3].strip()
                        self.blacklist[rfc] = {
                            "nombre": nombre,
                            "situacion": situacion,
                            "oficio_publicacion": row[4] if len(row) > 4 else "N/A",
                            "fecha_dof": row[5] if len(row) > 5 else "N/A"
                        }
        except Exception as e:
            print(f"Warning: Could not parse SAT CSV: {e}")

    def check_rfc(self, rfc: str) -> Optional[Dict[str, Any]]:
        """
        O(1) search for an RFC. Returns EFOS metadata if flagged, None if clean.
        """
        if not rfc:
            return None
        return self.blacklist.get(rfc.strip().upper())
