# Ejemplos de Flujos de Trabajo del Agente

Este documento describe casos de uso reales paso a paso, mostrando cómo el agente procesa distintos tipos de consultas y qué decisiones toma en cada etapa.

---

## Caso 1: Consulta Informativa Simple

### Contexto
Cliente B2B que necesita saber el tiempo de tránsito de una ruta frecuente.

### Consulta del cliente
> "¿Cuánto demora un envío de Santiago a Valparaíso?"

### Paso a paso

1. **Recepción**: El orquestador recibe la consulta.
2. **Recuperación de contexto**: La memoria de largo plazo no encuentra interacciones previas relevantes para este cliente.
3. **Clasificación (Tool Razonamiento)**:
   - Intención: `informacional`
   - Complejidad: `simple`
   - Requiere escalamiento: `false`
   - Respuesta directa permitida: `true`
4. **Planificación**: El planificador genera 2 pasos:
   - Paso 1: Consultar documentos sobre "tiempo tránsito Santiago Valparaíso".
   - Paso 2: Redactar respuesta.
5. **Ejecución RAG**: La tool de consulta recupera del `tarifario_2024.txt`: "Ruta Santiago-Valparaíso... Tiempo estimado de tránsito: 1.5 a 2.5 horas".
6. **Redacción**: La tool de redacción transforma el dato técnico en un mensaje cordial:
   > "Estimado cliente, el tiempo de tránsito estimado para la ruta Santiago-Valparaíso es de 1.5 a 2.5 horas. Frecuencia diaria. ¿Puedo ayudarle con algo más?"
7. **Validación**: El razonador valida que no hay garantías de disponibilidad ni cotizaciones vinculantes. Respuesta válida.
8. **Almacenamiento**: La interacción se guarda en memoria corto plazo y un resumen en memoria largo plazo.

### Resultado
- **Acción**: `responder`
- **Fuente**: `tarifario_2024.txt`
- **Escalamiento**: No requerido.

---

## Caso 2: Consulta Compleja Multipaso

### Contexto
Cliente que necesita información combinada de tarifa, tiempo y frecuencia para una ruta larga.

### Consulta del cliente
> "Necesito enviar carga a Puerto Montt. ¿Cuánto cuesta por tonelada, cuánto demora y qué días operan?"

### Paso a paso

1. **Recepción**: Orquestador recibe consulta.
2. **Clasificación (Tool Razonamiento)**:
   - Intención: `informacional`
   - Complejidad: `compleja` (3 datos entrelazados: tarifa, tiempo, frecuencia)
   - Requiere escalamiento: `false`
3. **Planificación**: Plan de 4 pasos:
   - Paso 1: Consultar tarifa Santiago-Puerto Montt.
   - Paso 2: Consultar tiempo de tránsito Santiago-Puerto Montt.
   - Paso 3: Consultar frecuencia de servicio.
   - Paso 4: Sintetizar y redactar respuesta única.
4. **Ejecución paso 1**: RAG recupera tarifa ($45.000 CLP/ton) del tarifario.
5. **Ejecución paso 2**: RAG recupera tiempo (18-22 horas).
6. **Ejecución paso 3**: RAG recupera frecuencia (Lunes, Miércoles, Viernes).
7. **Ejecución paso 4**: La tool de redacción sintetiza los 3 datos en un solo mensaje estructurado, citando el tarifario como fuente.
8. **Validación**: Se verifica que no se menciona "garantía de cupo" ni "precio final". Válida.
9. **Almacenamiento**: Interacción guardada. Memoria largo plazo registra preferencia por ruta Santiago-Puerto Montt.

### Resultado
- **Acción**: `responder`
- **Fuentes**: `tarifario_2024.txt`
- **Plan ejecutado**: 4 pasos

---

## Caso 3: Escalamiento a Ejecutivo por Cotización Formal

### Contexto
Cliente con volumen mayor al habitual solicita precio vinculante.

### Consulta del cliente
> "Necesito una cotización formal vinculante para transportar 200 toneladas mensuales desde Santiago a Concepción."

### Paso a paso

1. **Recepción**: Orquestador recibe consulta.
2. **Clasificación (Tool Razonamiento)**:
   - Intención: `cotizacion`
   - Complejidad: `compleja`
   - Requiere escalamiento: `true`
   - Motivo: "Solicitud de cotización formal con volumen recurrente mayor a 100 toneladas mensuales. Requiere ejecutivo de cuentas según protocolo."
   - Respuesta directa permitida: `false`
3. **Planificación**: El planificador no genera plan de ejecución porque la decisión del razonador es de escalamiento.
4. **Respuesta de escalamiento**: El orquestador genera un mensaje cordial explicando que un ejecutivo se contactará dentro de las primeras 4 horas del siguiente día hábil, indicando horarios de atención.
5. **Almacenamiento**: Se registra la intención de cotización en memoria largo plazo para que el ejecutivo tenga contexto previo al contactar al cliente.

### Resultado
- **Acción**: `escalar`
- **Motivo**: Cotización formal con volumen mayor a 100 toneladas/mes
- **Respuesta**: Mensaje de escalamiento con horarios de atención.

---

## Caso 4: Rechazo de Carga Peligrosa por Documentación Incompleta

### Contexto
Cliente intenta transportar solventes sin tener la hoja de seguridad.

### Consulta del cliente
> "Quiero transportar solventes industriales pero no tengo la hoja de seguridad. ¿Puedo enviarlos igual?"

### Paso a paso

1. **Recepción**: Orquestador recibe consulta.
2. **Clasificación (Tool Razonamiento)**:
   - Intención: `peligrosa`
   - Complejidad: `simple`
   - Requiere escalamiento: `true`
   - Motivo: "Carga peligrosa clase 3 (líquidos inflamables) sin MSDS/SDS. Transporte prohibido sin documentación completa según normativas ADR y protocolo de CargaMax."
   - Respuesta directa permitida: `false`
3. **Respuesta**: El orquestador entrega una respuesta que:
   - Explica claramente que el transporte es rechazado por normativa.
   - Enumera los documentos requeridos (MSDS, declaración jurada, etiquetado ADR).
   - Informa que puede contactar a un ejecutivo para orientación pero que la carga no será aceptada sin papeles.
4. **Almacenamiento**: Se registra el rechazo normativo en memoria para futuras interacciones.

### Resultado
- **Acción**: `escalar`
- **Motivo**: Carga peligrosa sin documentación obligatoria
- **Respuesta**: Rechazo normativo con instructivo de documentación requerida.

---

## Caso 5: Memoria Largo Plazo entre Sesiones

### Contexto
Cliente que ya había consultado por una ruta en una sesión anterior.

### Sesión anterior (almacenada en memoria)
> Cliente: "¿Cuánto cuesta el envío express a Valparaíso?"
> Agente: "Tarifa base $12.000/ton + recargo 25% express = $15.000/ton aprox."

### Sesión actual
> Cliente: "¿Recuerdan que pregunté por el express a Valparaíso? ¿Cuánto era exactamente el recargo?"

### Paso a paso

1. **Recepción**: Orquestador recibe consulta.
2. **Recuperación de contexto**: La memoria de largo plazo realiza una búsqueda semántica con el query "express Valparaíso recargo" y recupera el resumen de la interacción anterior.
3. **Clasificación**: Intención `informacional`, complejidad `simple`.
4. **Planificación**: 2 pasos (consultar para confirmar + redactar).
5. **Ejecución**: La tool de consulta confirma el recargo del 25% en el tarifario. La memoria larga aporta contexto de que el cliente ya conoce la ruta.
6. **Redacción**: La respuesta es más directa porque el agente "sabe" que no es la primera vez:
   > "Sí, claro. En su consulta anterior sobre la ruta Santiago-Valparaíso, le indicamos que el servicio express tiene un recargo del 25% sobre la tarifa base. ¿Necesita agendar un envío?"
7. **Validación y almacenamiento**: Válida. Se actualiza memoria.

### Resultado
- **Acción**: `responder`
- **Personalización**: Respuesta adaptada al historial del cliente.
- **Valor agregado**: Evita repetir información ya entregada, mejorando la experiencia B2B.

