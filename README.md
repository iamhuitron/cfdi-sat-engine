# 🛡️ CFDI SAT Engine

[![CI](https://github.com/iamhuitron/cfdi-sat-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/iamhuitron/cfdi-sat-engine/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![SAT CFDI 4.0](https://img.shields.io/badge/CFDI-4.0%20%2F%203.3-orange.svg)](http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20.htm)

> **High-performance Mexican CFDI 4.0 / 3.3 fiscal auditor, Anexo 20 math validator, and official SAT Article 69-B (EFOS) sentinel.** Zero external runtime dependencies. 100% standard library Python.


> 🌐 **Fiscal Ecosystem — Looking for an in-browser interactive Web UI with Excel export?**  
> Check out **[CFDI Sentinel](https://github.com/iamhuitron/cfdi-sentinel)**: Our 100% client-side Next.js / React 19 web application for drag-and-drop XML/ZIP auditing, visual KPI dashboards, and DIOT calculation with zero server exposure.


Created by **[Ian Miguel Delgado Huitron](https://portfolio-pink-five-jaih91sunw.vercel.app/)** (@iamhuitron)  
*UNAM Informatics undergraduate & Fiscal Accounting Specialist.*

---

## ⚡ Key Highlights

* **Zero Third-Party Dependencies:** Powered strictly by Python's standard library (`xml.etree.ElementTree`, `decimal`, `csv`, `re`). Ultra-fast execution and zero supply-chain risk.
* **$O(1)$ SAT 69-B (EFOS) Sentinel:** Instant cross-referencing against official blacklists for simulated fiscal operations (*Definitivo, Desvirtuado, Presunto*).
* **Anexo 20 Mathematical Precision:** High-precision Decimal verification of:
  $$\text{SubTotal} - \text{Descuento} + \sum \text{Traslados} - \sum \text{Retenciones} = \text{Total}$$
* **RFC Format Intelligence:** Regex validation distinguishing Persona Moral (12 chars), Persona Física (13 chars), and generic RFCs (`XAXX010101000`, `XEXX010101000`).
* **High-Throughput Batch Auditing:** Audit thousands of XML invoices in seconds with consolidated terminal and JSON summaries.

---

## 🏗️ Architecture

```
                      ┌────────────────────────────────┐
                      │    CFDI 4.0 / 3.3 XML File     │
                      └───────────────┬────────────────┘
                                      │
                                      ▼
                        [ cfdi_engine.parser ]
                       (Namespace-Free AST Parser)
                                      │
                   ┌──────────────────┴──────────────────┐
                   ▼                                     ▼
        [ cfdi_engine.validator ]             [ cfdi_engine.sat_blacklist ]
        - Anexo 20 Math Check                 - SAT Art. 69-B Hash Map O(1)
        - RFC Syntax Validation               - Situación: Definitivo/Presunto
        - UUID RFC-4122 Check                 - Oficio DOF & Publicación
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      ▼
                        [ cfdi_engine.reporter ]
                       - CLI Visual Audit Report
                       - Structured JSON Export
```

---

## 🚀 Quick Start

### 1. Installation
Clone the repository:
```bash
git clone https://github.com/iamhuitron/cfdi-sat-engine.git
cd cfdi-sat-engine
```

### 2. Audit a single CFDI XML:
```bash
python3 -m cfdi_engine.cli audit tests/fixtures/sample_efos.xml
```

**Terminal Output:**
```text
====================================================================
 🏛️  DICTAMEN FISCAL AUTOMATIZADO CFDI 4.0 / SAT
====================================================================
UUID:       9B8A7C6D-5E4F-4A3B-2C1D-0E9F8A7B6C5D
Serie/Folio:F-999 | Tipo: I | Fecha: 2026-03-01T12:00:00
Emisor:     DISTRIBUIDORA COMERCIAL FANTASMA SA DE CV (XEF980101XYZ)
Receptor:   CLIENTE EJEMPLAR SA DE CV (CTE900202ABC)
--------------------------------------------------------------------
SubTotal:   $50,000.00 MXN
Descuento:  $0.00
Traslados:  $8,000.00
Retenciones:$0.00
TOTAL:      $58,000.00
--------------------------------------------------------------------
🛡️  ALERTA SAT ARTÍCULO 69-B (EFOS):
  🚨 PELIGRO: Emisor en lista negra SAT! Situación: Definitivo
     Oficio: 500-05-2023-14523 | Fecha DOF: 2023-04-15
  ✓ Receptor: Limpio
--------------------------------------------------------------------
📐  INTEGRIDAD Y MATEMÁTICA ANEXO 20:
  ✓ Fórmulas cuadran exactamente. Todos los RFCs son válidos.
====================================================================
```

### 3. Output as JSON for integration with APIs or databases:
```bash
python3 -m cfdi_engine.cli audit tests/fixtures/sample_valid.xml --json
```

### 4. Audit an entire directory of invoices:
```bash
python3 -m cfdi_engine.cli batch /path/to/invoices_folder/
```

### 5. Check any RFC directly against the SAT 69-B Blacklist:
```bash
python3 -m cfdi_engine.cli check-rfc XEF980101XYZ
```

---

## 🐍 Python API Usage

```python
from pathlib import Path
from cfdi_engine.parser import parse_cfdi_xml
from cfdi_engine.validator import validate_cfdi_math
from cfdi_engine.sat_blacklist import EFOSSentinel

# 1. Parse CFDI
cfdi = parse_cfdi_xml(Path("tests/fixtures/sample_valid.xml"))

# 2. Validate Anexo 20 Math
result = validate_cfdi_math(cfdi)
if not result.is_valid:
    print(f"Inconsistencias: {result.issues}")

# 3. Screen for Tax Fraud / EFOS
sentinel = EFOSSentinel()
flagged = sentinel.check_rfc(cfdi["emisor"]["rfc"])
if flagged:
    print(f"ALERTA: Proveedor catalogado como EFOS: {flagged['situacion']}")
```

---

## 🧪 Running Tests

```bash
python3 -m unittest discover -s tests -v
```

All tests execute in milliseconds using standard `unittest`.

---

## 📄 License
MIT License. Created by [Ian Miguel Delgado Huitron](https://github.com/iamhuitron).
