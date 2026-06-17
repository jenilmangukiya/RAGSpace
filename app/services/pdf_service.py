import fitz


class PDFService:
    @staticmethod
    def extract_text(file_path: str) -> str:
        doc = fitz.open(file_path)

        pages = []

        for page_number, page in enumerate(doc):
            text = page.get_text()

            if text:
                pages.append(
                    {
                        "page_number": page_number + 1,
                        "page_content": text,
                    }
                )

        doc.close()

        return pages
