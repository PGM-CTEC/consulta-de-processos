import json
import os
import sqlite3
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx


DEFAULT_BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8011")
DEFAULT_DB_PATH = os.environ.get("DB_PATH", "consulta_processual.db")


def _find_venv_python() -> List[str]:
    # Prefer project venv for consistent deps.
    venv_py = os.path.join(".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return [venv_py]
    return [sys.executable]


def _is_backend_up(base_url: str) -> bool:
    try:
        r = httpx.get(f"{base_url}/health", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


def _start_backend(base_url: str) -> Optional[subprocess.Popen]:
    if _is_backend_up(base_url):
        return None

    # Extract host/port from the default URL shape.
    host = "127.0.0.1"
    port = "8011"
    try:
        # base_url like http://127.0.0.1:8011
        port = base_url.rsplit(":", 1)[-1]
    except Exception:
        pass

    py = _find_venv_python()
    proc = subprocess.Popen(
        py
        + [
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            host,
            "--port",
            str(port),
            "--reload",
        ],
        cwd=os.getcwd(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Wait up to ~15s for backend to come up.
    for _ in range(30):
        if _is_backend_up(base_url):
            return proc
        time.sleep(0.5)

    proc.terminate()
    return None


def _stop_backend(proc: Optional[subprocess.Popen]) -> None:
    if not proc:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        pass


def _load_db_multi_instance_numbers(db_path: str, limit: int = 10) -> List[Tuple[str, int]]:
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("select number, raw_data from processes")
        out: List[Tuple[str, int]] = []
        for number, raw_data in cur.fetchall():
            try:
                data = json.loads(raw_data) if raw_data else {}
            except Exception:
                continue
            cnt = (data.get("__meta__") or {}).get("instances_count")
            if isinstance(cnt, int) and cnt > 1:
                out.append((number, cnt))
            if len(out) >= limit:
                break
        return out
    finally:
        conn.close()


def _get_json(client: httpx.Client, url: str) -> Tuple[int, Any, str]:
    try:
        # Some DataJud-backed endpoints can take >30s when the upstream is slow.
        r = client.get(url, timeout=120.0)
        status = r.status_code
        try:
            return status, r.json(), ""
        except Exception:
            return status, None, (r.text or "")[:500]
    except Exception as e:
        return 0, None, str(e)


def verify_process(base_url: str, number: str, out_lines: List[str], dump_path: Optional[str] = None) -> None:
    with httpx.Client() as client:
        out_lines.append(f"Testing process: {number}")

        st, proc, err = _get_json(client, f"{base_url}/processes/{number}")
        out_lines.append(f"GET {base_url}/processes/{number}")
        if st != 200 or not isinstance(proc, dict):
            out_lines.append(f"Failed to fetch process: {st} {err}".strip())
            out_lines.append("")
            return

        out_lines.append("Process fetched successfully.")

        raw = proc.get("raw_data") or {}
        meta = raw.get("__meta__") if isinstance(raw, dict) else None
        out_lines.append(f"Raw Data Keys: {list(raw.keys()) if isinstance(raw, dict) else type(raw)}")
        out_lines.append(f"Meta Keys: {list(meta.keys()) if isinstance(meta, dict) else []}")
        out_lines.append(f"Instances count in meta: {(meta or {}).get('instances_count') if isinstance(meta, dict) else None}")
        out_lines.append(
            f"Actual hits in all_hits: {len((meta or {}).get('all_hits') or []) if isinstance(meta, dict) else 0}"
        )

        if dump_path:
            try:
                with open(dump_path, "w", encoding="utf-8") as f:
                    json.dump(proc, f, ensure_ascii=False)
                out_lines.append(f"Wrote process dump: {dump_path}")
            except Exception as e:
                out_lines.append(f"Failed to write process dump: {e}")

        st, inst, err = _get_json(client, f"{base_url}/processes/{number}/instances")
        out_lines.append("")
        out_lines.append(f"GET {base_url}/processes/{number}/instances")
        if st != 200 or not isinstance(inst, dict):
            out_lines.append(f"Failed to fetch instances list: {st} {err}".strip())
            out_lines.append("")
            return

        instances_count = inst.get("instances_count", 1)
        out_lines.append(f"Instances count reported: {instances_count}")

        indices = list(range(int(instances_count))) if isinstance(instances_count, int) and instances_count > 0 else [0]
        out_lines.append("")

        for idx in indices:
            out_lines.append(f"Fetching Instance {idx}...")
            st, detail, err = _get_json(client, f"{base_url}/processes/{number}/instances/{idx}")
            if st != 200 or not isinstance(detail, dict):
                out_lines.append(f"Failed to fetch instance {idx}: {st} {err}".strip())
                out_lines.append("")
                continue

            detail_raw = detail.get("raw_data") or {}
            detail_grau = None
            try:
                detail_grau = (detail_raw.get("__meta__") or {}).get("instances", [])[idx].get("grau")
            except Exception:
                pass
            if not detail_grau and isinstance(detail_raw, dict):
                detail_grau = detail_raw.get("grau")

            out_lines.append(
                f"OK instance {idx}: grau={detail_grau} class={detail.get('class_nature')} phase={detail.get('phase')} movements={len(detail.get('movements') or [])}"
            )
            out_lines.append("")


def main() -> int:
    base_url = DEFAULT_BACKEND_URL
    db_path = DEFAULT_DB_PATH

    # If the user passed explicit process numbers, use them.
    cli_numbers = [a for a in sys.argv[1:] if a and not a.startswith("-")]
    candidates: List[str] = []

    if cli_numbers:
        candidates = cli_numbers
    else:
        multi = _load_db_multi_instance_numbers(db_path=db_path, limit=5)
        if multi:
            candidates = [n for n, _ in multi]
        else:
            # Fallback to a known example used in previous debug sessions.
            candidates = ["0435756-80.2012.8.19.0001"]

    proc = _start_backend(base_url)
    if not _is_backend_up(base_url):
        print(f"Backend not reachable at {base_url}")
        return 2

    out_lines: List[str] = []
    try:
        out_lines.append(f"Backend: {base_url}")
        out_lines.append(f"DB: {db_path}")
        out_lines.append("")

        for i, number in enumerate(candidates):
            dump_path = "process_dump.json" if i == 0 else None
            verify_process(base_url, number, out_lines, dump_path=dump_path)

        out_lines.append("Verification Complete.")
    finally:
        _stop_backend(proc)

    with open("verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")

    print("Wrote verify_output.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
