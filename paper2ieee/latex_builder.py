import re
from .parser import PaperParser

class LatexBuilder:
    """Builds an authentic IEEEtran LaTeX (.tex) manuscript from parsed Markdown."""

    def __init__(self, parser: PaperParser):
        self.parser = parser

    def build(self, output_path: str):
        meta = self.parser.metadata
        title = meta.get("title", "Research Paper Title")
        author = meta.get("author", "Author Name")
        affiliation = meta.get("affiliation", "Department of Electrical Engineering, University Name")
        email = meta.get("email", "author@institution.edu")

        lines = [
            r"\documentclass[journal,twocolumn,10pt]{IEEEtran}",
            r"\usepackage{amsmath,amssymb,amsfonts}",
            r"\usepackage{algorithmic}",
            r"\usepackage{graphicx}",
            r"\usepackage{textcomp}",
            r"\usepackage{xcolor}",
            r"\usepackage{cite}",
            r"\usepackage{booktabs}",
            r"\usepackage{hyperref}",
            r"\hypersetup{colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue}",
            "",
            r"\begin{document}",
            "",
            f"\\title{{{title}}}",
            "",
            f"\\author{{{author},~\\IEEEmembership{{Member,~IEEE}}%",
            f"\\thanks{{{author} is with {affiliation} (e-mail: {email}).}}}}",
            "",
            r"\markboth{IEEE Transactions / Letters Formatted Manuscript}%",
            f"{{{author}: {title[:35]}...}}",
            "",
            r"\maketitle",
            ""
        ]

        # Abstract
        if self.parser.abstract:
            lines.extend([
                r"\begin{abstract}",
                self.parser.abstract,
                r"\end{abstract}",
                ""
            ])

        # Index Terms
        if self.parser.index_terms:
            terms_str = ", ".join(self.parser.index_terms)
            lines.extend([
                r"\begin{IEEEkeywords}",
                f"{terms_str}.",
                r"\end{IEEEkeywords}",
                ""
            ])

        # Sections
        for sec in self.parser.sections:
            stitle = sec["title"]
            # Clean leading roman numerals if present
            clean_title = re.sub(r"^[IVXLCDM]+\.\s*", "", stitle).strip()
            clean_title = re.sub(r"^[A-Z]\.\s*", "", clean_title).strip()

            if sec["level"] == 1:
                lines.append(f"\\section{{{clean_title}}}")
            elif sec["level"] == 2:
                lines.append(f"\\subsection{{{clean_title}}}")
            else:
                lines.append(f"\\subsubsection{{{clean_title}}}")

            for elem in sec["elements"]:
                etype = elem["type"]
                if etype == "paragraph":
                    lines.append(elem["text"])
                    lines.append("")
                elif etype == "equation":
                    raw_eq = elem["text"]
                    clean_eq = re.sub(r"\(\d+\)\s*$", "", raw_eq).strip()
                    lines.extend([
                        r"\begin{equation}",
                        clean_eq,
                        r"\end{equation}",
                        ""
                    ])
                elif etype == "figure":
                    fpath = elem["path"]
                    caption = elem["caption"]
                    lines.extend([
                        r"\begin{figure}[!t]",
                        r"\centering",
                        f"\\includegraphics[width=\\columnwidth]{{{fpath}}}",
                        f"\\caption{{{caption}}}",
                        r"\label{fig_demo}",
                        r"\end{figure}",
                        ""
                    ])
                elif etype == "table":
                    tdata = elem["data"]
                    headers = tdata.get("headers", [])
                    rows = tdata.get("rows", [])
                    cols_fmt = "c" * len(headers)
                    lines.extend([
                        r"\begin{table}[!t]",
                        r"\caption{Quantitative Benchmark Evaluation}",
                        r"\centering",
                        f"\\begin{{tabular}}{{{cols_fmt}}}",
                        r"\toprule",
                        " & ".join(headers) + r" \\",
                        r"\midrule"
                    ])
                    for row in rows:
                        lines.append(" & ".join(row) + r" \\")
                    lines.extend([
                        r"\bottomrule",
                        r"\end{tabular}",
                        r"\end{table}",
                        ""
                    ])

        # References
        if self.parser.references:
            lines.extend([
                r"\begin{thebibliography}{00}",
                ""
            ])
            for i, ref in enumerate(self.parser.references, 1):
                clean_ref = re.sub(r"^\[\d+\]\s*", "", ref).strip()
                lines.append(f"\\bibitem{{b{i}}} {clean_ref}")
            lines.extend([
                r"\end{thebibliography}",
                ""
            ])

        lines.append(r"\end{document}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output_path
