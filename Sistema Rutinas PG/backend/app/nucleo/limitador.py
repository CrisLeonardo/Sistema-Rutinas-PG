"""Limite de intentos sobre las rutas sensibles del acceso (requerimiento 4.5.1).

Nada impedia enviar diez mil intentos de acceso por minuto contra la ruta de
autenticacion. El sistema no revela cual dato fallo, de modo que un correo
existente no se distingue de uno inexistente, pero la contrasena si podia
adivinarse por fuerza bruta sin obstaculo alguno.

Hay una segunda razon, propia de este despliegue. El cifrado de contrasenas usa
bcrypt, que es lento a proposito: cada intento consume cerca de un decimo de
segundo de procesador. En una instancia de medio nucleo, unas pocas peticiones
simultaneas de acceso bastan para dejar sin capacidad al resto del sistema, de
modo que el limite protege tanto las cuentas como la disponibilidad.

El registro vive en la memoria del proceso. Es suficiente para el despliegue
declarado en `render.yaml`, que corre un unico proceso de trabajo por la memoria
que ocupa TensorFlow. Si alguna vez se levanta mas de una instancia, este
registro debera trasladarse a un almacen compartido: cada instancia contaria sus
propios intentos y el limite efectivo se multiplicaria por el numero de ellas.
"""

import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

# Intentos fallidos admitidos dentro de la ventana, por identificador.
INTENTOS_MAXIMOS = 8
VENTANA_SEGUNDOS = 300  # cinco minutos

# Tiempo que la llave queda bloqueada tras agotar los intentos.
BLOQUEO_SEGUNDOS = 900  # quince minutos

# Cantidad de llaves a partir de la cual se hace limpieza de las vencidas. Sin
# este barrido, una avalancha de correos distintos haria crecer el registro sin
# limite, que es la forma en que un limitador mal hecho se convierte el mismo en
# la vulnerabilidad que pretendia evitar.
LLAVES_PARA_LIMPIEZA = 2048


@dataclass(frozen=True)
class Veredicto:
    """Resultado de consultar el limitador."""

    permitido: bool
    segundos_de_espera: int = 0


class LimitadorDeIntentos:
    """Cuenta intentos fallidos por llave dentro de una ventana deslizante."""

    def __init__(
        self,
        intentos_maximos: int = INTENTOS_MAXIMOS,
        ventana_segundos: int = VENTANA_SEGUNDOS,
        bloqueo_segundos: int = BLOQUEO_SEGUNDOS,
    ) -> None:
        self.intentos_maximos = intentos_maximos
        self.ventana_segundos = ventana_segundos
        self.bloqueo_segundos = bloqueo_segundos
        self._intentos: dict[str, deque[float]] = defaultdict(deque)
        self._bloqueos: dict[str, float] = {}
        self._cerrojo = threading.Lock()

    def _purgar(self, llave: str, ahora: float) -> deque[float]:
        """Descarta los intentos que ya salieron de la ventana."""
        registro = self._intentos[llave]
        limite = ahora - self.ventana_segundos
        while registro and registro[0] < limite:
            registro.popleft()
        return registro

    def _limpiar_vencidos(self, ahora: float) -> None:
        """Retira las llaves sin intentos vigentes ni bloqueo activo."""
        limite = ahora - self.ventana_segundos
        vencidas = [
            llave
            for llave, registro in self._intentos.items()
            if (not registro or registro[-1] < limite)
            and self._bloqueos.get(llave, 0) <= ahora
        ]
        for llave in vencidas:
            self._intentos.pop(llave, None)
            self._bloqueos.pop(llave, None)

    def revisar(self, llave: str) -> Veredicto:
        """Indica si la llave puede intentar de nuevo, y cuanto debe esperar."""
        ahora = time.monotonic()
        with self._cerrojo:
            hasta = self._bloqueos.get(llave)
            if hasta is not None and hasta > ahora:
                return Veredicto(permitido=False, segundos_de_espera=int(hasta - ahora) + 1)
            return Veredicto(permitido=True)

    def registrar_fallo(self, llave: str) -> Veredicto:
        """Anota un intento fallido y bloquea la llave si agoto los admitidos."""
        ahora = time.monotonic()
        with self._cerrojo:
            if len(self._intentos) > LLAVES_PARA_LIMPIEZA:
                self._limpiar_vencidos(ahora)

            registro = self._purgar(llave, ahora)
            registro.append(ahora)

            if len(registro) >= self.intentos_maximos:
                self._bloqueos[llave] = ahora + self.bloqueo_segundos
                registro.clear()
                return Veredicto(
                    permitido=False, segundos_de_espera=self.bloqueo_segundos
                )
            return Veredicto(permitido=True)

    def registrar_exito(self, llave: str) -> None:
        """Borra el historial de la llave tras un acceso correcto."""
        with self._cerrojo:
            self._intentos.pop(llave, None)
            self._bloqueos.pop(llave, None)

    def reiniciar(self) -> None:
        """Vacia el registro completo. Lo usan las pruebas para aislarse."""
        with self._cerrojo:
            self._intentos.clear()
            self._bloqueos.clear()


# Un limitador por tipo de operacion, para que agotar los intentos de acceso no
# bloquee tambien el registro de cuentas nuevas.
limitador_de_acceso = LimitadorDeIntentos()
limitador_de_registro = LimitadorDeIntentos(intentos_maximos=12, bloqueo_segundos=600)
