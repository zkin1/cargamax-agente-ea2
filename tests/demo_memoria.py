"""
Demo 2: Memoria de Corto y Largo Plazo

Muestra cómo el agente mantiene coherencia en una conversación
prolongada (memoria corto plazo) y recupera contexto de sesiones
anteriores (memoria largo plazo).
"""

from agente_cargamax.core.agent import AgenteCargaMax

def demo_memoria():
    print("=" * 70)
    print("  DEMO 2: MEMORIA DE CORTO Y LARGO PLAZO")
    print("=" * 70)
    
    cliente_id = "cliente_memoria_demo"
    agente = AgenteCargaMax(cliente_id=cliente_id)
    
    # Simulamos una conversación larga para probar memoria corto plazo
    print("\n[MEMORIA DE CORTO PLAZO - Conversación actual]")
    print("-" * 70)
    
    intercambios = [
        "¿Cuánto cuesta enviar carga a Valparaíso?",
        "Y si necesito servicio express, ¿cuánto sería el recargo?",
        "¿Me pueden dar una cotización formal para 50 toneladas mensuales?",
        "Prefiero que me contacte un ejecutivo entonces.",
        "¿Cuál es el horario de atención?"
    ]
    
    for i, consulta in enumerate(intercambios, 1):
        print(f"\n   Turno {i}:")
        print(f"   Cliente: \"{consulta}\"")
        resultado = agente.procesar_consulta(consulta)
        print(f"   Agente:  \"{resultado['respuesta_final'][:120]}...\"" if len(resultado['respuesta_final']) > 120 else f"   Agente:  \"{resultado['respuesta_final']}\"")
        print(f"   [Acción: {resultado['accion']} | Historial: {len(agente.memoria_corto.obtener_historial())} mensajes]")
    
    # Mostrar historial acumulado
    print(f"\n   Historial completo almacenado en memoria corto plazo:")
    print(f"   {agente.memoria_corto.obtener_historial_texto()[:500]}...")
    
    # Ahora simulamos un nuevo agente para el mismo cliente (memoria largo plazo)
    print("\n\n[MEMORIA DE LARGO PLAZO - Nueva sesión, mismo cliente]")
    print("-" * 70)
    
    agente_nuevo = AgenteCargaMax(cliente_id=cliente_id)
    consulta_recurrente = "¿Recuerdan que hablé de un envío a Valparaíso con express? ¿Cuál era el recargo?"
    
    print(f"\n   Cliente (nueva sesión): \"{consulta_recurrente}\"")
    resultado = agente_nuevo.procesar_consulta(consulta_recurrente)
    print(f"\n   Contexto recuperado de memoria semántica:")
    print(f"   {agente_nuevo.memoria_largo.obtener_contexto_texto(consulta_recurrente, cliente_id)[:400]}...")
    
    print("\n" + "=" * 70)
    print("  DEMO 2 FINALIZADA")
    print("=" * 70)

if __name__ == "__main__":
    demo_memoria()

