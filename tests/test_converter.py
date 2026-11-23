import os
import unittest
from paper2ieee.parser import PaperParser
from paper2ieee.docx_builder import DocxBuilder
from paper2ieee.latex_builder import LatexBuilder
from paper2ieee.validator import IEEEValidator

SAMPLE_MD = """---
title: "Autonomous Edge Telemetry"
author: "Mohammad Hossein Nosrati"
affiliation: "Iran University of Science and Technology (IUST)"
email: "nosrati_m@nt.iust.ac.ir"
---

## Abstract
Continuous telemetry in resource-constrained wireless sensor networks requires severe optimization of physical layer radio transceiver power dissipation. As demonstrated in this work, compressive projection transforms high-dimensional physiological waveforms into compact measurement vectors prior to radio frequency modulation, achieving over 50% on-air payload reduction.

## Index Terms
Compressive Sensing, Wireless Telemetry, Signal Processing.

# I. INTRODUCTION
Wearable sensor networks operate under strict energy and bandwidth budgets. As shown in Fig. 1 and Table 1, the architecture resolves the classical throughput-energy trade-off.

# II. BENCHMARKS
The results are verified in Table 1.

| Metric | Proposed | Target |
| :--- | :---: | :---: |
| Compression | 50% | 40% |
| PRD Error | 0.24% | 2.0% |

# REFERENCES
[1] A. L. Goldberger et al., "PhysioBank," Circulation, vol. 101, 2000.
[2] Z. Zhang et al., "Compressed sensing review," IEEE JBHI, 2013.
[3] H. Mamaghanian et al., "Real-time ECG compression," IEEE TBME, 2011.
[4] D. L. Donoho, "Compressed sensing," IEEE TIT, 2006.
[5] E. J. Candes et al., "Compressive sampling," IEEE SPM, 2008.
"""

class TestPaper2IEEE(unittest.TestCase):

    def setUp(self):
        self.parser = PaperParser(SAMPLE_MD)

    def test_metadata_extraction(self):
        self.assertEqual(self.parser.metadata.get("author"), "Mohammad Hossein Nosrati")
        self.assertEqual(self.parser.metadata.get("title"), "Autonomous Edge Telemetry")
        self.assertTrue(len(self.parser.abstract) > 50)
        self.assertEqual(len(self.parser.index_terms), 3)

    def test_section_parsing(self):
        self.assertGreaterEqual(len(self.parser.sections), 2)
        self.assertEqual(len(self.parser.references), 5)

    def test_validator(self):
        val = IEEEValidator(self.parser)
        report = val.validate()
        self.assertTrue(report["passed"])
        self.assertEqual(report["errors_count"], 0)

    def test_docx_generation(self):
        builder = DocxBuilder(self.parser)
        out_path = "test_output.docx"
        builder.build(out_path)
        self.assertTrue(os.path.exists(out_path))
        self.assertGreater(os.path.getsize(out_path), 5000)
        os.remove(out_path)

    def test_latex_generation(self):
        builder = LatexBuilder(self.parser)
        out_path = "test_output.tex"
        builder.build(out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(r"\documentclass[journal,twocolumn,10pt]{IEEEtran}", content)
        self.assertIn("Mohammad Hossein Nosrati", content)
        os.remove(out_path)

if __name__ == "__main__":
    unittest.main()
