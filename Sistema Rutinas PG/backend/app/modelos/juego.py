"""Entidades de los puntos y las insignias.

El acumulado de puntos no se guarda como un contador. Se guarda como una
bitacora de hechos —un evento por cada motivo, con su fecha y su referencia— y
el total se obtiene sumandolos. Cuesta una consulta mas, y a cambio resuelve de
una vez tres problemas que un contador deja abiertos:

1. *Idempotencia.* La referencia dice a que hecho concreto corresponde el evento
   —el dia de la sesion, la semana de la racha, el ejercicio de la marca— y una
   restriccion de unicidad impide que el mismo hecho se pague dos veces. Sin
   ella, reenviar una peticion sumaria puntos otra vez.
2. *Reconstruccion.* Si manana cambia el valor de un motivo, el total viejo no
   queda como un numero que nadie puede explicar: los eventos siguen ahi con su
   motivo y su fecha.
3. *El camino recorrido.* La pantalla de la senda muestra en que fecha se alcanzo
   cada nivel. Eso no se puede deducir de un contador; se deduce recorriendo los
   eventos en orden y viendo cuando el acumulado cruzo cada umbral.

Los dos totales —puntos y logros— se filtran siempre por la cuenta en sesion, en
cumplimiento de la regla del negocio *f* del apartado 4.3.4.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.nucleo.base_datos import Base


class EventoJuego(Base):
    """Un hecho por el que el sistema otorgo puntos."""

    __tablename__ = "eventos_juego"
    __table_args__ = (
        # La pareja motivo-referencia es la que hace idempotente el otorgamiento:
        # «la sesion del 12 de marzo» o «la racha de la semana del 9 de junio» se
        # pagan una sola vez por mas veces que se recalculen.
        UniqueConstraint("usuario_id", "tipo", "referencia", name="uq_evento_juego"),
        Index("ix_eventos_juego_usuario_fecha", "usuario_id", "fecha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # Valor de `motor.juego.TipoEvento`. Se guarda como texto y no como tipo
    # enumerado del gestor porque la tabla de motivos crecera con el producto, y
    # agregar un motivo no deberia exigir migrar un tipo de PostgreSQL.
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    # A que hecho concreto corresponde: «2026-03-12», «semana:2026-06-09»,
    # «ejercicio:14:80.0». Es lo que la restriccion de unicidad compara.
    referencia: Mapped[str] = mapped_column(String(80), nullable=False)
    puntos: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    fecha: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<EventoJuego usuario_id={self.usuario_id} tipo={self.tipo!r} "
            f"referencia={self.referencia!r} puntos={self.puntos}>"
        )


class LogroObtenido(Base):
    """Una insignia que el usuario ya consiguio, con la fecha en que la consiguio.

    Solo se guardan las conseguidas. El catalogo completo vive en
    `motor.juego.LOGROS`, que es codigo y no datos: una insignia cuyo texto o
    cuyo umbral cambia no obliga a tocar la base de datos, y las que el usuario
    todavia no tiene no ocupan una fila que solo diria «no».
    """

    __tablename__ = "logros_obtenidos"
    __table_args__ = (
        UniqueConstraint("usuario_id", "clave", name="uq_logro_obtenido"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    clave: Mapped[str] = mapped_column(String(40), nullable=False)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<LogroObtenido usuario_id={self.usuario_id} clave={self.clave!r}>"
