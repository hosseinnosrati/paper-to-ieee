import re
from typing import Dict, List, Any, Optional

class PaperParser:
    """Parses research Markdown documents and extracts structural IEEE components."""

    def __init__(self, content: str):
        self.raw_content = content
        self.metadata: Dict[str, Any] = {}
        self.abstract: str = ""
        self.index_terms: List[str] = []
        self.sections: List[Dict[str, Any]] = []
        self.references: List[str] = []
        self._parse()

    def _parse(self):
        text = self.raw_content

        # 1. Extract YAML Frontmatter if present
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            text = text[fm_match.end():]
            self._parse_yaml(fm_text)

        # 2. Extract Abstract if marked with ## Abstract or **Abstract**
        abs_match = re.search(r"(?:##\s*Abstract|(?:\*\*|_)?Abstract(?:\*\*|_)?[:—-])\s*(.*?)(?=\n##|\n#|\n\*\*Index Terms|\n\*\*Keywords|$)", text, re.DOTALL | re.IGNORECASE)
        if abs_match:
            self.abstract = abs_match.group(1).strip()
            text = text[:abs_match.start()] + text[abs_match.end():]
        elif "abstract" in self.metadata:
            self.abstract = self.metadata["abstract"].strip()

        # 3. Extract Index Terms / Keywords
        kw_match = re.search(r"(?:##\s*Index Terms|(?:\*\*|_)?Index Terms(?:\*\*|_)?[:—-]|##\s*Keywords|(?:\*\*|_)?Keywords(?:\*\*|_)?[:—-])\s*(.*?)(?=\n##|\n#|$)", text, re.DOTALL | re.IGNORECASE)
        if kw_match:
            raw_kws = kw_match.group(1).strip()
            self.index_terms = [k.strip().rstrip(".,") for k in re.split(r"[,;]", raw_kws) if k.strip()]
            text = text[:kw_match.start()] + text[kw_match.end():]
        elif "keywords" in self.metadata:
            raw_k = self.metadata["keywords"]
            if isinstance(raw_k, list):
                self.index_terms = raw_k
            else:
                self.index_terms = [k.strip() for k in str(raw_k).split(",")]

        # 4. Extract References
        ref_match = re.search(r"\n#+\s*(?:References|REFERENCES)\s*\n(.*)$", text, re.DOTALL | re.IGNORECASE)
        if ref_match:
            ref_body = ref_match.group(1).strip()
            text = text[:ref_match.start()]
            for line in ref_body.splitlines():
                line = line.strip()
                if line:
                    self.references.append(line)

        # 5. Parse remaining body sections, headings, equations, tables, and figures
        self._parse_body(text)

    def _parse_yaml(self, fm_text: str):
        lines = fm_text.splitlines()
        current_key = None
        for line in lines:
            if not line.strip() or line.strip().startswith("#"):
                continue
            if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip("\"'")
                self.metadata[k] = v
                current_key = k
            elif current_key and (line.startswith(" ") or line.startswith("\t")):
                self.metadata[current_key] += " " + line.strip().strip("\"'")

    def _parse_body(self, text: str):
        lines = text.splitlines()
        current_section = {"title": "I. INTRODUCTION", "level": 1, "elements": []}
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]
            sline = line.strip()

            if not sline:
                i += 1
                continue

            # Heading 1 (# Title)
            if sline.startswith("# ") and not sline.startswith("## "):
                if current_section["elements"]:
                    self.sections.append(current_section)
                h_title = sline[2:].strip()
                current_section = {"title": h_title, "level": 1, "elements": []}
                i += 1
                continue

            # Heading 2 (## Title)
            if sline.startswith("## ") and not sline.startswith("### "):
                if current_section["elements"]:
                    self.sections.append(current_section)
                h_title = sline[3:].strip()
                current_section = {"title": h_title, "level": 2, "elements": []}
                i += 1
                continue

            # Heading 3 (### Title)
            if sline.startswith("### "):
                if current_section["elements"]:
                    self.sections.append(current_section)
                h_title = sline[4:].strip()
                current_section = {"title": h_title, "level": 3, "elements": []}
                i += 1
                continue

            # Figure: ![Caption](path)
            fig_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", sline)
            if fig_match:
                caption = fig_match.group(1).strip()
                path = fig_match.group(2).strip()
                current_section["elements"].append({
                    "type": "figure",
                    "caption": caption,
                    "path": path
                })
                i += 1
                continue

            # Table (Markdown format starting with |)
            if sline.startswith("|") and "|" in sline[1:]:
                table_lines = [sline]
                i += 1
                while i < n and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i].strip())
                    i += 1
                current_section["elements"].append({
                    "type": "table",
                    "data": self._parse_markdown_table(table_lines)
                })
                continue

            # Display Equation: $$ ... $$
            if sline.startswith("$$"):
                eq_lines = [sline.replace("$$", "").strip()]
                if not sline.endswith("$$") or sline == "$$":
                    i += 1
                    while i < n and not lines[i].strip().endswith("$$"):
                        eq_lines.append(lines[i].strip())
                        i += 1
                    if i < n:
                        eq_lines.append(lines[i].strip().replace("$$", "").strip())
                eq_text = " ".join([l for l in eq_lines if l])
                current_section["elements"].append({
                    "type": "equation",
                    "text": eq_text
                })
                i += 1
                continue

            # Regular Paragraph
            para_lines = [sline]
            i += 1
            while i < n and lines[i].strip() and not lines[i].strip().startswith("#") and not lines[i].strip().startswith("|") and not lines[i].strip().startswith("$$") and not lines[i].strip().startswith("!["):
                para_lines.append(lines[i].strip())
                i += 1

            full_para = " ".join(para_lines)
            current_section["elements"].append({
                "type": "paragraph",
                "text": full_para
            })

        if current_section["elements"]:
            self.sections.append(current_section)

    def _parse_markdown_table(self, lines: List[str]) -> Dict[str, Any]:
        headers = []
        rows = []
        for idx, line in enumerate(lines):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if idx == 0:
                headers = cells
            elif idx == 1 and all(set(c).issubset({"-", ":", " "}) for c in cells):
                continue # Separator line
            else:
                rows.append(cells)
        return {"headers": headers, "rows": rows}
