"""
Demo 3: Toma de Decisiones Adaptativas

Muestra cómo el agente ajusta su comportamiento según la intención,
la complejidad y las condiciones de la consulta (escalamiento,
validación de guardrails, planificación dinámica).
"""

from agente_cargamax.core.agent import AgenteCargaMax

def demo_decisiones():
    print("=" * 70)
    print("  DEMO 3: TOMA DE DECISIONES ADAPTATIVAS")
    print("=" * 70)
    
    escenarios = [
        {
            "nombre": "Consulta informativa simple",
            "consulta": "¿Cuál es el tiempo de tránsito entre Santiago y Concepción?",
            "descripcion": "Una sola pregunta directa resoluble con un documento."
        },
        {
            "nombre": "Consulta compleja multipaso",
            "consulta": "Necesito enviar carga a Puerto Montt. ¿Cuánto cuesta, cuánto demora y qué días operan?",
            "descripcion": "Requiere síntesis de múltiples datos: tarifa, tiempo, frecuencia."
        },
        {
            "nombre": "Solicitud que requiere escalamiento",
            "consulta": "Necesito una cotización formal vinculante para 500 toneladas mensuales en ruta Santiago-Concepción.",
            "descripcion": "Volumen mayor a lo habitual y solicitud de cotización vinculante."
        },
        {
            "nombre": "Reclamo formal",
            "consulta": "Mi carga llegó dañada y quiero presentar un reclamo formal por el seguro.",
            "descripcion": "Requiere atención de ejecutivo humano por protocolo de reclamos."
        },
        {
            "nombre": "Carga peligrosa sin documentación",
            "consulta": "Quiero transportar solventes industriales pero no tengo la hoja de seguridad.",
            "descripcion": "Carga peligrosa con documentación incompleta: rechazo normativo."
        }
    ]
    
    for i, escenario in enumerate(escenarios, 1):
        print(f"\n{'-' * 70}")
        print(f"  ESCENARIO {i}: {escenario['nombre'].upper()}")
        print(f"  {escenario['descripcion']}")
        print("-" * 70)
        
        agente = AgenteCargaMax(cliente_id=f"demo_decision_{i}")
        resultado = agente.procesar_consulta(escenario['consulta'])
        
        print(f"\n  [Consulta] \"{escenario['consulta']}\"")
        print(f"\n  [Decisión del agente]")
        
        if 'decision' in resultado['metadata']:
            decision = resultado['metadata']['decision']
            print(f"     - Intención detectada: {decision.get('intencion', 'N/A')}")
            print(f"     - Complejidad: {decision.get('complejidad', 'N/A')}")
            print(f"     - Requiere escalamiento: {'Sí' if decision.get('requiere_escalamiento') else 'No'}")
            if decision.get('requiere_escalamiento'):
                print(f"     - Motivo: {decision.get('motivo_escalamiento', 'N/A')}")
        
        print(f"\n  [Acción final] {resultado['accion'].upper()}")
        print(f"\n  [Respuesta]\n{resultado['respuesta_final']}")
    
    print("\n" + "=" * 70)
    print("  DEMO 3 FINALIZADA")
    print("=" * 70)

if __name__ == "__main__":
    demo_decisiones()

