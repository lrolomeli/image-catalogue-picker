#!/usr/bin/env python3
"""
Catalog Studio - Local Development Server

Usage:
    python server.py                    # Default port 3456
    python server.py 8080                # Custom port

API Endpoints:
    POST /api/download   - Download images for a product
    POST /api/export    - Export catalog to folder
    GET  /api/status    - Check dependencies
"""

import http.server
import socketserver
import json
import os
import sys
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urlparse

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3456
BASE_DIR = Path(__file__).parent.resolve()

# CORS headers
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class CatalogHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        for k, v in HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/download":
            self.handle_download()
        elif parsed.path == "/api/save":
            self.handle_save()
        elif parsed.path == "/api/status":
            self.handle_status()
        else:
            self.send_error(404)

    def handle_download(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            product_id = data.get("productId")
            product_name = data.get("productName")
            images_base_path = data.get("imagesBasePath", "")

            if not product_id or not product_name:
                self.send_json({"success": False, "error": "Missing parameters"})
                return

            product_num = int(product_id.split("-")[-1])
            output_dir = images_base_path.replace("file://", "")

            os.makedirs(output_dir, exist_ok=True)

            script_path = BASE_DIR / "download-images.js"
            result = subprocess.run(
                ["node", str(script_path), str(product_num), product_name, output_dir, product_id],
                capture_output=True,
                text=True,
                cwd=str(BASE_DIR),
                timeout=120
            )

            try:
                lines = result.stdout.strip().split('\n')
                output = json.loads(lines[-1])
                self.send_json({"success": True, **output})
            except:
                self.send_json({"success": False, "error": result.stderr or result.stdout})

        except subprocess.TimeoutExpired:
            self.send_json({"success": False, "error": "Timeout"})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)})

    def handle_save(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            catalog = data.get("catalog", {})
            product_selections = data.get("selections", {})
            images_base_path = data.get("imagesBasePath", "")

            if not catalog:
                self.send_json({"success": False, "error": "Missing catalog"})
                return

            giro_slug = catalog.get("giro", {}).get("slug", "catalog")
            source_base = images_base_path.replace("file://", "")
            images_dir = Path(source_base)
            images_dir.mkdir(parents=True, exist_ok=True)

            saved_products = []
            for product in catalog.get("products", []):
                product_id = product.get("id")
                selection = product_selections.get(product_id, {})
                selected_idx = selection.get("selectedIdx")
                existing_image = product.get("image")

                new_image = None

                if selected_idx is not None and selected_idx != 'existing':
                    candidate_dir = Path(source_base) / "_candidates" / product_id
                    if candidate_dir.exists():
                        src_webp = candidate_dir / f"{pad(selected_idx)}.webp"
                        if src_webp.exists():
                            slug = product.get("name", "").lower().replace(" ", "-")
                            dst_webp = images_dir / f"{slug}.webp"
                            shutil.copy2(src_webp, dst_webp)
                            new_image = f"/images/catalogs/{giro_slug}/{slug}.webp"
                        else:
                            new_image = existing_image
                    else:
                        new_image = existing_image
                elif selected_idx == 'existing' or (selected_idx is None and existing_image):
                    new_image = existing_image

                saved_products.append({
                    **product,
                    "image": new_image
                })

            saved_catalog = {
                "giro": catalog.get("giro"),
                "products": saved_products
            }

            data_dir = BASE_DIR / "data"
            data_dir.mkdir(exist_ok=True)
            catalog_path = data_dir / f"{giro_slug}.json"
            with open(catalog_path, "w", encoding="utf-8") as f:
                json.dump(saved_catalog, f, indent=2, ensure_ascii=False)

            self.send_json({"success": True, "path": str(catalog_path)})

        except Exception as e:
            self.send_json({"success": False, "error": str(e)})

    def handle_status(self):
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            node_ok = result.returncode == 0
        except:
            node_ok = False
        
        try:
            result = subprocess.run(
                ["python3", "-c", "import sharp; print(sharp.__version__)"],
                capture_output=True, text=True
            )
            sharp_ok = result.returncode == 0
        except:
            sharp_ok = False
        
        self.send_json({
            "status": "ok",
            "node": node_ok,
            "sharp": sharp_ok,
            "python_version": sys.version.split()[0],
            "base_dir": str(BASE_DIR)
        })

    def send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        for k, v in HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)


def main():
    print(f"Catalog Studio server starting...")
    print(f"Base directory: {BASE_DIR}")
    print(f"Open http://localhost:{PORT} in your browser")
    print(f"Press Ctrl+C to stop\n")
    
    with socketserver.TCPServer(("", PORT), CatalogHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
