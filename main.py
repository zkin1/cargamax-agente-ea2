"""
Punto de entrada principal del Agente CargaMax Sur Ltda.

Uso básico:
    python main.py

Configuración:
    Exportar GROQ_API_KEY antes de ejecutar:
    Windows PowerShell: $env:GROQ_API_KEY="gsk_..."
    Windows CMD: set GROQ_API_KEY=gsk_...
    Linux/Mac: export GROQ_API_KEY=gsk_...
"""

import os
from agente_cargamax.core.agent import AgenteCargaMax
from agente_cargamax.config import config

def main():
    print("=" * 60)
    print("  AGENTE DE ATENCIÓN AL CLIENTE - CARGAMAX SUR LTDA.")
    print("=" * 60)
    print()
    
    if not config.GROQ_API_KEY:
        print("[!] ADVERTENCIA: GROQ_API_KEY no configurada.")
        print("   El agente funcionará en modo simulación.")
        print("   Para ejecución real, configure la variable de entorno.")
        print()
    else:
        print("[OK] API Key detectada. Modo ejecución real activo.")
        print(f"   Modelo: {config.MODELO_LLM}")
        print()
    
    agente = AgenteCargaMax(cliente_id="demo_cliente_001")
    
    # Consultas de demostración
    consultas_demo = [
        "¿Cuánto cuesta enviar carga desde Santiago a Concepción?",
        "Necesito transportar pinturas desde Santiago a Puerto Montt. ¿Qué documentación necesito?",
        "Quiero una cotización formal mensual de 200 toneladas en ruta Santiago-Valparaíso.",
        "¿Cuál es el horario de atención de CargaMax?"
    ]
    
    for i, consulta in enumerate(consultas_demo, 1):
        print(f"\n{'-' * 60}")
        print(f"[CONSULTA {i}] Cliente: \"{consulta}\"")
        print("-" * 60)
        
        resultado = agente.procesar_consulta(consulta)
        
        print(f"\n[ACCIÓN] {resultado['accion'].upper()}")
        print(f"\n[RESPUESTA DEL AGENTE]\n{resultado['respuesta_final']}")
        
        if resultado['metadata']:
            print(f"\n[METADATA]")
            meta = resultado['metadata']
            if 'decision' in meta:
                decision = meta['decision']
                print(f"  Intención: {decision.get('intencion', 'N/A')}")
                print(f"  Complejidad: {decision.get('complejidad', 'N/A')}")
                print(f"  Escalamiento: {'Sí' if decision.get('requiere_escalamiento') else 'No'}")
            if 'plan' in meta:
                print(f"  Plan generado: {len(meta['plan'])} paso(s)")
            if 'fuentes' in meta and meta['fuentes']:
                print(f"  Fuentes: {', '.join(meta['fuentes'])}")
    
    print("\n" + "=" * 60)
    print("  DEMO FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    main()

