import os
import sys

class PdfBuilder:
    """Converts IEEE DOCX into publication-ready vector PDF."""

    @staticmethod
    def convert_docx_to_pdf(docx_path: str, pdf_path: str) -> bool:
        abs_docx = os.path.abspath(docx_path)
        abs_pdf = os.path.abspath(pdf_path)

        # 1. Primary method on Windows: Word COM (highest fidelity)
        if sys.platform == "win32":
            try:
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(abs_docx)
                doc.SaveAs(abs_pdf, FileFormat=17) # 17 = wdFormatPDF
                doc.Close()
                word.Quit()
                if os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 0:
                    return True
            except Exception as e:
                pass

        # 2. Secondary fallback: LibreOffice headless
        try:
            import subprocess
            cmd = ["soffice", "--headless", "--convert-to", "pdf", abs_docx, "--outdir", os.path.dirname(abs_pdf)]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            if os.path.exists(abs_pdf):
                return True
        except Exception:
            pass

        return False
