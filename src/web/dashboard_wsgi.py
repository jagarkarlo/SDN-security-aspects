from __future__ import annotations
import os
from typing import Any, Dict

from ryu.app.wsgi import ControllerBase, Response, route

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def _read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _content_type(path: str) -> str:
    if path.endswith(".html"):
        return "text/html; charset=utf-8"
    if path.endswith(".css"):
        return "text/css; charset=utf-8"
    if path.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if path.endswith(".json"):
        return "application/json; charset=utf-8"
    return "application/octet-stream"


class DashboardWSGI(ControllerBase):
    def __init__(self, req, link, data: Dict[str, Any], **config):
        super().__init__(req, link, data, **config)
        self.store = data["store"]

    @route("root", "/", methods=["GET"])
    def root(self, req, **kwargs):
        body = "<html><head><meta http-equiv='refresh' content='0; url=/dashboard'></head></html>"
        return Response(content_type="text/html; charset=utf-8", body=body)

    @route("ui", "/dashboard", methods=["GET"])
    def dashboard(self, req, **kwargs):
        html_path = os.path.join(STATIC_DIR, "index.html")
        return Response(content_type="text/html; charset=utf-8", body=_read_file(html_path))

    @route("static", "/static/{fname:.*}", methods=["GET"])
    def static(self, req, fname: str, **kwargs):
        safe = os.path.normpath(fname).replace("\\", "/")
        if safe.startswith("..") or "/.." in safe:
            return Response(status=403, body=b"Forbidden")
        path = os.path.join(STATIC_DIR, safe)
        if not os.path.isfile(path):
            return Response(status=404, body=b"Not found")
        return Response(content_type=_content_type(path), body=_read_file(path))

    @route("api", "/api/dashboard", methods=["GET"])
    def api_dashboard(self, req, **kwargs):
        return Response(content_type="application/json; charset=utf-8", body=self.store.snapshot_json())
