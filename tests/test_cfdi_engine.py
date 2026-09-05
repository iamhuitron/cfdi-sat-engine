"""
Unit Test Suite for CFDI SAT Engine.
"""

import unittest
from pathlib import Path
from decimal import Decimal

from cfdi_engine.parser import parse_cfdi_xml, CFDIParseError
from cfdi_engine.validator import validate_rfc, validate_cfdi_math
from cfdi_engine.sat_blacklist import EFOSSentinel

FIXTURES_DIR = Path(__file__).parent / "fixtures"

class TestCFDIEngine(unittest.TestCase):

    def setUp(self):
        self.sentinel = EFOSSentinel()

    def test_rfc_validation(self):
        # Moral
        self.assertTrue(validate_rfc("MAS850101XYZ"))
        self.assertTrue(validate_rfc("AAA010101AAA"))
        # Física
        self.assertTrue(validate_rfc("DEHI030915XYZ"))
        # Genéricos
        self.assertTrue(validate_rfc("XAXX010101000"))
        self.assertTrue(validate_rfc("XEXX010101000"))
        # Inválidos
        self.assertFalse(validate_rfc("INVALID_RFC"))
        self.assertFalse(validate_rfc("12345"))
        self.assertFalse(validate_rfc(""))

    def test_parse_valid_cfdi40(self):
        valid_xml = FIXTURES_DIR / "sample_valid.xml"
        data = parse_cfdi_xml(valid_xml)

        self.assertEqual(data["version"], "4.0")
        self.assertEqual(data["emisor"]["rfc"], "MAS850101XYZ")
        self.assertEqual(data["receptor"]["rfc"], "CTE900202ABC")
        self.assertEqual(data["subtotal"], Decimal("1000.00"))
        self.assertEqual(data["total"], Decimal("1160.00"))
        self.assertEqual(data["uuid"], "9B8A7C6D-5E4F-4A3B-2C1D-0E9F8A7B6C5D")

    def test_math_validation_valid(self):
        valid_xml = FIXTURES_DIR / "sample_valid.xml"
        cfdi = parse_cfdi_xml(valid_xml)
        val = validate_cfdi_math(cfdi)
        self.assertTrue(val.is_valid)
        self.assertEqual(len(val.issues), 0)

    def test_math_validation_invalid(self):
        invalid_xml = FIXTURES_DIR / "sample_invalid_math.xml"
        cfdi = parse_cfdi_xml(invalid_xml)
        val = validate_cfdi_math(cfdi)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("RFC de Emisor inválido" in issue for issue in val.issues))
        self.assertTrue(any("Fórmula de Total no cuadra" in issue for issue in val.issues))

    def test_efos_detection(self):
        efos_xml = FIXTURES_DIR / "sample_efos.xml"
        cfdi = parse_cfdi_xml(efos_xml)
        flagged = self.sentinel.check_rfc(cfdi["emisor"]["rfc"])

        self.assertIsNotNone(flagged)
        self.assertEqual(flagged["situacion"], "Definitivo")
        self.assertIn("FANTASMA", flagged["nombre"])

    def test_clean_rfc_not_flagged(self):
        flagged = self.sentinel.check_rfc("MAS850101XYZ")
        self.assertIsNone(flagged)

if __name__ == "__main__":
    unittest.main()
