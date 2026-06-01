"""
Modo interactivo del Agente CargaMax.

Permite al usuario escribir consultas personalizadas y ver la respuesta
 del agente en tiempo real, demostrando el funcionamiento real del sistema.

Uso:
    python chat_interactivo.py

Escribe 'salir' para terminar la sesion.
"""

import sys
import os

# Asegurar que el paquete agente_cargamax sea importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agente_cargamax.core.agent import AgenteCargaMax


def main():
    print("=" * 70)
    print("  AGENTE CARGAMAX - MODO INTERACTIVO")
    print("  Escribe tu consulta y presiona Enter.")
    print("  Comandos: 'salir' para terminar, 'nuevo' para reiniciar sesion.")
    print("=" * 70)
    print()

    # Crear agente con un cliente ID
    cliente_id = "usuario_interactivo"
    agente = AgenteCargaMax(cliente_id=cliente_id)

    print("[Sistema] Agente inicializado y listo para recibir consultas.")
    print("[Sistema] Esperando consultas...\n")

    while True:
        try:
            consulta = input("Cliente: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[Sistema] Sesion terminada.")
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

        print("\n[Agente procesando...]\n")

        resultado = agente.procesar_consulta(consulta)

        print(f"[Accion: {resultado['accion'].upper()}]")
        print(f"[Respuesta]\n{resultado['respuesta_final']}")

        if resultado['metadata']:
            meta = resultado['metadata']
            if 'decision' in meta:
                decision = meta['decision']
                print(f"\n[Detalle] Intencion: {decision.get('intencion', 'N/A')} | "
                      f"Complejidad: {decision.get('complejidad', 'N/A')}")
            if 'fuentes' in meta and meta['fuentes']:
                print(f"[Fuentes] {', '.join(meta['fuentes'])}")

        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()

