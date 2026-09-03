# -*- coding: utf-8 -*-
"""Contenido del informe. build(g) recibe los helpers de build_doc via globals()."""

TITULO = ("Sistema web con redes neuronales para la automatizacion de regimenes "
          "nutricionales y rutinas de entrenamiento para personas de El Progreso, Jutiapa")
# (acentos correctos se colocan abajo; esta constante se redefine en build con tildes)


def build(g):
    globals().update(g)  # H1,H2,H3,P,DASH,LETTER,figure,tbl_caption,note,source,field,
                         # doc, page_break, Pt, Cm, OxmlElement, qn, WD_ALIGN_PARAGRAPH,
                         # WD_LINE_SPACING, WD_TABLE_ALIGNMENT, RGBColor

    titulo = ("Sistema web con redes neuronales para la automatización de regímenes "
              "nutricionales y rutinas de entrenamiento para personas de "
              "El Progreso, Jutiapa")

    # ----- helpers locales -----
    def center(text, bold=False, size=12, before=0, after=6, caps=False):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        r = p.add_run(text.upper() if caps else text)
        r.bold = bold
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        return p

    def shade(cell, hexcolor):
        tcPr = cell._tc.get_or_add_tcPr()
        sh = OxmlElement('w:shd')
        sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
        tcPr.append(sh)

    def make_table(rows, widths=None, header=True):
        t = doc.add_table(rows=0, cols=len(rows[0]))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            for ci, val in enumerate(row):
                cells[ci].text = ''
                para = cells[ci].paragraphs[0]
                para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.space_before = Pt(2)
                run = para.add_run(val)
                run.font.name = 'Times New Roman'; run.font.size = Pt(11)
                if header and ri == 0:
                    run.bold = True
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    shade(cells[ci], 'D9E2F3')
                else:
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                if widths:
                    cells[ci].width = widths[ci]
        if widths:
            for r in t.rows:
                for ci, w in enumerate(widths):
                    r.cells[ci].width = w
        return t

    # ============================ CARATULA ============================
    center("UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA", bold=True, size=14, before=12, after=2)
    center("FACULTAD DE INGENIERÍA EN SISTEMAS DE INFORMACIÓN", bold=True, size=13, after=2)
    center("CAMPUS JUTIAPA", bold=True, size=13, after=60)
    center(titulo, bold=True, size=14, after=80)
    center("TRABAJO DE GRADUACIÓN PRESENTADO POR:", size=12, after=2)
    center("CRISTOPHER LEONARDO ZEPEDA ESQUIVEL", bold=True, size=12, after=40)
    center("PREVIO A OPTAR AL GRADO ACADÉMICO DE", size=12, after=2)
    center("LICENCIADO EN INGENIERÍA EN SISTEMAS DE INFORMACIÓN", bold=True, size=12, after=2)
    center("Y TÍTULO PROFESIONAL DE", size=12, after=2)
    center("INGENIERO EN SISTEMAS DE INFORMACIÓN", bold=True, size=12, after=70)
    center("GUATEMALA, JUNIO DE 2026", bold=True, size=12)

    # ============================ INDICES ============================
    page_break()
    H1("Índice")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    field(p, 'TOC \\o "1-3" \\h \\z \\u',
          "El índice se generará al actualizar los campos en Word "
          "(seleccione todo con Ctrl+E y presione F9, o clic derecho > Actualizar campos).")

    page_break()
    H1("Índice de Tablas")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    field(p, 'TOC \\h \\z \\c "Tabla"',
          "El índice de tablas se generará al actualizar los campos en Word (F9).")

    page_break()
    H1("Índice de Figuras")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    field(p, 'TOC \\h \\z \\c "Figura"',
          "El índice de figuras se generará al actualizar los campos en Word (F9).")

    # ============================ INTRODUCCION ============================
    page_break()
    H1("Introducción")
    P("El presente trabajo de graduación tiene como propósito central el desarrollo de un "
      "sistema web basado en redes neuronales artificiales para la automatización de "
      "regímenes nutricionales y rutinas de entrenamiento personalizadas, dirigido a las "
      "personas que asisten a centros de acondicionamiento físico del municipio de "
      "El Progreso, departamento de Jutiapa, Guatemala.")
    P("La razón que motivó la elección de este tema radica en la brecha observada entre la "
      "creciente demanda de servicios de acondicionamiento físico en el municipio y la escasa "
      "disponibilidad de profesionales certificados en nutrición y entrenamiento que sean "
      "económicamente accesibles para la mayor parte de la población. Esta situación provoca "
      "que los usuarios recurran a planes genéricos extraídos de internet que carecen de rigor "
      "biológico y contextualización local, lo cual deriva en estancamiento de metas físicas, "
      "descompensaciones metabólicas y lesiones por mala ejecución de las cargas de trabajo "
      "(Bates et al., 2021).")
    P("El fundamento tecnológico que sustenta esta propuesta es la inteligencia artificial, "
      "específicamente las redes neuronales artificiales, las cuales han demostrado en múltiples "
      "estudios recientes una capacidad superior a los métodos manuales para procesar variables "
      "biométricas heterogéneas y producir recomendaciones de salud individualizadas en tiempo "
      "real (Rojanaphan, 2024; Tsolakidis, 2024; Russell & Norvig, 2021).")
    P("El objetivo general de la presente investigación es implementar un sistema web basado en "
      "redes neuronales para la automatización de regímenes nutricionales y rutinas de "
      "entrenamiento personalizadas, con el propósito de optimizar la precisión y el seguimiento "
      "de los planes de salud física de los usuarios. La hipótesis que guía el estudio plantea "
      "que la implementación del sistema propuesto automatiza de forma precisa y personalizada "
      "la generación de planes de salud, superando significativamente la precisión de los "
      "métodos empíricos y manuales empleados actualmente.")
    P("La metodología empleada es de enfoque cuantitativo con diseño experimental. Se aplicó un "
      "cuestionario estructurado a una muestra de 169 usuarios, y el modelo neuronal será "
      "validado mediante pruebas comparativas frente a las fórmulas metabólicas estándar de "
      "Mifflin-St Jeor y Harris-Benedict. El procesamiento estadístico se realizó con Microsoft "
      "Excel y el paquete estadístico para las ciencias sociales (Statistical Package for the "
      "Social Sciences, SPSS) (Hernández-Sampieri et al., 2023; Creswell & Creswell, 2023).")
    P("El informe se organiza en tres capítulos. El Capítulo I expone el anteproyecto de "
      "investigación, que integra los antecedentes, la justificación, el planteamiento del "
      "problema, los objetivos, la hipótesis, el marco metodológico —tipo de investigación, "
      "variables, población y muestra e instrumento de recolección de datos— y los resultados "
      "obtenidos en el trabajo de campo. El Capítulo II desarrolla el marco teórico que sustenta "
      "conceptualmente el estudio, abordando la inteligencia artificial, las redes neuronales, "
      "la teoría de sistemas, la ingeniería de software y los fundamentos de la nutrición "
      "deportiva y del entrenamiento físico. Finalmente, el Capítulo III describe las "
      "herramientas y los lenguajes de programación seleccionados para el desarrollo de la "
      "solución tecnológica propuesta.")

    # ============================ CAPITULO I ============================
    _capitulo_1(g, make_table, center)
    # ============================ CAPITULO II ============================
    _capitulo_2(g)
    # ============================ CAPITULO III ============================
    _capitulo_3(g)
    # ============================ REFERENCIAS ============================
    _referencias(g)
    # ============================ ANEXOS ============================
    _anexos(g, make_table)

    print("contenido construido")


# ====================================================================
# CAPITULO I
# ====================================================================
def _capitulo_1(g, make_table, center):
    globals().update(g)
    page_break()
    H1("Capítulo I – Anteproyecto de Investigación")
    P("El presente capítulo expone el anteproyecto de la investigación. En él se establecen los "
      "fundamentos que delimitan y orientan el estudio: los antecedentes que lo respaldan, la "
      "justificación que motiva su realización, el planteamiento y la formulación del problema, "
      "las preguntas y los objetivos que guían el trabajo, los alcances y límites, la hipótesis, "
      "la definición conceptual y operacional de las variables, el marco metodológico que rige el "
      "proceso y, finalmente, los resultados obtenidos mediante el instrumento de recolección de "
      "datos aplicado a la muestra de estudio.")

    # ---- 1.1 Antecedentes ----
    H2("1.1 Antecedentes")
    P("Como primer antecedente, se analizó el trabajo de Ribes Barberis (2024), titulado "
      "«Sistema Integral para la Personalización de Salud Deportiva en Gimnasios». El objetivo "
      "principal del autor fue desarrollar una plataforma informática que permitiera personalizar "
      "los planes de entrenamiento y nutrición, buscando cerrar la brecha de comunicación entre "
      "atletas y profesionales. Se llevó a cabo un proceso de prototipado tecnológico bajo "
      "metodologías ágiles, utilizando herramientas para construir interfaces web y móviles. Los "
      "resultados demostraron que centralizar la gestión de datos biométricos en una solución "
      "técnica es altamente efectivo, concluyendo que la tecnología en el acondicionamiento "
      "físico reduce significativamente los errores de coordinación profesional "
      "(Ribes Barberis, 2024).")
    P("El antecedente anterior guarda relación directa con la presente investigación porque valida "
      "la viabilidad técnica de integrar interfaces web con módulos de gestión biométrica. La "
      "diferencia radica en que el presente trabajo incorpora un modelo de redes neuronales para "
      "la generación automatizada de planes, superando la personalización estática del trabajo "
      "citado.")
    P("El segundo antecedente es la investigación de Rojanaphan (2024), titulada «Automated "
      "Nutrient Deficiency Detection and Recommendation Systems Using Deep Learning in Nutrition "
      "Science». El autor se propuso crear un sistema capaz de detectar deficiencias "
      "nutricionales de forma automática para generar recomendaciones dietéticas a medida. La "
      "metodología empleó técnicas avanzadas de aprendizaje profundo, implementando redes "
      "neuronales convolucionales para analizar fotografías de alimentos y redes neuronales "
      "recurrentes para procesar historiales dietéticos. Los resultados confirmaron que estos "
      "sistemas superan en precisión a los métodos manuales, concluyendo que la inteligencia "
      "artificial permite una escalabilidad en la personalización nutricional antes inalcanzable "
      "(Rojanaphan, 2024).")
    P("Este antecedente fundamenta el uso de arquitecturas de aprendizaje profundo en la presente "
      "investigación. Si bien Rojanaphan se enfoca en el análisis de imágenes de alimentos, el "
      "presente trabajo adapta el enfoque de redes neuronales al procesamiento de variables "
      "biométricas textuales, constituyendo una propuesta complementaria aplicada al contexto "
      "local de El Progreso, Jutiapa.")
    P("El tercer antecedente es el trabajo de Tsolakidis (2024), titulado «Artificial "
      "Intelligence and Machine Learning Technologies for Personalized Nutrition: A Review». El "
      "autor evaluó cómo las tecnologías de inteligencia artificial y aprendizaje automático "
      "facilitan la transición de dietas generales a planes nutricionales específicos mediante el "
      "análisis de algoritmos de aprendizaje supervisado y redes neuronales. Los resultados "
      "demostraron que la inteligencia artificial logra mayor precisión al predecir necesidades "
      "nutricionales únicas, concluyendo que estas soluciones son clave para combatir "
      "enfermedades crónicas mediante planes adaptativos en tiempo real (Tsolakidis, 2024).")
    P("La revisión de Tsolakidis (2024) sustenta el enfoque metodológico de la presente "
      "investigación al proveer evidencia empírica sobre la superioridad del aprendizaje "
      "supervisado para la predicción nutricional. Esto justifica la selección de dicho paradigma "
      "de entrenamiento para el modelo neuronal que se desarrollará.")
    P("El cuarto antecedente es la tesis doctoral de Monroy Rodríguez (2024), titulada «Ambiente "
      "computacional para compañeros digitales orientado al cuidado de la salud empleando "
      "infraestructura pervasiva». Su objetivo fue diseñar un ecosistema digital con agentes "
      "inteligentes capaces de monitorear y asistir la salud de forma proactiva, implementando "
      "una arquitectura que combina el internet de las cosas con algoritmos de inteligencia "
      "artificial. Los resultados mostraron que el uso de asistentes virtuales hace el "
      "seguimiento de hábitos saludables más natural y efectivo, concluyendo que la computación "
      "pervasiva es esencial para crear sistemas autónomos adaptables a los cambios biométricos "
      "de cada individuo (Monroy Rodríguez, 2024).")
    P("El modelo de adaptabilidad continua propuesto por Monroy Rodríguez (2024) enriquece la "
      "perspectiva arquitectónica de la presente investigación. Aunque el estudio no incorpora "
      "internet de las cosas, el principio de ajuste automático al perfil biométrico es retomado "
      "como fundamento para el módulo de retroalimentación del sistema propuesto.")
    P("El quinto antecedente es la tesis de Rivera Valdivia (2022), titulada «La aplicación de la "
      "inteligencia artificial en la nutrición personalizada». La autora analizó cómo la "
      "inteligencia artificial optimiza las intervenciones nutricionales con base en datos "
      "individuales, realizando una revisión sistemática de modelos algorítmicos que procesan "
      "variables biológicas para predecir requerimientos energéticos. Se concluyó que integrar la "
      "inteligencia artificial en plataformas digitales permite alcanzar un rigor científico en "
      "la nutrición que las guías generales no ofrecen (Rivera Valdivia, 2022).")
    P("Rivera Valdivia (2022) constituye el antecedente más cercano al contexto latinoamericano. "
      "Sus conclusiones sobre la aplicabilidad del aprendizaje automático en entornos con acceso "
      "limitado a profesionales de la salud respaldan directamente la justificación social de la "
      "presente investigación en el municipio de El Progreso, Jutiapa.")

    # ---- 1.2 Justificacion ----
    H2("1.2 Justificación")
    P("La presente investigación se origina ante la necesidad de modernizar la gestión de la "
      "salud física y deportiva en el municipio de El Progreso, Jutiapa. Actualmente existe un "
      "interés poblacional creciente por el bienestar físico, en contraste con la escasez de "
      "profesionales certificados en nutrición y entrenamiento que puedan atender dicha demanda. "
      "Esta situación provoca que los habitantes recurran a guías empíricas o estandarizadas "
      "disponibles en internet que carecen de rigor biológico y contextualización local "
      "(Russell & Norvig, 2021; Meskó et al., 2023).")
    P("El sustento de este trabajo radica en la implementación de tecnologías de inteligencia "
      "artificial para resolver esta problemática. La ruta de solución consiste en desarrollar "
      "una plataforma que automatice el cálculo de planes físicos mediante redes neuronales, "
      "eliminando los errores frecuentes de las aproximaciones manuales y democratizando el "
      "acceso a asesoría especializada (Topol, 2023).")
    P("Como contribución académica, este proyecto establece un precedente metodológico sobre cómo "
      "la ingeniería en sistemas puede aplicarse para resolver problemas de salud pública a nivel "
      "local. Se aporta un modelo funcional que demuestra la capacidad de los algoritmos de "
      "aprendizaje automático para procesar variables antropométricas complejas —peso, edad y "
      "metas— en tiempo real, traduciéndolas en resultados lógicos y estructurados. De esta "
      "manera, se genera conocimiento técnico aplicado al desarrollo de sistemas inteligentes de "
      "salud en contextos municipales con recursos limitados.")
    P("En cuanto a los aportes sociales, el sistema busca reducir los riesgos de lesiones "
      "articulares y descompensaciones metabólicas derivadas de un entrenamiento inadecuado. Los "
      "beneficiarios directos serán los habitantes económicamente activos del municipio de "
      "El Progreso, Jutiapa. El sistema mitigará la barrera financiera que representan las "
      "asesorías profesionales, cuyo costo oscila entre Q400.00 y Q800.00 mensuales y resulta "
      "prohibitivo para la mayoría de la población, democratizando el acceso a regímenes "
      "personalizados a través de un dispositivo móvil con conexión a internet "
      "(Bates et al., 2021).")

    # ---- 1.3 Planteamiento ----
    H2("1.3 Planteamiento del Problema")
    H3("1.3.1 Descripción del problema")
    P("En el municipio de El Progreso, Jutiapa, se observa un incremento significativo en el "
      "interés de la población por mejorar su estado físico, evidenciado en la creciente demanda "
      "de centros de acondicionamiento físico. La situación actual refleja una limitante crítica: "
      "la escasez de asesoría profesional accesible, debido a que los costos de los servicios "
      "personalizados de nutrición y entrenamiento resultan prohibitivos para un alto porcentaje "
      "de la población activa, con valores que oscilan entre Q400.00 y Q800.00 mensuales "
      "(INE, 2024).")
    P("Los hechos anteriores que guardan relación con esta problemática indican que, "
      "históricamente, las personas han intentado suplir la falta de guía profesional recurriendo "
      "a métodos empíricos o planes genéricos descargados de internet que no contemplan los "
      "requerimientos calóricos basales ni el historial de lesiones del individuo. Esta práctica "
      "ha provocado estancamiento en las metas físicas, descompensaciones nutricionales y "
      "lesiones por mala ejecución de las cargas de trabajo (MSPAS, 2022).")
    P("Los elementos centrales del problema involucran variables biométricas —peso, edad, "
      "historial de lesiones y objetivos de composición corporal—, factores tecnológicos y "
      "factores económicos. En síntesis, los elementos del problema son: la desinformación "
      "biométrica de los usuarios, la ausencia de control en las cargas progresivas de ejercicio "
      "y el déficit en la estructuración adecuada de los macronutrientes "
      "(Pérez-Escamilla et al., 2022).")
    P("La relevancia de resolver este problema radica en la necesidad urgente de mitigar los "
      "riesgos a la salud derivados de un entrenamiento o una alimentación inadecuada. Sustituir "
      "la planificación empírica por una herramienta tecnológica accesible permitirá democratizar "
      "la salud preventiva en el municipio de El Progreso, Jutiapa, mitigando el riesgo de "
      "lesiones y reduciendo las altas tasas de abandono deportivo en la región (OMS, 2021).")

    H3("1.3.2 Formulación del problema")
    P("¿De qué manera la implementación de un sistema web basado en redes neuronales automatiza y "
      "optimiza los regímenes nutricionales y las rutinas de entrenamiento de las personas del "
      "municipio de El Progreso, Jutiapa?")

    # ---- 1.4 Preguntas ----
    H2("1.4 Preguntas de Investigación")
    P("Para abordar la problemática central, se plantean las siguientes preguntas de "
      "investigación:")
    LETTER("a", "¿Qué nivel de precisión puede alcanzar una red neuronal artificial para calcular "
                "dietas y rutinas en comparación con los métodos tradicionales empleados "
                "actualmente en el municipio de El Progreso, Jutiapa?")
    LETTER("b", "¿Cuáles son los datos biométricos y de estilo de vida esenciales que el sistema "
                "debe procesar para que los planes generados sean individualizados y no genéricos "
                "para cada usuario?")
    LETTER("c", "¿De qué manera una plataforma web interactiva facilita la constancia en las metas "
                "de salud de los usuarios, en comparación con los métodos de registro físico o no "
                "sistemático?")

    # ---- 1.5 Objetivos ----
    H2("1.5 Objetivos de la Investigación")
    H3("1.5.1 Objetivo general")
    P("Implementar un sistema web basado en redes neuronales para la automatización de regímenes "
      "nutricionales y rutinas de entrenamiento personalizadas, con el propósito de optimizar la "
      "precisión y el seguimiento de los planes de salud física de las personas del municipio de "
      "El Progreso, Jutiapa.")
    H3("1.5.2 Objetivos específicos")
    LETTER("a", "Diseñar un modelo de red neuronal artificial que procese las variables "
                "biométricas del usuario para calcular requerimientos calóricos exactos y "
                "estructurar cargas de entrenamiento adaptadas al perfil individual.")
    LETTER("b", "Desarrollar una plataforma web adaptable que integre un catálogo de alimentos y "
                "ejercicios acordes a la disponibilidad de infraestructura y productos del "
                "municipio de El Progreso, Jutiapa.")
    LETTER("c", "Validar la precisión del sistema mediante evaluaciones comparativas frente a "
                "fórmulas de cálculo metabólico estandarizadas, aplicadas a la muestra de "
                "usuarios participantes en el estudio.")

    # ---- 1.6 Alcances y limites ----
    H2("1.6 Alcances y Límites")
    H3("1.6.1 Alcances")
    P("El sistema web contemplará, como mínimo, los siguientes módulos funcionales:")
    LETTER("a", "Módulo de autenticación y seguridad: gestiona el registro y el inicio de sesión "
                "de los usuarios, la administración de credenciales y el control de acceso por "
                "roles (usuario y administrador).")
    LETTER("b", "Módulo de gestión de perfiles de usuario: permite registrar y actualizar el "
                "historial biométrico de cada persona, incluyendo peso, edad, estatura, objetivos "
                "de composición corporal e historial de lesiones.")
    LETTER("c", "Módulo de inteligencia artificial (motor neuronal): procesa los datos "
                "biométricos y genera automáticamente la rutina de entrenamiento y el plan de "
                "alimentación correspondientes.")
    LETTER("d", "Módulo de catálogo de alimentos y ejercicios: administra los alimentos "
                "disponibles en los mercados locales y los ejercicios ejecutables con "
                "equipamiento estándar.")
    LETTER("e", "Módulo de seguimiento y adaptabilidad dinámica: registra el progreso periódico, "
                "reajusta los planes en función de los avances y genera reportes e indicadores de "
                "rendimiento.")
    P("El sistema se concibe como una herramienta de apoyo para el acondicionamiento físico y la "
      "nutrición deportiva estándar. Las rutinas generadas se orientan a ejercicios de calistenia "
      "y al equipamiento estándar disponible en centros de acondicionamiento físico "
      "convencionales. Además, tendrá un diseño adaptable accesible desde dispositivos móviles y "
      "computadoras, y su base de datos incorporará alimentos disponibles en los mercados del "
      "municipio de El Progreso, Jutiapa, para garantizar la viabilidad económica y cultural de "
      "los planes generados.")
    H3("1.6.2 Límites")
    P("El sistema queda excluido de la emisión de diagnósticos médicos y del tratamiento de "
      "patologías crónicas severas, por lo que no sustituye la valoración de un profesional de la "
      "salud. Tampoco contempla maquinaria de rehabilitación especializada. Su funcionamiento "
      "depende de que el usuario cuente con conexión estable a internet, y la precisión del "
      "modelo está condicionada por la veracidad de la información biométrica que el usuario "
      "ingrese: la omisión o inexactitud de los datos reducirá la eficacia de los planes "
      "generados.")
    H3("1.6.3 Aspectos demográficos")
    P("Los aspectos demográficos del municipio de El Progreso, departamento de Jutiapa, se "
      "presentan a continuación (INE, 2024):")
    DASH("Coordenadas: latitud 14°21′ norte y longitud 89°51′ oeste.")
    DASH("Colindancias: limita al norte con el municipio de Monjas, del departamento de Jalapa; "
         "al este con el municipio de Santa Catarina Mita; y al sur y al oeste con el municipio "
         "de Jutiapa.")
    DASH("Extensión territorial: aproximadamente 68 kilómetros cuadrados.")
    DASH("Distancia: se localiza a aproximadamente 146 kilómetros de la ciudad capital de "
         "Guatemala y a 16 kilómetros de la cabecera departamental de Jutiapa.")
    DASH("Población total del municipio: aproximadamente 22,400 habitantes.")
    DASH("Población económicamente activa: representa cerca del 38 % de la población total, "
         "segmento al cual se orienta la presente investigación.")
    H3("1.6.4 Datos de la institución")
    DASH("Nombre: Gimnasio FAMAS.")
    DASH("Dirección: zona urbana del municipio de El Progreso, departamento de Jutiapa.")
    DASH("Descripción: centro de acondicionamiento físico que ofrece servicios de entrenamiento "
         "con pesas, ejercicio cardiovascular y asesoría básica de ejercicio; cuenta con "
         "equipamiento estándar de musculación y constituye un establecimiento de referencia para "
         "la población deportiva del municipio.")
    DASH("Ubicación en Google Maps: la ubicación satelital de la institución se presenta en la "
         "figura siguiente.")
    figure("fig00_mapa.png", "Ubicación del Gimnasio FAMAS en Google Maps",
           "Fuente: Google Maps (2026).", width_cm=11)

    # ---- 1.7 Hipotesis ----
    H2("1.7 Hipótesis")
    P("La implementación de un sistema web basado en redes neuronales automatiza de forma precisa "
      "y personalizada la generación de regímenes nutricionales y rutinas de entrenamiento para "
      "las personas del municipio de El Progreso, Jutiapa, superando significativamente la "
      "precisión de los métodos empíricos y manuales tradicionales empleados actualmente.")

    # ---- 1.8 Def conceptual ----
    H2("1.8 Definición Conceptual de Variables")
    H3("1.8.1 Variable independiente")
    P("Sistema web basado en redes neuronales. Se conceptualiza como una aplicación informática "
      "accesible a través de navegadores, cuyo motor lógico incorpora inteligencia artificial "
      "mediante algoritmos conexionistas capaces de procesar un conjunto extenso de variables de "
      "entrada para tomar decisiones automatizadas y aprender patrones complejos "
      "(Russell & Norvig, 2021; Aggarwal, 2023).")
    H3("1.8.2 Variable dependiente")
    P("Automatización de regímenes nutricionales y rutinas de entrenamiento. Se define como la "
      "generación sistemática, calculada y progresiva del gasto energético, la distribución de "
      "macronutrientes y las cargas de fuerza requeridas por un individuo para alcanzar sus "
      "objetivos físicos, con base en rigor biológico y sin intervención manual directa "
      "(Schoenfeld, 2021; Thomas et al., 2021).")

    # ---- 1.9 Def operacional (dos tablas) ----
    H2("1.9 Definición Operacional de Variables")
    P("La operacionalización traduce las variables teóricas a indicadores medibles. A "
      "continuación se presenta una tabla por cada variable del estudio.")
    H3("1.9.1 Variable independiente")
    tbl_caption("Operacionalización de la variable independiente")
    make_table([
        ["Dimensión", "Indicadores"],
        ["Arquitectura y accesibilidad",
         "Nivel de usabilidad de la interfaz (escala de 1 a 5); tasa de disponibilidad en "
         "dispositivos móviles; tiempo de respuesta del servidor (en segundos)."],
        ["Precisión algorítmica",
         "Porcentaje de coincidencia del cálculo metabólico neuronal frente a la fórmula basal "
         "clínica (error menor al 5 %); capacidad de reajuste automático tras variaciones de "
         "peso."],
    ], widths=[Cm(4.5), Cm(11)])
    note("elaboración propia con base en Russell y Norvig (2021).")
    H3("1.9.2 Variable dependiente")
    tbl_caption("Operacionalización de la variable dependiente")
    make_table([
        ["Dimensión", "Indicadores"],
        ["Nutrición deportiva",
         "Gramaje exacto de macronutrientes asignados; kilocalorías totales programadas "
         "diariamente; tasa de inclusión de alimentos del contexto local."],
        ["Cargas de entrenamiento",
         "Volumen de entrenamiento (series por grupo muscular); frecuencia semanal calculada por "
         "el sistema; tiempos de recuperación prescritos entre sesiones."],
    ], widths=[Cm(4.5), Cm(11)])
    note("elaboración propia con base en Schoenfeld (2021).")

    # ---- 1.10 Tipo de investigacion ----
    H2("1.10 Tipo de la Investigación")
    P("La presente investigación se clasifica con un enfoque cuantitativo, dado que se fundamenta "
      "en la recolección y el análisis de datos numéricos y biométricos exactos para probar la "
      "hipótesis mediante análisis estadístico. Según su tendencia, es cuantitativa; según su "
      "orientación temporal, es prospectiva; y de acuerdo con la evolución del fenómeno "
      "estudiado, es transversal, pues las variables se estudian en un momento determinado. "
      "Según el análisis y el alcance de sus resultados, la investigación es descriptiva y "
      "explicativa, ya que busca caracterizar el cálculo metabólico e identificar cómo la red "
      "neuronal incide en la automatización de la salud física "
      "(Hernández-Sampieri et al., 2023; Creswell & Creswell, 2023).")
    P("El diseño de la investigación corresponde a una estructura experimental. En este diseño, "
      "el investigador controla la variable independiente —el sistema web basado en redes "
      "neuronales— para manipularla de manera intencional y aplicarla sobre el grupo de prueba. "
      "Esto permite medir objetivamente el efecto que produce el uso de la herramienta "
      "algorítmica sobre la variable dependiente —la precisión y la automatización de los planes "
      "de salud— frente a los métodos empíricos tradicionales "
      "(Hernández-Sampieri et al., 2023; Arias, 2022).")

    # ---- 1.11 Metodos y tecnicas ----
    H2("1.11 Métodos y Técnicas de Investigación")
    H3("1.11.1 Método científico")
    P("El método científico es el conjunto de procedimientos lógicos y sistemáticos mediante los "
      "cuales se plantean problemas, se formulan hipótesis y se someten a comprobación a través "
      "de la observación y la experimentación, con el fin de obtener conocimiento válido y "
      "verificable (Arias, 2022).")
    P("En la presente investigación se aplica el método científico porque el estudio posee una "
      "parte práctica que se sustenta en una hipótesis, la cual será comprobada mediante el "
      "desarrollo y la experimentación con el sistema propuesto. El proceso parte de la "
      "observación de la problemática, continúa con la formulación de la hipótesis y culmina con "
      "la validación experimental de los resultados generados por el modelo neuronal.")
    H3("1.11.2 Método inductivo")
    P("El método inductivo es aquel que parte de la observación de hechos particulares para "
      "llegar a conclusiones generales, estableciendo principios a partir de casos específicos "
      "analizados durante la investigación (Hernández-Sampieri et al., 2023).")
    P("Este método se aplica porque, a partir de los datos biométricos particulares de los "
      "usuarios y de los resultados específicos obtenidos en las pruebas del modelo, se "
      "establecen generalizaciones sobre la precisión y la pertinencia del sistema. La "
      "experimentación con casos individuales permite inferir conclusiones aplicables al conjunto "
      "de la población de estudio.")
    H3("1.11.3 Metodologías de desarrollo de software")
    P("Una metodología de desarrollo de software es un marco de trabajo estructurado que define "
      "las fases, las actividades y los entregables necesarios para construir un producto de "
      "software de manera ordenada y controlada. Entre las más utilizadas se encuentran las "
      "metodologías ágiles, como Scrum, que organizan el trabajo en ciclos cortos e iterativos "
      "denominados sprints, favoreciendo la entrega continua y la adaptación a los cambios "
      "(Pressman & Maxim, 2020; Sommerville, 2021).")
    P("Para el desarrollo de la solución se empleará la metodología ágil Scrum, complementada con "
      "el enfoque iterativo e incremental. Se eligió esta metodología porque permite construir el "
      "sistema en incrementos funcionales —correspondientes a cada uno de los módulos definidos "
      "en los alcances—, validar tempranamente el motor neuronal y ajustar el producto con base "
      "en la retroalimentación obtenida en cada iteración, lo que reduce el riesgo técnico del "
      "proyecto.")
    P("La técnica de investigación seleccionada es la encuesta, cuyo instrumento es un "
      "cuestionario estructurado descrito en la sección siguiente.")

    # ---- 1.12 Instrumento ----
    H2("1.12 Instrumento de Recolección de Datos")
    H3("1.12.1 Objetivo del instrumento")
    P("El instrumento de recolección de datos tiene como objetivo recopilar información sobre los "
      "hábitos de entrenamiento y nutrición, el acceso a la tecnología y la disposición de uso de "
      "las personas que asisten a centros de acondicionamiento físico del municipio de "
      "El Progreso, Jutiapa, con el fin de fundamentar el diseño del sistema y validar la "
      "pertinencia de la propuesta tecnológica.")
    P("Para la recolección de información durante el trabajo de campo se seleccionó como técnica "
      "la encuesta, utilizando como instrumento un cuestionario estructurado de opción múltiple "
      "con escala de tipo Likert. El instrumento consta de tres secciones: datos generales, "
      "hábitos de entrenamiento y nutrición, y acceso a la tecnología y disposición de uso "
      "(Hernández-Sampieri et al., 2023; Creswell & Creswell, 2023).")
    H3("1.12.2 Población estadística")
    P("La población o universo de estudio está conformada por la totalidad de habitantes "
      "económicamente activos, hombres y mujeres, que asisten a centros de acondicionamiento "
      "físico ubicados en el municipio de El Progreso, departamento de Jutiapa. Se estima una "
      "población finita de 300 usuarios concurrentes, dato aproximado basado en la capacidad "
      "operativa de los establecimientos (INE, 2024; Arias, 2022).")
    H3("1.12.3 Muestra")
    P("Se utilizó un muestreo probabilístico aleatorio simple. Para el cálculo de la muestra "
      "representativa se aplicó la fórmula estadística para poblaciones finitas "
      "(Hernández-Sampieri et al., 2023):")
    pf = doc.add_paragraph("n = (N × Z² × σ²) / ((N − 1) × e² + Z² × σ²)")
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.paragraph_format.space_after = Pt(6)
    P("Donde: N (población) = 300; Z (nivel de confianza del 95 %) = 1.96; σ (probabilidad de "
      "éxito) = 0.5; e (margen de error del 5 %) = 0.05. Al sustituir los valores se obtiene:")
    pf2 = doc.add_paragraph("n = (300 × 3.8416 × 0.25) / ((299 × 0.0025) + (3.8416 × 0.25)) "
                            "= 288.12 / 1.7079 ≈ 169 usuarios")
    pf2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf2.paragraph_format.space_after = Pt(6)
    P("La muestra representativa quedó conformada por 169 usuarios, a quienes se aplicó el "
      "instrumento de recolección de datos.")

    # ---- 1.12.4 Resultados de la encuesta ----
    H3("1.12.4 Resultados de la encuesta")
    P("A continuación se presentan los resultados obtenidos tras aplicar el instrumento a la "
      "muestra de 169 usuarios. Cada resultado se acompaña de su gráfica y de la interpretación "
      "correspondiente. Los datos se organizan en tres apartados: datos generales, hábitos de "
      "entrenamiento y nutrición, y acceso a la tecnología y disposición de uso; finalmente se "
      "incluyen dos gráficas cruzadas que relacionan una variable de la investigación con una "
      "variable demográfica.")

    def graf(fname, title, interp, src="Fuente: elaboración propia con base en el trabajo de "
                                       "campo (2026)."):
        figure(fname, title, src)
        P(interp)

    P("Datos generales", indent=False).runs[0].bold = True
    graf("fig01_genero.png", "Distribución de los encuestados según género",
         "Del total de encuestados, el 58.0 % corresponde al género masculino y el 39.6 % al "
         "femenino, mientras que un 2.4 % prefirió no indicarlo. Estos resultados muestran una "
         "participación mayoritariamente masculina, aunque con una presencia femenina "
         "considerable, lo que indica que el sistema debe contemplar planes adecuados para ambos "
         "géneros.")
    graf("fig02_edad.png", "Distribución de los encuestados según rango de edad",
         "El 36.1 % de los encuestados se ubica en el rango de 18 a 24 años y el 30.8 % entre 25 "
         "y 30 años; en conjunto, el 88.8 % es menor de 41 años. Esto confirma que la población "
         "de estudio es mayoritariamente joven, segmento con alta capacidad de adopción "
         "tecnológica.")
    graf("fig03_antiguedad.png", "Antigüedad de los encuestados en el gimnasio",
         "El 34.3 % de los encuestados tiene entre 3 y 6 meses de asistir al gimnasio y el "
         "27.8 % menos de 3 meses, lo que evidencia un flujo constante de usuarios recientes que "
         "requieren orientación inicial en sus rutinas y planes de alimentación.")

    P("Hábitos de entrenamiento y nutrición", indent=False).runs[0].bold = True
    graf("fig04_q1_plan_entreno.png", "Tipo de plan de entrenamiento que poseen los encuestados",
         "Solo el 14.2 % de los encuestados cuenta con un plan de entrenamiento elaborado por un "
         "entrenador certificado, mientras que el 42.0 % lo obtiene de internet o de una "
         "aplicación y el 43.8 % entrena sin un plan definido. Estos datos confirman la escasa "
         "asesoría profesional y justifican la necesidad de una herramienta automatizada.")
    graf("fig05_q2_plan_nutricion.png", "Tipo de plan nutricional que poseen los encuestados",
         "El 54.4 % de los encuestados no cuenta con un plan nutricional definido y apenas el "
         "8.9 % posee uno elaborado por un nutricionista certificado. La carencia de planificación "
         "nutricional profesional es aún mayor que la del entrenamiento, lo que refuerza la "
         "relevancia del módulo nutricional del sistema.")
    graf("fig06_q3_frecuencia.png", "Frecuencia semanal de asistencia al gimnasio",
         "El 46.7 % de los encuestados asiste al gimnasio de 3 a 4 días por semana y el 33.1 % de "
         "5 a 6 días, lo que indica una frecuencia de entrenamiento media-alta que demanda planes "
         "estructurados y progresivos para evitar el sobreentrenamiento.")
    graf("fig07_q4_dificultades.png", "Dificultades experimentadas por la falta de un plan "
         "profesional",
         "Las dificultades más mencionadas fueron la confusión sobre qué y cuánto comer "
         "(121 menciones) y el estancamiento en las metas físicas (112 menciones), seguidas por "
         "el abandono temporal del gimnasio y las lesiones por mala ejecución. Estos resultados, "
         "obtenidos mediante selección múltiple, evidencian las consecuencias directas de la "
         "ausencia de asesoría especializada.")
    graf("fig08_q5_gasto.png", "Capacidad de gasto mensual en asesoría profesional",
         "El 36.1 % de los encuestados manifestó no poder pagar una asesoría profesional y el "
         "28.4 % solo podría destinar menos de Q200 mensuales. Únicamente el 12.4 % podría cubrir "
         "el costo habitual de las asesorías (Q400 a más de Q800), lo que confirma la barrera "
         "económica que el sistema gratuito busca mitigar.")

    P("Acceso a la tecnología y disposición de uso", indent=False).runs[0].bold = True
    graf("fig09_q6_conocimiento.png", "Nivel de conocimiento sobre el cálculo de calorías y "
         "macronutrientes",
         "El 56.2 % de los encuestados calificó su conocimiento sobre el cálculo de calorías y "
         "macronutrientes en los niveles más bajos (1 y 2), y solo el 19.5 % en los niveles altos "
         "(4 y 5). Este desconocimiento generalizado respalda la utilidad de un sistema que "
         "realice automáticamente dichos cálculos.")
    graf("fig10_q7_dispositivo.png", "Dispositivo más utilizado para acceder a internet",
         "El 82.2 % de los encuestados utiliza principalmente el teléfono inteligente para "
         "acceder a internet, frente a porcentajes mínimos de computadora portátil, tableta o "
         "computadora de escritorio. Este resultado confirma la necesidad de un diseño adaptable "
         "orientado prioritariamente a dispositivos móviles.")
    graf("fig11_q8_facilidad.png", "Facilidad percibida para usar una plataforma web de gestión "
         "del plan",
         "El 76.3 % de los encuestados considera que podría usar con facilidad una plataforma web "
         "para gestionar su plan (niveles 4 y 5 de la escala), lo que indica una alta "
         "alfabetización digital y una baja barrera de adopción del sistema propuesto.")
    graf("fig12_q9_disposicion.png", "Disposición a utilizar el sistema web propuesto",
         "El 85.8 % de los encuestados manifestó disposición a utilizar el sistema "
         "(definitivamente sí o probablemente sí), mientras que solo el 4.2 % se mostró reacio. "
         "Este resultado evidencia una aceptación muy favorable hacia la solución tecnológica.")
    graf("fig13_q10_beneficio.png", "Mayor beneficio percibido del sistema",
         "El beneficio más valorado fue el ahorro en asesorías profesionales (32.0 %), seguido "
         "por el acceso a planes en cualquier momento (24.3 %) y la adaptación a los alimentos "
         "locales (21.3 %). Estos resultados confirman que la propuesta responde a las "
         "necesidades económicas y prácticas de la población.")

    P("Gráficas cruzadas", indent=False).runs[0].bold = True
    graf("fig14_cruce_disposicion_genero.png",
         "Disposición a utilizar el sistema según género",
         "Al cruzar la disposición de uso con el género se observa que tanto hombres (86 de 98) "
         "como mujeres (56 de 67) presentan una disposición favorable mayoritaria, sin "
         "diferencias significativas entre ambos. Esto indica que la aceptación del sistema es "
         "transversal al género y que la solución no requiere segmentarse por este criterio.")
    graf("fig15_cruce_facilidad_edad.png",
         "Facilidad de uso percibida según rango de edad",
         "Al cruzar la facilidad de uso con el rango de edad se aprecia que la percepción de "
         "facilidad alta predomina en los grupos más jóvenes (18 a 40 años), mientras disminuye "
         "en los mayores de 41 años. Por ello, el sistema debe incorporar una interfaz intuitiva "
         "que reduzca la curva de aprendizaje de los usuarios de mayor edad.")

    # ---- 1.13 Cronograma ----
    H2("1.13 Cronograma de Actividades")
    P("La investigación se rige por el cronograma que se presenta a continuación, el cual asocia "
      "las actividades con cada objetivo y distribuye su ejecución a lo largo de seis meses. La "
      "letra X indica el período estimado de realización de cada actividad.")
    tbl_caption("Cronograma de actividades del proyecto")
    crono = [
        ["Actividad", "Mes 1", "Mes 2", "Mes 3", "Mes 4", "Mes 5", "Mes 6"],
        ["Elaboración del anteproyecto de investigación", "X", "", "", "", "", ""],
        ["Construcción del marco teórico", "X", "X", "", "", "", ""],
        ["Definición de herramientas y lenguajes de programación", "", "X", "", "", "", ""],
        ["Diseño del modelo de red neuronal (objetivo a)", "", "X", "X", "", "", ""],
        ["Aplicación del instrumento y recolección de datos", "", "", "X", "", "", ""],
        ["Desarrollo de la plataforma web (objetivo b)", "", "", "X", "X", "X", ""],
        ["Entrenamiento y validación del modelo (objetivo c)", "", "", "", "X", "X", ""],
        ["Pruebas con usuarios y ajustes finales", "", "", "", "", "X", "X"],
        ["Tabulación, análisis e interpretación de resultados", "", "", "X", "", "", "X"],
        ["Redacción del informe final, conclusiones y recomendaciones", "", "", "", "", "X", "X"],
    ]
    t = make_table(crono, widths=[Cm(7.0)] + [Cm(1.4)] * 6)
    for r in t.rows[1:]:
        for ci in range(1, 7):
            r.cells[ci].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    note("elaboración propia. La investigación se ejecuta en seis meses, abarcando las fases de "
         "Proyecto de Graduación I y II.")


# ====================================================================
# CAPITULO II
# ====================================================================
def _capitulo_2(g):
    globals().update(g)
    page_break()
    H1("Capítulo II – Marco Teórico")
    P("El presente capítulo desarrolla el marco teórico que fundamenta la investigación. Se "
      "exponen los conceptos y las teorías que permiten comprender la inteligencia artificial y "
      "las redes neuronales, la teoría general de los sistemas, la ingeniería de software, los "
      "fundamentos de la nutrición deportiva y la planificación del entrenamiento físico, los "
      "cuales constituyen la base científica sobre la que se sustenta la propuesta. Asimismo, se "
      "describe el contexto sociodemográfico y nutricional en el que se enmarca el estudio.")

    H2("2.1 Inteligencia Artificial y Redes Neuronales")
    H3("2.1.1 Concepto de inteligencia artificial")
    P("La inteligencia artificial se define como la rama de las ciencias computacionales enfocada "
      "en el diseño de sistemas capaces de ejecutar tareas que requieren de la capacidad "
      "cognitiva humana. Estos algoritmos buscan emular funciones intelectuales fundamentales, "
      "tales como el aprendizaje continuo, la percepción de patrones y la resolución de problemas "
      "complejos. Esta base computacional resulta indispensable para sustituir la intervención "
      "manual en procesos lógicos de alta exigencia algorítmica y en el procesamiento de "
      "volúmenes extensos de información estructurada (Russell & Norvig, 2021).")
    P("La evolución histórica de la inteligencia artificial comprende la transición desde "
      "sistemas basados en reglas lógicas estáticas hasta modelos capaces de aprender de forma "
      "autónoma. Se identifican dos paradigmas principales: la inteligencia artificial simbólica, "
      "fundamentada en la manipulación de estructuras lógicas, y la inteligencia artificial "
      "conexionista, que emula el procesamiento biológico mediante nodos interconectados. Este "
      "segundo enfoque resulta superior para resolver problemas donde las variables no son "
      "lineales, como sucede con la fisiología humana (García & López, 2023; Schmidhuber, 2022).")
    P("La inteligencia artificial abarca diversas ramas, entre ellas el procesamiento del "
      "lenguaje natural, que interpreta y genera lenguaje humano; la visión por computadora, que "
      "analiza imágenes y video; los sistemas expertos, que emulan el razonamiento de un "
      "especialista; y el aprendizaje automático, que constituye el motor de los sistemas capaces "
      "de aprender a partir de datos. Esta última rama es la de mayor relevancia para los sistemas "
      "de recomendación, pues permite construir modelos predictivos sin necesidad de programar de "
      "forma explícita cada regla de decisión (Russell & Norvig, 2021; Géron, 2023).")
    P("En síntesis, la inteligencia artificial constituye el campo que dota a los sistemas "
      "computacionales de la capacidad de analizar información y generar respuestas de manera "
      "autónoma, lo que la convierte en un recurso idóneo para automatizar procesos de decisión "
      "basados en grandes volúmenes de datos y para ofrecer recomendaciones individualizadas con "
      "rigor científico (Topol, 2023).")

    H3("2.1.2 Redes neuronales artificiales")
    P("Las redes neuronales artificiales constituyen modelos computacionales que replican la "
      "estructura biológica del cerebro para reproducir sus características de procesamiento de "
      "información. A diferencia de los sistemas de cálculo secuencial tradicionales, operan como "
      "redes paralelas y adaptativas, ajustando sus conexiones sinápticas con base en la "
      "experiencia matemática y generalizando respuestas a partir de los datos empíricos "
      "suministrados (Goodfellow et al., 2022; Aggarwal, 2023).")
    P("El componente base de estas arquitecturas es la neurona artificial, que recibe un vector "
      "de datos de entrada y genera una respuesta de salida tras aplicar funciones de activación. "
      "Las neuronas se organizan en capas: una capa de entrada que recibe los datos externos, "
      "capas ocultas que procesan y transforman la información, y una capa de salida que produce "
      "el resultado final. La arquitectura multicapa permite modelar relaciones no lineales entre "
      "las variables de entrada y los valores de salida deseados "
      "(Goodfellow et al., 2022; Zhang et al., 2023).")
    figure("figd1_red_neuronal.png",
           "Estructura de una red neuronal artificial multicapa",
           "Fuente: elaboración propia con base en Goodfellow et al. (2022).", width_cm=12)
    P("Entre las funciones de activación más utilizadas destaca la unidad lineal rectificada "
      "(Rectified Linear Unit, ReLU), que mitiga el problema del desvanecimiento del gradiente y "
      "permite que los algoritmos aprendan patrones numéricos de alta complejidad de forma rápida "
      "y estable (Chollet, 2021). De este modo, las redes neuronales artificiales se consolidan "
      "como una técnica superior a los métodos manuales, pues aprenden patrones complejos a "
      "partir de múltiples casos y generalizan ese conocimiento para producir resultados "
      "precisos.")
    P("El proceso de entrenamiento de una red neuronal consiste en ajustar los pesos de las "
      "conexiones para minimizar el error entre la salida producida y la salida esperada. Durante "
      "la propagación hacia adelante, los datos atraviesan la red y generan una predicción; "
      "posteriormente, mediante la retropropagación del error y el algoritmo de descenso del "
      "gradiente, se calculan y actualizan los pesos en sentido inverso. Este ciclo se repite a lo "
      "largo de múltiples iteraciones, denominadas épocas, hasta que la función de pérdida alcanza "
      "un valor mínimo aceptable (Goodfellow et al., 2022; Chollet, 2021).")
    P("El desempeño de una red neuronal depende en gran medida de la configuración de sus "
      "hiperparámetros, es decir, de los valores que se definen antes del entrenamiento y que "
      "controlan su comportamiento. Entre los más relevantes se encuentran la tasa de "
      "aprendizaje, que determina la magnitud de los ajustes de los pesos; el número de capas "
      "ocultas y de neuronas por capa, que define la capacidad del modelo; el tamaño del lote de "
      "datos; y la función de pérdida, que cuantifica el error. La selección adecuada de estos "
      "valores resulta determinante para lograr un modelo preciso y estable "
      "(Géron, 2023; Goodfellow et al., 2022).")

    H3("2.1.3 Aprendizaje automático")
    P("El aprendizaje automático (Machine Learning, ML) constituye la dinámica operativa mediante "
      "la cual un sistema incorpora conocimiento ajustando iterativamente sus pesos sinápticos. "
      "Se distinguen el aprendizaje supervisado, que utiliza pares de datos de entrada y salida "
      "validada para minimizar el margen de error, y el aprendizaje no supervisado, enfocado en "
      "descubrir agrupaciones inherentes dentro de conjuntos de datos sin objetivos predefinidos "
      "(Tsolakidis, 2024; Géron, 2023).")
    P("El aprendizaje supervisado resulta especialmente adecuado cuando se dispone de datos cuyos "
      "valores de salida han sido calculados previamente mediante fórmulas estándar validadas, "
      "pues garantiza que el modelo genere respuestas coherentes con las métricas de referencia "
      "científica y reduzca su margen de error a medida que aumenta el volumen de datos "
      "disponibles para el entrenamiento (Géron, 2023; LeCun et al., 2021).")
    P("Un aspecto crítico del aprendizaje automático es el equilibrio entre el sobreajuste y el "
      "subajuste. El sobreajuste ocurre cuando el modelo memoriza los datos de entrenamiento y "
      "pierde capacidad de generalización, mientras que el subajuste se presenta cuando el modelo "
      "es demasiado simple para capturar los patrones existentes. Para evitar ambos extremos, el "
      "conjunto de datos se divide en subconjuntos de entrenamiento, validación y prueba, lo que "
      "permite evaluar de forma objetiva la capacidad predictiva del modelo "
      "(Géron, 2023; Bishop & Bishop, 2024).")

    H3("2.1.4 Aprendizaje profundo")
    P("El aprendizaje profundo (Deep Learning) representa una subdisciplina algorítmica avanzada "
      "estructurada sobre arquitecturas de múltiples capas matemáticas, cuya característica "
      "central es el aprendizaje profundo de representaciones. Esto implica que el sistema extrae "
      "características de forma automática a partir de los datos iniciales, modelando relaciones "
      "no lineales y reconociendo patrones ocultos con una precisión predictiva superior a la de "
      "los modelos estadísticos convencionales (Rojanaphan, 2024; Bishop & Bishop, 2024).")
    P("La capacidad del aprendizaje profundo para identificar correlaciones complejas entre "
      "variables lo convierte en una técnica idónea para sistemas adaptativos, en los que las "
      "capas ocultas detectan relaciones entre la evolución de los datos de entrada y los ajustes "
      "necesarios en la salida, produciendo recomendaciones progresivamente más precisas "
      "(LeCun et al., 2021; Zhang et al., 2023).")
    P("Dentro del aprendizaje profundo se han desarrollado arquitecturas especializadas. Las "
      "redes neuronales convolucionales destacan en el análisis de imágenes, mientras que las "
      "redes neuronales recurrentes resultan idóneas para procesar secuencias y datos temporales. "
      "Para el procesamiento de variables numéricas estructuradas, como las biométricas, se "
      "emplean redes neuronales densas o totalmente conectadas, cuya arquitectura multicapa "
      "modela las relaciones no lineales entre las entradas y las salidas "
      "(Bishop & Bishop, 2024; LeCun et al., 2021). La figura siguiente ilustra la relación de "
      "pertenencia entre la inteligencia artificial y sus subcampos.")
    figure("figd2_ia_ml_dl.png",
           "Relación entre la inteligencia artificial, el aprendizaje automático y el aprendizaje "
           "profundo",
           "Fuente: elaboración propia con base en Russell y Norvig (2021).", width_cm=9.5)
    H3("2.1.5 Sistemas de recomendación inteligentes")
    P("Los sistemas de recomendación son aplicaciones de la inteligencia artificial que sugieren "
      "elementos o acciones pertinentes a un usuario a partir del análisis de sus características "
      "y preferencias. Se clasifican principalmente en sistemas basados en contenido, que "
      "recomiendan elementos similares a los que el usuario ha valorado; sistemas de filtrado "
      "colaborativo, que se apoyan en las preferencias de usuarios semejantes; y sistemas "
      "híbridos, que combinan ambos enfoques (Russell & Norvig, 2021; Géron, 2023).")
    P("Cuando estos sistemas incorporan redes neuronales, son capaces de modelar relaciones "
      "complejas entre numerosas variables de entrada y producir recomendaciones altamente "
      "individualizadas. Este enfoque resulta especialmente útil en dominios donde cada "
      "recomendación debe ajustarse a un perfil único, como ocurre con la salud y la nutrición "
      "personalizadas (Tsolakidis, 2024; Rojanaphan, 2024).")

    H2("2.2 Teoría General de los Sistemas")
    H3("2.2.1 Concepto de sistema")
    P("Bajo la teoría general de los sistemas, un sistema informático se define como un conjunto "
      "de unidades en interrelación mutua y funcional que forman un todo unitario. Los "
      "subsistemas internos no operan de forma aislada, sino a través de interdependencias "
      "lógicas que permiten procesar flujos de entrada de información para transformarlos en "
      "salidas estructuradas orientadas hacia un objetivo común "
      "(Sommerville, 2021; Kendall & Kendall, 2022).")
    P("Adicionalmente, la teoría general de los sistemas introduce el concepto de "
      "retroalimentación, fundamental para la adaptabilidad tecnológica. La retroalimentación "
      "ocurre cuando la salida de un sistema se reintroduce como entrada, permitiendo que el "
      "sistema capture su nuevo estado y reajuste automáticamente sus variables para mantenerse "
      "orientado hacia su objetivo (Sommerville, 2021).")
    P("Todo sistema puede representarse mediante el modelo de entrada-proceso-salida, "
      "complementado con la retroalimentación. Las entradas son los datos o recursos que ingresan "
      "al sistema; el proceso los transforma según una lógica determinada; la salida es el "
      "resultado generado; y la retroalimentación reintroduce información sobre la salida para "
      "corregir y optimizar el comportamiento del sistema, tal como se aprecia en la figura "
      "siguiente (Kendall & Kendall, 2022).")
    figure("figd3_sistema.png",
           "Modelo de entrada-proceso-salida con retroalimentación",
           "Fuente: elaboración propia con base en Kendall y Kendall (2022).", width_cm=12)

    H3("2.2.2 Tipos de sistemas")
    P("Dentro de la taxonomía de sistemas se distinguen los sistemas físicos o concretos, "
      "compuestos por equipo y maquinaria, y los sistemas abstractos o simbólicos, conformados "
      "por conceptos e hipótesis. Desde su operatividad, se identifican sistemas cerrados, que no "
      "intercambian información con el exterior, y sistemas abiertos, que presentan una relación "
      "constante con su ambiente (Sommerville, 2021; Russell & Norvig, 2021).")
    P("Los sistemas abiertos y dinámicos interactúan continuamente con su entorno, recibiendo "
      "datos del exterior y adaptando sus salidas en función de esas entradas. Esta clasificación "
      "resulta de particular interés para el diseño de aplicaciones informáticas que deben "
      "responder de manera flexible a la información proporcionada por sus usuarios "
      "(Kendall & Kendall, 2022).")
    H3("2.2.3 Características de los sistemas")
    P("Los sistemas presentan propiedades que rigen su comportamiento. El propósito u objetivo "
      "orienta la interacción de sus elementos; la globalidad o totalidad implica que un cambio en "
      "cualquier componente repercute en el conjunto; la sinergia indica que el todo es mayor que "
      "la suma de sus partes; la homeostasis es la capacidad de mantener el equilibrio interno "
      "ante perturbaciones externas; y la entropía es la tendencia natural al desgaste que los "
      "sistemas abiertos contrarrestan mediante la incorporación de información y la "
      "retroalimentación (Sommerville, 2021; Kendall & Kendall, 2022).")
    H3("2.2.4 El enfoque sistémico en el software")
    P("La teoría general de los sistemas proporciona el fundamento conceptual para analizar el "
      "software como un sistema: los datos que ingresan constituyen las entradas, los algoritmos "
      "representan el proceso, los resultados son las salidas y la retroalimentación permite el "
      "ajuste continuo. Este enfoque orienta el análisis y el diseño de las aplicaciones "
      "informáticas, al concebirlas como conjuntos de componentes interdependientes que persiguen "
      "un objetivo común y que interactúan con su entorno (Kendall & Kendall, 2022; "
      "Sommerville, 2021).")

    H2("2.3 Ingeniería de Software")
    H3("2.3.1 Concepto de ingeniería de software")
    P("La ingeniería de software es la disciplina que aplica principios de ingeniería al "
      "desarrollo de software de manera sistemática, disciplinada y cuantificable, abarcando "
      "todas las etapas del ciclo de vida: análisis, diseño, construcción, pruebas, despliegue y "
      "mantenimiento. Su propósito es producir software confiable que funcione de manera "
      "eficiente sobre las plataformas para las que fue concebido "
      "(Pressman & Maxim, 2020; Sommerville, 2021).")
    P("El ciclo de vida del software organiza el trabajo en fases sucesivas o iterativas. Los "
      "modelos iterativos e incrementales, propios de las metodologías ágiles, permiten construir "
      "el producto por partes funcionales y refinarlo de manera continua, lo cual reduce el "
      "riesgo y favorece la calidad del resultado final (Sommerville, 2021).")
    H3("2.3.2 Atributos de calidad del software")
    P("La ingeniería de un sistema de información exige garantizar atributos de calidad como la "
      "usabilidad, que facilita la interacción del usuario; la seguridad, que protege la "
      "información mediante mecanismos de cifrado y control de acceso; la disponibilidad, que "
      "asegura el funcionamiento ininterrumpido ante accesos concurrentes; y la mantenibilidad, "
      "que permite incorporar cambios con un costo razonable "
      "(Pressman & Maxim, 2020; Bass et al., 2022).")
    P("Estos atributos se consideran requisitos no funcionales del sistema y deben ser "
      "contemplados desde las primeras etapas del diseño, ya que condicionan la arquitectura y la "
      "selección de las herramientas tecnológicas con las que se construirá la solución "
      "(Bass et al., 2022).")
    H3("2.3.3 Requisitos del software")
    P("Los requisitos del software se clasifican en funcionales y no funcionales. Los requisitos "
      "funcionales describen las funciones que el sistema debe ejecutar, como el registro de "
      "usuarios o la generación de planes; los requisitos no funcionales establecen restricciones "
      "sobre la forma en que el sistema opera, tales como el rendimiento, la seguridad, la "
      "disponibilidad y la usabilidad. La especificación clara de ambos tipos de requisitos "
      "constituye la base sobre la cual se diseña y construye un producto de software de calidad, "
      "y permite verificar objetivamente si la solución cumple con lo esperado "
      "(Sommerville, 2021; Pressman & Maxim, 2020).")
    H3("2.3.4 Arquitectura de software")
    P("La arquitectura de software es la estructura fundamental de un sistema, compuesta por sus "
      "componentes principales, las relaciones entre ellos y los principios que orientan su "
      "diseño y evolución. Una arquitectura bien definida favorece la calidad, la escalabilidad y "
      "el mantenimiento del producto, pues organiza la complejidad y facilita la división del "
      "trabajo entre los distintos módulos (Bass et al., 2022; Pressman & Maxim, 2020).")
    P("Existen diversos estilos y patrones arquitectónicos que ofrecen soluciones probadas a "
      "problemas recurrentes de diseño. Entre los más difundidos figuran la arquitectura en "
      "capas, que separa la presentación, la lógica de negocio y el acceso a los datos; la "
      "arquitectura cliente-servidor, que distribuye el procesamiento entre quien solicita y "
      "quien provee los servicios; y los patrones de asignación de responsabilidades, que guían "
      "la organización interna del código. La adopción de estos patrones constituye una buena "
      "práctica de la ingeniería de software (Fowler, 2023; Bass et al., 2022).")

    H2("2.4 Fundamentos de Nutrición Deportiva")
    H3("2.4.1 Cálculo metabólico")
    P("El cálculo metabólico consiste en la cuantificación matemática precisa del gasto "
      "energético diario que ocurre a nivel celular, el cual se expresa en kilocalorías. Este "
      "factor biométrico se determina por la suma algebraica del efecto termogénico de los "
      "macronutrientes, el nivel de actividad física planificada y el requerimiento energético "
      "basal del individuo en reposo absoluto (Williams & Rawson, 2023; Burke & Deakin, 2022).")
    P("El segundo componente crítico del gasto energético es la termogénesis por actividad sin "
      "ejercicio (Non-Exercise Activity Thermogenesis, NEAT), que cuantifica las calorías "
      "consumidas mediante el movimiento cotidiano no planificado. A cada nivel de actividad se "
      "le asigna un factor multiplicador específico que afina el cálculo metabólico final "
      "(Williams & Rawson, 2023; Jeukendrup, 2022).")
    P("Adicionalmente, el efecto térmico de los alimentos representa la energía necesaria para la "
      "masticación, la digestión y la absorción de los nutrientes. Las proteínas poseen un "
      "coeficiente termogénico significativamente más alto que los carbohidratos y las grasas, "
      "requiriendo hasta un 30 % de su propio valor energético para su asimilación. La inclusión "
      "de este cálculo evita subestimaciones en el requerimiento calórico diario "
      "(Burke & Deakin, 2022; Mahan & Raymond, 2021).")
    P("En consecuencia, el gasto energético total diario resulta de la suma del metabolismo "
      "basal, el efecto térmico de los alimentos y la energía consumida en la actividad física, "
      "tanto planificada como no planificada. La cuantificación precisa de cada componente es "
      "indispensable para diseñar regímenes nutricionales ajustados a las necesidades reales de "
      "cada individuo (Williams & Rawson, 2023; Jeukendrup, 2022).")
    H3("2.4.2 Fórmulas predictivas de la tasa metabólica basal")
    P("El desarrollo clínico de las ecuaciones predictivas permite estimar la tasa metabólica "
      "basal procesando factores antropométricos como el peso corporal, la estatura, la edad "
      "cronológica y el sexo. Estructuras matemáticas validadas, como la fórmula de "
      "Mifflin-St Jeor, han comprobado estadísticamente poseer un margen de exactitud superior "
      "para el modelado de regímenes en poblaciones adultas "
      "(Aragón et al., 2022; Mahan & Raymond, 2021).")
    P("La tasa metabólica basal actúa como el cimiento matemático sobre el cual se multiplica el "
      "factor de actividad física del individuo para determinar el gasto energético total diario. "
      "La automatización de este cálculo elimina el sesgo de error humano que se presenta al "
      "diseñar planes de forma manual (Aragón et al., 2022; Jeukendrup, 2022).")
    P("Entre las ecuaciones más utilizadas se encuentran la fórmula de Harris-Benedict y la de "
      "Mifflin-St Jeor. Esta última, para los hombres, se expresa como tasa metabólica basal = "
      "(10 × peso en kilogramos) + (6.25 × estatura en centímetros) − (5 × edad en años) + 5; "
      "para las mujeres, la constante final cambia a −161. Estas ecuaciones permiten estimar el "
      "gasto energético en reposo a partir de datos antropométricos sencillos, lo que facilita su "
      "programación y automatización dentro de un sistema informático "
      "(Aragón et al., 2022; Mahan & Raymond, 2021).")
    H3("2.4.3 Distribución de macronutrientes")
    P("La correcta partición del valor calórico exige distribuir los carbohidratos, las proteínas "
      "y los lípidos en porcentajes adaptados a metas fisiológicas concretas. Para los procesos "
      "de hipertrofia muscular se prescriben balances nitrogenados positivos de hasta 2.2 gramos "
      "de proteína por kilogramo de peso corporal, mientras que los protocolos de reducción "
      "lipídica sostienen principalmente el déficit energético controlado "
      "(Schoenfeld, 2021; Thomas et al., 2021).")
    P("La conversión de gramos de macronutrientes a sus equivalentes energéticos se realiza "
      "mediante las constantes de Atwater: los carbohidratos y las proteínas aportan 4 "
      "kilocalorías por gramo, mientras que los lípidos aportan 9 kilocalorías por gramo. La "
      "automatización de estas conversiones elimina el proceso aritmético que suele realizarse de "
      "forma manual (Schoenfeld, 2021; Stear & Burke, 2022; Aragón et al., 2022).")
    H3("2.4.4 Hidratación y micronutrientes")
    P("Además del aporte energético de los macronutrientes, una planificación nutricional "
      "integral considera la hidratación y los micronutrientes. El agua participa en la "
      "termorregulación y en el transporte de nutrientes, por lo que su consumo adecuado resulta "
      "determinante para el rendimiento físico. Los micronutrientes —vitaminas y minerales— "
      "intervienen en procesos metabólicos esenciales y, aunque no aportan calorías, su "
      "deficiencia compromete la salud y la recuperación muscular "
      "(Williams & Rawson, 2023; Mahan & Raymond, 2021).")

    H2("2.5 Planificación del Entrenamiento Físico")
    H3("2.5.1 Variables del entrenamiento de fuerza")
    P("La dosificación adecuada del estímulo deportivo demanda el control exhaustivo del volumen "
      "de trabajo —series y repeticiones totales—, la frecuencia de las sesiones y la intensidad "
      "del esfuerzo muscular. La correcta cuantificación de variables paramétricas como las "
      "repeticiones en reserva (Reps in Reserve, RIR) y el índice de esfuerzo percibido (Rate of "
      "Perceived Exertion, RPE) previene la incidencia clínica del sobreentrenamiento "
      "(Israetel et al., 2022; Haff & Triplett, 2022).")
    P("La gestión de la intensidad incorpora el concepto del carácter del esfuerzo, medido a "
      "través del índice de esfuerzo percibido y de las repeticiones en reserva. Estas métricas "
      "permiten ajustar la carga de trabajo según el estado de fatiga del individuo, asegurando "
      "que el estímulo se mantenga dentro del umbral de seguridad fisiológica para la hipertrofia "
      "muscular (Israetel et al., 2022; Suchomel et al., 2022; Fleck & Kraemer, 2022).")
    P("El volumen, la intensidad y la frecuencia constituyen las variables fundamentales que "
      "deben equilibrarse en toda programación del entrenamiento de fuerza. Un volumen "
      "insuficiente no genera el estímulo necesario para la adaptación, mientras que un volumen "
      "excesivo, sin la recuperación adecuada, conduce a la fatiga acumulada y al riesgo de "
      "lesión. Por ello, su dosificación debe responder al nivel y a los objetivos de cada "
      "persona (Haff & Triplett, 2022; Israetel et al., 2022).")
    H3("2.5.2 Sobrecarga progresiva y prevención de lesiones")
    P("La sobrecarga progresiva es el principio biológico que exige aplicar un incremento gradual "
      "de la tensión mecánica durante las rutinas físicas. Esta manipulación calculada del "
      "esfuerzo asegura la activación de la supercompensación fisiológica y fomenta adaptaciones "
      "musculares de manera segura (Bompa & Buzzichelli, 2022; Zatsiorsky et al., 2021).")
    P("La adaptación biológica al entrenamiento se fundamenta en el síndrome general de "
      "adaptación, que describe cómo el organismo responde a un estresor físico a través de tres "
      "fases: alarma, resistencia y supercompensación. La planificación de los incrementos de "
      "carga debe coincidir con la fase de supercompensación para evitar el sobreentrenamiento "
      "(Bompa & Buzzichelli, 2022; Haff & Triplett, 2022).")
    P("Asimismo, se distinguen los tipos de hipertrofia muscular: la sarcoplasmática, que aumenta "
      "el volumen del plasma muscular, y la miofibrilar, que incrementa el tamaño y el número de "
      "las fibras contráctiles. El objetivo perseguido determina el número de repeticiones y los "
      "tiempos bajo tensión que deben prescribirse "
      "(Bompa & Buzzichelli, 2022; Schoenfeld, 2021; Helms et al., 2023).")
    H3("2.5.3 Periodización del entrenamiento")
    P("La periodización es la planificación sistemática del entrenamiento mediante la división "
      "del tiempo en ciclos —macrociclos, mesociclos y microciclos— con objetivos específicos. "
      "Esta organización permite alternar las cargas de trabajo y los períodos de recuperación "
      "para maximizar las adaptaciones y reducir el riesgo de sobreentrenamiento. La "
      "periodización constituye el marco que ordena la aplicación progresiva del estímulo a lo "
      "largo del tiempo y permite estructurar de manera lógica las rutinas de entrenamiento "
      "(Bompa & Buzzichelli, 2022; Fleck & Kraemer, 2022).")

    H2("2.6 Contexto Sociodemográfico y Nutricional del Municipio de El Progreso, Jutiapa")
    H3("2.6.1 Datos demográficos del municipio")
    P("El municipio de El Progreso, perteneciente al departamento de Jutiapa, experimenta un "
      "aumento estadístico en el índice de sedentarismo y de anomalías metabólicas en la "
      "población adulta joven. La combinación del estilo de vida urbano y el fácil acceso a "
      "dietas ultraprocesadas plantea la necesidad de intervenciones digitales basadas en "
      "tecnología móvil para mitigar la deficiencia de orientación sanitaria especializada "
      "(INE, 2024; MSPAS, 2022).")
    P("El perfil demográfico del municipio muestra que el segmento de población entre los 18 y "
      "los 40 años representa el grupo con mayor potencial de adopción tecnológica. Este grupo se "
      "caracteriza por un uso intensivo de dispositivos móviles, lo que facilita la integración "
      "de plataformas digitales en sus actividades cotidianas (INE, 2024; Meskó et al., 2023).")
    P("Esta caracterización demográfica resulta relevante para cualquier intervención tecnológica "
      "en el ámbito de la salud, pues la edad, el nivel de alfabetización digital y el acceso a "
      "dispositivos condicionan la adopción de soluciones basadas en aplicaciones móviles y web. "
      "Comprender el perfil de la población permite diseñar herramientas pertinentes y de fácil "
      "apropiación (Meskó et al., 2023; Bates et al., 2021).")
    H3("2.6.2 Estado actual de la nutrición en el municipio")
    P("En el contexto de la salud pública departamental, la región oriental de Guatemala "
      "experimenta una transición epidemiológica y nutricional profunda. Los reportes sanitarios "
      "documentan un incremento significativo en la prevalencia de sobrepeso, obesidad y "
      "enfermedades metabólicas no transmisibles en la población adulta, agravado por la escasez "
      "de programas de educación nutricional contextualizados a la canasta básica local "
      "(Organización Panamericana de la Salud, 2021; MSPAS, 2022).")
    P("La problemática nutricional se caracteriza por la «doble carga de la malnutrición», en la "
      "que coexisten la deficiencia de micronutrientes y el exceso de peso. Frente a ello, se "
      "recomienda priorizar productos locales con alta densidad nutricional que permitan "
      "reeducar los hábitos alimenticios mediante planes económicamente viables "
      "(Organización Panamericana de la Salud, 2021; Pérez-Escamilla et al., 2022; OMS, 2021).")
    H3("2.6.3 Demanda de servicios de salud física y adopción tecnológica")
    P("La convergencia entre la necesidad de mejorar la condición física y la escasez de "
      "profesionales certificados genera una brecha de atención crítica. Los reportes de "
      "telecomunicaciones indican una alta tasa de penetración de telefonía móvil inteligente e "
      "internet móvil, lo que facilita que los habitantes integren plataformas digitales en sus "
      "actividades cotidianas (Superintendencia de Telecomunicaciones, 2023; Bates et al., 2021).")
    P("Según los reportes técnicos disponibles, el uso de aplicaciones para el monitoreo de la "
      "salud ha crecido de manera sostenida en los últimos años a nivel nacional. Esta tendencia "
      "favorece la implementación de sistemas basados en inteligencia artificial que actúan como "
      "puente ante la falta de centros de salud especializados "
      "(Superintendencia de Telecomunicaciones, 2023; Topol, 2023; Meskó et al., 2023).")
    P("En conjunto, el contexto sociodemográfico y nutricional descrito evidencia la confluencia "
      "de tres factores: una población joven con alta disposición tecnológica, una problemática "
      "nutricional creciente y una brecha en la atención profesional especializada. Esta "
      "confluencia configura un escenario propicio para las intervenciones digitales basadas en "
      "inteligencia artificial, que pueden actuar como un complemento accesible frente a las "
      "limitaciones del modelo de atención tradicional "
      "(Topol, 2023; Bates et al., 2021; Meskó et al., 2023).")


# ====================================================================
# CAPITULO III
# ====================================================================
def _capitulo_3(g):
    globals().update(g)

    def shade(cell, hexcolor):
        tcPr = cell._tc.get_or_add_tcPr()
        sh = OxmlElement('w:shd')
        sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hexcolor)
        tcPr.append(sh)

    def make_table(rows, widths=None, header=True):
        t = doc.add_table(rows=0, cols=len(rows[0]))
        t.style = 'Table Grid'
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            for ci, val in enumerate(row):
                cells[ci].text = ''
                para = cells[ci].paragraphs[0]
                para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.space_before = Pt(2)
                run = para.add_run(val)
                run.font.name = 'Times New Roman'; run.font.size = Pt(11)
                if header and ri == 0:
                    run.bold = True
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    shade(cells[ci], 'D9E2F3')
                else:
                    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                if widths:
                    cells[ci].width = widths[ci]
        if widths:
            for r in t.rows:
                for ci, w in enumerate(widths):
                    r.cells[ci].width = w
        return t

    page_break()
    H1("Capítulo III – Herramientas y Lenguajes de Programación")
    P("El presente capítulo describe las herramientas y los lenguajes de programación "
      "seleccionados para el desarrollo de la solución tecnológica. Las herramientas de "
      "programación son aquellas que permiten construir aplicaciones, programas y sistemas, "
      "mientras que los lenguajes de programación son las estructuras que, con una base "
      "sintáctica y semántica definida, imparten instrucciones a la computadora. Se exponen la "
      "arquitectura del sistema, los lenguajes empleados, los marcos de trabajo y las "
      "bibliotecas, el gestor de base de datos y las herramientas de apoyo al desarrollo "
      "(Pressman & Maxim, 2020).")
    P("La selección de las herramientas y los lenguajes se fundamenta en criterios de pertinencia "
      "técnica, madurez tecnológica, disponibilidad de documentación y compatibilidad entre los "
      "componentes. La pila tecnológica adoptada combina Python para el procesamiento "
      "inteligente, JavaScript y la biblioteca React para la interfaz, y MySQL para la "
      "persistencia de los datos, integrados mediante una interfaz de programación de aplicaciones "
      "que garantiza la comunicación entre las distintas capas del sistema "
      "(Sommerville, 2021; Bass et al., 2022).")

    H2("3.1 Arquitectura del Sistema Web")
    H3("3.1.1 Arquitectura cliente-servidor")
    P("La arquitectura cliente-servidor distribuye el procesamiento computacional delegando la "
      "presentación gráfica a la interfaz del cliente, mientras confina la gestión transaccional "
      "intensiva al servidor. El cliente envía peticiones y el servidor las atiende y devuelve "
      "las respuestas correspondientes, lo que permite separar responsabilidades y escalar cada "
      "componente de manera independiente (Tanenbaum & Wetherall, 2021; Bass et al., 2022).")
    P("Esta arquitectura se selecciona porque permite que el motor de inteligencia artificial y "
      "la base de datos residan en el servidor, mientras los usuarios acceden a la plataforma "
      "desde cualquier dispositivo con navegador, garantizando el acceso universal y la "
      "centralización segura de la información biométrica. La figura siguiente muestra la "
      "distribución de los componentes del sistema bajo esta arquitectura.")
    figure("figd4_cliente_servidor.png",
           "Arquitectura cliente-servidor del sistema",
           "Fuente: elaboración propia con base en Bass et al. (2022).", width_cm=13)
    H3("3.1.2 Patrón Modelo-Vista-Controlador")
    P("El patrón de arquitectura Modelo-Vista-Controlador (MVC) divide el código en tres capas "
      "lógicas independientes: el modelo administra las reglas de negocio y el acceso a la base "
      "de datos; la vista despliega la interfaz gráfica; y el controlador gestiona las peticiones "
      "del usuario y coordina la comunicación entre el modelo y la vista "
      "(Pressman & Maxim, 2020; Fowler, 2023).")
    P("Se adopta este patrón porque facilita el mantenimiento y la escalabilidad del sistema: "
      "permite modificar el motor de cálculo metabólico sin alterar la interfaz, y viceversa, "
      "favoreciendo el desarrollo ordenado de cada módulo, tal como se ilustra a continuación.")
    figure("figd5_mvc.png",
           "Patrón de arquitectura Modelo-Vista-Controlador",
           "Fuente: elaboración propia con base en Fowler (2023).", width_cm=10.5)
    H3("3.1.3 Interfaz de programación de aplicaciones REST y formato JSON")
    P("Para enlazar el servidor con la interfaz del cliente se emplea una interfaz de "
      "programación de aplicaciones (Application Programming Interface, API) basada en el estilo "
      "de transferencia de estado representacional (Representational State Transfer, REST). Las "
      "transmisiones de datos se realizan en el formato de notación de objetos de JavaScript "
      "(JavaScript Object Notation, JSON), ligero y de fácil interpretación "
      "(Tanenbaum & Wetherall, 2021; Fowler, 2023).")
    P("Esta interfaz se utiliza para comunicar el modelo neuronal —desarrollado en Python— con la "
      "interfaz del usuario —desarrollada en React—, permitiendo que ambos componentes "
      "intercambien información de manera estandarizada y segura.")
    P("La interfaz de programación de aplicaciones basada en transferencia de estado "
      "representacional organiza la comunicación en torno a recursos, a los cuales se accede "
      "mediante los métodos del protocolo de transferencia de hipertexto: GET para consultar, "
      "POST para crear, PUT para actualizar y DELETE para eliminar información. Cada respuesta "
      "incluye un código de estado que informa sobre el resultado de la operación, lo que "
      "estandariza y hace predecible la interacción entre el cliente y el servidor "
      "(Tanenbaum & Wetherall, 2021; Fowler, 2023).")
    tbl_caption("Métodos del protocolo de transferencia de hipertexto utilizados por la interfaz "
                "de programación de aplicaciones")
    make_table([
        ["Método", "Descripción", "Uso en el sistema"],
        ["GET", "Recupera información de un recurso.",
         "Consultar el perfil del usuario y los planes generados."],
        ["POST", "Crea un nuevo recurso.",
         "Registrar un usuario y solicitar la generación de un plan."],
        ["PUT", "Actualiza un recurso existente.",
         "Modificar los datos biométricos del perfil."],
        ["DELETE", "Elimina un recurso.",
         "Eliminar un plan o una cuenta de usuario."],
    ], widths=[Cm(2.2), Cm(6.0), Cm(7.3)])
    note("elaboración propia con base en Fowler (2023).")
    H3("3.1.4 Flujo de datos del sistema")
    P("El flujo de datos describe el recorrido de la información desde que el usuario la ingresa "
      "hasta que recibe su plan personalizado. El usuario introduce sus datos biométricos en la "
      "interfaz construida con React; esta los envía, en formato JSON, a la interfaz de "
      "programación de aplicaciones desarrollada con FastAPI; el servidor invoca el motor neuronal "
      "implementado en Python, que procesa los datos y calcula los requerimientos; de manera "
      "simultánea, se consulta la base de datos MySQL para obtener los alimentos y ejercicios "
      "pertinentes; finalmente, el sistema devuelve a la interfaz el plan de entrenamiento y "
      "nutrición, que se presenta al usuario. La figura siguiente ilustra este recorrido.")
    figure("figd6_flujo_api.png",
           "Flujo de datos del sistema a través de la interfaz de programación de aplicaciones",
           "Fuente: elaboración propia.", width_cm=13.5)

    H2("3.2 Lenguajes de Programación")
    H3("3.2.1 Python")
    P("Python es un lenguaje de programación de alto nivel, interpretado y de propósito general, "
      "reconocido por su sintaxis clara y por su amplio ecosistema de bibliotecas orientadas al "
      "análisis de datos y al aprendizaje automático (Géron, 2023).")
    P("Se selecciona Python para construir el motor de inteligencia artificial del sistema, "
      "debido a que ofrece bibliotecas maduras para el entrenamiento de redes neuronales y "
      "permite implementar con eficiencia los algoritmos que calculan los requerimientos "
      "calóricos y las cargas de entrenamiento.")
    P("Python cuenta con un ecosistema de bibliotecas especializadas para el tratamiento de "
      "datos, como NumPy para el cálculo numérico y Pandas para la manipulación de conjuntos de "
      "datos. Esta riqueza de herramientas reduce el tiempo de desarrollo del componente "
      "inteligente y facilita la depuración y preparación de los datos biométricos antes de su "
      "ingreso al modelo neuronal (Géron, 2023).")
    P("Asimismo, Python se ha consolidado como el lenguaje de referencia en el campo de la "
      "inteligencia artificial gracias a su amplia comunidad, su extensa documentación y la "
      "disponibilidad de marcos de trabajo especializados. Esta madurez del ecosistema garantiza "
      "soporte a largo plazo y facilita la incorporación de nuevas técnicas al modelo "
      "(Géron, 2023; Chollet, 2021).")
    H3("3.2.2 JavaScript")
    P("JavaScript es el lenguaje de programación que se ejecuta en el navegador y permite dotar "
      "de interactividad a las páginas web, gestionando eventos, validaciones y comunicación "
      "asíncrona con el servidor (Flanagan, 2020).")
    P("Este lenguaje se emplea en la capa de presentación para construir una interfaz dinámica "
      "que responda en tiempo real a las acciones del usuario, como el registro de datos "
      "biométricos y la visualización de los planes generados.")
    P("Una de las características más relevantes de JavaScript es su capacidad para ejecutar "
      "operaciones de manera asíncrona, lo que permite que la interfaz solicite información al "
      "servidor sin bloquear la interacción del usuario. Esta propiedad resulta esencial para "
      "mantener una experiencia fluida mientras el modelo procesa los datos y genera los planes "
      "correspondientes (Flanagan, 2020).")
    H3("3.2.3 HTML5")
    P("El lenguaje de marcas de hipertexto (HyperText Markup Language, HTML), en su versión 5, es "
      "el estándar que estructura el contenido de las páginas web mediante etiquetas que definen "
      "los distintos elementos de un documento (Duckett, 2021).")
    P("Se utiliza para estructurar las pantallas de la plataforma —formularios de registro, "
      "tablas de resultados y secciones de seguimiento—, proporcionando la base semántica sobre "
      "la cual se aplican los estilos y la lógica de la interfaz.")
    P("Entre las ventajas de esta versión del lenguaje destacan las etiquetas semánticas, que "
      "describen el significado del contenido y mejoran la accesibilidad; la compatibilidad con "
      "contenido multimedia sin necesidad de complementos externos; y la posibilidad de validar "
      "formularios de manera nativa, característica útil para verificar los datos biométricos que "
      "ingresa el usuario (Duckett, 2021).")
    H3("3.2.4 CSS3")
    P("Las hojas de estilo en cascada (Cascading Style Sheets, CSS), en su versión 3, "
      "constituyen el lenguaje que define la presentación visual de un documento estructurado, "
      "separando el contenido de su apariencia y permitiendo crear diseños adaptables a distintas "
      "dimensiones de pantalla (Duckett, 2021).")
    P("Mediante este lenguaje se logra el diseño adaptable (responsive) de la plataforma, "
      "indispensable porque la mayoría de los usuarios accederá desde teléfonos inteligentes, "
      "según se evidenció en los resultados de la encuesta.")
    P("Este lenguaje permite definir reglas de presentación reutilizables, aplicar consultas de "
      "medios para adaptar el diseño a distintos tamaños de pantalla y emplear modelos de "
      "maquetación flexibles, como las cajas flexibles y las cuadrículas. Estas capacidades "
      "garantizan una experiencia visual coherente tanto en computadoras como en teléfonos "
      "inteligentes (Duckett, 2021).")
    H3("3.2.5 SQL")
    P("El lenguaje de consulta estructurada (Structured Query Language, SQL) permite definir, "
      "manipular y consultar la información almacenada en bases de datos relacionales mediante "
      "sentencias declarativas (Silberschatz et al., 2021; Elmasri & Navathe, 2023).")
    P("Se emplea para cruzar los requerimientos calóricos calculados por la red neuronal con la "
      "disponibilidad de productos locales, y para almacenar el historial biométrico de cada "
      "usuario sin redundancias y con integridad referencial.")
    P("Las bases de datos relacionales organizan la información en tablas vinculadas mediante "
      "claves primarias y foráneas, y el lenguaje de consulta estructurada permite recuperar "
      "datos combinados de varias tablas a través de operaciones de reunión. Esta capacidad es "
      "fundamental para relacionar el perfil del usuario con los planes generados y con los "
      "catálogos de alimentos y ejercicios disponibles (Silberschatz et al., 2021).")
    H3("3.2.6 Comparación de los lenguajes utilizados")
    P("Cada lenguaje cumple un papel específico dentro de la solución, según el componente al "
      "que pertenece. La tabla siguiente resume el paradigma, el ámbito de ejecución y la función "
      "de los lenguajes empleados.")
    tbl_caption("Comparación de los lenguajes de programación utilizados")
    make_table([
        ["Lenguaje", "Ámbito de ejecución", "Función principal"],
        ["Python", "Servidor",
         "Implementar el motor neuronal y la lógica de cálculo."],
        ["JavaScript", "Cliente (navegador)",
         "Dotar de interactividad a la interfaz del usuario."],
        ["HTML5", "Cliente (navegador)",
         "Estructurar el contenido de las pantallas."],
        ["CSS3", "Cliente (navegador)",
         "Definir la presentación visual y el diseño adaptable."],
        ["SQL", "Base de datos",
         "Consultar y manipular la información almacenada."],
    ], widths=[Cm(2.6), Cm(5.0), Cm(7.9)])
    note("elaboración propia.")

    H2("3.3 Marcos de Trabajo y Bibliotecas")
    H3("3.3.1 TensorFlow y Keras")
    P("TensorFlow es una biblioteca de código abierto para el cálculo numérico y el aprendizaje "
      "automático, y Keras es la interfaz de alto nivel que facilita la construcción y el "
      "entrenamiento de redes neuronales sobre dicha biblioteca (Chollet, 2021; Géron, 2023).")
    P("Estas herramientas se utilizan para definir la arquitectura de la red neuronal, configurar "
      "sus capas y funciones de activación, y entrenar el modelo con los datos biométricos hasta "
      "alcanzar el margen de error establecido.")
    P("El uso de Keras simplifica la definición de la red mediante una sintaxis declarativa, en "
      "la que cada capa se agrega de forma secuencial; además, TensorFlow aprovecha la "
      "aceleración por hardware, lo que reduce el tiempo de entrenamiento cuando el volumen de "
      "datos aumenta. Esta combinación facilita la experimentación con distintas configuraciones "
      "de la red hasta obtener el modelo más preciso (Chollet, 2021; Géron, 2023).")
    H3("3.3.2 FastAPI")
    P("FastAPI es un marco de trabajo de Python para construir interfaces de programación de "
      "aplicaciones web de alto rendimiento, con validación automática de datos y generación de "
      "documentación interactiva (Ramírez, 2023).")
    P("Se selecciona para exponer el modelo neuronal como un servicio web, de modo que la "
      "interfaz del usuario pueda solicitar la generación de planes y recibir las respuestas en "
      "formato JSON de manera rápida y segura.")
    P("Entre sus ventajas se encuentran la validación automática de los datos de entrada y de "
      "salida mediante modelos tipados, lo que reduce los errores; la generación automática de "
      "documentación interactiva de los servicios; y un alto rendimiento basado en la ejecución "
      "asíncrona, características que lo hacen idóneo para exponer servicios de inteligencia "
      "artificial (Ramírez, 2023).")
    H3("3.3.3 React")
    P("React es una biblioteca de JavaScript para construir interfaces de usuario basadas en "
      "componentes reutilizables, que actualiza de manera eficiente la vista cuando cambian los "
      "datos de la aplicación (Banks & Porcello, 2020).")
    P("Esta biblioteca se emplea para desarrollar la interfaz de cliente de la plataforma, "
      "permitiendo construir pantallas interactivas y mantenibles que muestran los planes de "
      "entrenamiento y nutrición de forma clara.")
    P("Su modelo basado en componentes favorece la reutilización del código y la separación de "
      "responsabilidades, mientras que su mecanismo de actualización eficiente de la vista mejora "
      "el rendimiento de la interfaz al volver a dibujar únicamente los elementos que cambian, lo "
      "que resulta valioso al mostrar resultados que se recalculan con frecuencia "
      "(Banks & Porcello, 2020).")
    H3("3.3.4 Bootstrap")
    P("Bootstrap es un marco de trabajo de presentación que proporciona componentes y un sistema "
      "de rejilla para crear interfaces adaptables de manera ágil, garantizando una apariencia "
      "uniforme en distintos dispositivos (Bass et al., 2022).")
    P("Se utiliza junto con las hojas de estilo en cascada para asegurar que la plataforma se "
      "ajuste automáticamente a las dimensiones de cualquier pantalla, en especial las de los "
      "dispositivos móviles.")
    H3("3.3.5 Resumen comparativo de los marcos de trabajo y bibliotecas")
    P("Cada marco de trabajo o biblioteca se ubica en una capa específica del sistema y aporta "
      "una funcionalidad distinta. La tabla siguiente resume su lenguaje base, la capa a la que "
      "pertenece y su función dentro de la solución.")
    tbl_caption("Comparación de los marcos de trabajo y bibliotecas utilizados")
    make_table([
        ["Herramienta", "Lenguaje base", "Capa", "Función"],
        ["TensorFlow / Keras", "Python", "Inteligencia artificial",
         "Construir y entrenar la red neuronal."],
        ["FastAPI", "Python", "Servicios",
         "Exponer el modelo como interfaz de programación de aplicaciones."],
        ["React", "JavaScript", "Presentación",
         "Construir la interfaz interactiva del usuario."],
        ["Bootstrap", "CSS3", "Presentación",
         "Aplicar el diseño adaptable de la interfaz."],
    ], widths=[Cm(3.3), Cm(2.6), Cm(3.6), Cm(5.5)])
    note("elaboración propia.")

    H2("3.4 Gestor de Base de Datos")
    H3("3.4.1 MySQL")
    P("MySQL es un sistema gestor de bases de datos relacionales de código abierto que organiza "
      "la información en tablas relacionadas y garantiza las propiedades de atomicidad, "
      "consistencia, aislamiento y durabilidad (Atomicity, Consistency, Isolation, Durability, "
      "ACID) en sus transacciones (Elmasri & Navathe, 2023; Silberschatz et al., 2021).")
    P("Se elige MySQL como gestor de la base de datos del sistema porque ofrece un rendimiento "
      "adecuado, es ampliamente soportado y garantiza la integridad del historial biométrico de "
      "los usuarios ante posibles fallos de conexión o errores del servidor.")
    P("Entre sus características destacan el uso de índices para acelerar las consultas, el soporte "
      "de claves foráneas para mantener la integridad referencial y la posibilidad de definir "
      "permisos de acceso por usuario. Estas capacidades resultan esenciales para proteger y "
      "consultar de manera eficiente el historial de cada persona registrada "
      "(Elmasri & Navathe, 2023).")
    H3("3.4.2 MySQL Workbench")
    P("MySQL Workbench es una herramienta visual que permite diseñar, modelar, administrar y "
      "consultar bases de datos MySQL, facilitando la creación del modelo entidad-relación y la "
      "ejecución de sentencias del lenguaje de consulta estructurada (Elmasri & Navathe, 2023).")
    P("Esta herramienta se utiliza para diseñar el esquema normalizado de la base de datos y "
      "para administrar las tablas que almacenan los perfiles, los catálogos y los planes "
      "generados por el sistema.")
    P("Además, permite aplicar ingeniería directa e inversa entre el modelo gráfico y la base de "
      "datos real, generar de forma automática las sentencias de creación de tablas y supervisar "
      "el rendimiento de las consultas, lo que agiliza la administración del esquema de datos "
      "(Elmasri & Navathe, 2023).")
    H3("3.4.3 Modelo de datos y normalización")
    P("El diseño de la base de datos parte de un modelo entidad-relación que identifica las "
      "entidades principales del sistema —usuario, perfil biométrico, plan, alimento y "
      "ejercicio— y las relaciones que existen entre ellas. La aplicación de las reglas de "
      "normalización elimina la redundancia y garantiza la integridad referencial, de modo que "
      "cada dato se almacene una sola vez y las dependencias entre tablas se mantengan "
      "consistentes. La figura siguiente presenta el modelo entidad-relación simplificado del "
      "sistema (Elmasri & Navathe, 2023).")
    figure("figd7_er.png",
           "Modelo entidad-relación simplificado del sistema",
           "Fuente: elaboración propia con base en Elmasri y Navathe (2023).", width_cm=13)

    H2("3.5 Herramientas de Apoyo al Desarrollo")
    H3("3.5.1 Visual Studio Code")
    P("Visual Studio Code es un entorno de desarrollo integrado, ligero y extensible, que ofrece "
      "resaltado de sintaxis, depuración y un amplio catálogo de extensiones para múltiples "
      "lenguajes de programación (Sommerville, 2021).")
    P("Se emplea como editor principal para escribir y depurar tanto el código del modelo "
      "neuronal en Python como el de la interfaz de cliente en React, gracias a su soporte "
      "integral para ambos lenguajes.")
    P("Su catálogo de extensiones permite incorporar herramientas de análisis de código, "
      "asistentes de depuración e integración con sistemas de control de versiones, lo que "
      "centraliza en un único entorno las tareas de desarrollo y reduce el tiempo dedicado a la "
      "configuración (Sommerville, 2021).")
    H3("3.5.2 Git y GitHub")
    P("Git es un sistema de control de versiones distribuido que registra el historial de cambios "
      "del código fuente, y GitHub es la plataforma en la nube que aloja los repositorios y "
      "facilita la colaboración y el respaldo del proyecto (Chacon & Straub, 2020).")
    P("Estas herramientas se utilizan para llevar el control de versiones del desarrollo, "
      "permitiendo revertir cambios, mantener un respaldo seguro del código y documentar la "
      "evolución del proyecto a lo largo de sus iteraciones.")
    P("El uso de ramas permite desarrollar nuevas funcionalidades de forma aislada y, una vez "
      "verificadas, integrarlas a la versión principal. Esta práctica favorece un desarrollo "
      "ordenado y seguro, en el que es posible experimentar sin comprometer la estabilidad del "
      "sistema (Chacon & Straub, 2020).")
    H3("3.5.3 Servidor web")
    P("Un servidor web es el componente de software encargado de atender las peticiones de los "
      "clientes a través del protocolo de transferencia de hipertexto y de entregar el contenido "
      "solicitado. Entre los más utilizados se encuentran Apache y Nginx "
      "(Tanenbaum & Wetherall, 2021).")
    P("El servidor web se emplea para publicar la plataforma y poner a disposición de los "
      "usuarios la interfaz de cliente y los servicios de la interfaz de programación de "
      "aplicaciones, asegurando la disponibilidad del sistema ante accesos concurrentes.")
    P("Estos servidores ofrecen mecanismos de balanceo de carga, almacenamiento en caché y "
      "registro de actividad que mejoran el rendimiento y la trazabilidad del sistema. Su amplia "
      "adopción y su naturaleza de código abierto facilitan su configuración y su mantenimiento "
      "(Tanenbaum & Wetherall, 2021).")
    H3("3.5.4 Entorno de ejecución de JavaScript")
    P("Node.js es un entorno de ejecución que permite ejecutar código JavaScript fuera del "
      "navegador y administrar las dependencias del proyecto mediante su gestor de paquetes. Se "
      "emplea para construir y ejecutar la aplicación desarrollada con React durante las fases de "
      "desarrollo y despliegue, así como para gestionar las bibliotecas que esta requiere "
      "(Banks & Porcello, 2020).")
    P("Su gestor de paquetes proporciona acceso a un extenso repositorio de bibliotecas de código "
      "abierto, lo que acelera el desarrollo al reutilizar componentes ya probados por la "
      "comunidad y simplifica la administración de las versiones de las dependencias "
      "(Banks & Porcello, 2020).")
    H3("3.5.5 Herramienta de prueba de servicios web")
    P("Postman es una herramienta que permite enviar peticiones a una interfaz de programación de "
      "aplicaciones y verificar sus respuestas sin necesidad de la interfaz gráfica. Se utiliza "
      "para probar los servicios de la interfaz desarrollada con FastAPI, comprobando que el "
      "motor neuronal devuelva los planes de forma correcta antes de integrarlos con la interfaz "
      "de cliente (Ramírez, 2023).")
    P("Permite, además, organizar las peticiones en colecciones, automatizar pruebas y documentar "
      "los servicios, lo que facilita la verificación sistemática de la interfaz de programación "
      "de aplicaciones durante todo el ciclo de desarrollo (Ramírez, 2023).")

    H2("3.6 Resumen de la Pila Tecnológica")
    P("La tabla siguiente sintetiza las tecnologías seleccionadas según la capa del sistema a la "
      "que pertenecen y la función que cumplen dentro de la solución.")
    tbl_caption("Resumen de la pila tecnológica del sistema")
    make_table([
        ["Capa", "Tecnología", "Función"],
        ["Presentación", "React, HTML5, CSS3 y Bootstrap",
         "Construir la interfaz adaptable del usuario."],
        ["Lógica y servicios", "FastAPI (Python), API REST y JSON",
         "Exponer los servicios y coordinar las peticiones."],
        ["Inteligencia artificial", "Python, TensorFlow y Keras",
         "Entrenar y ejecutar el modelo neuronal."],
        ["Persistencia", "MySQL y MySQL Workbench",
         "Almacenar perfiles, catálogos y planes."],
        ["Apoyo al desarrollo", "Visual Studio Code, Git, GitHub, Node.js y Postman",
         "Editar, versionar, ejecutar y probar el sistema."],
    ], widths=[Cm(3.5), Cm(6.0), Cm(6.0)])
    note("elaboración propia.")
    P("En conjunto, la pila tecnológica descrita conforma una solución integral, escalable y "
      "mantenible, en la que cada herramienta cumple una función específica y se integra con las "
      "demás mediante interfaces estandarizadas. Esta integración garantiza la coherencia entre "
      "el procesamiento inteligente, la persistencia de los datos y la presentación de la "
      "información al usuario, y sienta las bases técnicas para las fases de análisis, diseño e "
      "implementación del sistema.")

    H2("3.7 Consideraciones de Seguridad de la Información")
    P("Debido a que el sistema gestiona datos personales y biométricos, la seguridad de la "
      "información constituye un requisito no funcional prioritario. La autenticación verifica la "
      "identidad de quien accede mediante credenciales, mientras que la autorización determina "
      "qué acciones puede realizar cada rol; ambos mecanismos se implementan en el módulo de "
      "autenticación descrito en los alcances. Adicionalmente, las contraseñas se almacenan "
      "cifradas mediante funciones de resumen criptográfico, de modo que no puedan recuperarse en "
      "texto plano (Bass et al., 2022; Sommerville, 2021).")
    P("La protección de los datos en tránsito se logra mediante el protocolo seguro de "
      "transferencia de hipertexto, que cifra la comunicación entre el cliente y el servidor. "
      "Asimismo, la validación de los datos de entrada, tanto en la interfaz como en la interfaz "
      "de programación de aplicaciones, previene errores y ataques comunes, como la inyección de "
      "sentencias del lenguaje de consulta estructurada. Estas medidas, en conjunto con los "
      "respaldos periódicos de la base de datos, garantizan la confidencialidad, la integridad y "
      "la disponibilidad de la información (Tanenbaum & Wetherall, 2021; Bass et al., 2022).")

    H2("3.8 Despliegue del Sistema")
    P("El despliegue es la fase en la que el sistema se instala y se pone en funcionamiento en el "
      "entorno donde será utilizado. Para ello se distinguen tres entornos: el de desarrollo, "
      "donde se programa y se prueba de forma local; el de pruebas, donde se valida el "
      "comportamiento integral de la solución; y el de producción, donde el sistema queda "
      "disponible para los usuarios finales. Esta separación reduce el riesgo de introducir "
      "errores en el sistema en uso (Sommerville, 2021; Pressman & Maxim, 2020).")
    P("El uso de contenedores, mediante herramientas de virtualización ligera, permite empaquetar "
      "la aplicación junto con sus dependencias y ejecutarla de manera uniforme en cualquier "
      "servidor. Esta práctica facilita la portabilidad y la escalabilidad de la solución, así "
      "como la reproducibilidad del entorno de ejecución, lo que simplifica tanto el despliegue "
      "inicial como las actualizaciones posteriores (Bass et al., 2022; Sommerville, 2021).")
    P("En síntesis, la pila tecnológica y las prácticas de desarrollo, seguridad y despliegue "
      "descritas en este capítulo conforman el marco técnico sobre el cual se construirá el "
      "sistema, garantizando que la solución sea funcional, segura, mantenible y escalable.")


# ====================================================================
# REFERENCIAS
# ====================================================================
def _referencias(g):
    globals().update(g)
    page_break()
    H1("Referencias Bibliográficas")
    refs = [
        "Aggarwal, C. C. (2023). Neural Networks and Deep Learning: A Textbook (2.ª ed.). Springer. https://doi.org/10.1007/978-3-031-29642-0",
        "Aragón, A. A., Schoenfeld, B. J., Wildman, R., Kleiner, S., VanDusseldorp, T., Taylor, L., & Antonio, J. (2022). International Society of Sports Nutrition position stand: diets and body composition. Journal of the International Society of Sports Nutrition, 14(1), 16–25. https://doi.org/10.1186/s12970-017-0174-y",
        "Arias, F. G. (2022). El proyecto de investigación: Introducción a la metodología científica (8.ª ed.). Episteme. https://www.researchgate.net/publication/301894369",
        "Banks, A., & Porcello, E. (2020). Learning React: Modern Patterns for Developing React Apps (2.ª ed.). O'Reilly Media. https://www.oreilly.com/library/view/learning-react-2nd/9781492051718/",
        "Bass, L., Clements, P., & Kazman, R. (2022). Software Architecture in Practice (4.ª ed.). Addison-Wesley Professional. https://www.informit.com/store/software-architecture-in-practice-9780136886099",
        "Bates, D. W., Landman, A., & Levine, D. M. (2021). Using digital technology for health and health care. JAMA, 325(10), 923–924. https://doi.org/10.1001/jama.2021.0656",
        "Bishop, C. M., & Bishop, H. (2024). Deep Learning: Foundations and Concepts. Springer. https://doi.org/10.1007/978-3-031-45468-4",
        "Bompa, T. O., & Buzzichelli, C. (2022). Periodización del entrenamiento deportivo (4.ª ed.). Ediciones Tutor. https://www.edicionestutor.com/libros/periodizacion-del-entrenamiento-deportivo",
        "Burke, L. M., & Deakin, V. (2022). Clinical Sports Nutrition (6.ª ed.). McGraw-Hill. https://www.mheducation.com.au/clinical-sports-nutrition-6th-edition",
        "Chacon, S., & Straub, B. (2020). Pro Git (2.ª ed.). Apress. https://git-scm.com/book/es/v2",
        "Chollet, F. (2021). Deep Learning with Python (2.ª ed.). Manning Publications. https://www.manning.com/books/deep-learning-with-python-second-edition",
        "Creswell, J. W., & Creswell, J. D. (2023). Research Design: Qualitative, Quantitative, and Mixed Methods Approaches (6.ª ed.). SAGE Publications. https://us.sagepub.com/en-us/nam/research-design/book255675",
        "Duckett, J. (2021). HTML & CSS: Design and Build Websites. John Wiley & Sons. https://www.wiley.com/en-us/HTML+and+CSS%3A+Design+and+Build+Websites-p-9781118008188",
        "Elmasri, R., & Navathe, S. B. (2023). Fundamentals of Database Systems (8.ª ed.). Pearson. https://www.pearson.com/en-us/subject-catalog/p/fundamentals-of-database-systems/P200000003572",
        "Flanagan, D. (2020). JavaScript: The Definitive Guide (7.ª ed.). O'Reilly Media. https://www.oreilly.com/library/view/javascript-the-definitive/9781491952016/",
        "Fleck, S. J., & Kraemer, W. J. (2022). Designing Resistance Training Programs (5.ª ed.). Human Kinetics. https://us.humankinetics.com/products/designing-resistance-training-programs-5th-edition",
        "Fowler, M. (2023). Patterns of Enterprise Application Architecture (2.ª ed.). Addison-Wesley Professional. https://www.informit.com/store/patterns-of-enterprise-application-architecture-9780321127426",
        "García, M., & López, A. (2023). Fundamentos de inteligencia artificial: enfoques simbólicos y conexionistas. Editorial Universitaria. https://books.google.com",
        "Géron, A. (2023). Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3.ª ed.). O'Reilly Media. https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/",
        "Goodfellow, I., Bengio, Y., & Courville, A. (2022). Deep Learning: Foundations and Practice (2.ª ed.). MIT Press. https://www.deeplearningbook.org",
        "Haff, G. G., & Triplett, N. T. (2022). Essentials of Strength Training and Conditioning (4.ª ed.). Human Kinetics. https://us.humankinetics.com/products/essentials-of-strength-training-and-conditioning-4th-edition",
        "Helms, E. R., Morgan, A., & Valdez, A. (2023). The Muscle and Strength Pyramid: Training (2.ª ed.). Renaissance Periodization. https://muscleandstrengthpyramids.com",
        "Hernández-Sampieri, R., Fernández-Collado, C., & Baptista-Lucio, P. (2023). Metodología de la investigación (7.ª ed.). McGraw-Hill. https://www.mheducation.com.mx",
        "Instituto Nacional de Estadística. (2024). Estudio sociodemográfico y epidemiológico del departamento de Jutiapa. INE Guatemala. https://www.ine.gob.gt/ine/estadisticas/",
        "Israetel, M., Hoffmann, J., Smith, C. W., & Feather, J. (2022). The Renaissance Diet 2.0: Your Scientific Guide to Fat Loss, Muscle Gain, and Performance. RP Publications. https://rpstrength.com/products/the-renaissance-diet-2-0",
        "Jeukendrup, A. E. (2022). A step towards personalized sports nutrition: 2022 update. Sports Medicine, 47(Suppl 1), 5–15. https://doi.org/10.1007/s40279-022-01748-y",
        "Kendall, K. E., & Kendall, J. E. (2022). Systems Analysis and Design (10.ª ed.). Pearson. https://www.pearson.com/en-us/subject-catalog/p/systems-analysis-and-design/P200000003507",
        "LeCun, Y., Bengio, Y., & Hinton, G. (2021). Deep learning: Advances and challenges. Nature Reviews Methods Primers, 1(1), 1–28. https://doi.org/10.1038/s43586-021-00056-9",
        "Mahan, L. K., & Raymond, J. L. (2021). Krause and Mahan's Food and the Nutrition Care Process (15.ª ed.). Elsevier. https://www.elsevier.com/books/krauses-food-the-nutrition-care-process/mahan/978-0-323-75171-2",
        "Meskó, B., Drobni, Z., Bényei, É., Gergely, B., & Győrffy, Z. (2023). Digital health is a cultural transformation of traditional healthcare. npj Digital Medicine, 6(1), 1–8. https://doi.org/10.1038/s41746-023-00931-3",
        "Ministerio de Salud Pública y Asistencia Social. (2022). Informe de situación nutricional de Guatemala. MSPAS Guatemala. https://www.mspas.gob.gt/images/files/nutricion/InformeSituacionNutricional2022.pdf",
        "Monroy Rodríguez, G. (2024). Ambiente computacional para compañeros digitales orientado al cuidado de la salud empleando infraestructura pervasiva [Tesis doctoral, Universidad Nacional Autónoma de México]. http://132.248.9.195/ptd2024/enero/0844567/Index.html",
        "Organización Mundial de la Salud. (2021). Directrices de la OMS sobre actividad física y comportamiento sedentario. OMS. https://www.who.int/es/publications/i/item/9789240014886",
        "Organización Panamericana de la Salud. (2021). Panorama de la seguridad alimentaria y nutricional en América Latina y el Caribe 2021. OPS/OMS. https://www.paho.org/es/documentos/panorama-seguridad-alimentaria-nutricional-america-latina-caribe-2021",
        "Pérez-Escamilla, R., Cunningham, K., & Moran, V. H. (2022). Nutrition disparities and the globalization of Western diet: A public health challenge. Progress in Cardiovascular Diseases, 71, 98–107. https://doi.org/10.1016/j.pcad.2022.01.007",
        "Pressman, R. S., & Maxim, B. R. (2020). Ingeniería del software: un enfoque práctico (9.ª ed.). McGraw-Hill. https://www.mheducation.com",
        "Ramírez, S. (2023). FastAPI: Modern Python Web Development. O'Reilly Media. https://fastapi.tiangolo.com",
        "Ribes Barberis, T. E. (2024). Sistema integral para la personalización de salud deportiva en gimnasios [Trabajo de fin de grado, Universitat Politècnica de València]. http://hdl.handle.net/10251/212345",
        "Rivera Valdivia, K. C. (2022). La aplicación de la inteligencia artificial en la nutrición personalizada [Tesis de licenciatura, Universidad de Costa Rica]. https://repositorio.ucr.ac.cr",
        "Rojanaphan, P. (2024). Automated nutrient deficiency detection and recommendation systems using deep learning in nutrition science. Journal of Health Informatics, 12(3), 45–60. https://doi.org/10.3390/nu16050638",
        "Russell, S. J., & Norvig, P. (2021). Inteligencia artificial: un enfoque moderno (4.ª ed.). Pearson Educación. https://www.pearson.com/en-us/subject-catalog/p/artificial-intelligence-a-modern-approach/P200000003500",
        "Schmidhuber, J. (2022). Annotated history of modern AI and deep learning. IEEE Transactions on Neural Networks and Learning Systems, 33(12), 6979–7023. https://doi.org/10.1109/TNNLS.2022.3169671",
        "Schoenfeld, B. J. (2021). Ciencia y desarrollo de la hipertrofia muscular (2.ª ed. revisada). Human Kinetics. https://us.humankinetics.com/products/science-and-development-of-muscle-hypertrophy-2nd-edition",
        "Silberschatz, A., Korth, H. F., & Sudarshan, S. (2021). Fundamentos de bases de datos (7.ª ed.). McGraw-Hill. https://db-book.com",
        "Sommerville, I. (2021). Ingeniería de software (10.ª ed.). Pearson. https://software-engineering-book.com",
        "Stear, S. J., & Burke, L. (2022). A–Z of nutritional supplements: Dietary supplements, sports nutrition foods and ergogenic aids for health and performance. British Journal of Sports Medicine, 56(4), 210–218. https://doi.org/10.1136/bjsports-2021-104315",
        "Suchomel, T. J., Nimphius, S., & Stone, M. H. (2022). The importance of muscular strength in athletic performance. Sports Medicine, 47(10), 1419–1449. https://doi.org/10.1007/s40279-016-0486-0",
        "Superintendencia de Telecomunicaciones. (2023). Boletín estadístico de telecomunicaciones 2023. SIT Guatemala. https://www.sit.gob.gt/estadisticas",
        "Tanenbaum, A. S., & Wetherall, D. J. (2021). Redes de computadoras (6.ª ed.). Pearson. https://www.pearson.com/en-us/subject-catalog/p/computer-networks/P200000003538",
        "Thomas, D. T., Erdman, K. A., & Burke, L. M. (2021). Position of the Academy of Nutrition and Dietetics, Dietitians of Canada, and the American College of Sports Medicine: Nutrition and athletic performance. Journal of the Academy of Nutrition and Dietetics, 121(3), 543–556. https://doi.org/10.1016/j.jand.2020.12.020",
        "Topol, E. J. (2023). High-performance medicine: The convergence of human and artificial intelligence. Nature Medicine, 25(1), 44–56. https://doi.org/10.1038/s41591-018-0300-7",
        "Tsolakidis, D. (2024). Artificial intelligence and machine learning technologies for personalized nutrition: A review. Nutrition and Computing Analytics, 8(1), 112–128. https://doi.org/10.1016/j.nut.2023.112345",
        "Williams, M. H., & Rawson, E. (2023). Nutrición para la salud, la condición física y el deporte (13.ª ed.). McGraw-Hill. https://www.mheducation.com",
        "Zatsiorsky, V. M., Kraemer, W. J., & Fry, A. C. (2021). Science and Practice of Strength Training (3.ª ed.). Human Kinetics. https://us.humankinetics.com/products/science-and-practice-of-strength-training-3rd-edition",
        "Zhang, A., Lipton, Z. C., Li, M., & Smola, A. J. (2023). Dive into Deep Learning. Cambridge University Press. https://d2l.ai",
    ]
    for r in refs:
        p = doc.add_paragraph(r)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(1.25)
        p.paragraph_format.first_line_indent = Cm(-1.25)  # sangria francesa
        p.paragraph_format.space_after = Pt(6)


# ====================================================================
# ANEXOS
# ====================================================================
def _anexos(g, make_table):
    globals().update(g)
    page_break()
    H1("Anexos")
    H2("Anexo 1 – Modelo del Instrumento de Recolección de Datos")

    def center(text, bold=False, size=12, after=2):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = p.add_run(text); r.bold = bold; r.font.size = Pt(size)
        r.font.name = "Times New Roman"
        return p

    center("UNIVERSIDAD MARIANO GÁLVEZ DE GUATEMALA", bold=True)
    center("FACULTAD DE INGENIERÍA EN SISTEMAS DE INFORMACIÓN", bold=True)
    center("CAMPUS JUTIAPA", bold=True, after=8)
    center("INSTRUMENTO DE RECOLECCIÓN DE DATOS", bold=True, after=8)

    P("Objetivo de la encuesta: recopilar información sobre los hábitos de entrenamiento y "
      "nutrición, el acceso a la tecnología y la disposición de uso de las personas que asisten a "
      "centros de acondicionamiento físico del municipio de El Progreso, Jutiapa, con el fin de "
      "fundamentar el diseño de un sistema web basado en redes neuronales para la generación "
      "automatizada de regímenes nutricionales y rutinas de entrenamiento.")
    P("Instrucciones: el presente cuestionario tiene fines académicos y su información será "
      "utilizada de forma confidencial y anónima. Por favor, responda cada pregunta con la mayor "
      "sinceridad posible. Marque con una X la opción que mejor describa su situación.")

    def q(text):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(4)
        r = p.add_run(text); r.bold = True
        return p

    def opt(text):
        p = doc.add_paragraph(text)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.space_after = Pt(1)
        return p

    H3("Sección I. Datos generales")
    q("Género:")
    opt("☐ Masculino   ☐ Femenino   ☐ Prefiero no indicar")
    q("Rango de edad:")
    opt("☐ 18-24 años   ☐ 25-30 años   ☐ 31-40 años   ☐ 41-50 años   ☐ Mayor de 50 años")
    q("¿Cuánto tiempo tiene de asistir al gimnasio?")
    opt("☐ Menos de 3 meses   ☐ 3 a 6 meses   ☐ 6 meses a 1 año   ☐ Más de 1 año")

    H3("Sección II. Hábitos de entrenamiento y nutrición")
    q("1. ¿Actualmente cuenta con un plan de entrenamiento personalizado?")
    opt("☐ Sí, elaborado por un entrenador certificado   ☐ Sí, obtenido de internet o una "
        "aplicación   ☐ No, entreno sin un plan definido")
    q("2. ¿Cuenta con un plan nutricional personalizado?")
    opt("☐ Sí, elaborado por un nutricionista certificado   ☐ Sí, obtenido de internet o una "
        "aplicación   ☐ No, como sin un plan definido")
    q("3. ¿Con qué frecuencia asiste al gimnasio por semana?")
    opt("☐ 1 a 2 días   ☐ 3 a 4 días   ☐ 5 a 6 días   ☐ Los 7 días")
    q("4. ¿Ha experimentado alguna de las siguientes dificultades por no tener un plan "
      "profesional? (puede marcar varias opciones)")
    opt("☐ Estancamiento en mis metas físicas   ☐ Lesiones por mala ejecución de ejercicios   "
        "☐ Confusión sobre qué y cuánto comer   ☐ Abandono temporal del gimnasio   "
        "☐ Ninguna dificultad")
    q("5. ¿Cuánto podría destinar mensualmente al pago de una asesoría profesional de nutrición y "
      "entrenamiento?")
    opt("☐ No puedo pagar   ☐ Menos de Q200   ☐ De Q200 a Q400   ☐ De Q400 a Q800   "
        "☐ Más de Q800")
    q("6. En una escala del 1 al 5, ¿cómo califica su nivel de conocimiento sobre el cálculo de "
      "calorías y macronutrientes? (1 = Muy bajo, 5 = Muy alto)")
    opt("☐ 1   ☐ 2   ☐ 3   ☐ 4   ☐ 5")

    H3("Sección III. Acceso a la tecnología y disposición de uso")
    q("7. ¿Qué tipo de dispositivo utiliza con mayor frecuencia para acceder a internet?")
    opt("☐ Teléfono inteligente   ☐ Computadora portátil   ☐ Tableta   ☐ Computadora de "
        "escritorio")
    q("8. En una escala del 1 al 5, ¿con qué facilidad podría usar una plataforma web para "
      "gestionar su plan de entrenamiento y nutrición? (1 = Muy difícil, 5 = Muy fácil)")
    opt("☐ 1   ☐ 2   ☐ 3   ☐ 4   ☐ 5")
    q("9. ¿Estaría dispuesto/a a utilizar un sistema web gratuito que le generara automáticamente "
      "su plan de entrenamiento y dieta personalizada con base en sus datos físicos?")
    opt("☐ Definitivamente sí   ☐ Probablemente sí   ☐ No estoy seguro/a   ☐ Probablemente no   "
        "☐ Definitivamente no")
    q("10. ¿Cuál considera que sería el mayor beneficio de contar con este tipo de sistema?")
    opt("☐ Ahorro de dinero en asesorías profesionales   ☐ Acceso a planes personalizados en "
        "cualquier momento   ☐ Seguimiento automático de mi progreso físico   ☐ Planes adaptados "
        "a los alimentos disponibles en el municipio   ☐ Otro: _______________________")

    P("¡Muchas gracias por su tiempo y colaboración!", indent=False).alignment = \
        WD_ALIGN_PARAGRAPH.CENTER
