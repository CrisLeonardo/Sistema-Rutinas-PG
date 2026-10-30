"""Identidad exacta del único sostén del catálogo piloto; sin inferir por ID."""
def es_plancha(ejercicio):
    grupo = getattr(ejercicio.grupo_muscular, "value", ejercicio.grupo_muscular)
    return (ejercicio.nombre == "Plancha frontal" and grupo == "abdomen"
            and ejercicio.equipamiento == "Peso corporal")
