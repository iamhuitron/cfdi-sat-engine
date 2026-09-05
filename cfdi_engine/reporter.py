"""
Audit Reporter module.
Generates human-readable CLI summaries and machine-readable JSON reports.
"""

from typing import Dict, Any, List

def format_terminal_audit(cfdi: Dict[str, Any], validation: Dict[str, Any], efos_emisor: Any, efos_receptor: Any) -> str:
    lines = []
    lines.append("=" * 68)
    lines.append(" 🏛️  DICTAMEN FISCAL AUTOMATIZADO CFDI 4.0 / SAT")
    lines.append("=" * 68)
    
    # Overview
    lines.append(f"UUID:       {cfdi.get('uuid') or 'SIN TIMBRE DIGITAL'}")
    lines.append(f"Serie/Folio:{cfdi.get('serie', '')}-{cfdi.get('folio', '')} | Tipo: {cfdi.get('tipo_comprobante')} | Fecha: {cfdi.get('fecha')}")
    lines.append(f"Emisor:     {cfdi.get('emisor', {}).get('nombre')} ({cfdi.get('emisor', {}).get('rfc')})")
    lines.append(f"Receptor:   {cfdi.get('receptor', {}).get('nombre')} ({cfdi.get('receptor', {}).get('rfc')})")
    lines.append("-" * 68)
    
    # Amounts
    lines.append(f"SubTotal:   ${cfdi.get('subtotal', 0):,.2f} {cfdi.get('moneda')}")
    lines.append(f"Descuento:  ${cfdi.get('descuento', 0):,.2f}")
    lines.append(f"Traslados:  ${cfdi.get('impuestos', {}).get('total_trasladados', 0):,.2f}")
    lines.append(f"Retenciones:${cfdi.get('impuestos', {}).get('total_retenidos', 0):,.2f}")
    lines.append(f"TOTAL:      ${cfdi.get('total', 0):,.2f}")
    lines.append("-" * 68)

    # EFOS Sentinel Status
    lines.append("🛡️  ALERTA SAT ARTÍCULO 69-B (EFOS):")
    if efos_emisor:
        lines.append(f"  🚨 PELIGRO: Emisor en lista negra SAT! Situación: {efos_emisor['situacion']}")
        lines.append(f"     Oficio: {efos_emisor.get('oficio_publicacion')} | Fecha DOF: {efos_emisor.get('fecha_dof')}")
    else:
        lines.append("  ✓ Emisor: Limpio (No detectado en lista negra)")

    if efos_receptor:
        lines.append(f"  ⚠️  ADVERTENCIA: Receptor en lista SAT. Situación: {efos_receptor['situacion']}")
    else:
        lines.append("  ✓ Receptor: Limpio")

    lines.append("-" * 68)
    # Mathematical & Normative Validation
    lines.append("📐  INTEGRIDAD Y MATEMÁTICA ANEXO 20:")
    if validation["is_valid"]:
        lines.append("  ✓ Fórmulas cuadran exactamente. Todos los RFCs son válidos.")
    else:
        lines.append("  ❌ INCONSISTENCIAS DETECTADAS:")
        for issue in validation["issues"]:
            lines.append(f"     • {issue}")

    lines.append("=" * 68)
    return "\n".join(lines)
