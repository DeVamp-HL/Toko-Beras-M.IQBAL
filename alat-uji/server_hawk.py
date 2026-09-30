#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server_hawk.py — server statis untuk HawkScan di runner GitHub: menyajikan satu folder (isi `git archive` commit yang diuji = yang diterbitkan
Pages) dengan header meniru GitHub Pages; tanpa daftar isi folder. Dipakai .github/workflows/hawkscan.yml.

    python3 alat-uji/server_hawk.py 8765 /tmp/situs
"""
import http.server, sys, functools


class Penangan(http.server.SimpleHTTPRequestHandler):
    server_version = 'GitHub.com'   # header GitHub Pages: server tanpa versi, ACAO *, cache 600 dtk
    sys_version = ''

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'max-age=600')
        super().end_headers()

    def list_directory(self, path):
        self.send_error(404, 'File not found')
        return None

    def log_message(self, fmt, *args):
        pass


class Server(http.server.ThreadingHTTPServer):
    request_queue_size = 256
    daemon_threads = True


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    akar = sys.argv[2] if len(sys.argv) > 2 else '.'
    Server(('127.0.0.1', port), functools.partial(Penangan, directory=akar)).serve_forever()
