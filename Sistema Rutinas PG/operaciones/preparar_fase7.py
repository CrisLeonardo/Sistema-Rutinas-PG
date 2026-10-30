"""Crea otra base PostgreSQL ficticia y versionada para revisar fase 7 localmente.

Ejecutar con backend/.venv/Scripts/python.exe desde backend. No usa .env ni
producción. Conserva la base de ensayo y escribe solo su nombre en evidencias.
"""
from pathlib import Path
import sys
from uuid import uuid4
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.nucleo.migraciones import actualizar, diferencias
from app.nucleo.catalogo_inicial import cargar_ejercicios
from app.nucleo.alimentos_iniciales import cargar_alimentos
from app.esquemas.usuario import RegistroUsuario
from app.modelos.perfil import PerfilBiometrico
from app.servicios import autenticacion, plan
from sqlalchemy.orm import Session

def main():
    nombre = "senda_fase0_validacion_" + uuid4().hex[:12]
    prefijo = "postgresql+psycopg://senda_pruebas:SoloPruebasLocales2026@127.0.0.1:55432/"
    motor = create_engine(prefijo+"senda_fase0", isolation_level="AUTOCOMMIT")
    with motor.connect() as c:
        c.exec_driver_sql(f'CREATE DATABASE "{nombre}"')
    motor.dispose()
    motor = create_engine(prefijo+nombre)
    with motor.begin() as c:
        actualizar(c)
        assert diferencias(c) == []
    plan.obtener_motor = lambda: None
    with Session(motor) as s:
        cargar_ejercicios(s); cargar_alimentos(s)
        u = autenticacion.registrar_usuario(s, RegistroUsuario(
            correo="fase7@example.com", nombre="Demostración ficticia", contrasena="PruebaSenda2026!"))
        s.add(PerfilBiometrico(usuario_id=u.id, peso_kg=75, estatura_cm=172,
            edad=26, sexo="masculino", nivel_actividad="moderado", objetivo="ganancia_muscular",
            nivel_experiencia="principiante", dias_entrenamiento_semana=6))
        s.commit()
        # Recarga las enumeraciones desde PostgreSQL antes de construir el plan.
        s.expire_all(); plan.generar_plan(s,u)
    motor.dispose()
    salida=Path(__file__).resolve().parent/'evidencias/fase7'
    salida.mkdir(parents=True,exist_ok=True)
    (salida/'base-ui.txt').write_text(nombre,encoding='utf-8')
    print("Base ficticia preparada:",nombre)
    print("Cuenta de ensayo: fase7@example.com / PruebaSenda2026!")

if __name__ == '__main__':
    main()
