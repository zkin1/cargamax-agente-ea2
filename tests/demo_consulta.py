"""
Demo 1: Consulta Simple vs. Consulta Compleja con RAG

Muestra cómo el agente consulta documentos internos de CargaMax
y redacta respuestas diferenciadas según la complejidad.
"""

from agente_cargamax.core.agent import AgenteCargaMax

def demo_consulta():
    print("=" * 70)
    print("  DEMO 1: CONSULTA SIMPLE Y CONSULTA COMPLEJA (RAG)")
    print("=" * 70)
    
    agente = AgenteCargaMax(cliente_id="demo_consulta")
    
    # Consulta simple: una sola pregunta directa
    consulta_simple = "¿Cuál es el tiempo de tránsito entre Santiago y Valparaíso?"
    print(f"\n[CONSULTA SIMPLE]")
    print(f"   Cliente: \"{consulta_simple}\"")
    resultado = agente.procesar_consulta(consulta_simple)
    print(f"\n   Respuesta:\n{resultado['respuesta_final']}")
    print(f"\n   Metadata: {resultado['metadata']}")
    
    # Consulta compleja: múltiples aspectos entrelazados
    consulta_compleja = (
        "Necesito enviar carga desde Santiago a Puerto Montt. "
        "¿Cuánto cuesta por tonelada, cuánto demora y qué días hay servicio?"
    )
    print(f"\n\n[CONSULTA COMPLEJA]")
    print(f"   Cliente: \"{consulta_compleja}\"")
    resultado2 = agente.procesar_consulta(consulta_compleja)
    print(f"\n   Respuesta:\n{resultado2['respuesta_final']}")
    print(f"\n   Plan ejecutado: {resultado2['metadata'].get('plan', [])}")
    
    # Consulta con contexto de carga peligrosa (debe escalar o responder según normativa)
    consulta_peligrosa = (
        "Quiero transportar solventes industriales desde Santiago a Concepción. "
        "¿Qué necesito?"
    )
    print(f"\n\n[CONSULTA CARGA PELIGROSA]")
    print(f"   Cliente: \"{consulta_peligrosa}\"")
    resultado3 = agente.procesar_consulta(consulta_peligrosa)
    print(f"\n   Respuesta:\n{resultado3['respuesta_final']}")
    print(f"\n   Acción tomada: {resultado3['accion']}")
    
    print("\n" + "=" * 70)
    print("  DEMO 1 FINALIZADA")
    print("=" * 70)

if __name__ == "__main__":
    demo_consulta()

