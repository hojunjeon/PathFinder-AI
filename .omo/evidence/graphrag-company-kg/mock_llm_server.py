from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('content-length', '0'))
        if length:
            self.rfile.read(length)
        if self.path != '/llm/roadmap':
            self.send_response(404)
            self.end_headers()
            return
        body = {
            'competency_gap': {'strengths': ['curl API QA'], 'gaps': ['GraphRAG 운영']},
            'text_roadmap': 'curl 기반 Wave 1 QA 로드맵',
            'timeline_data': [{'week': 1, 'title': 'GraphRAG API 계약 검증', 'tasks': ['회사+공고+자소서 분석']}],
        }
        payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        return

HTTPServer(('127.0.0.1', 18081), Handler).serve_forever()
