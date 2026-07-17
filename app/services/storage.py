import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename


class StorageProvider:

    def save(self, file_obj, folder="uploads", filename=None):
        raise NotImplementedError

    def delete(self, path):
        raise NotImplementedError

    def url(self, path):
        raise NotImplementedError

    def list_files(self, folder="uploads"):
        raise NotImplementedError


class LocalStorageProvider(StorageProvider):

    def __init__(self, base_path=None):
        self.base_path = Path(base_path or current_app.root_path)

    def save(self, file_obj, folder="uploads", filename=None):
        if filename is None:
            ext = Path(file_obj.filename).suffix.lower()
            filename = f"{uuid.uuid4().hex}{ext}"
        else:
            filename = secure_filename(filename)

        upload_dir = self.base_path / "static" / folder
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / filename
        counter = 1

        while file_path.exists():
            stem = Path(filename).stem
            ext = Path(filename).suffix
            filename = f"{stem}_{counter}{ext}"
            file_path = upload_dir / filename
            counter += 1

        file_obj.save(str(file_path))
        return f"/static/{folder}/{filename}"

    def delete(self, url_path):
        if not url_path:
            return False

        full_path = self.base_path / url_path.lstrip("/")

        if full_path.exists():
            full_path.unlink()
            return True

        return False

    def url(self, path):
        return path

    def list_files(self, folder="uploads"):
        upload_dir = self.base_path / "static" / folder

        if not upload_dir.exists():
            return []

        files = []

        for f in sorted(
            upload_dir.iterdir(),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        ):
            if f.is_file():
                stat = f.stat()
                files.append(
                    {
                        "url": f"/static/{folder}/{f.name}",
                        "name": f.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "ext": f.suffix.lower(),
                    }
                )

        return files


class StorageService:
    _provider = None

    @classmethod
    def get_provider(cls):
        if cls._provider is None:
            cls._provider = LocalStorageProvider()

        return cls._provider

    @classmethod
    def set_provider(cls, provider):
        cls._provider = provider

    @classmethod
    def save(cls, file_obj, folder="uploads", filename=None):
        return cls.get_provider().save(file_obj, folder, filename)

    @classmethod
    def delete(cls, path):
        return cls.get_provider().delete(path)

    @classmethod
    def url(cls, path):
        return cls.get_provider().url(path)

    @classmethod
    def list_files(cls, folder="uploads"):
        return cls.get_provider().list_files(folder)