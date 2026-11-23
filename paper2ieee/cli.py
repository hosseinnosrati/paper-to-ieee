import os
import sys
import argparse
from .parser import PaperParser
from .docx_builder import DocxBuilder
from .pdf_builder import PdfBuilder
from .latex_builder import LatexBuilder
from .validator import IEEEValidator

def print_banner():
    banner = r"""
========================================================================
   ____                                   ___    ___ _____ _____ _____ 
  |  _ \ __ _ _ __   ___ _ __            |__ \  |_ _| ____| ____| ____|
  | |_) / _` | '_ \ / _ \ '__|  _____      ) |   | ||  _| |  _| |  _|  
  |  __/ (_| | |_) |  __/ |    |_____|    / /    | || |___| |___| |___ 
  |_|   \__,_| .__/ \___|_|              |____| |___|_____|_____|_____|
             |_|                                                       
  Autonomous Markdown-to-IEEE Publication Engine | Version 1.0.0
========================================================================
"""
    print(banner)

SAMPLE_TEMPLATE = r"""---
title: "Autonomous Edge Telemetry and Signal Processing in Wireless Sensor Networks"
author: "Mohammad Hossein Nosrati"
affiliation: "School of Electrical Engineering, Iran University of Science and Technology (IUST), Tehran, Iran"
email: "nosrati_m@nt.iust.ac.ir"
journal: "IEEE Communications Letters / Transactions Template"
---

## Abstract
Continuous telemetry in resource-constrained wireless sensor networks requires severe optimization of the physical-layer radio transceiver power dissipation. While traditional Nyquist-rate sampling imposes high digital signal processing overhead, compressed acquisition shifts the computational complexity away from battery-operated edge sensor nodes. In this letter, we present an end-to-end telemetry architecture that guarantees deterministic latency and clinical waveform fidelity across lossy wireless fading channels. Experimental evaluation demonstrates over 50% on-air radio frequency payload reduction while maintaining a Percentage Root-Mean-Square Difference (PRD) strictly under 0.5%, far exceeding standard diagnostic fidelity thresholds.

## Index Terms
Compressive Sensing, Wireless Telemetry, Edge Computing, Signal Processing, Green Telecommunications.

# I. INTRODUCTION
Wearable sensor networks and wireless IoT nodes operate under strict energy and bandwidth budgets. In conventional wireless transmission standards such as Bluetooth Low Energy and LoRaWAN, the radio frequency power amplifier dominates battery drain. To mitigate on-air energy consumption without placing computational burden on integer microcontrollers, asymmetric signal processing architectures have emerged as an effective paradigm.

As demonstrated in our empirical analysis, pre-filtering and deterministic projection transform high-dimensional physiological waveforms into compact measurement vectors prior to radio frequency modulation.

# II. SYSTEM MODEL AND FORMULATION
Consider an N-dimensional digitized signal vector $x \in \mathbb{R}^N$. Under an orthonormal transform basis $\Psi$, the signal exhibits K-sparse representation such that:

$$y = \Phi \cdot x = \Phi \cdot \Psi \cdot s = \Theta \cdot s$$

where $\Phi \in \mathbb{R}^{M \times N}$ represents the non-adaptive sensing matrix with $M \ll N$.

# III. QUANTITATIVE EXPERIMENTAL BENCHMARKS
The proposed framework was benchmarked under realistic wireless fading channel simulations. As summarized in Table 1, the architecture resolves the classical throughput-energy bottleneck.

| Performance Metric | Proposed Framework | Benchmark Threshold |
| :--- | :---: | :---: |
| On-Air RF Payload Reduction | 50.0% to 70.0% | >40.0% Target |
| Encoding Execution Latency | 0.005 ms / block | <10.0 ms Real-Time Budget |
| Reconstruction Error (PRD) | 0.24% | <2.0% AAMI Standard |
| Reconstruction SNR | 52.3 dB | >35.0 dB Fidelity Boundary |

# IV. CONCLUSION
This paper presented an ultra-low-power telemetry pipeline for bandwidth-constrained sensor nodes. By combining integer-only matrix evaluation with gateway sparse reconstruction, the architecture extends sensor node operating lifetime by over 2.5x while preserving signal integrity.

# REFERENCES
[1] A. L. Goldberger et al., "PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals," Circulation, vol. 101, no. 23, pp. e215-e220, Jun. 2000.
[2] Z. Zhang, T. P. Jung, S. Makeig, and B. D. Rao, "Compressed sensing for energy-efficient wireless telemonitoring: A review," IEEE J. Biomed. Health Inform., vol. 17, no. 5, pp. 913-920, Sep. 2013.
[3] H. Mamaghanian, N. Khaled, D. Atienza, and P. Vandergheynst, "Compressed sensing for real-time ECG compression," IEEE Trans. Biomed. Eng., vol. 58, no. 9, pp. 2456-2466, Sep. 2011.
[4] D. L. Donoho, "Compressed sensing," IEEE Trans. Inf. Theory, vol. 52, no. 4, pp. 1289-1306, Apr. 2006.
[5] E. J. Candes and M. B. Wakin, "An introduction to compressive sampling," IEEE Signal Process. Mag., vol. 25, no. 2, pp. 21-30, Mar. 2008.
"""

def main():
    parser = argparse.ArgumentParser(description="Paper2IEEE: Convert Markdown to IEEE Transactions DOCX/PDF/LaTeX.")
    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")

    # Command: build
    p_build = subparsers.add_parser("build", help="Build publication-grade IEEE manuscript from Markdown")
    p_build.add_argument("input", help="Path to input Markdown file")
    p_build.add_argument("-o", "--output", help="Path to output PDF file (defaults to <name>.pdf)")
    p_build.add_argument("--docx", action="store_true", help="Generate IEEE two-column DOCX file")
    p_build.add_argument("--tex", action="store_true", help="Generate IEEEtran LaTeX .tex file")

    # Command: check / lint
    p_check = subparsers.add_parser("check", help="Lint Markdown paper against official IEEE author guidelines")
    p_check.add_argument("input", help="Path to input Markdown file")

    # Command: init
    p_init = subparsers.add_parser("init", help="Scaffold a new IEEE paper Markdown template")
    p_init.add_argument("path", nargs="?", default="paper.md", help="Destination path for template file")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    if args.command == "init":
        dest = args.path
        if os.path.exists(dest):
            print(f"[!] Warning: File {dest} already exists. Refusing to overwrite.")
            sys.exit(1)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(SAMPLE_TEMPLATE.strip())
        print(f"[+] Successfully scaffolded IEEE paper template: {dest}")
        print("    Run 'paper2ieee build " + dest + "' to compile!")
        sys.exit(0)

    if args.command == "check":
        if not os.path.exists(args.input):
            print(f"[X] Error: Input file '{args.input}' not found.")
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
        p = PaperParser(content)
        v = IEEEValidator(p)
        res = v.validate()
        print(f"\n[*] IEEE Author Center Compliance Report for '{args.input}':")
        print(f"    Status: {res['status']} | Total Issues: {res['total_issues']}")
        print(f"    Errors: {res['errors_count']} | Warnings: {res['warnings_count']}\n")
        for iss in res["issues"]:
            prefix = "[ERROR]" if iss["severity"] == "ERROR" else "[WARN] "
            print(f"    {prefix} {iss['msg']}")
        print("\n")
        sys.exit(0 if res["passed"] else 1)

    if args.command == "build":
        if not os.path.exists(args.input):
            print(f"[X] Error: Input file '{args.input}' not found.")
            sys.exit(1)

        print_banner()
        print(f"[*] Parsing input Markdown: {args.input}")
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()

        p = PaperParser(content)
        title = p.metadata.get("title", "Untitled")
        print(f"    Title: {title}")
        print(f"    Author: {p.metadata.get('author', 'Unknown')}")
        print(f"    Sections: {len(p.sections)} parsed | References: {len(p.references)} entries")

        base_name = os.path.splitext(args.input)[0]
        out_docx = base_name + ".docx"
        out_pdf = args.output if args.output else (base_name + ".pdf")
        out_tex = base_name + ".tex"

        # 1. Build DOCX
        print(f"[*] Generating IEEE Transactions Two-Column DOCX: {out_docx}")
        db = DocxBuilder(p)
        db.build(out_docx)
        print(f"    [+] Created: {out_docx} ({os.path.getsize(out_docx)} bytes)")

        # 2. Build PDF
        print(f"[*] Converting to Publication-Grade Vector PDF: {out_pdf}")
        success = PdfBuilder.convert_docx_to_pdf(out_docx, out_pdf)
        if success:
            print(f"    [+] Created: {out_pdf} ({os.path.getsize(out_pdf)} bytes)")
        else:
            print("    [!] Word COM not available; PDF conversion skipped (DOCX is ready).")

        # 3. Build TeX if requested
        if args.tex:
            print(f"[*] Generating IEEEtran LaTeX source: {out_tex}")
            lb = LatexBuilder(p)
            lb.build(out_tex)
            print(f"    [+] Created: {out_tex} ({os.path.getsize(out_tex)} bytes)")

        print("\n[V] BUILD COMPLETE! Your IEEE manuscript is ready for journal submission.\n")

if __name__ == "__main__":
    main()
