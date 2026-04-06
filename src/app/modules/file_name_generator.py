import re
import unicodedata
from pathlib import Path


class FileNameGenerator:
    WINDOWS_RESERVED_NAMES = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    INVALID_CHARS_PATTERN = r'[<>:"/\\|?*\x00-\x1F]'

    def __init__(self, fragments, separator="_", max_length=255, allow_unicode=False, replacement="_"):
        """
        Parameters
        ----------
        fragments : list of callables
            Each callable returns a string fragment
        separator : str
            String used to join fragments
        """
        self.fragments = fragments
        self.separator = separator
        self.max_length = max_length
        self.allow_unicode = allow_unicode
        self.replacement = replacement

    def generate(self, directory: Path | None = None, ensure_unique=False) -> str:
        """
        Generate a sanitized filename. Optionally ensure uniqueness in a directory.
        """
        raw_name = self.separator.join(self.fragments)
        # Sanitize
        safe_name = self._sanitize(raw_name)
        # Ensure uniqueness if directory provided
        if directory and ensure_unique:
            safe_path = self._ensure_unique(Path(directory) / safe_name)
            return safe_path.name

        return safe_name

    def _sanitize(self, filename: str) -> str:
        if not filename or not filename.strip():
            return "unnamed"
        # Unicode normalization
        filename = unicodedata.normalize("NFKD", filename)
        if not self.allow_unicode:
            filename = filename.encode("ascii", "ignore").decode("ascii")
        p = Path(filename)
        stem = p.stem
        suffix = p.suffix
        # Remove invalid characters
        stem = re.sub(self.INVALID_CHARS_PATTERN, self.replacement, stem)
        # Normalize whitespace
        stem = re.sub(r"\s+", self.replacement, stem)
        # Collapse repeated separators
        stem = re.sub(f"{re.escape(self.replacement)}+", self.replacement, stem)
        # Strip edges
        stem = stem.strip(f"{self.replacement}. ")
        if not stem:
            stem = "unnamed"
        # Handle Windows reserved names
        if stem.upper() in self.WINDOWS_RESERVED_NAMES:
            stem = f"{stem}_file"
        full_name = stem + suffix
        # Enforce max length
        if len(full_name) > self.max_length:
            ext_len = len(suffix)
            allowed_stem_len = self.max_length - ext_len
            if allowed_stem_len <= 0:
                full_name = full_name[:self.max_length]
            else:
                stem = stem[:allowed_stem_len]
                full_name = stem + suffix

        return full_name

    @staticmethod
    def _ensure_unique(path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            new_name = f"{stem}_{counter:03d}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path

            counter += 1