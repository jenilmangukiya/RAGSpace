import tempfile

from app.integrations.storage import supabase


class StorageService:
    @staticmethod
    def download_document(storage_path: str):
        file_byte = supabase.storage.from_("documents").download(storage_path)

        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)

        temp_file.write(file_byte)
        temp_file.close()

        return temp_file.name
