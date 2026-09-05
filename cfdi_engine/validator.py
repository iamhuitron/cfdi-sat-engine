"""
Fiscal and Mathematical Validator module.
Validates Anexo 20 compliance, RFC formats, and tax reconciliation formulas.
"""

import re
from decimal import Decimal
from typing import Dict, Any, List

RFC_MORAL_REGEX = re.compile(r'^[A-Z&Ñ]{3}\d{6}[A-Z0-9]{3}$')
RFC_FISICA_REGEX = re.compile(r'^[A-Z&Ñ]{4}\d{6}[A-Z0-9]{3}$')
RFC_GENERICOS = {"XAXX010101000", "XEXX010101000"}

UUID_REGEX = re.compile(r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$')

class ValidationResult:
    def __init__(self, is_valid: bool, issues: List[str], discrepancies: Dict[str, Any]):
        self.is_valid = is_valid
        self.issues = issues
        self.discrepancies = discrepancies

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "issues": self.issues,
            "discrepancies": self.discrepancies
        }

def validate_rfc(rfc: str) -> bool:
    if not rfc:
        return False
    rfc_clean = rfc.strip().upper()
    if rfc_clean in RFC_GENERICOS:
        return True
    if len(rfc_clean) == 12:
        return bool(RFC_MORAL_REGEX.match(rfc_clean))
    if len(rfc_clean) == 13:
        return bool(RFC_FISICA_REGEX.match(rfc_clean))
    return False

def validate_cfdi_math(cfdi: Dict[str, Any], tolerance: Decimal = Decimal("0.05")) -> ValidationResult:
    issues = []
    discrepancies = {}

    # 1. Validate RFCs
    emisor_rfc = cfdi.get("emisor", {}).get("rfc", "")
    receptor_rfc = cfdi.get("receptor", {}).get("rfc", "")

    if not validate_rfc(emisor_rfc):
        issues.append(f"RFC de Emisor inválido: '{emisor_rfc}'")
    if not validate_rfc(receptor_rfc):
        issues.append(f"RFC de Receptor inválido: '{receptor_rfc}'")

    # 2. Validate UUID
    uuid = cfdi.get("uuid")
    if uuid and not UUID_REGEX.match(uuid):
        issues.append(f"Formato de UUID inválido en TimbreFiscalDigital: '{uuid}'")

    # 3. Sum of Conceptos vs SubTotal
    conceptos = cfdi.get("conceptos", [])
    if conceptos:
        calc_subtotal = sum(c.get("importe", Decimal("0.0")) for c in conceptos)
        diff_subtotal = abs(calc_subtotal - cfdi["subtotal"])
        if diff_subtotal > tolerance:
            issues.append(
                f"Discrepancia en SubTotal: Suma de conceptos ({calc_subtotal}) difiere del declarado ({cfdi['subtotal']})"
            )
            discrepancies["subtotal"] = {
                "declarado": float(cfdi["subtotal"]),
                "calculado": float(calc_subtotal),
                "diferencia": float(diff_subtotal)
            }

    # 4. Anexo 20 Total Formula: Total = SubTotal - Descuento + ImpuestosTrasladados - ImpuestosRetenidos
    subtotal = cfdi.get("subtotal", Decimal("0.0"))
    descuento = cfdi.get("descuento", Decimal("0.0"))
    total_traslados = cfdi.get("impuestos", {}).get("total_trasladados", Decimal("0.0"))
    total_retenciones = cfdi.get("impuestos", {}).get("total_retenidos", Decimal("0.0"))
    total_declarado = cfdi.get("total", Decimal("0.0"))

    # If total_traslados wasn't declared in the root attribute, sum from traslados list
    if total_traslados == Decimal("0.0") and cfdi.get("impuestos", {}).get("traslados"):
        total_traslados = sum(t.get("importe", Decimal("0.0")) for t in cfdi["impuestos"]["traslados"])

    if total_retenciones == Decimal("0.0") and cfdi.get("impuestos", {}).get("retenciones"):
        total_retenciones = sum(r.get("importe", Decimal("0.0")) for r in cfdi["impuestos"]["retenciones"])

    calc_total = subtotal - descuento + total_traslados - total_retenciones
    diff_total = abs(calc_total - total_declarado)

    if diff_total > tolerance:
        issues.append(
            f"Fórmula de Total no cuadra (Anexo 20): Calculado ({calc_total}) != Declarado ({total_declarado})"
        )
        discrepancies["total"] = {
            "declarado": float(total_declarado),
            "calculado": float(calc_total),
            "diferencia": float(diff_total)
        }

    is_valid = len(issues) == 0
    return ValidationResult(is_valid, issues, discrepancies)
