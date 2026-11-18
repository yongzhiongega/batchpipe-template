"""A pretend sentiment-model service for BatchPipe (used from Chapter 4).

Start it in its own terminal and leave it running:
    python tools/practice_service.py

It listens on http://localhost:8000 and needs only Python, no extra libraries.

Two versions of the same service:
    POST /v1/classify  {"text": "..."}  ->  {"label": "positive", "score": 0.91}
    POST /v2/classify  {"text": "..."}  ->  {"result": {"sentiment": "POS", "confidence": 0.91}}
    GET  /health                        ->  {"status": "ok"}

Like a real service it is slow and sometimes unreliable. Settings, as
environment variables before the command:
    DELAY=0.3            seconds per request (default 0.3)
    FAIL_RATE=0.2        share of requests that fail with 500/503 or hang (default 0)
    MAX_CONCURRENT=50    requests handled at once; more get 429 + Retry-After (default 50)
    PRACTICE_API_KEY=x   if set, requests need the header "Authorization: Bearer x"
    PORT=8000

Example:  FAIL_RATE=0.2 python tools/practice_service.py
The same text always gets the same answer, on v1 and v2.
"""

import hashlib
import json
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DELAY = float(os.environ.get("DELAY", "0.3"))
FAIL_RATE = float(os.environ.get("FAIL_RATE", "0"))
MAX_CONCURRENT = int(os.environ.get("MAX_CONCURRENT", "50"))
API_KEY = os.environ.get("PRACTICE_API_KEY", "")
PORT = int(os.environ.get("PORT", "8000"))
HANG_SECONDS = 15

POSITIVE = {"great", "love", "excellent", "happy", "best", "good", "amazing", "perfectly", "well", "early"}
NEGATIVE = {"died", "broke", "terrible", "disappointed", "damaged", "poor", "refund", "stopped", "waste", "late", "cheap"}

slots = threading.BoundedSemaphore(MAX_CONCURRENT)


def classify(text: str) -> tuple[str, float]:
    words = {w.strip(".,!?<>/").lower() for w in text.split()}
    score = len(words & POSITIVE) - len(words & NEGATIVE)
    label = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    confidence = round(0.6 + (digest[0] / 255) * 0.39, 2)    # 0.60 to 0.99, fixed per text
    return label, confidence


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # keep connections open, like real services

    def send_json(self, status: int, body: dict, headers: dict | None = None) -> None:
        data = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {"status": "ok"})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""

        if self.path not in ("/v1/classify", "/v2/classify"):
            self.send_json(404, {"error": "not found"})
            return
        if API_KEY and self.headers.get("Authorization") != f"Bearer {API_KEY}":
            self.send_json(401, {"error": "missing or wrong API key"})
            return
        if not slots.acquire(blocking=False):
            self.send_json(429, {"error": "too many requests at once"}, {"Retry-After": "1"})
            return
        try:
            try:
                text = json.loads(raw)["text"]
                if not isinstance(text, str):
                    raise TypeError
            except (ValueError, KeyError, TypeError):
                self.send_json(400, {"error": 'send JSON like {"text": "..."}'})
                return

            time.sleep(DELAY)
            if FAIL_RATE and random.random() < FAIL_RATE:
                roll = random.random()
                if roll < 0.1:
                    time.sleep(HANG_SECONDS)          # looks like a time-out to the client
                    self.send_json(504, {"error": "took too long"})
                elif roll < 0.55:
                    self.send_json(500, {"error": "internal error"})
                else:
                    self.send_json(503, {"error": "service unavailable"}, {"Retry-After": "1"})
                return

            label, conf = classify(text)
            if self.path == "/v1/classify":
                self.send_json(200, {"label": label, "score": conf})
            else:
                code = {"positive": "POS", "negative": "NEG", "neutral": "NEU"}[label]
                self.send_json(200, {"result": {"sentiment": code, "confidence": conf}})
        finally:
            slots.release()

    def log_message(self, fmt: str, *args) -> None:   # keep the terminal quiet
        pass


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 512


if __name__ == "__main__":
    print(f"Practice service on http://localhost:{PORT}  "
          f"(delay {DELAY}s, fail rate {FAIL_RATE}, max {MAX_CONCURRENT} at once"
          f"{', API key required' if API_KEY else ''}). Ctrl+C to stop.")
    try:
        Server(("0.0.0.0", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
