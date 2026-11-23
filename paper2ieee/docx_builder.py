import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from .parser import PaperParser

class DocxBuilder:
    """Builds an authentic two-column IEEE Transactions Word (.docx) document."""

    def __init__(self, parser: PaperParser):
        self.parser = parser
        self.doc = docx.Document()
        self.eq_counter = 1
        self.fig_counter = 1
        self.tbl_counter = 1

    def build(self, output_path: str):
        self._setup_page()
        self._add_title_and_authors()
        self._setup_two_columns()
        self._add_abstract_and_keywords()
        self._add_sections()
        self._add_references()
        self.doc.save(output_path)
        return output_path

    def _setup_page(self):
        sec = self.doc.sections[0]
        sec.top_margin = Inches(0.75)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.65)
        sec.right_margin = Inches(0.65)
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)

    def _add_title_and_authors(self):
        meta = self.parser.metadata

        # Running header / Journal banner
        journal = meta.get("journal", "IEEE TRANSACTIONS / LETTERS FORMATTED MANUSCRIPT")
        p_top = self.doc.add_paragraph()
        r_top = p_top.add_run(journal.upper())
        r_top.font.name = "Times New Roman"
        r_top.font.size = Pt(8.5)
        r_top.font.color.rgb = RGBColor(110, 110, 110)
        p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_top.paragraph_format.space_after = Pt(10)

        # Title
        title = meta.get("title", "Research Paper Title")
        p_title = self.doc.add_paragraph()
        r_title = p_title.add_run(title)
        r_title.bold = True
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(20)
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(8)

        # Author Block
        author = meta.get("author", "Author Name")
        affiliation = meta.get("affiliation", "Department of Electrical Engineering, University Name, City, Country")
        email = meta.get("email", "author@institution.edu")

        p_auth = self.doc.add_paragraph()
        r_name = p_auth.add_run(author)
        r_name.bold = True
        r_name.font.name = "Times New Roman"
        r_name.font.size = Pt(11)

        p_auth.add_run(", ")
        r_mem = p_auth.add_run("Member, IEEE\n")
        r_mem.font.name = "Times New Roman"
        r_mem.font.italic = True
        r_mem.font.size = Pt(10)

        r_aff = p_auth.add_run(f"{affiliation}\n")
        r_aff.font.name = "Times New Roman"
        r_aff.font.size = Pt(9.5)

        r_em = p_auth.add_run(f"e-mail: {email}")
        r_em.font.name = "Times New Roman"
        r_em.font.size = Pt(9)
        p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_auth.paragraph_format.space_after = Pt(14)

    def _setup_two_columns(self):
        sec2 = self.doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = sec2._sectPr
        # 2 columns with 0.20 in spacing (288 dxa)
        cols = parse_xml(f'<w:cols {nsdecls("w")} w:num="2" w:space="288"/>')
        sectPr.append(cols)

    def _add_abstract_and_keywords(self):
        if self.parser.abstract:
            p_abs = self.doc.add_paragraph()
            p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_abs.paragraph_format.space_after = Pt(4)
            p_abs.paragraph_format.line_spacing = Pt(11.5)

            r_h = p_abs.add_run("Abstract—")
            r_h.bold = True
            r_h.font.italic = True
            r_h.font.name = "Times New Roman"
            r_h.font.size = Pt(9)

            r_t = p_abs.add_run(self.parser.abstract)
            r_t.bold = True
            r_t.font.name = "Times New Roman"
            r_t.font.size = Pt(9)

        if self.parser.index_terms:
            p_kw = self.doc.add_paragraph()
            p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_kw.paragraph_format.space_after = Pt(10)
            p_kw.paragraph_format.line_spacing = Pt(11.5)

            r_kh = p_kw.add_run("Index Terms—")
            r_kh.bold = True
            r_kh.font.italic = True
            r_kh.font.name = "Times New Roman"
            r_kh.font.size = Pt(9)

            r_kt = p_kw.add_run(", ".join(self.parser.index_terms) + ".")
            r_kt.bold = True
            r_kt.font.name = "Times New Roman"
            r_kt.font.size = Pt(9)

    def _add_sections(self):
        first_para_done = False
        for sec in self.parser.sections:
            title = sec["title"]
            level = sec["level"]

            if level == 1:
                p_h = self.doc.add_paragraph()
                p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_h.paragraph_format.space_before = Pt(10)
                p_h.paragraph_format.space_after = Pt(3)
                r = p_h.add_run(title.upper())
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
            elif level == 2:
                p_h = self.doc.add_paragraph()
                p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_h.paragraph_format.space_before = Pt(7)
                p_h.paragraph_format.space_after = Pt(2)
                r = p_h.add_run(title)
                r.font.italic = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
            else:
                p_h = self.doc.add_paragraph()
                p_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_h.paragraph_format.space_before = Pt(5)
                p_h.paragraph_format.space_after = Pt(1)
                r = p_h.add_run(title)
                r.font.italic = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)

            for elem in sec["elements"]:
                etype = elem["type"]
                if etype == "paragraph":
                    p = self.doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = Pt(11.5)

                    text = elem["text"]
                    if not first_para_done:
                        # Drop Cap styling on first word
                        words = text.split(" ", 1)
                        if len(words) == 2:
                            w1, rest = words
                            r_d1 = p.add_run(w1[0].upper())
                            r_d1.bold = True
                            r_d1.font.name = "Times New Roman"
                            r_d1.font.size = Pt(13)

                            r_d2 = p.add_run(w1[1:].upper() + " ")
                            r_d2.bold = True
                            r_d2.font.name = "Times New Roman"
                            r_d2.font.size = Pt(8.5)

                            r_rest = p.add_run(rest)
                            r_rest.font.name = "Times New Roman"
                            r_rest.font.size = Pt(9.5)
                            first_para_done = True
                            continue
                        first_para_done = True

                    p.paragraph_format.first_line_indent = Inches(0.14)
                    r = p.add_run(text)
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(9.5)

                elif etype == "equation":
                    p_eq = self.doc.add_paragraph()
                    p_eq.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    p_eq.paragraph_format.space_before = Pt(3)
                    p_eq.paragraph_format.space_after = Pt(3)
                    eq_str = elem["text"]
                    if not re.search(r"\(\d+\)\s*$", eq_str):
                        eq_str = f"{eq_str}                                ({self.eq_counter})"
                        self.eq_counter += 1
                    r = p_eq.add_run(eq_str)
                    r.font.italic = True
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(9.5)

                elif etype == "figure":
                    fpath = elem["path"]
                    if os.path.exists(fpath):
                        p_f = self.doc.add_paragraph()
                        p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_f.paragraph_format.space_before = Pt(4)
                        p_f.paragraph_format.space_after = Pt(2)
                        p_f.add_run().add_picture(fpath, width=Inches(3.35))

                        p_cap = self.doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                        p_cap.paragraph_format.space_after = Pt(6)
                        r_fn = p_cap.add_run(f"Fig. {self.fig_counter}. ")
                        r_fn.bold = True
                        r_fn.font.name = "Times New Roman"
                        r_fn.font.size = Pt(8)
                        r_fc = p_cap.add_run(elem["caption"])
                        r_fc.font.name = "Times New Roman"
                        r_fc.font.size = Pt(8)
                        self.fig_counter += 1

                elif etype == "table":
                    tdata = elem["data"]
                    headers = tdata.get("headers", [])
                    rows = tdata.get("rows", [])
                    if headers:
                        p_tt = self.doc.add_paragraph()
                        p_tt.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_tt.paragraph_format.space_before = Pt(6)
                        p_tt.paragraph_format.space_after = Pt(2)
                        r_tt = p_tt.add_run(f"TABLE {self.tbl_counter}\nPERFORMANCE AND BENCHMARK RESULTS")
                        r_tt.bold = True
                        r_tt.font.name = "Times New Roman"
                        r_tt.font.size = Pt(8)
                        self.tbl_counter += 1

                        table = self.doc.add_table(rows=len(rows) + 1, cols=len(headers))
                        table.alignment = WD_TABLE_ALIGNMENT.CENTER

                        for c_i, h in enumerate(headers):
                            c = table.cell(0, c_i)
                            c.text = h
                            cp = c.paragraphs[0]
                            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            cp.runs[0].font.name = "Times New Roman"
                            cp.runs[0].font.size = Pt(7.5)
                            cp.runs[0].bold = True

                        for r_i, rvals in enumerate(rows, 1):
                            for c_i, val in enumerate(rvals):
                                if c_i < len(headers):
                                    c = table.cell(r_i, c_i)
                                    c.text = val
                                    cp = c.paragraphs[0]
                                    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 else WD_ALIGN_PARAGRAPH.CENTER
                                    cp.runs[0].font.name = "Times New Roman"
                                    cp.runs[0].font.size = Pt(7.5)

                        p_sp = self.doc.add_paragraph()
                        p_sp.paragraph_format.space_after = Pt(4)

    def _add_references(self):
        if not self.parser.references:
            return

        p_rh = self.doc.add_paragraph()
        p_rh.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_rh.paragraph_format.space_before = Pt(10)
        p_rh.paragraph_format.space_after = Pt(4)
        r = p_rh.add_run("REFERENCES")
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)

        for ref in self.parser.references:
            p_ref = self.doc.add_paragraph()
            p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_ref.paragraph_format.space_after = Pt(2)
            p_ref.paragraph_format.line_spacing = Pt(10)
            p_ref.paragraph_format.left_indent = Inches(0.20)
            p_ref.paragraph_format.first_line_indent = Inches(-0.20)

            run = p_ref.add_run(ref)
            run.font.name = "Times New Roman"
            run.font.size = Pt(8)
