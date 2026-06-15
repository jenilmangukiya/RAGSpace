import fitz


class PDFService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        doc = fitz.open(file_path)

        pages = []

        for page in doc:
            text = page.get_text()

            if text:
                pages.append(text)

        doc.close()

        return "\n".join(pages)
