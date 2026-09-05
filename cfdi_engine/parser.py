"""
CFDI XML Parser module.
Extracts structured invoice and fiscal metadata from CFDI 4.0 and 3.3 XML files.
"""

import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pathlib import Path

CFDI_NAMESPACES = {
    "cfdi4": "http://www.sat.gob.mx/cfd/4",
    "cfdi3": "http://www.sat.gob.mx/cfd/3",
    "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
}

class CFDIParseError(Exception):
    pass

def parse_cfdi_xml(xml_source: str | bytes | Path) -> Dict[str, Any]:
    """
    Parses a CFDI XML document and returns a normalized dictionary of fiscal data.
    """
    try:
        if isinstance(xml_source, Path):
            tree = ET.parse(xml_source)
            root = tree.getroot()
        elif isinstance(xml_source, (str, bytes)):
            if isinstance(xml_source, str) and xml_source.strip().startswith("<"):
                root = ET.fromstring(xml_source)
            elif isinstance(xml_source, bytes) and xml_source.strip().startswith(b"<"):
                root = ET.fromstring(xml_source)
            else:
                path = Path(xml_source)
                tree = ET.parse(path)
                root = tree.getroot()
        else:
            raise CFDIParseError("Invalid XML input format.")
    except Exception as e:
        raise CFDIParseError(f"XML syntax error: {str(e)}") from e

    # Determine CFDI Version
    version = root.attrib.get("Version") or root.attrib.get("version", "4.0")
    
    # Strip namespace for clean tag traversal
    def local_tag(elem):
        return elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

    data: Dict[str, Any] = {
        "version": version,
        "uuid": None,
        "serie": root.attrib.get("Serie", ""),
        "folio": root.attrib.get("Folio", ""),
        "fecha": root.attrib.get("Fecha", ""),
        "tipo_comprobante": root.attrib.get("TipoDeComprobante", "I"),
        "metodo_pago": root.attrib.get("MetodoPago", ""),
        "forma_pago": root.attrib.get("FormaPago", ""),
        "moneda": root.attrib.get("Moneda", "MXN"),
        "subtotal": Decimal(root.attrib.get("SubTotal", "0.0")),
        "descuento": Decimal(root.attrib.get("Descuento", "0.0")),
        "total": Decimal(root.attrib.get("Total", "0.0")),
        "emisor": {},
        "receptor": {},
        "conceptos": [],
        "impuestos": {
            "total_trasladados": Decimal("0.0"),
            "total_retenidos": Decimal("0.0"),
            "traslados": [],
            "retenciones": []
        }
    }

    for child in root:
        tag = local_tag(child)
        if tag == "Emisor":
            data["emisor"] = {
                "rfc": child.attrib.get("Rfc", "").strip().upper(),
                "nombre": child.attrib.get("Nombre", ""),
                "regimen_fiscal": child.attrib.get("RegimenFiscal", "")
            }
        elif tag == "Receptor":
            data["receptor"] = {
                "rfc": child.attrib.get("Rfc", "").strip().upper(),
                "nombre": child.attrib.get("Nombre", ""),
                "domicilio_fiscal": child.attrib.get("DomicilioFiscalReceptor", ""),
                "regimen_fiscal": child.attrib.get("RegimenFiscalReceptor", ""),
                "uso_cfdi": child.attrib.get("UsoCFDI", "")
            }
        elif tag == "Conceptos":
            for concepto in child:
                if local_tag(concepto) == "Concepto":
                    data["conceptos"].append({
                        "clave_prod_serv": concepto.attrib.get("ClaveProdServ", ""),
                        "descripcion": concepto.attrib.get("Descripcion", ""),
                        "cantidad": Decimal(concepto.attrib.get("Cantidad", "1")),
                        "valor_unitario": Decimal(concepto.attrib.get("ValorUnitario", "0.0")),
                        "importe": Decimal(concepto.attrib.get("Importe", "0.0"))
                    })
        elif tag == "Impuestos":
            if "TotalImpuestosTrasladados" in child.attrib:
                data["impuestos"]["total_trasladados"] = Decimal(child.attrib["TotalImpuestosTrasladados"])
            if "TotalImpuestosRetenidos" in child.attrib:
                data["impuestos"]["total_retenidos"] = Decimal(child.attrib["TotalImpuestosRetenidos"])
            
            for sub in child:
                subtag = local_tag(sub)
                if subtag == "Traslados":
                    for t in sub:
                        data["impuestos"]["traslados"].append({
                            "impuesto": t.attrib.get("Impuesto", "002"),
                            "tipo_factor": t.attrib.get("TipoFactor", "Tasa"),
                            "tasa_o_cuota": Decimal(t.attrib.get("TasaOCuota", "0.160000")),
                            "importe": Decimal(t.attrib.get("Importe", "0.0"))
                        })
                elif subtag == "Retenciones":
                    for r in sub:
                        data["impuestos"]["retenciones"].append({
                            "impuesto": r.attrib.get("Impuesto", ""),
                            "importe": Decimal(r.attrib.get("Importe", "0.0"))
                        })
        elif tag == "Complemento":
            for comp in child:
                if local_tag(comp) == "TimbreFiscalDigital":
                    data["uuid"] = comp.attrib.get("UUID", "").strip().upper()
                    data["fecha_timbrado"] = comp.attrib.get("FechaTimbrado", "")
                    data["rfc_prov_certif"] = comp.attrib.get("RfcProvCertif", "")

    return data
