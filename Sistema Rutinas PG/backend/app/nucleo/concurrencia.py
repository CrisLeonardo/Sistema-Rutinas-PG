"""Espera asíncrona antes de ocupar hilos y conexiones síncronas de la API."""
import anyio

class LimiteSolicitudesBD:
    def __init__(self, app, capacidad=5):
        self.app = app
        self.limite = anyio.CapacityLimiter(capacidad)

    async def __call__(self, scope, receive, send):
        # Salud, documentación y otros protocolos no necesitan una conexión.
        if (scope['type'] != 'http' or not scope['path'].startswith('/api/v1/')
                or scope['path'] == '/api/v1/estado' or scope['method'] == 'OPTIONS'):
            await self.app(scope, receive, send)
            return
        # La espera no ocupa un hilo de Starlette ni reserva una conexión.
        # El permiso se libera después del cierre de dependencias, incluso ante
        # una excepción o cancelación; no cambia cuerpos, permisos ni respuestas.
        async with self.limite:
            await self.app(scope, receive, send)
