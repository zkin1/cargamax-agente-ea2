"""
Punto de entrada principal del Agente CargaMax Sur Ltda.

Modo interactivo: permite al usuario escribir consultas personalizadas
y ver la respuesta del agente en tiempo real.

Uso:
    python main.py

Configuracion:
    Crear archivo .env en la raiz con: GROQ_API_KEY=tu_clave_aqui
    O exportar variable de entorno:
    Windows PowerShell: $env:GROQ_API_KEY="gsk_..."
    Windows CMD: set GROQ_API_KEY=gsk_...
    Linux/Mac: export GROQ_API_KEY=gsk_...

Comandos durante la ejecucion:
    'salir'  -> Termina la sesion
    'nuevo'  -> Reinicia la memoria (simula nuevo cliente)
    'demo'   -> Ejecuta las 4 consultas de demostracion predefinidas
"""

import os
import sys
from agente_cargamax.core.agent import AgenteCargaMax
from agente_cargamax.config import config


def ejecutar_demo(agente):
    """Ejecuta las 4 consultas de demostracion predefinidas."""
    consultas_demo = [
        "Cuanto cuesta enviar carga desde Santiago a Concepcion?",
        "Necesito transportar pinturas desde Santiago a Puerto Montt. Que documentacion necesito?",
        "Quiero una cotizacion formal mensual de 200 toneladas en ruta Santiago-Valparaiso.",
        "Cual es el horario de atencion de CargaMax?"
    ]
    
    for i, consulta in enumerate(consultas_demo, 1):
        print(f"\n{'-' * 60}")
        print(f"[CONSULTA {i}] Cliente: \"{consulta}\"")
        print("-" * 60)
        
        resultado = agente.procesar_consulta(consulta)
        mostrar_resultado(resultado)
    
    print("\n" + "=" * 60)
    print("  DEMO FINALIZADA")
    print("=" * 60)


def mostrar_resultado(resultado):
    """Muestra el resultado de una consulta de forma estructurada."""
    print(f"\n[ACCION] {resultado['accion'].upper()}")
    print(f"\n[RESPUESTA DEL AGENTE]\n{resultado['respuesta_final']}")
    
    if resultado['metadata']:
        print(f"\n[METADATA]")
        meta = resultado['metadata']
        if 'decision' in meta:
            decision = meta['decision']
            print(f"  Intencion: {decision.get('intencion', 'N/A')}")
            print(f"  Complejidad: {decision.get('complejidad', 'N/A')}")
            print(f"  Escalamiento: {'Si' if decision.get('requiere_escalamiento') else 'No'}")
        if 'plan' in meta:
            print(f"  Plan generado: {len(meta['plan'])} paso(s)")
        if 'fuentes' in meta and meta['fuentes']:
            print(f"  Fuentes: {', '.join(meta['fuentes'])}")
        if 'modo' in meta:
            print(f"  Modo: {meta['modo']}")


def main():
    print("=" * 60)
    print("  AGENTE DE ATENCION AL CLIENTE - CARGAMAX SUR LTDA.")
    print("=" * 60)
    print()
    
    if not config.GROQ_API_KEY:
        print("[!] ADVERTENCIA: GROQ_API_KEY no configurada.")
        print("   El agente funcionara en modo simulacion.")
        print("   Para ejecucion real, configure el archivo .env o la variable de entorno.")
        print()
    else:
        print("[OK] API Key detectada. Modo ejecucion real activo.")
        print(f"   Modelo: {config.MODELO_LLM}")
        print()
    
    cliente_id = "cliente_demo"
    agente = AgenteCargaMax(cliente_id=cliente_id)
    
    print("Escribe 'demo' para ver las consultas predefinidas,")
    print("o escribe tu propia consulta para probar el agente.")
    print("Comandos: 'salir' = terminar | 'nuevo' = reiniciar memoria")
    print()
    
    while True:
        try:
            consulta = input("Cliente: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n[Sistema] Sesion terminada por el usuario.")
            break
        
        if not consulta:
            continue
        
        if consulta.lower() in ("salir", "exit", "quit"):
            print("\n[Sistema] Sesion finalizada. Hasta luego.")
            break
        
        if consulta.lower() == "nuevo":
            agente = AgenteCargaMax(cliente_id=cliente_id)
            print("[Sistema] Memoria reiniciada. Nueva sesion iniciada.\n")
            continue
        
        if consulta.lower() == "demo":
            ejecutar_demo(agente)
            continue
        
        print("\n[Agente procesando...]\n")
        resultado = agente.procesar_consulta(consulta)
        mostrar_resultado(resultado)
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()

