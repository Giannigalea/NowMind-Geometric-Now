from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from nowmind.demo.web_controller import WebDemoController


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def make_handler(controller: WebDemoController) -> type[BaseHTTPRequestHandler]:
    class NowMindDemoHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            route = urlparse(self.path).path
            if route == "/":
                self._send_html(_INDEX_HTML)
            elif route == "/api/state":
                self._send_json(controller.to_dict())
            else:
                self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            route = urlparse(self.path).path
            try:
                payload = self._read_json()
                if route == "/api/demo":
                    data = controller.load_demo(str(payload.get("demo_id", "fresh_now")))
                elif route == "/api/run-cycle":
                    data = controller.run_cycle()
                elif route in {"/api/apply-world-event", "/api/apply-demo-a-move"}:
                    data = controller.apply_demo_world_event()
                elif route == "/api/g2-1-execute-step":
                    data = controller.g2_1_execute_one_step()
                elif route == "/api/g2-1-run-loop":
                    data = controller.g2_1_run_closed_loop()
                elif route == "/api/g2-1-reset":
                    data = controller.load_demo(controller.demo_id)
                elif route == "/api/g2-2-execute-step":
                    data = controller.g2_2_execute_one_step()
                elif route == "/api/g2-2-run-loop":
                    data = controller.g2_2_run_closed_loop()
                elif route == "/api/g2-2-reset":
                    data = controller.load_demo(controller.demo_id)
                elif route == "/api/g2-1-move-target":
                    data = controller.g2_1_move_target()
                elif route == "/api/g2-1-inject-stale-memory":
                    data = controller.g2_1_inject_stale_memory()
                elif route == "/api/g2-1-inject-false-memory":
                    data = controller.g2_1_inject_false_memory()
                elif route == "/api/g2-1-add-future":
                    data = controller.g2_1_add_future_hypothesis()
                elif route == "/api/g2-1-hide-region":
                    data = controller.g2_1_hide_region()
                elif route == "/api/query":
                    data = controller.set_query(str(payload["query_id"]))
                elif route == "/api/delete-history":
                    data = controller.delete_history_and_rerun()
                else:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self._send_json(data)
            except Exception as exc:  # noqa: BLE001 - local demo should surface errors.
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)

        def _send_json(self, data: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    return NowMindDemoHandler


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    controller: WebDemoController | None = None,
) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(controller or WebDemoController()))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local NowMind G1.1 web demo.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    url = f"http://{args.host}:{args.port}"
    print(f"Serving NowMind G1.1 demonstrator at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


_INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NowMind - Geometric Now G1</title>
  <style>
    :root {
      --ink: #17202a;
      --muted: #5c6672;
      --line: #c7d2df;
      --panel: #ffffff;
      --bg: #f4f6f8;
      --world: #dff0ff;
      --now: #e4f8e8;
      --history: #eceff3;
      --reason: #fff4dc;
      --danger: #b42318;
      --danger-bg: #fff0ed;
      --pass: #027a48;
      --pass-bg: #e7f7ed;
      --warn: #b54708;
      --warn-bg: #fff6e6;
      --shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.4;
      max-width: 100%;
    }
    header.hero {
      padding: 14px 16px;
      background: #fff;
      border-bottom: 1px solid var(--line);
    }
    .hero-grid {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 16px;
      align-items: stretch;
      max-width: 1180px;
      margin: 0 auto;
    }
    h1 {
      margin: 0;
      font-size: 26px;
      letter-spacing: 0;
      font-weight: 750;
    }
    h2, h3 {
      letter-spacing: 0;
      margin: 0 0 10px;
    }
    h2 { font-size: 18px; }
    h3 { font-size: 15px; }
    .subtitle {
      margin: 4px 0 8px;
      color: var(--muted);
      font-size: 15px;
    }
    .disclaimer {
      display: inline-block;
      max-width: 860px;
      color: #6a3b00;
      background: #fff8e6;
      border: 1px solid #ffd58a;
      border-radius: 8px;
      padding: 6px 9px;
      font-size: 12px;
    }
    .what-box {
      margin-top: 10px;
      background: #f8fbff;
      border: 1px solid #b8d4ef;
      border-radius: 8px;
      padding: 10px 12px;
    }
    .what-box ul {
      margin: 6px 0 0;
      padding-left: 18px;
      display: grid;
      grid-template-columns: repeat(2, minmax(180px, 1fr));
      gap: 3px 18px;
    }
    .what-box p {
      margin: 0;
    }
    .controls {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      box-shadow: var(--shadow);
    }
    .controls .toolbar {
      display: grid;
      grid-template-columns: 1fr;
    }
    .controls select,
    .controls button {
      width: 100%;
    }
    .toolbar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }
    button, select {
      min-height: 36px;
      border: 1px solid #93a4b7;
      background: #fff;
      color: var(--ink);
      padding: 7px 10px;
      border-radius: 6px;
      font: inherit;
    }
    button { cursor: pointer; font-weight: 650; }
    button:hover { background: #eef5fb; }
    #runCycle {
      background: #047857;
      border-color: #026a4f;
      color: #fff;
    }
    #runCycle:hover { background: #026a4f; }
    #moveEvent {
      background: #fff8e6;
      border-color: #f5c879;
      color: #7a3e00;
    }
    #moveEvent:hover { background: #fff0c2; }
    button:disabled {
      color: #9099a3;
      background: #f0f2f5;
      cursor: not-allowed;
    }
    main.app-shell {
      width: 100%;
      padding: 16px;
      display: grid;
      grid-template-columns: minmax(240px, 300px) minmax(0, 1fr);
      gap: 16px;
      align-items: start;
      max-width: 1440px;
      margin: 0 auto;
    }
    .side-panel {
      position: sticky;
      top: 12px;
      display: grid;
      gap: 12px;
      max-height: calc(100vh - 24px);
      overflow: auto;
      align-self: start;
      min-width: 0;
    }
    .content-flow {
      min-width: 0;
      display: grid;
      gap: 16px;
    }
    section, .cycle-rail-card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      box-shadow: var(--shadow);
      min-width: 0;
    }
    .architecture {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      align-items: center;
    }
    .arch-node {
      border-radius: 8px;
      border: 1px solid var(--line);
      padding: 10px;
      text-align: center;
      font-weight: 700;
      min-height: 58px;
      display: grid;
      place-items: center;
    }
    .arch-world { background: var(--world); border-color: #93c9f3; }
    .arch-now { background: var(--now); border-color: #9ad8b1; }
    .arch-answer { background: var(--reason); border-color: #f0c871; }
    .history-lane {
      margin-top: 12px;
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 8px;
      align-items: center;
    }
    .compact-architecture {
      display: grid;
      gap: 8px;
      margin-top: 8px;
    }
    .compact-architecture .arch-node {
      min-height: 42px;
      padding: 8px;
      text-align: left;
      justify-items: start;
    }
    .side-details {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px 10px;
    }
    .side-details summary {
      cursor: pointer;
      font-weight: 900;
    }
    .start-card {
      border-color: #93c9f3;
      background: #f8fbff;
    }
    .quick-steps {
      margin: 8px 0 0;
      padding-left: 22px;
      display: grid;
      gap: 6px;
    }
    .quick-steps li {
      padding-left: 2px;
    }
    .demo-brief {
      border: 1px solid #b8d4ef;
      background: #f8fbff;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 12px;
      display: grid;
      gap: 8px;
    }
    .demo-brief h3 {
      margin: 0;
      font-size: 17px;
    }
    .demo-brief p {
      margin: 0;
      color: var(--muted);
    }
    .demo-brief .quick-steps {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      padding-left: 0;
      list-style: none;
      gap: 8px;
    }
    .demo-brief .quick-steps li {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px;
      font-size: 13px;
    }
    .section-head {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: start;
      margin-bottom: 10px;
    }
    .section-copy {
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }
    .arch-arrow {
      text-align: center;
      font-size: 24px;
      color: #586474;
      font-weight: 800;
    }
    .blocked-x {
      color: var(--danger);
      font-size: 32px;
      text-align: center;
      font-weight: 900;
    }
    .triad {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr) minmax(0, 1fr);
      gap: 14px;
    }
    .concept-card {
      border-radius: 8px;
      padding: 14px;
      border: 1px solid var(--line);
      min-height: 360px;
      overflow: auto;
    }
    .world-card { background: var(--world); border-color: #93c9f3; }
    .now-card { background: var(--now); border-color: #9ad8b1; }
    .history-card { background: var(--history); border-color: #c4cbd3; }
    .eyebrow {
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }
    .badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0;
    }
    .badge {
      display: inline-flex;
      gap: 6px;
      align-items: center;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fff;
      padding: 4px 9px;
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    .badge.pass { color: var(--pass); background: var(--pass-bg); border-color: #99d8ad; }
    .badge.warn { color: var(--warn); background: var(--warn-bg); border-color: #f5c879; }
    .badge.block { color: var(--danger); background: var(--danger-bg); border-color: #ffb4a8; }
    .scene {
      position: relative;
      min-height: 190px;
      border-radius: 8px;
      border: 1px solid rgba(40, 50, 60, 0.18);
      background:
        linear-gradient(#ffffffcc, #ffffffcc),
        repeating-linear-gradient(90deg, transparent 0 38px, rgba(30, 70, 120, 0.08) 38px 39px),
        repeating-linear-gradient(0deg, transparent 0 38px, rgba(30, 70, 120, 0.08) 38px 39px);
      margin: 10px 0;
      overflow: hidden;
    }
    .mini-scene {
      min-height: 108px;
      margin: 8px 0 6px;
    }
    .cube {
      position: absolute;
      width: 86px;
      height: 74px;
      top: 56px;
      border-radius: 6px;
      display: grid;
      place-items: center;
      color: #fff;
      font-weight: 800;
      text-shadow: 0 1px 2px rgba(0,0,0,0.35);
      box-shadow: 0 10px 18px rgba(15, 23, 42, 0.22);
      transform: skewY(-2deg);
    }
    .cube.red { background: linear-gradient(145deg, #ff6b5f, #c81e1e); }
    .cube.blue { background: linear-gradient(145deg, #55aaff, #175cd3); }
    .cube.left { left: 18%; }
    .cube.right { right: 18%; }
    .mini-scene .cube {
      width: 58px;
      height: 46px;
      top: 24px;
      font-size: 11px;
    }
    .mini-scene .cube.left { left: 12%; }
    .mini-scene .cube.right { right: 12%; }
    .scene-arrow {
      position: absolute;
      left: 42%;
      right: 42%;
      top: 86px;
      height: 3px;
      background: #667085;
    }
    .scene-arrow::after {
      content: "";
      position: absolute;
      right: -2px;
      top: -5px;
      border-left: 10px solid #667085;
      border-top: 6px solid transparent;
      border-bottom: 6px solid transparent;
    }
    .scene-caption {
      position: absolute;
      left: 12px;
      right: 12px;
      bottom: 12px;
      border: 1px solid rgba(40, 50, 60, 0.14);
      background: #fff;
      color: #475467;
      border-radius: 6px;
      padding: 8px;
      font-weight: 800;
      text-align: center;
    }
    .mini-scene .scene-arrow { top: 48px; }
    .mini-scene .scene-caption {
      left: 8px;
      right: 8px;
      bottom: 6px;
      padding: 5px;
      font-size: 11px;
    }
    .containment-scene {
      min-height: 220px;
      display: grid;
      place-items: center;
      background: #f8fbff;
    }
    .cabinet {
      width: min(88%, 360px);
      height: 170px;
      border: 6px solid #7a5c3b;
      border-radius: 8px;
      background: #d7b98a;
      display: grid;
      place-items: center;
    }
    .box {
      width: 170px;
      height: 100px;
      border: 4px solid #8b5e34;
      border-radius: 6px;
      background: #f0c77e;
      display: grid;
      place-items: center;
      font-weight: 800;
    }
    .key {
      width: 54px;
      height: 16px;
      border-radius: 999px;
      background: #f7d046;
      position: relative;
      color: #604900;
      font-size: 11px;
      text-align: center;
      line-height: 16px;
    }
    .mini-scene.containment-scene { min-height: 120px; }
    .containment-row {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 18px;
      width: 100%;
      padding: 18px 12px 46px;
    }
    .mini-scene .containment-row {
      gap: 8px;
      padding: 10px 6px 32px;
    }
    .mini-scene .cabinet {
      width: 90%;
      height: 92px;
      border-width: 4px;
    }
    .mini-scene .box {
      width: 110px;
      height: 58px;
      border-width: 3px;
      font-size: 12px;
    }
    .mini-scene .key {
      width: 40px;
      height: 12px;
      line-height: 12px;
      font-size: 9px;
    }
    .mini-scene .key::before {
      left: -15px;
      top: -5px;
      width: 18px;
      height: 18px;
      border-width: 4px;
    }
    .loose-cabinet {
      width: 140px;
      height: 108px;
      font-weight: 900;
      color: #5a3c1e;
    }
    .mini-scene .loose-cabinet {
      width: 92px;
      height: 62px;
      font-size: 11px;
    }
    .key::before {
      content: "";
      position: absolute;
      left: -20px;
      top: -7px;
      width: 26px;
      height: 26px;
      border: 5px solid #f7d046;
      border-radius: 50%;
      background: transparent;
    }
    .conflict-scene {
      background: var(--danger-bg);
      border-color: #ffb4a8;
    }
    .conflict-scene .scene-caption {
      color: var(--danger);
      border-color: #ffb4a8;
    }
    .linear-scene {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 28px 14px 58px;
    }
    .object-strip {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      flex-wrap: nowrap;
    }
    .object-block {
      min-width: 72px;
      min-height: 64px;
      border: 2px solid #596579;
      border-radius: 7px;
      display: grid;
      place-items: center;
      color: #fff;
      font-weight: 900;
      text-align: center;
      padding: 8px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.35);
      box-shadow: 0 10px 18px rgba(15, 23, 42, 0.20);
      transform: skewY(-2deg);
      overflow-wrap: anywhere;
    }
    .object-link {
      color: #667085;
      font-weight: 900;
      white-space: nowrap;
    }
    .mini-scene.linear-scene {
      min-height: 112px;
      padding: 16px 8px 36px;
    }
    .mini-scene .object-strip {
      gap: 5px;
    }
    .mini-scene .object-block {
      min-width: 48px;
      min-height: 42px;
      padding: 5px;
      font-size: 11px;
    }
    .mini-scene .object-link {
      font-size: 11px;
    }
    .relation-graph {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 8px 0;
    }
    .edge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 7px 8px;
      background: #fff;
      font-size: 13px;
    }
    .edge.observed { border-color: #7bc69a; }
    .edge.inferred { border-color: #84adff; }
    .node {
      background: #f8fafc;
      border: 1px solid #d0d5dd;
      border-radius: 6px;
      padding: 3px 6px;
      font-weight: 800;
    }
    .arrow { color: #667085; font-weight: 900; }
    .stepper {
      display: grid;
      grid-template-columns: 1fr;
      gap: 6px;
    }
    .step {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px;
      min-height: 0;
    }
    .step.active { border-color: #7bc69a; background: #f0fff4; }
    .step-number {
      font-weight: 900;
      color: var(--pass);
      margin-bottom: 2px;
    }
    .compare, .can-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .compare-card, .can-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px;
    }
    .compare-card.current, .can-see {
      border-color: #7bc69a;
      background: #f4fff7;
    }
    .cannot-see {
      border-color: #c4cbd3;
      background: #f7f8fa;
    }
    .conclusion {
      margin-top: 10px;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid #99d8ad;
      background: var(--pass-bg);
      color: var(--pass);
      font-weight: 800;
    }
    details {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      margin-top: 10px;
      padding: 8px 10px;
      min-width: 0;
    }
    summary { cursor: pointer; font-weight: 800; }
    .table {
      width: 100%;
      max-width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin-top: 8px;
      font-size: 13px;
    }
    .table th, .table td {
      border-bottom: 1px solid rgba(60, 70, 80, 0.18);
      text-align: left;
      padding: 6px;
      vertical-align: top;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .pill {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fff;
      font-size: 12px;
      white-space: nowrap;
    }
    .pill.observed { border-color: #027a48; color: #027a48; }
    .pill.inferred { border-color: #175cd3; color: #175cd3; }
    .status-true { color: var(--pass); font-weight: 800; }
    .status-contradictory, .warning { color: var(--danger); font-weight: 800; }
    .small { color: var(--muted); font-size: 12px; }
    .empty {
      border: 1px dashed #b8c1cc;
      border-radius: 8px;
      padding: 12px;
      color: var(--muted);
      background: rgba(255,255,255,0.6);
    }
    .cycle-rail {
      display: grid;
      gap: 8px;
    }
    .cycle-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px;
    }
    .cycle-card.active {
      border-color: #7bc69a;
      background: #f4fff7;
      box-shadow: inset 4px 0 0 #039855;
    }
    .cycle-head {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      margin-bottom: 4px;
    }
    .cycle-number {
      font-size: 15px;
      font-weight: 900;
    }
    .cycle-summary {
      font-size: 12px;
      color: var(--muted);
      overflow-wrap: anywhere;
    }
    .cycle-answer {
      margin-top: 6px;
      font-size: 12px;
      font-weight: 800;
    }
    .pending-change {
      margin-top: 8px;
      border: 1px solid #f5c879;
      border-radius: 8px;
      background: var(--warn-bg);
      color: var(--warn);
      padding: 8px;
      font-size: 12px;
      font-weight: 800;
    }
    .inspector-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
      gap: 12px;
      align-items: start;
    }
    .plain-details {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 10px 12px;
      min-width: 0;
    }
    .temporal-lanes {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 12px;
    }
    .temporal-lane {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
      min-width: 0;
    }
    .temporal-present {
      border-color: #7bc69a;
      background: #f4fff7;
      box-shadow: inset 4px 0 0 #039855;
    }
    .temporal-memory {
      border-color: #f5c879;
      background: #fff8e6;
      box-shadow: inset 4px 0 0 #d98a00;
    }
    .temporal-future {
      border-color: #a8b7ff;
      background: #f4f6ff;
      box-shadow: inset 4px 0 0 #445bd8;
    }
    .temporal-scene {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin: 10px 0;
      align-items: end;
    }
    .box-slot {
      min-height: 94px;
      border: 2px solid #95a3b8;
      border-radius: 8px;
      background: #f8fafc;
      display: grid;
      place-items: center;
      position: relative;
      font-weight: 800;
      color: var(--muted);
    }
    .box-slot.active-present { border-color: #039855; background: #e7f7ed; color: #027a48; }
    .box-slot.active-memory { border-color: #d98a00; background: #fff2cc; color: #92400e; }
    .box-slot.active-future { border-color: #445bd8; background: #edf0ff; color: #303f9f; }
    .ball-token {
      width: 34px;
      height: 34px;
      border-radius: 999px;
      display: grid;
      place-items: center;
      background: #ffffff;
      border: 2px solid currentColor;
      color: inherit;
      font-size: 11px;
      margin-top: 6px;
    }
    .temporal-answer {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fff;
      margin-top: 12px;
    }
    .g21-controls {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin: 12px 0;
    }
    .g21-controls button {
      min-width: 0;
      padding-inline: 8px;
    }
    .spatial-layout {
      display: grid;
      grid-template-columns: minmax(320px, 1fr) minmax(280px, 0.75fr);
      gap: 12px;
      align-items: start;
    }
    .spatial-board {
      display: grid;
      gap: 4px;
      width: 100%;
      max-width: 720px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      padding: 8px;
    }
    .spatial-cell {
      aspect-ratio: 1;
      min-height: 34px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      background: #f8fafc;
      position: relative;
      display: grid;
      place-items: center;
      font-size: 11px;
      font-weight: 900;
      color: #344054;
      overflow: hidden;
    }
    .spatial-cell.occupied {
      background: #334155;
      border-color: #0f172a;
      color: #fff;
    }
    .spatial-cell.unknown {
      background:
        repeating-linear-gradient(45deg, #e2e8f0 0 7px, #f8fafc 7px 14px);
      color: #64748b;
    }
    .spatial-cell.selected-path {
      box-shadow: inset 0 0 0 3px #0ea5e9;
      background: #e0f2fe;
    }
    .spatial-cell.memory-cell {
      outline: 3px dashed #d98a00;
      outline-offset: -5px;
      background: #fff8e6;
    }
    .spatial-cell.future-cell {
      outline: 3px dotted #7c3aed;
      outline-offset: -8px;
      background: #f4f0ff;
    }
    .spatial-cell.scan-cell {
      box-shadow: inset 0 0 0 3px #14b8a6;
    }
    .spatial-cell.rejected-cell {
      box-shadow: inset 0 0 0 3px #dc2626;
    }
    .spatial-token {
      display: inline-grid;
      place-items: center;
      width: 24px;
      height: 24px;
      border-radius: 999px;
      color: #fff;
      font-size: 11px;
      font-weight: 950;
      z-index: 2;
    }
    .agent-token { background: #027a48; }
    .target-token { background: #175cd3; }
    .obstacle-token { background: #0f172a; }
    .path-dot {
      position: absolute;
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: #0284c7;
      bottom: 4px;
      right: 4px;
    }
    .spatial-legend {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      margin: 10px 0;
      font-size: 12px;
      font-weight: 800;
    }
    .legend-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 8px;
      background: #fff;
    }
    .legend-solid { box-shadow: inset 4px 0 0 #039855; }
    .legend-dashed { box-shadow: inset 4px 0 0 #d98a00; }
    .legend-dotted { box-shadow: inset 4px 0 0 #7c3aed; }
    .plan-panel {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px;
      display: grid;
      gap: 8px;
    }
    .metric-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 8px;
      margin-top: 8px;
    }
    .metric-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      background: #fff;
    }
    .metric-card strong {
      display: block;
      font-size: 18px;
    }
    .benchmark-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(260px, 0.8fr);
      gap: 12px;
      align-items: start;
    }
    .g23-compare-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      align-items: start;
      margin-top: 12px;
    }
    .g23-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 12px;
      min-width: 0;
    }
    .g23-card.nowmind { border-color: #7bc69a; background: #f4fff7; }
    .g23-card.chronological { border-color: #84adff; background: #f6f8ff; }
    .g23-metrics {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px;
      margin: 8px 0;
    }
    .g23-metric {
      border: 1px solid rgba(60, 70, 80, 0.16);
      border-radius: 8px;
      background: #fff;
      padding: 7px;
      min-width: 0;
    }
    .json-block {
      max-height: 320px;
      overflow: auto;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border: 1px solid rgba(60, 70, 80, 0.18);
      border-radius: 8px;
      background: #101828;
      color: #f8fafc;
      padding: 10px;
      font-size: 12px;
      line-height: 1.35;
    }
    @media (max-width: 820px) {
      main.app-shell {
        grid-template-columns: minmax(220px, 270px) minmax(0, 1fr);
        gap: 10px;
        padding: 10px;
      }
      section, .cycle-rail-card {
        padding: 12px;
      }
    }
    @media (max-width: 1080px) {
      .hero-grid, .triad, .can-grid, .compare, .inspector-grid, .temporal-lanes, .benchmark-grid, .g23-compare-grid, .spatial-layout, .g21-controls, .metric-strip, .spatial-legend { grid-template-columns: 1fr; }
      .architecture, .stepper, .history-lane { grid-template-columns: 1fr; }
      .what-box ul, .demo-brief .quick-steps { grid-template-columns: 1fr; }
    }
    @media (max-width: 700px) {
      main.app-shell { grid-template-columns: 1fr; }
      .side-panel {
        position: static;
        max-height: none;
      }
    }
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-grid">
      <div>
        <h1>NowMind - Geometric Now G1</h1>
        <p class="subtitle">A PCT-inspired experiment in rebuilding a fresh cognitive state every cycle.</p>
        <p class="disclaimer">This prototype tests representation and reasoning behavior. It does not demonstrate or claim phenomenal consciousness.</p>
        <div class="what-box">
          <h2>What this tests</h2>
          <p><strong>One rule:</strong> the world can persist, but every <strong>Run cycle</strong> rebuilds a fresh Current Now. The reasoner sees only that Now; history is for inspection, not cognition.</p>
        </div>
      </div>
    </div>
  </header>

  <main class="app-shell">
    <aside class="side-panel" aria-label="Demo controls and cycles">
      <div class="controls">
        <h2>Demo controls</h2>
        <div class="toolbar">
          <select id="demoSelect" title="Demo">
            <option value="fresh_now">Demo A - Fresh Now</option>
            <option value="inference">Demo B - Inference</option>
            <option value="containment">Demo C - Containment</option>
            <option value="contradiction">Demo D - Contradiction</option>
            <option value="g2_memory_present">G2-A - Memory vs Present</option>
            <option value="g2_false_memory">G2-B - False Memory</option>
            <option value="g2_future">G2-C - Future Hypothesis</option>
            <option value="g2_confidence">G2-D - Confidence Conflict</option>
            <option value="g2_hidden">G2-E - No Current Visibility</option>
            <option value="g2_contradiction">G2-F - Current Contradiction</option>
            <option value="g2_1_replanning">G2.1-A - Possibility Replanning</option>
            <option value="g2_1_stale_memory">G2.1-B - Stale Memory Rejection</option>
            <option value="g2_1_unknown_memory">G2.1-C - Conditional Memory Route</option>
            <option value="g2_1_future_target">G2.1-D - Future Target Hypothesis</option>
            <option value="g2_2_verify_false">G2.2-A - Verify False Memory</option>
            <option value="g2_2_verify_correct">G2.2-B - Verify Correct Memory</option>
            <option value="g2_2_1_stale_target_recovery">G2.2.1-R1 - Stale Target Recovery</option>
            <option value="g2_2_1_hidden_obstacle_recovery">G2.2.1-R2 - Hidden Obstacle Recovery</option>
            <option value="g2_3_model_comparison">G2.3 - Model Comparison</option>
            <option value="full_g_reviewer">Full-G Reviewer</option>
          </select>
          <button id="runCycle">Run cycle</button>
          <button id="moveEvent">Apply world event</button>
          <button id="deleteHistory">Delete external history</button>
        </div>
        <p class="small" id="worldEventHelp"></p>
        <div class="badges" id="badgeBody"></div>
      </div>
      <div class="cycle-rail-card start-card">
        <h2>Start here</h2>
        <ol class="quick-steps">
          <li>Choose a demo.</li>
          <li>Click <strong>Run cycle</strong> to build the fresh Current Now.</li>
          <li>Click the world event button, then run another cycle.</li>
          <li>Watch the answer and cycle rail change.</li>
        </ol>
      </div>
      <div class="cycle-rail-card">
        <h2>World now</h2>
        <div id="sideWorldBody"></div>
      </div>
      <div class="cycle-rail-card" aria-live="polite">
        <h2>Cycle rail</h2>
        <div id="cycleRailBody"></div>
      </div>
      <div class="cycle-rail-card">
        <h2>How it works</h2>
        <details class="side-details">
          <summary>Visual architecture</summary>
          <div class="compact-architecture" aria-label="World to current Now to answer">
            <div class="arch-node arch-world">WorldState<br><span class="small">persistent environment</span></div>
            <div class="arch-node arch-world">Observation<br><span class="small">current snapshot</span></div>
            <div class="arch-node arch-now">PresentGeometry<br><span class="small">current relations</span></div>
            <div class="arch-node arch-now">NowState<br><span class="small">fresh object per cycle</span></div>
            <div class="arch-node arch-now">Reasoner<br><span class="small">current Now only</span></div>
            <div class="arch-node arch-answer">Answer<br><span class="small">with explanation</span></div>
            <div class="arch-node" style="background: var(--history); border-color: #c4cbd3;">External history<br><span class="small">researcher-only, blocked from reasoner</span></div>
          </div>
        </details>
        <details class="side-details">
          <summary>Guided processing path</summary>
          <div class="stepper" id="stepperBody"></div>
        </details>
      </div>
    </aside>

    <div class="content-flow">
    <section id="liveSection">
      <div class="section-head">
        <div>
          <h2>Live experiment</h2>
          <p class="section-copy">Read this as three separate things: the outside world, the fresh Current Now, and old cycles kept only for inspection.</p>
        </div>
      </div>
      <div class="demo-brief" id="demoBriefBody"></div>
      <div class="triad">
        <div class="concept-card world-card">
          <div class="eyebrow">Persistent world</div>
          <h3>What currently exists outside cognition</h3>
          <div id="worldBody"></div>
        </div>
        <div class="concept-card now-card">
          <div class="eyebrow">Current Now</div>
          <h3>What the reasoner currently sees</h3>
          <div id="nowBody"></div>
        </div>
        <div class="concept-card history-card">
          <div class="eyebrow">External history</div>
          <h3>Previous Nows visible to researcher only</h3>
          <div id="historyBody"></div>
        </div>
      </div>
    </section>

    <section id="beforeAfterSection">
      <h2>Demo A before / after</h2>
      <div id="beforeAfterBody"></div>
    </section>

    <section id="g1ReasonerSection">
      <div class="section-head">
        <div>
          <h2>Reasoner answer</h2>
          <p class="section-copy">This is the result produced from the current Now only. If the world changed, run the next cycle before expecting this answer to change.</p>
        </div>
      </div>
      <div class="toolbar">
        <select id="querySelect" title="Predefined query"></select>
        <button id="runQuery">Run current query</button>
      </div>
      <div id="reasoningBody"></div>
    </section>

    <section id="temporalSection" hidden>
      <div class="section-head">
        <div>
          <h2 id="temporalTitle">Temporal Geometry</h2>
          <p class="section-copy" id="temporalCopy">G2 keeps present evidence, reconstructed memory, and future hypothesis visible as separate current channels.</p>
        </div>
      </div>
      <div id="temporalBody"></div>
    </section>

    <section id="benchmarkSection" hidden>
      <div class="section-head">
        <div>
          <h2>Benchmark dashboard</h2>
          <p class="section-copy">Synthetic source-separation results generated by the local G2 benchmark runner.</p>
        </div>
      </div>
      <div id="benchmarkBody"></div>
    </section>

    <section id="fullGSection" hidden>
      <div class="section-head">
        <div>
          <h2>Full-G reviewer package</h2>
          <p class="section-copy">A local, offline milestone view from G1 through G2.3.4. It summarizes what changed, what passed, and what did not replicate.</p>
        </div>
      </div>
      <div id="fullGBody"></div>
    </section>

    <section id="g1InspectorSection">
      <details class="plain-details" open>
        <summary>Why this answer?</summary>
        <div class="inspector-grid">
          <div>
            <h3>Present Geometry graph</h3>
            <div id="graphBody"></div>
          </div>
          <div>
            <h3>Reasoner boundary</h3>
            <div class="can-grid">
              <div class="can-card can-see">
                <h3>What the reasoner can see right now</h3>
                <div id="canSeeBody"></div>
              </div>
              <div class="can-card cannot-see">
                <h3>What exists but the reasoner cannot see</h3>
                <div id="cannotSeeBody"></div>
              </div>
            </div>
          </div>
        </div>
      </details>
    </section>

    <section id="technicalSection">
      <h2>Technical details</h2>
      <details>
        <summary>Relation tables and validation output</summary>
        <div id="technicalBody"></div>
      </details>
    </section>
    </div>
  </main>

  <script>
    let state = null;
    const isG2 = () => state?.schema === "nowmind.g2.web_state.v1";
    const isG21 = () => state?.schema === "nowmind.g2_1.web_state.v1";
    const isG22 = () => state?.schema === "nowmind.g2_2.web_state.v1";
    const isG23 = () => state?.schema === "nowmind.g2_3.web_state.v1";
    const isFullG = () => state?.schema === "nowmind.full_g.web_state.v1";
    const isTemporalFamily = () => isG2() || isG21() || isG22() || isG23();
    const relationText = (rel) => `${rel.relation_type.toUpperCase()}(${rel.source_id}, ${rel.target_id})`;
    const humanRelation = (rel) => `${rel.source_id} ${rel.relation_type.toUpperCase()} ${rel.target_id}`;
    const allCurrentRelations = () => state?.current_now ? [...state.current_now.observed_relations, ...state.current_now.inferred_relations] : [];
    const post = async (url, data = {}) => {
      const res = await fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      });
      state = await res.json();
      render();
    };
    const getState = async () => {
      const res = await fetch("/api/state");
      state = await res.json();
      render();
    };
    const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    })[char]);
    const findRelation = (relations, source, target, type) =>
      relations.find((rel) => rel.source_id === source && rel.target_id === target && rel.relation_type === type);
    const leftRightRelations = (relations) =>
      (relations || []).filter((rel) => rel.relation_type === "left_of" || rel.relation_type === "right_of");
    const objectColors = (entityId, index) => {
      const known = {
        red_cube: ["#ff6b5f", "#c81e1e", "#a31313"],
        blue_cube: ["#55aaff", "#175cd3", "#0b4bb3"],
        a: ["#34d399", "#047857", "#026a4f"],
        b: ["#fbbf24", "#b45309", "#92400e"],
        c: ["#a78bfa", "#6d28d9", "#5b21b6"]
      };
      const palette = [
        ["#38bdf8", "#0369a1", "#075985"],
        ["#fb7185", "#be123c", "#9f1239"],
        ["#4ade80", "#15803d", "#166534"],
        ["#facc15", "#a16207", "#854d0e"],
        ["#c084fc", "#7e22ce", "#6b21a8"]
      ];
      return known[entityId] || palette[index % palette.length];
    };
    const entityIds = (entities) => (entities || []).map((entity) => entity.entity_id);
    const orderedLeftRightObjects = (relations, entities = []) => {
      const scores = new Map();
      const seenOrder = [];
      const ensure = (id) => {
        if (!scores.has(id)) {
          scores.set(id, 0);
          seenOrder.push(id);
        }
      };
      leftRightRelations(relations).forEach((rel) => {
        ensure(rel.source_id);
        ensure(rel.target_id);
        if (rel.relation_type === "left_of") {
          scores.set(rel.source_id, scores.get(rel.source_id) - 1);
          scores.set(rel.target_id, scores.get(rel.target_id) + 1);
        } else {
          scores.set(rel.source_id, scores.get(rel.source_id) + 1);
          scores.set(rel.target_id, scores.get(rel.target_id) - 1);
        }
      });
      const connected = seenOrder.sort((left, right) =>
        scores.get(left) - scores.get(right) || left.localeCompare(right)
      );
      const disconnected = entityIds(entities)
        .filter((entityId) => !scores.has(entityId))
        .sort((left, right) => left.localeCompare(right));
      return { connected, disconnected, ordered: [...connected, ...disconnected] };
    };
    const renderLinearScene = (relations, title, compact, contradiction, entities = []) => {
      const compactClass = compact ? " mini-scene" : "";
      const { connected, disconnected, ordered } = orderedLeftRightObjects(relations, entities);
      if (!ordered.length) {
        return `<div class="scene${compactClass}" aria-label="${escapeHtml(title || "No relation scene")}">
          <div class="scene-caption">No left/right relation to draw</div>
        </div>`;
      }
      const blockFor = (entityId, index) => {
        const colors = objectColors(entityId, index);
        return `<div class="object-block" style="background: linear-gradient(145deg, ${colors[0]}, ${colors[1]}); border-color: ${colors[2]};">${escapeHtml(entityId)}</div>`;
      };
      const connectedStrip = connected.map((entityId, index) =>
        index === 0 ? blockFor(entityId, index) : `<span class="object-link">-&gt;</span>${blockFor(entityId, index)}`
      ).join("");
      const disconnectedStrip = disconnected.map((entityId, index) =>
        `${index === 0 ? "<span class='object-link'>gap</span>" : ""}${blockFor(entityId, connected.length + index)}`
      ).join("");
      const strip = `${connectedStrip}${disconnectedStrip}`;
      const caption = contradiction
        ? "Contradiction: incompatible left/right facts are both observed now"
        : disconnected.length
          ? `Known chain: ${connected.map(escapeHtml).join(" -&gt; ")}; disconnected: ${disconnected.map(escapeHtml).join(", ")}`
          : `Left-to-right order: ${connected.map(escapeHtml).join(" -&gt; ")}`;
      return `<div class="scene${compactClass} linear-scene ${contradiction ? "conflict-scene" : ""}" aria-label="${escapeHtml(title || caption)}">
        <div class="object-strip">${strip}</div>
        <div class="scene-caption">${caption}</div>
      </div>`;
    };
    const renderContainmentScene = (relations, title, compact, entities = []) => {
      const compactClass = compact ? " mini-scene" : "";
      const hasKeyInsideBox = !!findRelation(relations, "key", "box", "inside");
      const hasBoxInsideCabinet = !!findRelation(relations, "box", "cabinet", "inside");
      const hasKey = entityIds(entities).includes("key") || hasKeyInsideBox;
      if (hasKeyInsideBox && hasBoxInsideCabinet) {
        return `<div class="scene${compactClass} containment-scene" aria-label="${escapeHtml(title || "key inside box inside cabinet")}">
          <div class="cabinet"><div class="box">box<div class="key">key</div></div></div>
          <div class="scene-caption">Nested containment: key inside box inside cabinet</div>
        </div>`;
      }
      if (hasKeyInsideBox) {
        return `<div class="scene${compactClass} containment-scene" aria-label="${escapeHtml(title || "key inside box, cabinet disconnected")}">
          <div class="containment-row">
            <div class="box">box<div class="key">key</div></div>
            <span class="object-link">gap</span>
            <div class="cabinet loose-cabinet">cabinet</div>
          </div>
          <div class="scene-caption">Known containment: key inside box; cabinet disconnected</div>
        </div>`;
      }
      if (hasBoxInsideCabinet) {
        return `<div class="scene${compactClass} containment-scene" aria-label="${escapeHtml(title || "box inside cabinet, key disconnected")}">
          <div class="containment-row">
            ${hasKey ? `<div class="key">key</div><span class="object-link">gap</span>` : ""}
            <div class="cabinet loose-cabinet"><div class="box">box</div></div>
          </div>
          <div class="scene-caption">Known containment: box inside cabinet; key disconnected</div>
        </div>`;
      }
      return `<div class="scene${compactClass} containment-scene" aria-label="${escapeHtml(title || "No containment relation")}">
        <div class="containment-row">
          ${entityIds(entities).map((entityId, index) => `<div class="object-block" style="background: linear-gradient(145deg, ${objectColors(entityId, index)[0]}, ${objectColors(entityId, index)[1]}); border-color: ${objectColors(entityId, index)[2]};">${escapeHtml(entityId)}</div>`).join("<span class='object-link'>gap</span>")}
        </div>
        <div class="scene-caption">No containment relation to draw</div>
      </div>`;
    };
    const renderBadges = () => {
      const badges = state.success_badges || [];
      if (!badges.length) return `<span class="badge">Run a cycle to see PASS indicators</span>`;
      return badges.map((badge) => `<span class="badge ${badge.tone === "pass" ? "pass" : "warn"}">${badge.label}: ${badge.status}</span>`).join("");
    };
    const renderStepper = () => {
      if (isFullG()) {
        const steps = [
          ["Open package", "Start with milestone freeze and results summary."],
          ["Inspect architecture", "Check that memory and previous Nows do not feed cognition directly."],
          ["Read results", "Positive source invariants and negative N/C model results are both visible."],
          ["Check nonclaims", "No consciousness, sentience, quantum, or general superiority claim is made."],
          ["Reproduce locally", "Run tests, demos, and local benchmarks without paid cloud services."]
        ];
        return steps.map((step, index) => `
          <div class="step active">
            <div class="step-number">${index + 1}</div>
            <div><strong>${step[0]}</strong><div class="small">${step[1]}</div></div>
          </div>`).join("");
      }
      if (isG23()) {
        const steps = [
          ["Build one task", "The hero scenario contains current observation, stale memory, future hypothesis, and the current query."],
          ["Render N and C", "NowMind structured and chronological prompts are built from the same admissible fact set."],
          ["Call same faculty", "The same replaceable backend produces proposal JSON for each representation."],
          ["Validate", "Symbolic validation keeps proposal-only and validated results separate."],
          ["Inspect", "Evaluator truth stays hidden until you open the reveal control."]
        ];
        return steps.map((step, index) => `
          <div class="step active">
            <div class="step-number">${index + 1}</div>
            <div><strong>${step[0]}</strong><div class="small">${step[1]}</div></div>
          </div>`).join("");
      }
      if (isG22()) {
        const done = !!state.epistemic_now;
        const steps = [
          ["Observe partially", "Sensor builds visible cells; fog remains UNKNOWN."],
          ["Reconstruct", "Memory appears as typed assumptions, not observed cells."],
          ["Compare choices", "Policy scores safe, shortcut, and verify-first options."],
          ["Inspect", "SCAN costs time and reveals current evidence."],
          ["Replan", "Fresh TemporalNowState is built before action continues."]
        ];
        return steps.map((step, index) => `
          <div class="step ${done ? "active" : ""}">
            <div class="step-number">${index + 1}</div>
            <div><strong>${step[0]}</strong><div class="small">${step[1]}</div></div>
          </div>`).join("");
      }
      if (isG21()) {
        const done = !!state.spatial_now;
        const steps = [
          ["Observe", "WorldState -> current 2D SpatialGeometry."],
          ["Hypothesize", "Transformations create candidate future geometries."],
          ["Plan", "A* selects a path with assumptions labeled."],
          ["Execute", "Only one action mutates the external world."],
          ["Reobserve", "Fresh TemporalNowState is built before continuing."]
        ];
        return steps.map((step, index) => `
          <div class="step ${done ? "active" : ""}">
            <div class="step-number">${index + 1}</div>
            <div><strong>${step[0]}</strong><div class="small">${step[1]}</div></div>
          </div>`).join("");
      }
      if (isG2()) {
        const done = !!state.temporal_now;
        const steps = [
          ["World observed", "Current observation builds Present Geometry."],
          ["Trace retrieved", "MemoryStore returns traces, not old Nows."],
          ["Memory reconstructed", "Past content is rebuilt now and labeled."],
          ["Future represented", "Hypotheses remain possible future content."],
          ["Temporal answer", "Query policy selects the right source lane."]
        ];
        return steps.map((step, index) => `
          <div class="step ${done ? "active" : ""}">
            <div class="step-number">${index + 1}</div>
            <strong>${step[0]}</strong>
            <div class="small">${step[1]}</div>
          </div>`).join("");
      }
      const done = !!state.current_now;
      const steps = [
        ["World exists", "Persistent environment has objects and relations."],
        ["Observation taken", "Current world snapshot is read."],
        ["Geometry built", "Observed and inferred relations are separated."],
        ["Fresh Now created", "A new now_id appears for this cycle."],
        ["Reasoner answers", "The query is answered from the current Now only."],
        ["Archived externally", "The researcher can inspect old cycles outside cognition."]
      ];
      return steps.map((step, index) => `
        <div class="step ${done ? "active" : ""}">
          <div class="step-number">${index + 1}</div>
          <strong>${step[0]}</strong>
          <div class="small">${step[1]}</div>
        </div>`).join("");
    };
    const renderScene = (relations, title = "", compact = false, entities = []) => {
      const rels = relations || [];
      const compactClass = compact ? " mini-scene" : "";
      const contradiction = rels.some((rel) => rel.source_id === "red_cube" && rel.target_id === "blue_cube" && rel.relation_type === "left_of")
        && rels.some((rel) => rel.source_id === "red_cube" && rel.target_id === "blue_cube" && rel.relation_type === "right_of");
      const containment = rels.some((rel) => rel.source_id === "key" && rel.target_id === "box" && rel.relation_type === "inside")
        || rels.some((rel) => rel.source_id === "box" && rel.target_id === "cabinet" && rel.relation_type === "inside");
      if (containment) {
        return renderContainmentScene(rels, title, compact, entities);
      }
      if (leftRightRelations(rels).length) {
        return renderLinearScene(rels, title, compact, contradiction, entities);
      }
      const redRight = findRelation(rels, "red_cube", "blue_cube", "right_of");
      const redClass = redRight ? "right" : "left";
      const blueClass = redRight ? "left" : "right";
      const caption = redRight ? "red_cube is right of blue_cube" : "red_cube is left of blue_cube";
      return `<div class="scene${compactClass} ${contradiction ? "conflict-scene" : ""}" aria-label="${title || caption}">
        <div class="cube red ${redClass}">red_cube</div>
        <div class="scene-arrow"></div>
        <div class="cube blue ${blueClass}">blue_cube</div>
        <div class="scene-caption">${contradiction ? "Contradiction: LEFT_OF and RIGHT_OF are both observed now" : caption}</div>
      </div>`;
    };
    const relationGraph = (relations, limit = 10) => {
      if (!relations || relations.length === 0) return `<div class="empty">No relations yet. Run a cycle.</div>`;
      return `<div class="relation-graph">${relations.slice(0, limit).map((rel) => `
        <div class="edge ${rel.provenance === "observed_now" ? "observed" : "inferred"}">
          <span class="node">${rel.source_id}</span>
          <span class="arrow">-- ${rel.relation_type.toUpperCase()} --&gt;</span>
          <span class="node">${rel.target_id}</span>
          <span class="pill ${rel.provenance === "observed_now" ? "observed" : "inferred"}">${rel.provenance}</span>
        </div>`).join("")}</div>`;
    };
    const relationTable = (relations) => {
      if (!relations || relations.length === 0) return "<p>None.</p>";
      return `<table class="table"><thead><tr><th>Relation</th><th>Confidence</th><th>Provenance</th><th>Rule</th></tr></thead><tbody>${
        relations.map((rel) => `<tr><td>${relationText(rel)}</td><td>${rel.confidence.toFixed(2)}</td><td><span class="pill ${rel.provenance === "observed_now" ? "observed" : "inferred"}">${rel.provenance}</span></td><td>${rel.rule_id || ""}</td></tr>`).join("")
      }</tbody></table>`;
    };
    const renderWorld = () => {
      const relations = state.world.relations || [];
      return `
        <p><strong>World version:</strong> ${state.world.world_version}</p>
        ${renderScene(relations, "Persistent world scene", false, state.world.entities)}
        ${renderPendingWorldChange()}
        <p class="small">This external world can persist and change through explicit world events.</p>
        <details><summary>World facts</summary>
          <ul>${relations.map((rel) => `<li>${humanRelation(rel)} confidence=${rel.confidence.toFixed(2)}</li>`).join("") || "<li>No world relations</li>"}</ul>
        </details>`;
    };
    const renderNow = () => {
      if (!state.current_now) {
        return `<div class="empty">No current Now yet. Click <strong>Run cycle</strong> to rebuild the current cognitive state.</div>`;
      }
      const now = state.current_now;
      const relations = [...now.observed_relations, ...now.inferred_relations];
      const validation = now.validation;
      return `
        <p><strong>Cycle:</strong> ${now.cycle_id}</p>
        <p><strong>Now ID:</strong> ${now.now_id}</p>
        <p><strong>Validation:</strong> ${validation.is_valid ? "<span class='status-true'>VALID</span>" : "<span class='warning'>ISSUES</span>"}</p>
        ${renderScene(now.observed_relations, "Current Now scene", false, now.entities)}
        ${state.world_changed_since_now ? `<p class="warning">The world has changed since this Now was built. Run the next cycle to rebuild the active Now from the new observation.</p>` : ""}
        ${state.stale_red_left_blue_present === false && state.demo_id === "fresh_now" ? `<p class="status-true">No stale red_cube LEFT_OF blue_cube relation in the active Now.</p>` : ""}
        ${validation.issues.length ? `<p class="warning">Current contradiction detected.</p>` : ""}
        ${relationGraph(relations, 6)}`;
    };
    const renderHistory = () => {
      const history = state.external_history || [];
      if (!history.length) return `<div class="empty">No previous cycles recorded externally yet.</div>`;
      return history.map((item, index) => `
        <div class="compare-card">
          <strong>Cycle ${item.cycle_id}</strong>
          <div class="small">Now ID: ${item.now_id}</div>
          <div class="small">${index === history.length - 1 ? "Latest archive" : "External history only"}</div>
          ${renderScene(item.now.observed_relations, "Archived cycle scene", false, item.now.entities)}
          <div class="small">Answer: ${item.answer}</div>
        </div>`).join("");
    };
    const compactRelationSummary = (relations) => {
      if (!relations || relations.length === 0) return "No observed relations";
      const visible = relations.slice(0, 2).map(humanRelation).join("; ");
      return relations.length > 2 ? `${visible}; +${relations.length - 2} more` : visible;
    };
    const renderPendingWorldChange = () => {
      if (!state.world_changed_since_now) return "";
      return `<div class="pending-change">World changed. The Current Now still shows the last cycle; click Run cycle to observe the new state.</div>`;
    };
    const renderSideWorld = () => {
      if (isFullG()) {
        const sections = state.full_g?.sections || [];
        return `
          <div class="cycle-summary">Full-G local reviewer package: ${sections.length} staged evidence sections.</div>
          <div class="cycle-answer">Model work: FROZEN</div>
          <div class="cycle-summary">Cloud calls: off. Paid APIs: off.</div>
          <div class="warning">qwen3:0.6b did not show a NowMind accuracy advantage over chronology.</div>`;
      }
      if (isG23()) {
        const comparison = state.g2_3_comparison || {};
        const selected = comparison.model_manifest?.selected || {};
        const prerequisite = comparison.model_manifest?.local_model_runtime_prerequisite;
        const rows = comparison.comparisons || [];
        return `
          <div class="cycle-summary">G2.3 compares representation format while holding task facts and backend configuration fixed.</div>
          <div class="cycle-answer">Backend: ${escapeHtml(selected.backend || "unknown")}</div>
          <div class="cycle-summary">Model: ${escapeHtml(selected.model || "unknown")}</div>
          ${prerequisite ? `<div class="warning">${escapeHtml(prerequisite)}</div>` : ""}
          <div class="cycle-summary">${rows.length} comparison rows: N and C across Regime A/B.</div>`;
      }
      if (isG22()) {
        return `
          <div class="cycle-summary">${escapeHtml(state.g2_2_note || "G2.2 Epistemic Geometry")}</div>
          ${renderEpistemicGrid(state.epistemic_now, true)}
          <div class="cycle-answer">Decision: ${state.plan ? String(state.plan.decision_type || "planned").toUpperCase() : "NOT RUN"}</div>`;
      }
      if (isG21()) {
        return `
          <div class="cycle-summary">${escapeHtml(state.g2_1_note || "G2.1 Possibility Geometry")}</div>
          ${renderSpatialGrid(state.spatial_now, true)}
          <div class="cycle-answer">Plan: ${state.plan ? (state.plan.valid ? "VALID" : "NO ROUTE") : "NOT RUN"}</div>`;
      }
      if (isG2()) {
        const now = state.temporal_now;
        const answer = state.temporal_answer;
        return `
          <div class="cycle-summary">${escapeHtml(state.g2_note || "G2 Temporal Geometry")}</div>
          ${now ? renderTemporalScene(now, true) : "<div class='empty'>Run cycle to build TemporalNow.</div>"}
          <div class="cycle-answer">Answer: ${answer ? answer.status.toUpperCase() : "NOT RUN"}</div>`;
      }
      const relations = state.world.relations || [];
      return `
        ${renderScene(relations, "World now scene", true, state.world.entities)}
        <div class="cycle-summary">${compactRelationSummary(relations)}</div>
        ${renderPendingWorldChange()}`;
    };
    const renderCycleRail = () => {
      if (isFullG()) {
        const sections = state.full_g?.sections || [];
        return `<div class="cycle-rail">${sections.map((section, index) => `
          <div class="cycle-card ${index === 0 ? "active" : ""}">
            <div class="cycle-head">
              <span class="cycle-number">${escapeHtml(section.title)}</span>
              <span class="badge ${index < 4 ? "pass" : "warn"}">${index < 4 ? "local" : "frozen"}</span>
            </div>
            <div class="cycle-summary">${escapeHtml(section.answer)}</div>
            <div class="cycle-answer">${escapeHtml(section.metric)}</div>
          </div>`).join("")}</div>`;
      }
      if (isG23()) {
        const rows = state.g2_3_comparison?.comparisons || [];
        return `<div class="cycle-rail">${rows.map((row) => `
          <div class="cycle-card ${row.condition === "N_NOWMIND_STRUCTURED" ? "active" : ""}">
            <div class="cycle-head">
              <span class="cycle-number">${escapeHtml(row.regime)}</span>
              <span class="badge ${row.validated_score?.correct ? "pass" : "warn"}">${escapeHtml(row.condition)}</span>
            </div>
            <div class="cycle-summary">Prompt tokens: ${row.input_tokens}</div>
            <div class="cycle-summary">Source: ${escapeHtml(row.parsed_output?.source_used || "none")}</div>
            <div class="cycle-answer">Validated: ${escapeHtml(row.validator?.final_status || "UNKNOWN")}</div>
          </div>`).join("")}</div>`;
      }
      if (isG22()) {
        const history = state.external_history || [];
        if (!history.length) {
          return `<div class="empty">No G2.2 cycles yet. Plan builds the first fresh epistemic Now.</div>`;
        }
        return `<div class="cycle-rail">${[...history].reverse().map((item, index) => `
          <div class="cycle-card ${index === 0 ? "active" : ""}">
            <div class="cycle-head">
              <span class="cycle-number">Cycle ${item.cycle_id}</span>
              <span class="badge ${item.decision_type === "verify_first" ? "warn" : "pass"}">${escapeHtml(item.decision_type)}</span>
            </div>
            <div class="cycle-summary">Now ID: ${item.now_id}</div>
            <div class="cycle-summary">Observation: ${escapeHtml(item.now_type || "local")}</div>
            <div class="cycle-answer">Plan: ${item.plan_valid ? `${item.plan_steps} step(s)` : "NO ROUTE"}</div>
          </div>`).join("")}</div>`;
      }
      if (isG21()) {
        const history = state.external_history || [];
        if (!history.length) {
          return `<div class="empty">No G2.1 cycles yet. Plan builds the first fresh TemporalNowState.</div>`;
        }
        return `<div class="cycle-rail">${[...history].reverse().map((item, index) => `
          <div class="cycle-card ${index === 0 ? "active" : ""}">
            <div class="cycle-head">
              <span class="cycle-number">Cycle ${item.cycle_id}</span>
              <span class="badge ${item.conditional ? "warn" : "pass"}">${item.conditional ? "Conditional" : "Observed route"}</span>
            </div>
            <div class="cycle-summary">Now ID: ${item.now_id}</div>
            <div class="cycle-summary">Agent (${item.agent_pose.x},${item.agent_pose.y}) -> Target (${item.target_pose.x},${item.target_pose.y})</div>
            <div class="cycle-answer">Plan: ${item.plan_valid ? `${item.plan_steps} steps` : "NO ROUTE"}</div>
          </div>`).join("")}</div>`;
      }
      if (isG2()) {
        const history = state.external_history || [];
        if (!history.length) {
          return `<div class="empty">No temporal cycles yet. Run cycle creates a fresh TemporalNowState.</div>`;
        }
        return `<div class="cycle-rail">${[...history].reverse().map((item) => `
          <div class="cycle-card active">
            <div class="cycle-head">
              <span class="cycle-number">Cycle ${item.cycle_id}</span>
              <span class="badge pass">TemporalNow</span>
            </div>
            <div class="cycle-summary">Now ID: ${item.now_id}</div>
            <div class="cycle-summary">${escapeHtml(item.query)}</div>
            <div class="cycle-answer">Answer: ${String(item.answer).toUpperCase()}</div>
          </div>`).join("")}</div>`;
      }
      const history = state.external_history || [];
      const activeNowId = state.current_now?.now_id;
      if (!history.length && !state.current_now) {
        return `<div class="empty">No cycles yet. Run cycle creates the first visible card here.</div>`;
      }
      const entries = history.length ? [...history].reverse() : [{
        cycle_id: state.current_now.cycle_id,
        now_id: state.current_now.now_id,
        now: state.current_now,
        query: state.active_query.display,
        answer: state.current_answer?.status || "not answered"
      }];
      return `<div class="cycle-rail">${entries.map((item) => {
        const observed = item.now?.observed_relations || [];
        const isActive = item.now_id === activeNowId;
        const validation = item.now?.validation?.is_valid ? "VALID" : "ISSUES";
        return `
          <div class="cycle-card ${isActive ? "active" : ""}">
            <div class="cycle-head">
              <span class="cycle-number">Cycle ${item.cycle_id}</span>
              <span class="badge ${isActive ? "pass" : ""}">${isActive ? "Active" : "Archived"}</span>
            </div>
            <div class="cycle-summary">Now ID: ${item.now_id}</div>
            ${renderScene(observed, `Cycle ${item.cycle_id} scene`, true, item.now?.entities || [])}
            <div class="cycle-summary">${compactRelationSummary(observed)}</div>
            <div class="cycle-answer">Answer: ${String(item.answer).toUpperCase()}</div>
            <div class="cycle-summary">Validation: ${validation}</div>
          </div>`;
      }).join("")}</div>`;
    };
    const renderBeforeAfter = () => {
      if (state.demo_id !== "fresh_now") {
        return `<div class="empty">The before / after comparison is specific to Demo A - Fresh Now.</div>`;
      }
      const history = state.external_history || [];
      if (history.length < 2 || !state.current_now) {
        return `<div class="empty">Run cycle 1, apply the move event, then run cycle 2 to see the visual before / after comparison.</div>`;
      }
      const previous = history[0];
      const current = state.current_now;
      return `
        <div class="compare">
          <div class="compare-card">
            <h3>Previous cycle</h3>
            <p><strong>Cycle ${previous.cycle_id}</strong></p>
            <p class="small">Now ID: ${previous.now_id}</p>
            <span class="badge block">External history only</span>
            ${renderScene(previous.now.observed_relations, "Previous cycle scene", false, previous.now.entities)}
          </div>
          <div class="compare-card current">
            <h3>Current active Now</h3>
            <p><strong>Cycle ${current.cycle_id}</strong></p>
            <p class="small">Now ID: ${current.now_id}</p>
            <span class="badge pass">Current active Now</span>
            ${renderScene(current.observed_relations, "Current active Now scene", false, current.entities)}
          </div>
        </div>
        <div class="conclusion">PASS: The current Now contains only the new relation. The previous Now still exists in external researcher history, but it is not available to the reasoner.</div>`;
    };
    const renderBoundary = () => {
      const now = state.current_now;
      const canSee = now ? `
        <p><strong>Current Now ID:</strong> ${now.now_id}</p>
        <p><strong>Current query:</strong> ${state.active_query.display}</p>
        ${relationGraph([...now.observed_relations, ...now.inferred_relations], 8)}
      ` : `<div class="empty">Run a cycle to create a current Now.</div>`;
      const cannotSee = `
        <p><strong>Previous Nows:</strong> ${state.external_history.length}</p>
        <p><strong>External experiment history:</strong> visible here for the researcher, blocked from the reasoner.</p>
        ${state.history_firewall_message ? `<p class="status-true">${state.history_firewall_message}</p>` : ""}
        <div class="badges"><span class="badge block">Blocked from reasoner</span></div>`;
      document.getElementById("canSeeBody").innerHTML = canSee;
      document.getElementById("cannotSeeBody").innerHTML = cannotSee;
    };
    const renderReasoning = () => {
      if (!state.current_answer) {
        return `<p><strong>Selected query:</strong> ${state.active_query.display}</p><div class="empty">Run a cycle to answer it.</div>`;
      }
      const answer = state.current_answer;
      const issueHtml = answer.issues.length ? `<div class="warning">Contradiction/validation issues are surfaced; no guessed TRUE/FALSE answer is rendered.</div><ul>${answer.issues.map((i) => `<li>${i.issue_type}: ${i.message}</li>`).join("")}</ul>` : "";
      const steps = answer.explanation.length ? `<table class="table"><thead><tr><th>Rule</th><th>Premises</th><th>Conclusion</th></tr></thead><tbody>${answer.explanation.map((s) => `<tr><td>${s.rule_id}</td><td>${s.premises.join(", ")}</td><td>${s.conclusion}</td></tr>`).join("")}</tbody></table>` : "<p>Observed directly or no supporting inference.</p>";
      return `
        <p><strong>Query:</strong> ${state.active_query.display}</p>
        <p><strong>Reasoner answer:</strong> <span class="status-${answer.status}">${answer.status.toUpperCase()}</span></p>
        <p><strong>Confidence:</strong> ${answer.confidence.toFixed(2)}</p>
        ${issueHtml}
        <details open><summary>Explanation chain</summary>${steps}</details>`;
    };
    const renderTechnical = () => {
      if (!state.current_now) return `<p>No technical details until a cycle is run.</p>`;
      const now = state.current_now;
      return `
        <h3>Observed now</h3>
        ${relationTable(now.observed_relations)}
        <h3>Inferred now</h3>
        ${relationTable(now.inferred_relations)}
        <h3>Validator output</h3>
        ${now.validation.issues.length ? `<ul class="warning">${now.validation.issues.map((i) => `<li>${i.issue_type}: ${i.message}</li>`).join("")}</ul>` : "<p class='status-true'>No validation issues.</p>"}
        <h3>Supporting relations</h3>
        ${state.current_answer ? relationTable(state.current_answer.supporting_relations) : "<p>No answer yet.</p>"}`;
    };
    const poseKey = (pose) => pose ? `${pose.x},${pose.y}` : "";
    const renderEpistemicGrid = (epistemic, compact = false) => {
      if (!epistemic) return `<div class="empty">Click Plan to build the partial epistemic Now.</div>`;
      const plan = state.plan;
      const selected = new Set((plan?.steps || []).filter((step) => step.action_type !== "scan").map((step) => poseKey(step.to_pose)));
      const scanCells = new Set((plan?.steps || []).filter((step) => step.action_type === "scan").map((step) => poseKey(step.to_pose)));
      const memory = new Set((state.memory_cells || []).map((cell) => poseKey(cell.pose)));
      const future = new Set((state.future_cells || []).map((cell) => poseKey(cell.pose)));
      const cellsByPose = new Map((epistemic.cells || []).map((cell) => [poseKey(cell.pose), cell]));
      const entitiesByPose = new Map();
      (state.world?.entities || []).forEach((entity) => {
        const key = poseKey(entity.pose);
        if (!entitiesByPose.has(key)) entitiesByPose.set(key, []);
        entitiesByPose.get(key).push(entity);
      });
      const cells = [];
      for (let y = 0; y < epistemic.height; y += 1) {
        for (let x = 0; x < epistemic.width; x += 1) {
          const key = `${x},${y}`;
          const cell = cellsByPose.get(key);
          const stateName = cell?.observed_occupancy || "unknown";
          const classes = [
            "spatial-cell",
            stateName === "occupied" ? "occupied" : "",
            stateName === "unknown" ? "unknown" : "",
            selected.has(key) ? "selected-path" : "",
            scanCells.has(key) ? "scan-cell" : "",
            memory.has(key) ? "memory-cell" : "",
            future.has(key) ? "future-cell" : ""
          ].filter(Boolean).join(" ");
          const tokens = (entitiesByPose.get(key) || [])
            .filter((entity) => stateName !== "unknown" || entity.kind === "agent")
            .map((entity) => {
              const tokenClass = entity.kind === "agent" ? "agent-token" : entity.kind === "target" ? "target-token" : "obstacle-token";
              const label = entity.kind === "agent" ? "A" : entity.kind === "target" ? "T" : "O";
              return `<span class="spatial-token ${tokenClass}" title="${escapeHtml(entity.entity_id)}">${label}</span>`;
            }).join("");
          const label = stateName === "unknown" ? "FOG" : "";
          cells.push(`<div class="${classes}" title="(${x},${y}) ${stateName} confidence=${cell?.observation_confidence ?? "none"}">${tokens}${!tokens ? label : ""}${selected.has(key) ? "<span class='path-dot'></span>" : ""}</div>`);
        }
      }
      return `<div class="spatial-board ${compact ? "mini-spatial" : ""}" style="grid-template-columns: repeat(${epistemic.width}, minmax(0, 1fr));">${cells.join("")}</div>`;
    };
    const renderG22Controls = () => `
      <div class="g21-controls">
        <button onclick="post('/api/run-cycle')">Plan</button>
        <button onclick="post('/api/g2-2-execute-step')">Execute next action</button>
        <button onclick="post('/api/g2-2-run-loop')">Run closed loop</button>
        <button onclick="post('/api/g2-2-reset')">Reset scenario</button>
        <button onclick="post('/api/apply-world-event')">Toggle memory truth</button>
      </div>`;
    const renderG22Legend = () => `
      <div class="spatial-legend">
        <div class="legend-item legend-solid">SOLID = observed now</div>
        <div class="legend-item legend-dashed">DASHED = MEMORY RECONSTRUCTION</div>
        <div class="legend-item legend-dotted">DOTTED = POSSIBLE FUTURE</div>
      </div>
      <p class="disclaimer">FOG = currently unknown. SCAN changes observation, not world truth. Selected plan is NOT reality.</p>`;
    const renderG22PlanPanel = () => {
      const plan = state.plan;
      if (!plan) return `<div class="plan-panel"><div class="empty">Click Plan to compare safe, shortcut, and verify-first options.</div></div>`;
      return `<div class="plan-panel">
        <h3>Epistemic decision</h3>
        <p><strong>Choice:</strong> ${escapeHtml(plan.decision_type || "none")} ${plan.verification_required ? "<span class='badge warn'>VERIFY FIRST</span>" : ""}</p>
        <p><strong>Status:</strong> ${plan.valid ? "VALID" : "NO ROUTE"} ${plan.conditional ? "<span class='badge warn'>CONDITIONAL</span>" : ""}</p>
        <p><strong>Cost:</strong> ${Number(plan.total_cost || 0).toFixed(1)} <strong>Evidence inspected:</strong> ${plan.evidence_items_inspected || 0}</p>
        ${plan.steps?.length ? `<ol>${plan.steps.slice(0, 8).map((step) => `<li>${escapeHtml(step.action_type)} -> (${step.to_pose.x},${step.to_pose.y}) ${escapeHtml(step.reason || "")}</li>`).join("")}</ol>` : "<p>No action steps.</p>"}
        ${plan.assumptions?.length ? `<details open><summary>Typed assumptions</summary><ul>${plan.assumptions.map((assumption) => `<li>${escapeHtml(assumption.source)}: ${escapeHtml(assumption.description)} confidence=${Number(assumption.confidence || 0).toFixed(2)}</li>`).join("")}</ul></details>` : "<p class='status-true'>No memory/future assumption promoted to observation.</p>"}
        <details open><summary>Policy explanation</summary><ul>${(plan.explanation || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul></details>
      </div>`;
    };
    const renderG22Sources = () => {
      const memories = state.temporal_now?.reconstructed_memories || [];
      const futures = state.temporal_now?.future_hypotheses || [];
      const observedCells = (state.epistemic_now?.cells || []).filter((cell) => cell.provenance === "observed_now").slice(0, 10);
      return `<div class="temporal-lanes">
        <div class="temporal-lane temporal-present"><div class="eyebrow">OBSERVED_NOW</div><h3>Visible cells</h3>${observedCells.length ? `<ul>${observedCells.map((cell) => `<li>(${cell.pose.x},${cell.pose.y}) ${cell.observed_occupancy} confidence=${Number(cell.observation_confidence || 0).toFixed(2)}</li>`).join("")}</ul>` : "<div class='empty'>No current cells yet.</div>"}</div>
        ${temporalLane("MEMORY GHOST", "RECONSTRUCTED_MEMORY", memories, "temporal-memory", "No memory reconstruction.")}
        ${temporalLane("FUTURE OVERLAY", "HYPOTHETICAL_FUTURE", futures, "temporal-future", "No future hypothesis.")}
      </div>`;
    };
    const renderG22BenchmarkDashboard = () => {
      const benchmark = state.benchmark;
      if (!benchmark) {
        return `<div class="empty">Run <strong>python -m nowmind.evaluation.run_g2_2_benchmark</strong> to populate local epistemic benchmark artifacts.</div>`;
      }
      const cards = Object.entries(benchmark.metrics || {}).map(([system, values]) => `
        <div class="metric-card">
          <h3>${escapeHtml(system)}</h3>
          <strong>${Number(values.goal_reached_rate || 0).toFixed(3)}</strong>
          <div class="small">goal reached</div>
          <div class="small">verify ${Number(values.verification_action_rate || 0).toFixed(3)}</div>
          <div class="small">memory ${Number(values.memory_use_rate || 0).toFixed(3)}</div>
          <div class="small">evidence ${Number(values.mean_evidence_items_inspected || 0).toFixed(1)}</div>
        </div>`).join("");
      return `<div>
        <p><strong>Seed:</strong> ${benchmark.config.seed} <strong>Trials:</strong> ${benchmark.config.trial_count}</p>
        <div class="metric-strip">${cards}</div>
      </div>`;
    };
    const renderG22Body = () => `
      <p class="section-copy">${escapeHtml(state.g2_2_note || "")}</p>
      ${state.g2_2_event_note ? `<div class="pending-change">${escapeHtml(state.g2_2_event_note)}</div>` : ""}
      ${renderG22Controls()}
      ${renderG22Legend()}
      <div class="spatial-layout">
        <div>
          ${renderEpistemicGrid(state.epistemic_now)}
          ${state.action_result ? `<p class="${state.action_result.success ? "status-true" : "warning"}">Last action: ${escapeHtml(state.action_result.action_type)} ${state.action_result.information_action ? "(information only)" : ""}</p>` : ""}
        </div>
        ${renderG22PlanPanel()}
      </div>
      ${renderG22Sources()}
      <details class="plain-details" open style="margin-top:12px;"><summary>Research inspector</summary>
        <div class="inspector-grid">
          <div>
            <h3>Epistemic state</h3>
            <p>Known free: ${state.epistemic_now?.known_free_count || 0}</p>
            <p>Known blocked: ${state.epistemic_now?.known_blocked_count || 0}</p>
            <p>Unknown: ${state.epistemic_now?.unknown_cell_count || 0}</p>
            <p>Disconfirmed targets: ${(state.recovery?.disconfirmed_target_poses || []).length}</p>
            <p>Invalidated assumptions: ${(state.recovery?.invalidated_poses || []).length}</p>
            <p>Reacquisition attempts: ${state.recovery?.reacquisition_attempts || 0}</p>
          </div>
          <div>
            <h3>External history</h3>
            ${(state.external_history || []).length ? `<ul>${state.external_history.slice(-6).map((item) => `<li>Cycle ${item.cycle_id}: now ${escapeHtml(item.now_id)} decision=${escapeHtml(item.decision_type)}</li>`).join("")}</ul>` : "<p>No cycles yet.</p>"}
          </div>
        </div>
      </details>`;
    const renderSpatialGrid = (spatial, compact = false) => {
      if (!spatial) return `<div class="empty">Click Plan to observe the 2D world.</div>`;
      const plan = state.plan;
      const selected = new Set((plan?.steps || []).map((step) => poseKey(step.to_pose)));
      const rejected = new Set((plan?.rejected_alternatives || []).filter((item) => item.violations?.length).map((item) => poseKey(item.to_pose)));
      const memory = new Set((state.memory_cells || []).map((cell) => poseKey(cell.pose)));
      const future = new Set((state.future_cells || []).map((cell) => poseKey(cell.pose)));
      const occupancy = new Map((spatial.occupancy || []).map((cell) => [poseKey(cell.pose), cell.state]));
      const entitiesByPose = new Map();
      (spatial.entities || []).forEach((entity) => {
        const key = poseKey(entity.pose);
        if (!entitiesByPose.has(key)) entitiesByPose.set(key, []);
        entitiesByPose.get(key).push(entity);
      });
      const cells = [];
      for (let y = 0; y < spatial.height; y += 1) {
        for (let x = 0; x < spatial.width; x += 1) {
          const key = `${x},${y}`;
          const stateName = occupancy.get(key) || "free";
          const classes = [
            "spatial-cell",
            stateName === "occupied" ? "occupied" : "",
            stateName === "unknown" ? "unknown" : "",
            selected.has(key) ? "selected-path" : "",
            rejected.has(key) ? "rejected-cell" : "",
            memory.has(key) ? "memory-cell" : "",
            future.has(key) ? "future-cell" : ""
          ].filter(Boolean).join(" ");
          const tokens = (entitiesByPose.get(key) || []).map((entity) => {
            const tokenClass = entity.kind === "agent" ? "agent-token" : entity.kind === "target" ? "target-token" : "obstacle-token";
            const label = entity.kind === "agent" ? "A" : entity.kind === "target" ? "T" : "O";
            return `<span class="spatial-token ${tokenClass}" title="${escapeHtml(entity.entity_id)}">${label}</span>`;
          }).join("");
          cells.push(`<div class="${classes}" title="(${x},${y}) ${stateName}">${tokens}${selected.has(key) ? "<span class='path-dot'></span>" : ""}</div>`);
        }
      }
      return `<div class="spatial-board ${compact ? "mini-spatial" : ""}" style="grid-template-columns: repeat(${spatial.width}, minmax(0, 1fr));">${cells.join("")}</div>`;
    };
    const renderG21Controls = () => `
      <div class="g21-controls">
        <button onclick="post('/api/run-cycle')">Plan</button>
        <button onclick="post('/api/g2-1-execute-step')">Execute one step</button>
        <button onclick="post('/api/g2-1-run-loop')">Run closed loop</button>
        <button onclick="post('/api/g2-1-reset')">Reset scenario</button>
        <button onclick="post('/api/apply-world-event')">Move obstacle</button>
        <button onclick="post('/api/g2-1-move-target')">Move target</button>
        <button onclick="post('/api/g2-1-inject-stale-memory')">Inject stale memory</button>
        <button onclick="post('/api/g2-1-inject-false-memory')">Inject false memory</button>
        <button onclick="post('/api/g2-1-add-future')">Add future hypothesis</button>
        <button onclick="post('/api/g2-1-hide-region')">Hide/reveal region</button>
      </div>`;
    const renderG21Legend = () => `
      <div class="spatial-legend">
        <div class="legend-item legend-solid">SOLID = observed now</div>
        <div class="legend-item legend-dashed">DASHED = MEMORY RECONSTRUCTION</div>
        <div class="legend-item legend-dotted">DOTTED = POSSIBLE FUTURE</div>
      </div>
      <p class="disclaimer">Selected plan is NOT reality. Only executed + observed states become current facts.</p>`;
    const renderG21PlanPanel = () => {
      const plan = state.plan;
      if (!plan) return `<div class="plan-panel"><div class="empty">Click Plan to generate candidate hypothetical geometries.</div></div>`;
      const rejected = (plan.rejected_alternatives || []).filter((item) => item.violations?.length).slice(0, 4);
      return `<div class="plan-panel">
        <h3>Selected Plan</h3>
        <p><strong>Status:</strong> ${plan.valid ? "VALID" : "NO ROUTE"} ${plan.conditional ? "<span class='badge warn'>CONDITIONAL</span>" : ""}</p>
        <p><strong>Start:</strong> (${plan.start.x},${plan.start.y}) <strong>Goal:</strong> (${plan.goal.x},${plan.goal.y})</p>
        <p><strong>Steps:</strong> ${plan.steps.length} <strong>Cost:</strong> ${Number(plan.total_cost || 0).toFixed(1)}</p>
        ${plan.assumptions?.length ? `<details open><summary>Planning assumptions</summary><ul>${plan.assumptions.map((assumption) => `<li>${escapeHtml(assumption.source)}: ${escapeHtml(assumption.description)} confidence=${Number(assumption.confidence || 0).toFixed(2)}</li>`).join("")}</ul></details>` : "<p class='status-true'>No memory-supported assumptions needed.</p>"}
        <details open><summary>Rejected candidate moves</summary>
          ${rejected.length ? `<ul>${rejected.map((item) => `<li>${escapeHtml(item.transformation.transformation_type)} to (${item.to_pose.x},${item.to_pose.y}): ${escapeHtml(item.reason)}</li>`).join("")}</ul>` : "<p>No invalid first-step candidates.</p>"}
        </details>
        <details><summary>Explanation</summary><ul>${(plan.explanation || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul></details>
      </div>`;
    };
    const renderG21Sources = () => {
      const memories = state.temporal_now?.reconstructed_memories || [];
      const futures = state.temporal_now?.future_hypotheses || [];
      return `<div class="temporal-lanes">
        ${temporalLane("CURRENT SPATIAL NOW", "OBSERVED_NOW / INFERRED_NOW", state.spatial_now?.derived_relations || [], "temporal-present", "Plan to build current spatial geometry.")}
        ${temporalLane("MEMORY OVERLAY", "RECONSTRUCTED_MEMORY", memories, "temporal-memory", "No memory reconstruction.")}
        ${temporalLane("FUTURE OVERLAY", "HYPOTHETICAL_FUTURE", futures, "temporal-future", "No future hypothesis.")}
      </div>`;
    };
    const renderG21BenchmarkDashboard = () => {
      const benchmark = state.benchmark;
      if (!benchmark) {
        return `<div class="empty">Run <strong>python -m nowmind.evaluation.run_g2_1_benchmark</strong> to populate local planning benchmark artifacts.</div>`;
      }
      const cards = Object.entries(benchmark.metrics || {}).map(([system, values]) => `
        <div class="metric-card">
          <h3>${escapeHtml(system)}</h3>
          <strong>${Number(values.goal_reached_rate || 0).toFixed(3)}</strong>
          <div class="small">goal reached</div>
          <div class="small">collisions ${Number(values.collision_rate || 0).toFixed(3)}</div>
          <div class="small">replans ${Number(values.mean_replans || 0).toFixed(2)}</div>
          <div class="small">oracle gap ${Number(values.optimality_gap_vs_oracle || 0).toFixed(2)}</div>
        </div>`).join("");
      return `<div>
        <p><strong>Seed:</strong> ${benchmark.config.seed} <strong>Trials:</strong> ${benchmark.config.trial_count}</p>
        <div class="metric-strip">${cards}</div>
      </div>`;
    };
    const renderG21Body = () => `
      <p class="section-copy">${escapeHtml(state.g2_1_note || "")}</p>
      ${state.g2_1_event_note ? `<div class="pending-change">${escapeHtml(state.g2_1_event_note)}</div>` : ""}
      ${renderG21Controls()}
      ${renderG21Legend()}
      <div class="spatial-layout">
        <div>
          ${renderSpatialGrid(state.spatial_now)}
          ${state.action_result ? `<p class="${state.action_result.success ? "status-true" : "warning"}">Last action: ${state.action_result.success ? "executed" : "rejected"} from (${state.action_result.before_pose.x},${state.action_result.before_pose.y}) to (${state.action_result.attempted_pose.x},${state.action_result.attempted_pose.y})</p>` : ""}
        </div>
        ${renderG21PlanPanel()}
      </div>
      ${renderG21Sources()}
      <details class="plain-details" open style="margin-top:12px;"><summary>Research inspector</summary>
        <div class="inspector-grid">
          <div>
            <h3>Candidate hypothetical geometries</h3>
            ${state.plan?.steps?.length ? `<ul>${state.plan.steps.slice(0, 8).map((step) => `<li>${escapeHtml(step.transformation.transformation_type)} -> (${step.to_pose.x},${step.to_pose.y}) provenance=hypothetical_future</li>`).join("")}</ul>` : "<p>No candidate path yet.</p>"}
          </div>
          <div>
            <h3>External history</h3>
            ${(state.external_history || []).length ? `<ul>${state.external_history.slice(-6).map((item) => `<li>Cycle ${item.cycle_id}: now ${escapeHtml(item.now_id)} plan=${item.plan_valid ? "valid" : "no route"}</li>`).join("")}</ul>` : "<p>No cycles yet.</p>"}
          </div>
        </div>
      </details>`;
    const temporalPropositionText = (item) => {
      const prop = item.proposition || item;
      if (!prop) return "None";
      return `${prop.source_id} ${String(prop.relation_type).toUpperCase()} ${prop.target_id}`;
    };
    const temporalTargetFor = (items) => {
      const first = (items || [])[0];
      return first?.proposition?.target_id || first?.target_id || null;
    };
    const renderTemporalScene = (now, compact = false) => {
      const presentTarget = temporalTargetFor(now?.observed_relations || []);
      const memoryTarget = temporalTargetFor(now?.reconstructed_memories || []);
      const futureTarget = temporalTargetFor(now?.future_hypotheses || []);
      const slots = [
        ["box_a", "Box A"],
        ["box_b", "Box B"],
        ["box_c", "Box C"],
        ["box_d", "Box D"]
      ];
      return `<div class="temporal-scene ${compact ? "mini-scene" : ""}">
        ${slots.map(([id, label]) => {
          const classes = [
            presentTarget === id ? "active-present" : "",
            memoryTarget === id ? "active-memory" : "",
            futureTarget === id ? "active-future" : ""
          ].filter(Boolean).join(" ");
          const markers = [
            presentTarget === id ? "<div class='ball-token'>NOW</div>" : "",
            memoryTarget === id ? "<div class='ball-token'>MEM</div>" : "",
            futureTarget === id ? "<div class='ball-token'>FUT</div>" : ""
          ].join("");
          return `<div class="box-slot ${classes}">${label}${markers}</div>`;
        }).join("")}
      </div>`;
    };
    const temporalLane = (title, source, items, className, emptyText) => `
      <div class="temporal-lane ${className}">
        <div class="eyebrow">${source}</div>
        <h3>${title}</h3>
        ${(items || []).length ? `<ul>${items.map((item) => `
          <li>
            <strong>${temporalPropositionText(item)}</strong>
            <div class="small">confidence=${Number(item.confidence || 0).toFixed(2)}</div>
          </li>`).join("")}</ul>` : `<div class="empty">${emptyText}</div>`}
      </div>`;
    const renderTemporalAnswer = () => {
      const answer = state.temporal_answer;
      if (!answer) {
        return `<div class="empty">Run cycle to answer the selected temporal query.</div>`;
      }
      const source = answer.source || "none";
      const propositions = answer.propositions || [];
      const context = answer.context || [];
      const contradiction = (answer.contradictions || []).length
        ? `<div class="warning">${answer.contradictions.map(escapeHtml).join("<br>")}</div>`
        : "";
      const notes = (answer.uncertainty_notes || []).length
        ? `<ul>${answer.uncertainty_notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>`
        : "";
      return `<div class="temporal-answer">
        <p><strong>Query:</strong> ${escapeHtml(answer.query.display)}</p>
        <p><strong>Temporal answer:</strong> <span class="status-${answer.status}">${String(answer.status).toUpperCase()}</span></p>
        <p><strong>Source used:</strong> <span class="pill">${source}</span></p>
        <p><strong>Confidence:</strong> ${Number(answer.confidence || 0).toFixed(2)}</p>
        ${propositions.length ? `<p><strong>Answer content:</strong> ${propositions.map(temporalPropositionText).join("; ")}</p>` : ""}
        ${contradiction}
        ${notes}
        ${context.length ? `<details open><summary>Visible temporal context, not automatically promoted</summary><ul>${context.map((item) => `<li>${item.source}: ${temporalPropositionText(item)} confidence=${Number(item.confidence || 0).toFixed(2)}</li>`).join("")}</ul></details>` : ""}
      </div>`;
    };
    const renderJsonBlock = (value) => `<pre class="json-block">${escapeHtml(JSON.stringify(value || {}, null, 2))}</pre>`;
    const g23ConditionTitle = (condition) => condition === "N_NOWMIND_STRUCTURED"
      ? "NOWMIND REPRESENTATION"
      : condition === "C_CHRONOLOGICAL"
        ? "CHRONOLOGICAL REPRESENTATION"
        : escapeHtml(condition || "REPRESENTATION");
    const renderG23ComparisonCard = (row) => {
      const proposal = row.parsed_output || {};
      const validator = row.validator || {};
      const conditionClass = row.condition === "N_NOWMIND_STRUCTURED" ? "nowmind" : "chronological";
      const staleBadge = proposal.source_used === "reconstructed_memory"
        ? `<span class="badge warn">stale memory used as current</span>`
        : `<span class="badge pass">no stale-memory contamination</span>`;
      return `
        <div class="g23-card ${conditionClass}">
          <div class="section-head">
            <div>
              <div class="eyebrow">${escapeHtml(row.regime)}</div>
              <h3>${g23ConditionTitle(row.condition)}</h3>
            </div>
            <span class="badge ${row.validated_score?.correct ? "pass" : "warn"}">${row.validated_score?.correct ? "validated correct" : "validated miss"}</span>
          </div>
          <p><strong>Same model identity:</strong> ${escapeHtml(row.backend)} / ${escapeHtml(row.model)}</p>
          <div class="g23-metrics">
            <div class="g23-metric"><strong>Source used</strong><br>${escapeHtml(proposal.source_used || "none")}</div>
            <div class="g23-metric"><strong>Raw correctness</strong><br>${row.proposal_score?.correct ? "correct" : "incorrect"}</div>
            <div class="g23-metric"><strong>Token count</strong><br>${row.input_tokens} in / ${row.output_tokens} out</div>
            <div class="g23-metric"><strong>Latency</strong><br>${Number(row.latency_ms || 0).toFixed(2)} ms</div>
          </div>
          ${staleBadge}
          <h3>Exact input representation</h3>
          ${renderJsonBlock(row.representation?.representation)}
          <h3>Model proposal</h3>
          ${renderJsonBlock(proposal)}
          <h3>Symbolic validator result</h3>
          ${renderJsonBlock(validator)}
          <p><strong>Final outcome:</strong> ${escapeHtml(validator.final_status || "UNKNOWN")} ${validator.final_answer ? `- ${escapeHtml(validator.final_answer)}` : ""}</p>
        </div>`;
    };
    const renderG23Body = () => {
      const comparison = state.g2_3_comparison || {};
      const rows = comparison.comparisons || [];
      const expected = comparison.expected_hidden_by_default || {};
      const manifest = comparison.model_manifest || {};
      const selected = manifest.selected || {};
      const rowsFor = (regime) => rows.filter((row) => row.regime === regime);
      return `
        <p class="section-copy">One long-history source-confusion scenario is rendered two ways, then sent to the same replaceable local reasoning faculty. The raw proposal and validated result are scored separately.</p>
        <div class="inspector-grid">
          <div class="can-card can-see">
            <h3>MODEL FACULTY</h3>
            <p><strong>Backend:</strong> ${escapeHtml(selected.backend || "unknown")}</p>
            <p><strong>Model:</strong> ${escapeHtml(selected.model || "unknown")}</p>
            <p><strong>Temperature:</strong> ${Number(selected.temperature || 0).toFixed(2)}</p>
            <p><strong>Seed:</strong> ${escapeHtml(selected.seed ?? "none")}</p>
          </div>
          <div class="can-card cannot-see">
            <h3>BOUNDARIES</h3>
            <ul>
              <li>Model output is proposal-only.</li>
              <li>No output becomes OBSERVED_NOW or MemoryTrace.</li>
              <li>Evaluator answer is hidden by default.</li>
            </ul>
            ${manifest.local_model_runtime_prerequisite ? `<p class="warning">${escapeHtml(manifest.local_model_runtime_prerequisite)}</p>` : ""}
          </div>
        </div>
        <details>
          <summary>Reveal evaluator answer</summary>
          ${renderJsonBlock(expected)}
        </details>
        <h3>Regime A - equal information, no truncation</h3>
        <div class="g23-compare-grid">${rowsFor("A_EQUAL_INFORMATION").map(renderG23ComparisonCard).join("")}</div>
        <h3>Regime B - fixed representation budget</h3>
        <div class="g23-compare-grid">${rowsFor("B_FIXED_BUDGET").map(renderG23ComparisonCard).join("")}</div>`;
    };
    const renderTemporalBody = () => {
      const now = state.temporal_now;
      if (!now) {
        return `<div class="empty">Run cycle to build the current TemporalNowState.</div>`;
      }
      const observed = now.observed_relations || [];
      const inferred = now.inferred_relations || [];
      const present = [...observed, ...inferred];
      const memories = now.reconstructed_memories || [];
      const futures = now.future_hypotheses || [];
      const falseMemoryBanner = state.demo_id === "g2_false_memory" && state.temporal_answer?.source === "observed_now"
        ? `<div class="conclusion">CONFLICTING MEMORY DID NOT REPLACE PRESENT</div>`
        : "";
      return `
        <p class="section-copy">${escapeHtml(state.g2_note || "")}</p>
        ${renderTemporalScene(now)}
        <div class="temporal-lanes">
          ${temporalLane("PRESENT", "OBSERVED_NOW / INFERRED_NOW", present, "temporal-present", "No current present evidence.")}
          ${temporalLane("RECONSTRUCTED PAST", "RECONSTRUCTED_MEMORY", memories, "temporal-memory", "No memory reconstruction.")}
          ${temporalLane("POSSIBLE FUTURE", "HYPOTHETICAL_FUTURE", futures, "temporal-future", "No future hypothesis.")}
        </div>
        ${falseMemoryBanner}
        ${renderTemporalAnswer()}
        <div class="inspector-grid" style="margin-top:12px;">
          <div class="can-card can-see">
            <h3>CURRENT TEMPORAL NOW</h3>
            <p><strong>Temporal now_id:</strong> ${now.now_id}</p>
            <p><strong>Current query:</strong> ${state.active_query.display}</p>
            <p class="small">The reasoner receives present evidence, reconstructed memories, and future hypotheses as labeled current channels.</p>
          </div>
          <div class="can-card cannot-see">
            <h3>NOT DIRECTLY AVAILABLE</h3>
            <ul>
              <li>Raw previous NowStates</li>
              <li>Researcher event log</li>
              <li>ExperimentRecorder history</li>
            </ul>
            ${state.history_firewall_message ? `<p class="status-true">${escapeHtml(state.history_firewall_message)}</p>` : ""}
          </div>
        </div>`;
    };
    const renderBenchmarkDashboard = () => {
      if (isG23()) {
        const manifest = state.g2_3_comparison?.model_manifest || {};
        const selected = manifest.selected || {};
        return `<div class="benchmark-grid">
          <div>
            <p><strong>G2.3 artifact directory:</strong> artifacts/g2_3</p>
            <p><strong>Active browser scenario:</strong> long-history source confusion</p>
            <p><strong>Backend:</strong> ${escapeHtml(selected.backend || "unknown")}</p>
            <p><strong>Model:</strong> ${escapeHtml(selected.model || "unknown")}</p>
            <p class="disclaimer">The browser tab is an inspection demo. Run <strong>python -m nowmind.evaluation.run_g2_3_benchmark</strong> for the full calibration/evaluation artifacts.</p>
          </div>
          <div>
            <h3>Locality status</h3>
            ${manifest.local_model_runtime_prerequisite ? `<div class="warning">${escapeHtml(manifest.local_model_runtime_prerequisite)}</div>` : "<p class='status-true'>Local model runtime available.</p>"}
            <p class="small">G2.3 has no cloud model backend and performs no automatic model download.</p>
          </div>
        </div>`;
      }
      if (isG22()) return renderG22BenchmarkDashboard();
      if (isG21()) return renderG21BenchmarkDashboard();
      const benchmark = state.benchmark;
      if (!benchmark) {
        return `<div class="empty">Run <strong>python -m nowmind.evaluation.run_g2_benchmark</strong> to populate local benchmark artifacts.</div>`;
      }
      const metrics = benchmark.metrics || {};
      const rows = Object.entries(metrics).map(([system, values]) => `
        <tr>
          <td>${escapeHtml(system)}</td>
          <td>${Number(values.overall_query_accuracy || 0).toFixed(3)}</td>
          <td>${Number(values.current_state_accuracy || 0).toFixed(3)}</td>
          <td>${values.stale_memory_as_current_count}</td>
          <td>${values.false_memory_contamination_count}</td>
          <td>${values.prediction_as_fact_count}</td>
        </tr>`).join("");
      const matrix = benchmark.confusion_matrix?.NowMindTemporalGeometry || {};
      const matrixRows = Object.entries(matrix).map(([expected, actuals]) => `
        <tr><td>${escapeHtml(expected)}</td><td>${Object.entries(actuals).map(([actual, count]) => `${escapeHtml(actual)}: ${count}`).join("; ")}</td></tr>`).join("");
      return `<div class="benchmark-grid">
        <div>
          <p><strong>Seed:</strong> ${benchmark.config.seed}</p>
          <p><strong>Trial count:</strong> ${benchmark.config.trial_count}</p>
          <p class="disclaimer">These synthetic symbolic benchmarks evaluate architecture and temporal-source handling. They are not evidence of consciousness and are not yet a comparison against state-of-the-art LLM agents.</p>
          <table class="table"><thead><tr><th>System</th><th>Overall</th><th>Current</th><th>Stale</th><th>False memory</th><th>Prediction fact</th></tr></thead><tbody>${rows}</tbody></table>
        </div>
        <div>
          <h3>NowMind source confusion matrix</h3>
          <table class="table"><thead><tr><th>Expected</th><th>Actual counts</th></tr></thead><tbody>${matrixRows}</tbody></table>
        </div>
      </div>`;
    };
    const renderFullGReviewer = () => {
      const full = state.full_g || {};
      const sections = full.sections || [];
      const nonclaims = full.nonclaims || [];
      const docs = full.documents || [];
      return `
        <div class="disclaimer"><strong>Local-only review:</strong> this page reads packaged milestone facts from the local controller. It does not call OpenRouter, Ollama, or any paid API.</div>
        <div class="conclusion" style="margin-top:12px;">Real-model result to date: ${escapeHtml(full.real_model_result || "No real-model advantage claim.")}</div>
        <div class="inspector-grid" style="margin-top:12px;">
          <div class="can-card cannot-see">
            <h3>What the demo does NOT prove</h3>
            <ul>${nonclaims.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
          </div>
          <div class="can-card can-see">
            <h3>Reviewer map</h3>
            <ul>
              <li>G1: Present Geometry</li>
              <li>G2: Temporal Source Separation</li>
              <li>G2.1: Possibility Geometry</li>
              <li>G2.2/G2.2.1: Epistemic Recovery</li>
              <li>G2.3: Real-model comparison infrastructure</li>
              <li>G2.3.4: frozen free-provider replication status</li>
            </ul>
          </div>
        </div>
        <div class="metric-strip" style="margin-top:12px;">
          ${sections.map((section) => `
            <div class="metric-card">
              <h3>${escapeHtml(section.title)}</h3>
              <p><strong>Scenario:</strong> ${escapeHtml(section.scenario)}</p>
              <p><strong>Current geometry/state:</strong> ${escapeHtml(section.state)}</p>
              <p><strong>Source labels:</strong> ${escapeHtml(section.source_labels)}</p>
              <p><strong>What changed:</strong> ${escapeHtml(section.changed)}</p>
              <p><strong>Answer/action:</strong> ${escapeHtml(section.answer)}</p>
              <p><strong>Why it matters:</strong> ${escapeHtml(section.why)}</p>
              <p><strong>Metric:</strong> ${escapeHtml(section.metric)}</p>
            </div>`).join("")}
        </div>
        <details class="plain-details" open style="margin-top:12px;">
          <summary>Core reviewer documents</summary>
          <ul>${docs.map((path) => `<li><code>${escapeHtml(path)}</code></li>`).join("")}</ul>
        </details>`;
    };
    const renderDemoBrief = () => {
      const briefs = {
        full_g_reviewer: {
          title: "Full-G reviewer: frozen local package",
          point: "This is the first-pass technical review path across G1 through G2.3.4. It highlights positive architecture evidence, negative model results, and the claims boundary.",
          steps: [
            "Read the six Full-G sections in order.",
            "Use the selector to open any underlying live demo for detail.",
            "Use REPRODUCE_FULL_G.md for local-only verification."
          ]
        },
        fresh_now: {
          title: "Demo A: fresh Now after a world change",
          point: "This shows the core G1 idea: the world can change immediately, but the Current Now changes only when a new cycle observes the world.",
          steps: [
            "Run cycle 1: red is left of blue.",
            "Move red_cube, then notice World now changes first.",
            "Run cycle 2: Current Now rebuilds and the stale relation is gone."
          ]
        },
        inference: {
          title: "Demo B: inference appears only while the chain exists",
          point: "The reasoner does not just repeat observed facts. It infers A LEFT_OF C from the current A -> B -> C chain.",
          steps: [
            "Run a cycle: A LEFT_OF C is TRUE by LEFT_TRANSITIVE.",
            "Break the b -> c link, then run the next cycle.",
            "The answer becomes UNKNOWN; restore the chain to make it TRUE again."
          ]
        },
        containment: {
          title: "Demo C: nested containment inference",
          point: "The reasoner infers key INSIDE cabinet only while the current Now contains key -> box -> cabinet.",
          steps: [
            "Run a cycle: key INSIDE cabinet is TRUE.",
            "Break the box -> cabinet bridge, then run the next cycle.",
            "The cabinet disconnects and the answer becomes UNKNOWN."
          ]
        },
        contradiction: {
          title: "Demo D: contradiction blocks guessing",
          point: "When the current Now contains incompatible facts, the reasoner surfaces CONTRADICTORY instead of guessing true or false.",
          steps: [
            "Run a cycle: LEFT_OF and RIGHT_OF conflict.",
            "Resolve the contradiction, then run the next cycle.",
            "The answer becomes TRUE; restore the contradiction to see it blocked again."
          ]
        },
        g2_memory_present: {
          title: "G2-A: memory vs present",
          point: "The current Now can contain present B, reconstructed past A, and possible future C without treating them as the same kind of fact.",
          steps: [
            "Run cycle: present lane shows Box B.",
            "Past query returns Box A as reconstructed memory.",
            "Future query returns Box C as a hypothesis only."
          ]
        },
        g2_false_memory: {
          title: "G2-B: false memory stays separate",
          point: "An injected memory says Box D, but the current answer remains Box B because memory cannot replace present evidence.",
          steps: [
            "Run cycle: present lane shows Box B.",
            "Memory lane shows the conflicting Box D reconstruction.",
            "The banner confirms the memory did not replace present."
          ]
        },
        g2_future: {
          title: "G2-C: future hypothesis is not fact",
          point: "The possible future lane can show Box C while the current answer still comes from present Box B.",
          steps: [
            "Run cycle: present is Box B.",
            "Future lane shows Box C.",
            "Future query answers from HYPOTHETICAL_FUTURE only."
          ]
        },
        g2_confidence: {
          title: "G2-D: confidence does not erase source type",
          point: "A high-confidence memory A does not override a lower-confidence current observation B.",
          steps: [
            "Run cycle: current observation is moderate confidence.",
            "Memory reconstruction is higher confidence.",
            "Current answer still uses OBSERVED_NOW."
          ]
        },
        g2_hidden: {
          title: "G2-E: no current visibility",
          point: "When no current observation exists, memory can be shown as context but the current answer is UNKNOWN.",
          steps: [
            "Run cycle: present lane has no ball location.",
            "Memory lane reconstructs Box A.",
            "Current query returns UNKNOWN, not memory-as-current."
          ]
        },
        g2_contradiction: {
          title: "G2-F: contradictory current perception",
          point: "Conflicting present observations produce a structured contradiction instead of choosing a memory or guessing.",
          steps: [
            "Run cycle: present lane contains incompatible current locations.",
            "Reasoner answer is CONTRADICTORY.",
            "Past and future channels remain separate context."
          ]
        },
        g2_1_replanning: {
          title: "G2.1-A: possibility planning and replanning",
          point: "The planner draws candidate future geometry, executes one real action, then observes again before continuing.",
          steps: [
            "Click Plan to draw the selected candidate path.",
            "Execute one step or move an obstacle onto the old path.",
            "Run closed loop to see the fresh Now and replanned path."
          ]
        },
        g2_1_stale_memory: {
          title: "G2.1-B: stale memory rejected by observation",
          point: "A remembered shortcut is shown as memory, while the solid observed obstacle controls current planning.",
          steps: [
            "Click Plan and inspect the dashed memory overlay.",
            "Notice the solid obstacle is still blocked.",
            "The selected route goes around observed reality."
          ]
        },
        g2_1_unknown_memory: {
          title: "G2.1-C: conditional route through unknown space",
          point: "Memory can support an unknown corridor, but the selected plan is marked conditional.",
          steps: [
            "Click Plan to show the hidden corridor.",
            "Inspect the memory assumption in the plan panel.",
            "Execute one step at a time; each action still requires observation."
          ]
        },
        g2_1_future_target: {
          title: "G2.1-D: future target hypothesis",
          point: "The dotted future target is a possible future, not the current goal.",
          steps: [
            "Click Plan and compare solid target with dotted future overlay.",
            "Move target to change the external world.",
            "Plan again: only the new observation updates the current goal."
          ]
        },
        g2_2_verify_false: {
          title: "G2.2-A: verify before trusting stale memory",
          point: "The shortcut is hidden by fog. Memory says it was clear, but SCAN reveals it is blocked before the agent commits.",
          steps: [
            "Click Plan: the selected decision is verify-first.",
            "Execute next action: SCAN creates a fresh Now ID and reveals the shortcut.",
            "Run closed loop: the agent replans around the blocked shortcut."
          ]
        },
        g2_2_verify_correct: {
          title: "G2.2-B: verification can make memory useful",
          point: "The same foggy shortcut is remembered as clear, and this time SCAN confirms the current shortcut is open.",
          steps: [
            "Click Plan: memory is a typed assumption, not observation.",
            "Execute next action: SCAN reveals current free cells.",
            "Run closed loop: the confirmed shortcut can be used safely."
          ]
        },
        g2_2_1_stale_target_recovery: {
          title: "G2.2.1-R1: stale target recovery",
          point: "Memory points to target location A, but A is visible and empty in the current Now. The assumption is disconfirmed without deleting the old trace.",
          steps: [
            "Click Plan: the stale target location is marked disconfirmed.",
            "Execute next action: SCAN creates a fresh Now and searches beyond A.",
            "Run closed loop: the newly observed target location becomes OBSERVED_NOW."
          ]
        },
        g2_2_1_hidden_obstacle_recovery: {
          title: "G2.2.1-R2: hidden obstacle recovery",
          point: "A remembered shortcut is hidden by fog after an obstacle moved there. The system does not know until SCAN reveals the conflict.",
          steps: [
            "Click Plan: the hidden shortcut remains an assumption, not fact.",
            "Execute next action: SCAN reveals the moved obstacle.",
            "Run closed loop: the old path is invalidated and the next plan avoids it."
          ]
        },
        g2_3_model_comparison: {
          title: "G2.3: model comparison",
          point: "The same long-history task is represented as NowMind structured input and as a clean chronological input, then sent to the same replaceable backend.",
          steps: [
            "Inspect Regime A for equal information with no truncation.",
            "Inspect Regime B for the same fixed representation budget.",
            "Open the reveal control only when you want to see evaluator truth."
          ]
        }
      };
      const brief = briefs[state.demo_id] || briefs.fresh_now;
      return `
        <h3>${brief.title}</h3>
        <p>${brief.point}</p>
        <ol class="quick-steps">${brief.steps.map((step) => `<li>${step}</li>`).join("")}</ol>`;
    };
    const render = () => {
      if (!state) return;
      const temporalMode = isTemporalFamily();
      const fullGMode = isFullG();
      document.getElementById("demoSelect").value = state.demo_id;
      document.getElementById("moveEvent").disabled = !state.world_event_available;
      document.getElementById("moveEvent").textContent = state.move_event_label || "Apply world event";
      document.getElementById("worldEventHelp").textContent = state.world_event_help || "";
      document.getElementById("badgeBody").innerHTML = renderBadges();
      document.getElementById("sideWorldBody").innerHTML = renderSideWorld();
      document.getElementById("cycleRailBody").innerHTML = renderCycleRail();
      document.getElementById("stepperBody").innerHTML = renderStepper();
      document.getElementById("demoBriefBody").innerHTML = renderDemoBrief();
      document.getElementById("temporalTitle").textContent = isG23() ? "G2.3 Model Comparison" : "Temporal Geometry";
      document.getElementById("temporalCopy").textContent = isG23()
        ? "G2.3 compares representation formats with the same task facts and the same replaceable model faculty."
        : "G2 keeps present evidence, reconstructed memory, and future hypothesis visible as separate current channels.";
      document.getElementById("liveSection").hidden = temporalMode || fullGMode;
      document.getElementById("beforeAfterSection").hidden = temporalMode || fullGMode || state.demo_id !== "fresh_now";
      document.getElementById("g1ReasonerSection").hidden = temporalMode || fullGMode;
      document.getElementById("g1InspectorSection").hidden = temporalMode || fullGMode;
      document.getElementById("technicalSection").hidden = temporalMode || fullGMode;
      document.getElementById("temporalSection").hidden = !temporalMode;
      document.getElementById("benchmarkSection").hidden = !temporalMode;
      document.getElementById("fullGSection").hidden = !fullGMode;
      const querySelect = document.getElementById("querySelect");
      querySelect.innerHTML = state.query_options.map((option) => `<option value="${option.query_id}">${option.label}</option>`).join("");
      querySelect.value = state.query_options.find((option) => option.query.display === state.active_query.display)?.query_id || state.query_options[0]?.query_id;
      if (fullGMode) {
        document.getElementById("fullGBody").innerHTML = renderFullGReviewer();
      } else if (temporalMode) {
        document.getElementById("temporalBody").innerHTML = isG23() ? renderG23Body() : isG22() ? renderG22Body() : isG21() ? renderG21Body() : renderTemporalBody();
        document.getElementById("benchmarkBody").innerHTML = renderBenchmarkDashboard();
      } else {
        document.getElementById("worldBody").innerHTML = renderWorld();
        document.getElementById("nowBody").innerHTML = renderNow();
        document.getElementById("historyBody").innerHTML = renderHistory();
        document.getElementById("beforeAfterBody").innerHTML = renderBeforeAfter();
        renderBoundary();
        document.getElementById("graphBody").innerHTML = relationGraph(allCurrentRelations(), 14);
        document.getElementById("reasoningBody").innerHTML = renderReasoning();
        document.getElementById("technicalBody").innerHTML = renderTechnical();
      }
    };
    document.getElementById("demoSelect").addEventListener("change", (event) => post("/api/demo", {demo_id: event.target.value}));
    document.getElementById("runCycle").addEventListener("click", () => post("/api/run-cycle"));
    document.getElementById("moveEvent").addEventListener("click", () => post("/api/apply-world-event"));
    document.getElementById("deleteHistory").addEventListener("click", () => post("/api/delete-history"));
    document.getElementById("runQuery").addEventListener("click", () => post("/api/query", {query_id: document.getElementById("querySelect").value}));
    getState().then(() => {
      const params = new URLSearchParams(window.location.search);
      const requestedDemo = params.get("demo");
      if (requestedDemo && state?.demo_id !== requestedDemo) {
        return post("/api/demo", {demo_id: requestedDemo});
      }
      return null;
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
