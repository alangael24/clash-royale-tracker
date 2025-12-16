"""
Clash Royale Tracker - Aplicacion Principal
Rastrea el elixir y ciclo de cartas del rival en tiempo real
Usa Gemini AI para deteccion automatica de cartas

Uso:
    python main.py           - Inicia con deteccion Gemini AI
    python main.py --manual  - Modo solo manual (sin deteccion automatica)
    python main.py --calibrate - Calibrar region de captura
"""

import sys
import threading
import time

# Importar modulos del proyecto
from capture import ScreenCapture, CalibrationTool
from detector_gemini import GeminiCardDetector
from tracker import GameTracker
from gui import TrackerGUI
from config import SCREEN_CONFIG


class ClashRoyaleTracker:
    """
    Aplicacion principal del tracker
    Integra captura, deteccion con Gemini AI, tracking y GUI
    """

    def __init__(self, manual_only=False):
        self.manual_only = manual_only

        # Componentes
        self.capture = None
        self.detector = None
        self.tracker = GameTracker()
        self.gui = None

        # Control de hilos
        self.running = False
        self.detection_thread = None

        # Inicializar componentes
        self._init_components()

    def _init_components(self):
        """Inicializa todos los componentes"""

        # Detector de cartas con Gemini (solo si no es modo manual)
        if not self.manual_only:
            print("Inicializando detector Gemini AI...")
            self.detector = GeminiCardDetector()
            self.capture = ScreenCapture()

        # Crear GUI con callbacks
        self.gui = TrackerGUI(
            on_start=self.start_tracking,
            on_stop=self.stop_tracking,
            on_reset=self.reset_tracking,
            on_elixir_mode=self.set_elixir_mode,
            on_manual_card=self.manual_card_input
        )

    def start_tracking(self):
        """Inicia el rastreo"""
        print("Iniciando rastreo...")
        self.tracker.start_match()
        self.running = True

        if not self.manual_only and self.detector and self.capture:
            # Iniciar hilo de deteccion
            self.detection_thread = threading.Thread(target=self._detection_loop)
            self.detection_thread.daemon = True
            self.detection_thread.start()

        # Iniciar loop de actualizacion de UI
        self._schedule_ui_update()

    def stop_tracking(self):
        """Detiene el rastreo"""
        print("Deteniendo rastreo...")
        self.running = False
        self.tracker.end_match()

        if self.detection_thread:
            self.detection_thread.join(timeout=1.0)
            self.detection_thread = None

    def reset_tracking(self):
        """Reinicia el tracker"""
        print("Reiniciando tracker...")
        self.tracker.reset()
        if self.detector:
            self.detector.reset_match()

    def set_elixir_mode(self, mode):
        """Cambia el modo de elixir"""
        print(f"Modo elixir: {mode}")
        self.tracker.set_elixir_mode(mode)

    def manual_card_input(self, card_name):
        """Procesa una carta ingresada manualmente"""
        print(f"Carta manual: {card_name}")
        result = self.tracker.card_detected(card_name)
        if result:
            self._update_gui()

    def _detection_loop(self):
        """Loop de deteccion de cartas con Gemini (corre en hilo separado)"""
        # Loop rapido - el detector tiene su propio sistema de movimiento y cooldown
        loop_interval = 0.2  # 5 FPS para detectar movimiento

        while self.running:
            start_time = time.time()

            try:
                # Capturar pantalla
                frame = self.capture.capture()

                # Detectar cartas (el detector maneja movimiento + cooldown internamente)
                detections = self.detector.detect_cards(frame)

                # Procesar detecciones nuevas
                for det in detections:
                    card_name = det["card"]
                    self.tracker.card_detected(card_name)

            except Exception as e:
                print(f"Error en deteccion: {e}")

            # Esperar hasta el siguiente ciclo
            elapsed = time.time() - start_time
            if elapsed < loop_interval:
                time.sleep(loop_interval - elapsed)

    def _schedule_ui_update(self):
        """Programa actualizaciones periodicas de la UI"""
        if self.running:
            self._update_gui()
            self.gui.schedule_update(self._schedule_ui_update, 100)

    def _update_gui(self):
        """Actualiza la interfaz grafica"""
        self.tracker.update()
        status = self.tracker.get_status()
        self.gui.update_from_status(status)

    def run(self):
        """Ejecuta la aplicacion"""
        print("=" * 50)
        print("  Clash Royale Tracker")
        print("  Powered by Gemini AI")
        print("=" * 50)

        if self.manual_only:
            print("Modo: Solo manual")
        else:
            print("Modo: Deteccion automatica con Gemini AI")

        print("\nInstrucciones:")
        print("1. Abre Clash Royale PC")
        print("2. Haz clic en 'Iniciar' cuando empiece la partida")
        print("3. Gemini detectara las cartas automaticamente")
        print("4. Cambia a 2x/3x cuando corresponda")
        print("\n")

        # Iniciar GUI
        self.gui.run()

        # Limpiar al cerrar
        self._cleanup()

    def _cleanup(self):
        """Limpia recursos al cerrar"""
        self.running = False
        if self.capture:
            self.capture.close()


def calibrate_screen():
    """Herramienta de calibracion de pantalla"""
    print("=" * 50)
    print("  Herramienta de Calibracion")
    print("=" * 50)
    print("\nInstrucciones:")
    print("1. Abre Clash Royale PC")
    print("2. Arrastra para seleccionar la ventana del juego")
    print("3. Presiona ENTER para confirmar")
    print("")

    calibrator = CalibrationTool()
    region = calibrator.select_region()

    if region:
        print(f"\nRegion seleccionada: {region}")
        print("\nActualiza estos valores en config.py:")
        print(f'    "capture_region": {region},')
    else:
        print("\nCalibracion cancelada")


def main():
    """Punto de entrada principal"""

    # Parsear argumentos
    manual_only = "--manual" in sys.argv
    calibrate = "--calibrate" in sys.argv

    if calibrate:
        calibrate_screen()
        return

    # Crear y ejecutar aplicacion
    app = ClashRoyaleTracker(manual_only=manual_only)
    app.run()


if __name__ == "__main__":
    main()
