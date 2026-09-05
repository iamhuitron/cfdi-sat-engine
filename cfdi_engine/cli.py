"""
Command Line Interface for CFDI SAT Engine.
"""

import argparse
import sys
import json
from pathlib import Path
from .parser import parse_cfdi_xml, CFDIParseError
from .validator import validate_cfdi_math
from .sat_blacklist import EFOSSentinel
from .reporter import format_terminal_audit

def main():
    parser = argparse.ArgumentParser(
        description="CFDI SAT Engine — Fiscal Auditor, Anexo 20 Math Validator & SAT Art. 69-B Sentinel",
        prog="cfdi-engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Audit a single CFDI XML file")
    audit_parser.add_argument("xml_path", type=str, help="Path to CFDI 4.0/3.3 XML file")
    audit_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # Command: batch
    batch_parser = subparsers.add_parser("batch", help="Audit a directory of CFDI XML files")
    batch_parser.add_argument("dir_path", type=str, help="Path to folder containing XML files")
    batch_parser.add_argument("--report", type=str, help="Save consolidated JSON report to file")

    # Command: check-rfc
    rfc_parser = subparsers.add_parser("check-rfc", help="Check RFC against SAT 69-B EFOS blacklist")
    rfc_parser.add_argument("rfc", type=str, help="RFC to query")

    args = parser.parse_args()

    sentinel = EFOSSentinel()

    if args.command == "audit":
        xml_file = Path(args.xml_path)
        if not xml_file.exists():
            print(f"Error: File not found: {xml_file}", file=sys.stderr)
            sys.exit(1)

        try:
            cfdi = parse_cfdi_xml(xml_file)
            validation = validate_cfdi_math(cfdi).to_dict()
            efos_emisor = sentinel.check_rfc(cfdi.get("emisor", {}).get("rfc", ""))
            efos_receptor = sentinel.check_rfc(cfdi.get("receptor", {}).get("rfc", ""))

            if args.json:
                result = {
                    "cfdi": {k: float(v) if hasattr(v, '__float__') else v for k, v in cfdi.items() if k != "conceptos"},
                    "validation": validation,
                    "efos_emisor": efos_emisor,
                    "efos_receptor": efos_receptor
                }
                print(json.dumps(result, indent=2, default=str))
            else:
                print(format_terminal_audit(cfdi, validation, efos_emisor, efos_receptor))

        except CFDIParseError as e:
            print(f"Error parsing CFDI: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "batch":
        target_dir = Path(args.dir_path)
        if not target_dir.exists():
            print(f"Error: Directory not found: {target_dir}", file=sys.stderr)
            sys.exit(1)

        xml_files = list(target_dir.glob("**/*.xml"))
        print(f"Auditing {len(xml_files)} CFDI XML files in {target_dir}...")
        
        passed = 0
        failed = 0
        efos_detected = 0

        for f in xml_files:
            try:
                cfdi = parse_cfdi_xml(f)
                val = validate_cfdi_math(cfdi)
                efos_e = sentinel.check_rfc(cfdi.get("emisor", {}).get("rfc", ""))
                efos_r = sentinel.check_rfc(cfdi.get("receptor", {}).get("rfc", ""))

                if efos_e or efos_r:
                    efos_detected += 1
                if val.is_valid and not efos_e:
                    passed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        print("\n" + "=" * 40)
        print(" RESUMEN DE AUDITORÍA MASIVA")
        print("=" * 40)
        print(f"Total procesados: {len(xml_files)}")
        print(f"Comprobantes conformes:  {passed}")
        print(f"Inconsistencias / Error: {failed}")
        print(f"Alertas EFOS detectadas: {efos_detected}")
        print("=" * 40)

    elif args.command == "check-rfc":
        rfc = args.rfc.strip().upper()
        found = sentinel.check_rfc(rfc)
        if found:
            print(f"🚨 ALERTA SAT 69-B: RFC '{rfc}' está registrado como EFOS!")
            print(f"Razón Social: {found.get('nombre')}")
            print(f"Situación:    {found.get('situacion')}")
            print(f"Oficio DOF:   {found.get('oficio_publicacion')}")
        else:
            print(f"✓ RFC '{rfc}' limpio. No figura en la lista negra de operaciones simuladas.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
