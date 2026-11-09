# CFDI SAT Engine

<p align="left">
  <strong>High-Throughput Mexican CFDI 4.0 / 3.3 Fiscal Auditor & SAT Art. 69-B (EFOS) Sentinel</strong><br>
  Open-Source Engine by <a href="https://github.com/iamhuitron"><strong>Ian Miguel Delgado Huitrón</strong></a> · Co-Founder at <a href="https://github.com/Xaol-Studio"><strong>@Xaol-Studio</strong></a>
</p>

<p align="left">
  <a href="https://github.com/iamhuitron"><img src="https://img.shields.io/badge/AUTHOR-@iamhuitron-1D1A16?style=for-the-badge&logo=github&logoColor=D4B87A&labelColor=141210" alt="Author" /></a>
  <a href="https://github.com/Xaol-Studio"><img src="https://img.shields.io/badge/STUDIO-@Xaol--Studio-B89758?style=for-the-badge&logo=github&logoColor=FAF8F5&labelColor=141210" alt="Studio" /></a>
</p>

<p align="left">
  <a href="https://github.com/iamhuitron/cfdi-sat-engine/actions/workflows/ci.yml"><img src="https://img.shields.io/badge/CI-Passing-1B3B2B?style=flat-square&logo=githubactions&logoColor=D4B87A&labelColor=141210" alt="CI" /></a>
  <img src="https://img.shields.io/badge/Python-3.10+-1D1A16?style=flat-square&logo=python&logoColor=D4B87A&labelColor=141210" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Dependencies-Zero_External_(Stdlib)-1D1A16?style=flat-square&labelColor=141210&logoColor=D4B87A" alt="Dependencies" />
  <img src="https://img.shields.io/badge/SAT_Audit-Anexo_20_&_Art._69B-611624?style=flat-square&labelColor=141210&logoColor=FAF8F5" alt="SAT Audit" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-1D1A16?style=flat-square&labelColor=141210&logoColor=D4B87A" alt="License" /></a>
</p>

> **High-performance Mexican CFDI 4.0 / 3.3 fiscal auditor, Anexo 20 math validator, and official SAT Article 69-B (EFOS) sentinel.** Zero external runtime dependencies. 100% standard library Python.

> 🌐 **Fiscal Ecosystem — Looking for an in-browser interactive Web UI with Excel export?**  
> Check out **[CFDI Sentinel](https://github.com/iamhuitron/cfdi-sentinel)**: Our 100% client-side Next.js / React 19 web application for drag-and-drop XML/ZIP auditing, visual KPI dashboards, and DIOT calculation with zero server exposure. Demo: [xaol-website.vercel.app/demo/sat-sentinel.html](https://xaol-website.vercel.app/demo/sat-sentinel.html)

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

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#141210', 'primaryTextColor': '#FAF8F5', 'primaryBorderColor': '#B89758', 'lineColor': '#B89758', 'secondaryColor': '#1D1A16', 'tertiaryColor': '#0D0C0A', 'mainBkg': '#141210', 'nodeBorder': '#B89758', 'clusterBkg': '#0D0C0A', 'clusterBorder': '#262420', 'titleColor': '#D4B87A', 'edgeLabelBackground': '#141210', 'fontFamily': 'JetBrains Mono, Plus Jakarta Sans, sans-serif' }}}%%
flowchart TD
    A["CFDI 4.0 / 3.3 XML Input"] --> B["cfdi_engine.parser<br/>(Namespace-Free AST Parser)"]
    B --> C["cfdi_engine.validator<br/>Anexo 20 Decimal Math · RFC Regex · UUID RFC-4122"]
    B --> D["cfdi_engine.sat_blacklist<br/>O(1) Hash Map · Art. 69-B (Definitivo / Presunto)"]
    C & D --> E["cfdi_engine.reporter<br/>CLI Dictamen Fiscal & Structured JSON Export"]
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
