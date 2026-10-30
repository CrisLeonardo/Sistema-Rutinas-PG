"""Autoriza solo gmail.send mediante un cliente OAuth de escritorio del propietario.

Uso manual: python configurar_gmail.py ruta/al/client_secret.json
Guarda credenciales en .env.gmail (ignorado por Git); nunca las imprime.
No se ejecuta durante el arranque ni autentica a los usuarios de Senda en Google.
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cliente", type=Path)
    args = parser.parse_args()
    salida = Path(__file__).resolve().parent / ".env.gmail"
    if salida.exists():
        print("Ya existe .env.gmail. Conserva o retira manualmente ese archivo antes de reconfigurar.")
        return 1
    try:
        datos = json.loads(args.cliente.read_text(encoding="utf-8"))["installed"]
        cliente, secreto = datos["client_id"], datos["client_secret"]
        if not isinstance(cliente, str) or not cliente.endswith(".apps.googleusercontent.com") or not isinstance(secreto, str):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError):
        print("El archivo no contiene un cliente OAuth válido de tipo Aplicación de escritorio.")
        return 1
    estado = secrets.token_urlsafe(32)
    verificador = secrets.token_urlsafe(48)
    desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).decode().rstrip("=")
    resultado = {}

    class Respuesta(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *args):
            pass  # El código OAuth no debe quedar en un registro de URLs.

        def do_GET(self):
            partes = urlsplit(self.path)
            consulta = parse_qs(partes.query)
            valido = partes.path == "/oauth2callback" and hmac.compare_digest(consulta.get("state", [""])[0], estado)
            codigo = consulta.get("code", [""])[0]
            if valido and codigo:
                resultado["codigo"] = codigo
            self.send_response(200 if valido and codigo else 400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()
            self.wfile.write(("Autorización recibida. Vuelve a la consola de configuración de Senda." if valido and codigo else "No se completó la autorización. Vuelve a la consola.").encode())

    with HTTPServer(("127.0.0.1", 0), Respuesta) as servidor:
        retorno = f"http://127.0.0.1:{servidor.server_port}/oauth2callback"
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": cliente, "redirect_uri": retorno, "response_type": "code",
            "scope": "https://www.googleapis.com/auth/gmail.send", "state": estado,
            "access_type": "offline", "prompt": "consent",
            "code_challenge": desafio, "code_challenge_method": "S256",
            "login_hint": "senda1986.gt@gmail.com",
        })
        print("Abre este enlace personalmente, verifica el proyecto y autoriza solo la cuenta remitente:")
        print(url)
        print("Esperando autorización local durante un máximo de cinco minutos…")
        servidor.timeout = 1
        limite = time.monotonic() + 300
        while not resultado and time.monotonic() < limite:
            servidor.handle_request()
    if not resultado:
        print("No se recibió autorización. No se guardaron credenciales.")
        return 1
    try:
        peticion = Request("https://oauth2.googleapis.com/token", data=urlencode({
            "client_id": cliente, "client_secret": secreto, "code": resultado["codigo"],
            "redirect_uri": retorno, "grant_type": "authorization_code", "code_verifier": verificador,
        }).encode(), headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urlopen(peticion, timeout=15) as respuesta:
            refresh = json.load(respuesta)["refresh_token"]
        if not isinstance(refresh, str) or not refresh:
            raise ValueError
        valores = {"CORREO_TRANSPORTE": "gmail_api", "CORREO_REMITENTE": "senda1986.gt@gmail.com",
                   "GMAIL_CLIENTE_ID": cliente, "GMAIL_CLIENTE_SECRETO": secreto, "GMAIL_REFRESH_TOKEN": refresh}
        descriptor = os.open(salida, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(f"{clave}={json.dumps(valor)}" for clave, valor in valores.items()) + "\n")
    except (OSError, ValueError, KeyError):
        print("No se completó la configuración. Revisa el cliente OAuth y la autorización; no compartas códigos ni secretos.")
        return 1
    print("Configuración guardada en backend/.env.gmail. Reinicia el servidor. No subas este archivo a Git.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
