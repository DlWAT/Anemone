from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse


class Handler(SimpleHTTPRequestHandler):
    # Force des MIME types compatibles modules ES sur Windows.
    # Certains environnements renvoient .js en text/plain via mimetypes système.
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".wasm": "application/wasm",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Static dev server with module-safe MIME types")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer(("", args.port), Handler)
    print(f"Serving on http://localhost:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
