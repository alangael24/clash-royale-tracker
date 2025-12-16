"""
Detector de cartas usando Gemini AI + Deteccion de movimiento
Sistema hibrido: OpenCV detecta cambios, Gemini identifica cartas
"""

import google.generativeai as genai
from PIL import Image
import time
import cv2
import numpy as np
from config import CARDS, SCREEN_CONFIG

# Configurar API de Gemini
GEMINI_API_KEY = "AIzaSyD67WKSUPaYe68pDgUrpMDymIQUsGbabRM"


class GeminiCardDetector:
    """
    Detector hibrido de cartas:
    - OpenCV detecta movimiento en la arena
    - Gemini AI identifica las cartas cuando hay cambios
    """

    def __init__(self):
        # Configurar Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Control de tiempo
        self.last_detection_time = 0
        self.detection_cooldown = 1.5  # segundos entre llamadas a Gemini
        self.last_detected_cards = []

        # Deteccion de movimiento
        self.last_frame_gray = None
        self.movement_threshold = 500  # pixeles que deben cambiar

        # Cartas ya detectadas en esta partida (evitar duplicados)
        self.detected_this_match = set()

        print("Detector Gemini AI + Movimiento inicializado")

    def _frame_to_pil(self, frame):
        """Convierte un frame de OpenCV a imagen PIL"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_frame)

    def _crop_arena(self, frame):
        """Recorta solo la region de la arena del frame"""
        top = SCREEN_CONFIG["arena_top"]
        bottom = SCREEN_CONFIG["arena_bottom"]
        left = SCREEN_CONFIG["arena_left"]
        right = SCREEN_CONFIG["arena_right"]

        # Asegurar limites dentro del frame
        h, w = frame.shape[:2]
        top = max(0, min(top, h))
        bottom = max(0, min(bottom, h))
        left = max(0, min(left, w))
        right = max(0, min(right, w))

        return frame[top:bottom, left:right]

    def _detect_movement(self, arena_frame):
        """
        Detecta si hubo movimiento significativo en la arena
        Retorna True si se debe llamar a Gemini
        """
        # Convertir a grises y desenfocar
        gray = cv2.cvtColor(arena_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.last_frame_gray is None:
            self.last_frame_gray = gray
            return True  # Primera vez, detectar

        # Calcular diferencia
        delta = cv2.absdiff(self.last_frame_gray, gray)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Contar pixeles que cambiaron
        changed_pixels = cv2.countNonZero(thresh)

        self.last_frame_gray = gray

        return changed_pixels > self.movement_threshold

    def detect_cards(self, frame, force=False):
        """
        Detecta cartas usando sistema hibrido

        Args:
            frame: Imagen BGR de OpenCV (captura completa)
            force: Forzar deteccion ignorando cooldown y movimiento

        Returns:
            Lista de cartas detectadas [{"card": "knight", "confidence": 0.9}]
        """
        current_time = time.time()

        # Recortar arena
        arena_frame = self._crop_arena(frame)

        # Verificar si hay movimiento (a menos que sea forzado)
        if not force:
            has_movement = self._detect_movement(arena_frame)
            if not has_movement:
                return []

            # Verificar cooldown
            if (current_time - self.last_detection_time) < self.detection_cooldown:
                return []

        self.last_detection_time = current_time

        try:
            # Convertir arena recortada a PIL
            pil_image = self._frame_to_pil(arena_frame)

            # Prompt optimizado para Clash Royale
            prompt = """You are analyzing a Clash Royale battle arena screenshot (top-down view).

TASK: Identify ONLY enemy troops, spells, or buildings that are CURRENTLY visible on the battlefield.

RULES:
- IGNORE the card hand at the bottom of the screen
- IGNORE text overlays, timers, elixir bars
- IGNORE towers (King Tower, Princess Towers)
- ONLY report troops/spells actively deployed on the arena
- Look for: moving troops, spell effects, spawning animations

Valid card names (use exactly these, lowercase with underscores):
knight, archers, fireball, hog_rider, giant, golem, pekka, wizard, witch, valkyrie,
musketeer, mini_pekka, prince, baby_dragon, skeleton_army, goblin_barrel, arrows,
zap, lightning, rocket, freeze, rage, clone, mirror, graveyard, poison, tornado,
electro_wizard, bandit, night_witch, mega_knight, royal_ghost, magic_archer,
lumberjack, inferno_dragon, miner, princess, ice_wizard, sparky, lava_hound,
balloon, bowler, executioner, hunter, goblin_gang, bats, wall_breakers,
royal_hogs, three_musketeers, barbarians, minion_horde, skeletons, goblins,
skeleton_barrel, goblin_giant, ram_rider, fisherman, phoenix, monk, log,
mighty_miner, golden_knight, skeleton_king, archer_queen, cannon, tesla,
inferno_tower, bomb_tower, tombstone, furnace, goblin_hut, x_bow, mortar,
minions, spear_goblins, fire_spirit, ice_spirit, electro_spirit, heal_spirit,
dark_prince, guards, ice_golem, mega_minion, flying_machine, cannon_cart,
royal_recruits, zappies, rascals, royal_delivery, earthquake, giant_snowball

RESPOND with ONLY a comma-separated list of card names you see.
If no cards are deployed, respond: none

Example: hog_rider, musketeer, fireball"""

            # Enviar a Gemini
            response = self.model.generate_content([prompt, pil_image])

            # Parsear respuesta
            result_text = response.text.strip().lower()

            if result_text == "none" or not result_text:
                return []

            # Extraer nombres de cartas
            detected = []
            card_names_found = [name.strip() for name in result_text.split(",")]

            for card_name in card_names_found:
                # Limpiar el nombre
                card_name = card_name.strip().replace(" ", "_").replace("-", "_")

                # Verificar que es una carta valida y no fue detectada antes
                if card_name in CARDS:
                    detected.append({
                        "card": card_name,
                        "confidence": 0.90
                    })

                    if card_name not in self.detected_this_match:
                        self.detected_this_match.add(card_name)
                        print(f"[GEMINI] Nueva carta detectada: {card_name}")
                    else:
                        print(f"[GEMINI] Carta en arena: {card_name}")

            self.last_detected_cards = detected
            return detected

        except Exception as e:
            print(f"Error en deteccion Gemini: {e}")
            return []

    def reset_match(self):
        """Reinicia el estado para una nueva partida"""
        self.detected_this_match.clear()
        self.last_frame_gray = None
        self.last_detection_time = 0
        print("Detector reseteado para nueva partida")

    def clear_cooldown(self):
        """Limpia el cooldown de deteccion"""
        self.last_detection_time = 0

    def get_card_info(self, card_name):
        """Obtiene informacion de una carta"""
        if card_name in CARDS:
            return CARDS[card_name]
        return None


def test_gemini():
    """Prueba el detector Gemini con una captura de pantalla"""
    from capture import ScreenCapture

    print("=" * 50)
    print("  Test Detector Gemini + Movimiento")
    print("=" * 50)

    # Capturar pantalla
    print("\nCapturando pantalla...")
    capture = ScreenCapture()
    frame = capture.capture()

    # Guardar captura
    cv2.imwrite("test_gemini_capture.png", frame)
    print("Captura guardada: test_gemini_capture.png")

    # Detectar cartas
    print("\nEnviando a Gemini para analisis...")
    detector = GeminiCardDetector()
    detections = detector.detect_cards(frame, force=True)

    print(f"\nCartas detectadas: {len(detections)}")
    for det in detections:
        card = det["card"]
        info = CARDS.get(card, {})
        print(f"  - {card}: {info.get('name', '?')} ({info.get('elixir', '?')} elixir)")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_gemini()
