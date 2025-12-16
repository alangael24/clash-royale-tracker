"""
Modulo de captura de pantalla para Clash Royale Tracker
Usa mss para capturas rapidas y eficientes
"""

import mss
import mss.tools
import numpy as np
from PIL import Image
import cv2
from config import SCREEN_CONFIG


class ScreenCapture:
    """
    Maneja la captura de pantalla del juego
    Thread-safe: crea nueva instancia de mss en cada captura
    """

    def __init__(self):
        self.region = SCREEN_CONFIG["capture_region"]
        self.monitor = None
        self._setup_monitor()

    def _setup_monitor(self):
        """Configura la region de captura"""
        x, y, width, height = self.region
        self.monitor = {
            "left": x,
            "top": y,
            "width": width,
            "height": height
        }

    def set_region(self, x, y, width, height):
        """
        Establece una nueva region de captura
        Util para cuando el usuario calibra la posicion del juego
        """
        self.region = (x, y, width, height)
        self._setup_monitor()

    def capture(self):
        """
        Captura la pantalla y devuelve una imagen numpy array
        Formato: BGR (compatible con OpenCV)
        Thread-safe: crea nueva instancia de mss cada vez
        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.monitor)
            # Convertir a numpy array
            img = np.array(screenshot)
            # Convertir de BGRA a BGR (eliminar canal alpha)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img

    def capture_pil(self):
        """
        Captura la pantalla y devuelve una imagen PIL
        Util para mostrar en Tkinter
        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    def get_arena_region(self, frame):
        """
        Extrae solo la region de la arena del frame capturado
        Esta es la zona donde aparecen las cartas jugadas
        """
        top = SCREEN_CONFIG["arena_top"]
        bottom = SCREEN_CONFIG["arena_bottom"]
        left = SCREEN_CONFIG["arena_left"]
        right = SCREEN_CONFIG["arena_right"]

        # Asegurarse de que las coordenadas estan dentro del frame
        h, w = frame.shape[:2]
        top = max(0, min(top, h))
        bottom = max(0, min(bottom, h))
        left = max(0, min(left, w))
        right = max(0, min(right, w))

        return frame[top:bottom, left:right]

    def list_monitors(self):
        """Lista todos los monitores disponibles"""
        with mss.mss() as sct:
            return sct.monitors

    def close(self):
        """Libera recursos (no hace nada ahora, pero mantiene compatibilidad)"""
        pass


class CalibrationTool:
    """
    Herramienta para calibrar la region de captura
    Permite al usuario seleccionar donde esta el juego en su pantalla
    """

    def __init__(self):
        self.start_point = None
        self.end_point = None
        self.selecting = False

    def select_region(self):
        """
        Permite al usuario seleccionar una region de la pantalla
        Devuelve (x, y, width, height) de la region seleccionada
        """
        # Capturar pantalla completa
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # Pantalla completa (todos los monitores)
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Crear ventana para seleccion
        window_name = "Selecciona la region del juego (arrastra con el mouse)"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # Variables para el rectangulo
        self.start_point = None
        self.end_point = None
        self.selecting = False
        img_copy = img.copy()

        def mouse_callback(event, x, y, flags, param):
            nonlocal img_copy

            if event == cv2.EVENT_LBUTTONDOWN:
                self.start_point = (x, y)
                self.selecting = True

            elif event == cv2.EVENT_MOUSEMOVE and self.selecting:
                img_copy = img.copy()
                cv2.rectangle(img_copy, self.start_point, (x, y), (0, 255, 0), 2)

            elif event == cv2.EVENT_LBUTTONUP:
                self.end_point = (x, y)
                self.selecting = False
                cv2.rectangle(img_copy, self.start_point, self.end_point, (0, 255, 0), 2)

        cv2.setMouseCallback(window_name, mouse_callback)

        print("Instrucciones:")
        print("1. Arrastra con el mouse para seleccionar la region del juego")
        print("2. Presiona ENTER para confirmar")
        print("3. Presiona ESC para cancelar")

        while True:
            cv2.imshow(window_name, img_copy)
            key = cv2.waitKey(1) & 0xFF

            if key == 13:  # ENTER
                break
            elif key == 27:  # ESC
                cv2.destroyAllWindows()
                return None

        cv2.destroyAllWindows()

        if self.start_point and self.end_point:
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            # Asegurar que las coordenadas estan en orden correcto
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            return (x, y, width, height)

        return None


def test_capture():
    """Funcion de prueba para verificar que la captura funciona"""
    print("Probando captura de pantalla...")
    capture = ScreenCapture()

    # Capturar un frame
    frame = capture.capture()
    print(f"Frame capturado: {frame.shape}")

    # Guardar para verificar
    cv2.imwrite("test_capture.png", frame)
    print("Frame guardado como 'test_capture.png'")

    capture.close()


if __name__ == "__main__":
    # Si se ejecuta directamente, hacer prueba
    test_capture()
