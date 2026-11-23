import re
from typing import List, Dict, Any
from .parser import PaperParser

class IEEEValidator:
    """Validates research manuscripts against official IEEE Author Center guidelines."""

    def __init__(self, parser: PaperParser):
        self.parser = parser
        self.issues: List[Dict[str, str]] = []

    def validate(self) -> Dict[str, Any]:
        self.issues = []
        self._check_metadata()
        self._check_abstract()
        self._check_keywords()
        self._check_citations()
        self._check_references()

        has_errors = any(i["severity"] == "ERROR" for i in self.issues)
        has_warnings = any(i["severity"] == "WARNING" for i in self.issues)

        return {
            "passed": not has_errors,
            "status": "PASSED" if not has_errors else "FAILED",
            "issues": self.issues,
            "total_issues": len(self.issues),
            "warnings_count": sum(1 for i in self.issues if i["severity"] == "WARNING"),
            "errors_count": sum(1 for i in self.issues if i["severity"] == "ERROR")
        }

    def _check_metadata(self):
        meta = self.parser.metadata
        if not meta.get("title"):
            self.issues.append({"severity": "ERROR", "msg": "Paper title is missing in YAML frontmatter."})
        if not meta.get("author"):
            self.issues.append({"severity": "ERROR", "msg": "Author name is missing in YAML frontmatter."})
        if not meta.get("email"):
            self.issues.append({"severity": "WARNING", "msg": "Corresponding author email is missing."})

    def _check_abstract(self):
        if not self.parser.abstract:
            self.issues.append({"severity": "ERROR", "msg": "Abstract is missing from the manuscript."})
            return
        words = self.parser.abstract.split()
        count = len(words)
        if count < 100:
            self.issues.append({
                "severity": "WARNING",
                "msg": f"Abstract word count is {count} words. IEEE guidelines recommend between 150 and 250 words."
            })
        elif count > 260:
            self.issues.append({
                "severity": "WARNING",
                "msg": f"Abstract is {count} words, which exceeds the typical 250-word IEEE limit."
            })

    def _check_keywords(self):
        if not self.parser.index_terms:
            self.issues.append({"severity": "ERROR", "msg": "Index Terms (Keywords) are missing."})
        elif len(self.parser.index_terms) < 3:
            self.issues.append({
                "severity": "WARNING",
                "msg": f"Only {len(self.parser.index_terms)} index terms found. IEEE recommends 3 to 6 keywords."
            })

    def _check_citations(self):
        all_text = ""
        figs_count = 0
        tbls_count = 0

        for sec in self.parser.sections:
            for elem in sec["elements"]:
                if elem["type"] == "paragraph":
                    all_text += " " + elem["text"]
                elif elem["type"] == "figure":
                    figs_count += 1
                elif elem["type"] == "table":
                    tbls_count += 1

        # Check if figures are cited in body text
        if figs_count > 0:
            fig_citations = re.findall(r"\b(?:Fig\.|Figure)\s*\d+", all_text, re.IGNORECASE)
            if not fig_citations:
                self.issues.append({
                    "severity": "ERROR",
                    "msg": "Figures are present in manuscript but never cited in body text (IEEE requires explicit citation, e.g. 'Fig. 1')."
                })

        # Check if tables are cited in body text
        if tbls_count > 0:
            tbl_citations = re.findall(r"\bTable\s*\d+", all_text, re.IGNORECASE)
            if not tbl_citations:
                self.issues.append({
                    "severity": "ERROR",
                    "msg": "Tables are present in manuscript but never cited in body text (IEEE requires explicit citation, e.g. 'Table I')."
                })

    def _check_references(self):
        if not self.parser.references:
            self.issues.append({"severity": "ERROR", "msg": "No references or bibliography section found."})
        elif len(self.parser.references) < 5:
            self.issues.append({
                "severity": "WARNING",
                "msg": f"Only {len(self.parser.references)} references found. Most IEEE papers require comprehensive literature citations."
            })
