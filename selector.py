"""
Selector visual de region - Como el recorte de Windows
Arrastra para seleccionar la ventana de Clash Royale
"""

import cv2
import mss
import numpy as np

# Variables globales para el mouse
start_point = None
end_point = None
selecting = False
img_copy = None

def mouse_callback(event, x, y, flags, param):
    global start_point, end_point, selecting, img_copy, img

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        selecting = True

    elif event == cv2.EVENT_MOUSEMOVE and selecting:
        img_copy = img.copy()
        cv2.rectangle(img_copy, start_point, (x, y), (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        selecting = False
        cv2.rectangle(img_copy, start_point, end_point, (0, 255, 0), 2)

def main():
    global img, img_copy

    print("=" * 50)
    print("  SELECTOR DE REGION")
    print("=" * 50)
    print("\n1. Abre Clash Royale en una partida")
    print("2. Presiona ENTER cuando este listo...")
    input()

    # Capturar pantalla completa
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Monitor principal
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    img_copy = img.copy()

    # Crear ventana
    cv2.namedWindow("Selecciona Clash Royale - ENTER para confirmar, ESC para cancelar", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Selecciona Clash Royale - ENTER para confirmar, ESC para cancelar",
                          cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("Selecciona Clash Royale - ENTER para confirmar, ESC para cancelar", mouse_callback)

    print("\n>> Arrastra un rectangulo sobre la ventana de Clash Royale")
    print(">> Presiona ENTER para confirmar")
    print(">> Presiona ESC para cancelar")

    while True:
        cv2.imshow("Selecciona Clash Royale - ENTER para confirmar, ESC para cancelar", img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == 13:  # ENTER
            break
        elif key == 27:  # ESC
            print("\nCancelado")
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    if start_point and end_point:
        x1, y1 = start_point
        x2, y2 = end_point

        # Ordenar coordenadas
        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        print("\n" + "=" * 50)
        print("  REGION SELECCIONADA")
        print("=" * 50)
        print(f"\n  capture_region: ({x}, {y}, {w}, {h})")

        # Calcular arena (parte central, sin torres ni mano)
        # Arena es aproximadamente el 50% central verticalmente
        arena_top = int(h * 0.12)      # 12% desde arriba (despues del header)
        arena_bottom = int(h * 0.65)   # 65% (antes de las cartas)
        arena_left = int(w * 0.05)     # 5% margen izquierdo
        arena_right = int(w * 0.95)    # 95% margen derecho

        print(f"\n  Arena sugerida:")
        print(f"    arena_top: {arena_top}")
        print(f"    arena_bottom: {arena_bottom}")
        print(f"    arena_left: {arena_left}")
        print(f"    arena_right: {arena_right}")

        # Preguntar si quiere guardar
        print("\n¿Guardar en config.py? (s/n): ", end="")
        resp = input().strip().lower()

        if resp == 's':
            actualizar_config(x, y, w, h, arena_top, arena_bottom, arena_left, arena_right)
            print("\n>> Configuracion guardada!")
        else:
            print("\n>> No guardado. Copia los valores manualmente a config.py")

def actualizar_config(x, y, w, h, arena_top, arena_bottom, arena_left, arena_right):
    """Actualiza config.py con los nuevos valores"""
    with open("config.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar capture_region
    import re

    # Reemplazar capture_region
    content = re.sub(
        r'"capture_region":\s*\([^)]+\)',
        f'"capture_region": ({x}, {y}, {w}, {h})',
        content
    )

    # Reemplazar arena values
    content = re.sub(r'"arena_top":\s*\d+', f'"arena_top": {arena_top}', content)
    content = re.sub(r'"arena_bottom":\s*\d+', f'"arena_bottom": {arena_bottom}', content)
    content = re.sub(r'"arena_left":\s*\d+', f'"arena_left": {arena_left}', content)
    content = re.sub(r'"arena_right":\s*\d+', f'"arena_right": {arena_right}', content)

    with open("config.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
