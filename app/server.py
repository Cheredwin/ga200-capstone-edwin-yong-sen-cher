"""Local Lunchbox Quote page. Listens on 127.0.0.1 only and never sends anything to a customer."""
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from drafter import draft_email
from env import load_api_key
from quote import APPROVED_AREAS, QuoteError, price_quote

HOST, PORT = "127.0.0.1", 8000
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
PAGE = APP_DIR / "static" / "index.html"
MAX_BODY = 10_000


def handle_quote(payload, draft_fn=draft_email):
    """Price the order, then draft. The customer name goes to the draft only, never to the calculation."""
    quote = price_quote(payload.get("boxes"), payload.get("delivery_date"), payload.get("area"))
    customer = str(payload.get("customer") or "").strip() or "Customer"
    return {"quote": quote, "draft": draft_fn(quote, customer)}


def render_page():
    options = "\n".join(
        f'          <option value="{html.escape(name)}">{html.escape(name)}</option>' for name in APPROVED_AREAS
    )
    return PAGE.read_text(encoding="utf-8").replace("<!--AREA_OPTIONS-->", options)


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, obj):
        self.send(status, json.dumps(obj), "application/json")

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send(200, render_page(), "text/html; charset=utf-8")
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/quote":
            self.send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self.send_json(400, {"error": "request body missing or too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError
        except ValueError:
            self.send_json(400, {"error": "request body must be a JSON object"})
            return
        try:
            self.send_json(200, handle_quote(payload))
        except QuoteError as err:
            self.send_json(400, {"error": str(err)})


def main():
    configured = load_api_key(ROOT / ".env")
    print(f"API key: {'configured' if configured else 'not configured'}")
    print(f"Lunchbox Quote page on http://{HOST}:{PORT} (drafts are never sent)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
