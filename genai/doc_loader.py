"""
Document Loaders for Smart Manufacturing RAG
Supports: PDF, TXT, CSV (sensor logs), JSON (MLflow reports)
"""

import os
import json
import csv
import io
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


# ─── PDF Loader ────────────────────────────────────────────────────────────────

def load_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"[Page {page_num + 1}]\n{text}")
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")
    except Exception as e:
        raise RuntimeError(f"Failed to load PDF '{file_path}': {e}")


def load_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> str:
    """Extract text from PDF bytes (from file upload)."""
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"[Page {page_num + 1}]\n{text}")
        doc.close()
        return "\n\n".join(text_parts)
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")


# ─── CSV Sensor Log Loader ─────────────────────────────────────────────────────

def load_sensor_csv(file_path: str, max_rows: int = 500) -> str:
    """
    Convert sensor CSV logs into natural language chunks for RAG indexing.
    Expected columns: timestamp, machine_id, sensor_name, value, unit, status
    """
    rows = []
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows:
                break
            rows.append(row)

    if not rows:
        return ""

    # Group by machine
    by_machine: Dict[str, List] = {}
    for row in rows:
        machine = row.get("machine_id", "unknown")
        by_machine.setdefault(machine, []).append(row)

    text_parts = [f"Sensor Log Data from {os.path.basename(file_path)}:"]
    for machine, machine_rows in by_machine.items():
        text_parts.append(f"\n== Machine: {machine} ({len(machine_rows)} readings) ==")
        for row in machine_rows[:10]:  # Summary of first 10 readings per machine
            ts = row.get("timestamp", "N/A")
            sensor = row.get("sensor_name", "N/A")
            value = row.get("value", "N/A")
            unit = row.get("unit", "")
            status = row.get("status", "N/A")
            text_parts.append(f"  [{ts}] {sensor}: {value} {unit} — Status: {status}")

        # Compute basic stats if values are numeric
        values = []
        for row in machine_rows:
            try:
                values.append(float(row.get("value", 0)))
            except:
                pass
        if values:
            avg = sum(values) / len(values)
            text_parts.append(
                f"  Stats: min={min(values):.2f}, max={max(values):.2f}, avg={avg:.2f}"
            )

    return "\n".join(text_parts)


# ─── MLflow Run Report Loader ──────────────────────────────────────────────────

def load_mlflow_report(file_path: str) -> str:
    """
    Convert an MLflow run JSON export into searchable text.
    Useful for letting the chatbot answer questions about past experiments.
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    runs = data if isinstance(data, list) else [data]
    text_parts = [f"MLflow Experiment Report — {len(runs)} run(s):"]

    for run in runs[:20]:  # Cap at 20 runs
        info = run.get("info", {})
        params = run.get("data", {}).get("params", {})
        metrics = run.get("data", {}).get("metrics", {})
        tags = run.get("data", {}).get("tags", {})

        text_parts.append(f"""
Run ID: {info.get('run_id', 'N/A')[:8]}...
  Experiment: {tags.get('mlflow.runName', info.get('experiment_id', 'N/A'))}
  Status: {info.get('status', 'N/A')}
  Model: {params.get('model_type', tags.get('model_name', 'N/A'))}
  Parameters: {json.dumps({k: v for k, v in list(params.items())[:6]}, indent=4)}
  Metrics: accuracy={metrics.get('accuracy', 'N/A')}, f1={metrics.get('f1_score', 'N/A')},
           precision={metrics.get('precision', 'N/A')}, recall={metrics.get('recall', 'N/A')}
  Start: {datetime.fromtimestamp(info.get('start_time', 0) / 1000).strftime('%Y-%m-%d %H:%M') if info.get('start_time') else 'N/A'}
""")

    return "\n".join(text_parts)


# ─── Generic TXT/Markdown Loader ──────────────────────────────────────────────

def load_text_file(file_path: str, encoding: str = "utf-8") -> str:
    """Load plain text or markdown files (SOPs, runbooks, documentation)."""
    with open(file_path, "r", encoding=encoding, errors="ignore") as f:
        return f.read()


# ─── Auto Loader (dispatch by extension) ──────────────────────────────────────

def load_document(file_path: str) -> Dict:
    """
    Auto-detect file type and load document.
    Returns: {text, source, filename, pages_or_rows}
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    filename = path.name

    loaders = {
        ".pdf": lambda: (load_pdf(file_path), "pdf"),
        ".txt": lambda: (load_text_file(file_path), "text"),
        ".md": lambda: (load_text_file(file_path), "markdown"),
        ".csv": lambda: (load_sensor_csv(file_path), "sensor_csv"),
        ".json": lambda: (load_mlflow_report(file_path), "mlflow_report"),
    }

    loader = loaders.get(ext)
    if not loader:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {list(loaders.keys())}")

    text, doc_type = loader()
    return {
        "text": text,
        "source": doc_type,
        "filename": filename,
        "char_count": len(text),
        "loaded_at": datetime.now().isoformat()
    }


# ─── Batch Loader ─────────────────────────────────────────────────────────────

def load_directory(directory: str, extensions: Optional[List[str]] = None) -> List[Dict]:
    """
    Load all supported documents from a directory.
    Useful for bulk-indexing a folder of SOPs or maintenance manuals.
    """
    supported = extensions or [".pdf", ".txt", ".md", ".csv", ".json"]
    results = []

    for file_path in Path(directory).rglob("*"):
        if file_path.suffix.lower() in supported:
            try:
                doc = load_document(str(file_path))
                results.append(doc)
                print(f"✅ Loaded: {file_path.name} ({doc['char_count']} chars)")
            except Exception as e:
                print(f"⚠️  Skipped {file_path.name}: {e}")

    print(f"\n📚 Loaded {len(results)} documents from {directory}")
    return results


# ─── CLI Usage ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python document_loaders.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        docs = load_directory(target)
        for d in docs:
            print(f"\n{'='*50}")
            print(f"File: {d['filename']} | Type: {d['source']}")
            print(d['text'][:300] + "...")
    else:
        doc = load_document(target)
        print(f"Loaded: {doc['filename']} ({doc['char_count']} chars)")
        print(doc['text'][:500])