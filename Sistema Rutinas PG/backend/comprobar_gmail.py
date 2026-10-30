"""Diagnóstico sin secretos. --enviar-a-remitente envía una prueba a la cuenta pública.

La aceptación de la API no acredita llegada a la bandeja; debe comprobarla el propietario.
"""
import argparse
from email.message import EmailMessage
from pathlib import Path
from app.nucleo.configuracion import configuracion as c
from app.servicios.recuperacion import enviar_por_gmail

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--enviar-a-remitente', action='store_true')
    args=p.parse_args()
    campos={"GMAIL_CLIENTE_ID": bool(c.gmail_cliente_id),
            "GMAIL_CLIENTE_SECRETO": bool(c.gmail_cliente_secreto),
            "GMAIL_REFRESH_TOKEN": bool(c.gmail_refresh_token),
            "CORREO_REMITENTE": str(c.correo_remitente or '') == 'senda1986.gt@gmail.com',
            "CORREO_TRANSPORTE=gmail_api": c.correo_transporte == 'gmail_api'}
    for nombre, disponible in campos.items():
        print(nombre+': '+('configurado' if disponible else 'pendiente'))
    if not all(campos.values()):
        print('No se puede verificar Gmail real. Complete la autorización del propietario según operaciones/CORREO_GMAIL.md.')
        return 2
    if not args.enviar_a_remitente:
        print('Configuración presente; no se hizo conexión ni envío. No acredita autorización vigente.')
        return 0
    mensaje=EmailMessage()
    mensaje['From']=mensaje['To']='senda1986.gt@gmail.com'
    mensaje['Subject']='Senda · prueba de entrega'
    mensaje.set_content('Prueba solicitada por el propietario. No contiene un enlace de recuperación ni datos de participantes. Comprueba la llegada y la carpeta de spam; después prueba el flujo de recuperación desde Senda con una cuenta controlada.')
    try:
        enviar_por_gmail(mensaje)
    except Exception:
        print('El proveedor no confirmó el envío. Revise la autorización privada; no comparta respuestas OAuth ni tokens.')
        return 1
    print('Gmail aceptó la prueba. Llegada a la bandeja y recuperación completa: pendientes de comprobación humana.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
