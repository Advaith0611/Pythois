"""Utilities for safely ingesting file objects from canvas payloads."""

from __future__ import annotations

import base64
import binascii
import csv
import io
import json
import re
from collections.abc import Mapping
from typing import Any, TypedDict


MAX_DECODED_FILE_SIZE_BYTES = 20 * 1024 * 1024

TEXT_MIME_TYPES = {"text/plain", "text/markdown"}
IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
SUPPORTED_MIME_TYPES = {
    *TEXT_MIME_TYPES,
    "application/pdf",
    "application/json",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    *IMAGE_MIME_TYPES,
}

_DATA_URL_PATTERN = re.compile(
    (
        r"^data:(?P<mime_type>[-\w.+]+/[-\w.+]+)"
        r"(?P<parameters>(?:;[-\w.]+=[^;,]+)*);base64,(?P<payload>.*)$"
    ),
    re.DOTALL | re.IGNORECASE,
)


class ParsedDataUrl(TypedDict):
    """Parsed components of a base64 data URL."""

    mime_type: str
    base64_data: str


class ProcessedCanvasFile(TypedDict):
    """Normalized result returned after processing a canvas file object."""

    title: str
    mime_type: str
    text_content: str | None
    image_data_url: str | None
    metadata: dict[str, Any]
    error: str | None


def parse_data_url(data_url: str) -> ParsedDataUrl:
    """Validate and parse a base64 data URL into MIME type and payload."""

    if not isinstance(data_url, str) or not data_url:
        raise ValueError("dataUrl must be a non-empty string.")

    match = _DATA_URL_PATTERN.match(data_url)
    if match is None:
        raise ValueError("Invalid data URL format. Expected data:<mime>;base64,<payload>.")

    return {
        "mime_type": match.group("mime_type").lower(),
        "base64_data": match.group("payload").strip(),
    }


def decode_base64_file(
    base64_data: str,
    max_size_bytes: int = MAX_DECODED_FILE_SIZE_BYTES,
) -> bytes:
    """Decode a base64 payload and reject files larger than the configured limit."""

    if not isinstance(base64_data, str) or not base64_data:
        raise ValueError("Base64 payload must be a non-empty string.")

    compact_payload = re.sub(r"\s+", "", base64_data)
    estimated_size = (len(compact_payload) * 3) // 4
    if compact_payload.endswith("=="):
        estimated_size -= 2
    elif compact_payload.endswith("="):
        estimated_size -= 1

    if estimated_size > max_size_bytes:
        raise ValueError("Decoded file exceeds the 20 MB size limit.")

    try:
        decoded = base64.b64decode(compact_payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Invalid base64 payload.") from exc

    if len(decoded) > max_size_bytes:
        raise ValueError("Decoded file exceeds the 20 MB size limit.")

    return decoded


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from every page of a PDF using pypdf."""

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_bytes))
        page_text = [page.extract_text() or "" for page in reader.pages]
    except ImportError as exc:
        raise ValueError("PDF support requires the pypdf package.") from exc
    except Exception as exc:  # pypdf can raise several parser-specific exceptions.
        raise ValueError("Unable to extract text from PDF.") from exc

    return "\n\n".join(text.strip() for text in page_text if text.strip())


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract paragraph text from a DOCX file while preserving paragraph breaks."""

    try:
        from docx import Document

        document = Document(io.BytesIO(file_bytes))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
    except ImportError as exc:
        raise ValueError("DOCX support requires the python-docx package.") from exc
    except Exception as exc:
        raise ValueError("Unable to extract text from DOCX file.") from exc

    return "\n".join(paragraphs)


def extract_csv_text(file_bytes: bytes) -> str:
    """Convert CSV bytes into readable text that includes headers and rows."""

    text = _decode_text_bytes(file_bytes)
    try:
        sample = text[:4096]
        dialect = csv.Sniffer().sniff(sample) if sample else csv.excel
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(io.StringIO(text), dialect)
    rows = list(reader)
    if not rows:
        return ""

    header = rows[0]
    output_lines = [f"Headers: {', '.join(header)}"]
    for index, row in enumerate(rows[1:], start=1):
        cells = []
        for column_index, value in enumerate(row):
            has_header = column_index < len(header) and header[column_index]
            label = header[column_index] if has_header else f"Column {column_index + 1}"
            cells.append(f"{label}: {value}")
        output_lines.append(f"Row {index}: " + "; ".join(cells))

    return "\n".join(output_lines)


def process_canvas_file(file_object: dict[str, Any]) -> ProcessedCanvasFile:
    """Process a canvas file object and return extracted text, image data, metadata, and errors."""

    result = _empty_result(file_object)

    try:
        if not isinstance(file_object, dict):
            raise ValueError("file_object must be a dictionary.")

        data_url = file_object.get("dataUrl")
        parsed_data_url = parse_data_url(data_url)
        declared_mime_type = _normalize_optional_string(file_object.get("mimeType"))
        detected_mime_type = _detect_mime_type(
            data_url_mime_type=parsed_data_url["mime_type"],
            declared_mime_type=declared_mime_type,
        )
        result["mime_type"] = detected_mime_type

        if detected_mime_type not in SUPPORTED_MIME_TYPES:
            raise ValueError(f"Unsupported file type: {detected_mime_type}.")

        file_bytes = decode_base64_file(parsed_data_url["base64_data"])
        _validate_file_signature(file_bytes, detected_mime_type)
        result["text_content"] = _extract_text_content(file_bytes, detected_mime_type)

        if detected_mime_type in IMAGE_MIME_TYPES:
            result["image_data_url"] = data_url

    except Exception as exc:
        result["error"] = str(exc)

    return result


def _empty_result(file_object: Any) -> ProcessedCanvasFile:
    """Create a default result structure from the safest available input fields."""

    title = ""
    metadata: dict[str, Any] = {}
    mime_type = ""

    if isinstance(file_object, Mapping):
        title = str(file_object.get("title") or "")
        raw_metadata = file_object.get("metadata")
        metadata = dict(raw_metadata) if isinstance(raw_metadata, Mapping) else {}
        mime_type = _normalize_optional_string(file_object.get("mimeType")) or ""

    return {
        "title": title,
        "mime_type": mime_type,
        "text_content": None,
        "image_data_url": None,
        "metadata": metadata,
        "error": None,
    }


def _detect_mime_type(data_url_mime_type: str, declared_mime_type: str | None) -> str:
    """Select a trusted MIME type from the data URL and optional object metadata."""

    normalized_data_url_mime = data_url_mime_type.lower().strip()
    normalized_declared_mime = declared_mime_type.lower().strip() if declared_mime_type else None

    if normalized_declared_mime and normalized_declared_mime != normalized_data_url_mime:
        raise ValueError(
            f"MIME type mismatch: data URL declares {normalized_data_url_mime}, "
            f"but object declares {normalized_declared_mime}."
        )

    return normalized_data_url_mime


def _extract_text_content(file_bytes: bytes, mime_type: str) -> str | None:
    """Dispatch text extraction based on normalized MIME type."""

    if mime_type in TEXT_MIME_TYPES:
        return _decode_text_bytes(file_bytes)
    if mime_type == "application/json":
        return _format_json_text(file_bytes)
    if mime_type == "text/csv":
        return extract_csv_text(file_bytes)
    if mime_type == "application/pdf":
        return extract_pdf_text(file_bytes)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_docx_text(file_bytes)
    if mime_type in IMAGE_MIME_TYPES:
        return None

    raise ValueError(f"Unsupported file type: {mime_type}.")


def _validate_file_signature(file_bytes: bytes, mime_type: str) -> None:
    """Validate magic bytes for binary formats where a reliable signature exists."""

    if mime_type == "application/pdf" and not file_bytes.startswith(b"%PDF-"):
        raise ValueError("File content does not match application/pdf.")
    if mime_type == "image/png" and not file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("File content does not match image/png.")
    if mime_type == "image/jpeg" and not file_bytes.startswith(b"\xff\xd8\xff"):
        raise ValueError("File content does not match image/jpeg.")
    if mime_type == "image/webp" and not (
        file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"
    ):
        raise ValueError("File content does not match image/webp.")
    if (
        mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        and not file_bytes.startswith(b"PK\x03\x04")
    ):
        raise ValueError("File content does not match DOCX format.")


def _decode_text_bytes(file_bytes: bytes) -> str:
    """Decode text bytes using UTF-8 with BOM support and a safe fallback."""

    try:
        return file_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def _format_json_text(file_bytes: bytes) -> str:
    """Decode JSON bytes and return a readable, consistently formatted string."""

    text = _decode_text_bytes(file_bytes)
    try:
        parsed_json = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON file.") from exc

    return json.dumps(parsed_json, indent=2, ensure_ascii=False)


def _normalize_optional_string(value: Any) -> str | None:
    """Return a stripped string for string-like values, otherwise None."""

    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


if __name__ == "__main__":
    example_text = "Hello from a canvas upload."
    encoded_text = base64.b64encode(example_text.encode("utf-8")).decode("ascii")
    example_data_url = f"data:text/plain;base64,{encoded_text}"
    example_file = {
        "dataUrl": example_data_url,
        "mimeType": "text/plain",
        "title": "example.txt",
        "metadata": {"source": "example"},
    }

    print(process_canvas_file(example_file))
