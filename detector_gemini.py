"""
Detector de cartas usando Gemini AI
Usa vision de Gemini para identificar cartas jugadas en Clash Royale
"""

import google.generativeai as genai
from PIL import Image
import io
import base64
import time
import cv2
import numpy as np
from config import CARDS

# Configurar API de Gemini
GEMINI_API_KEY = "AIzaSyD67WKSUPaYe68pDgUrpMDymIQUsGbabRM"

class GeminiCardDetector:
    """
    Detector de cartas usando Gemini AI
    Analiza capturas de pantalla para identificar cartas jugadas
    """

    def __init__(self):
        # Configurar Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

        # Cache para evitar detectar la misma carta varias veces
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # segundos entre detecciones
        self.last_detected_cards = []

        # Lista de nombres de cartas para el prompt
        self.card_names = list(CARDS.keys())

        print("Detector Gemini inicializado")

    def _frame_to_pil(self, frame):
        """Convierte un frame de OpenCV a imagen PIL"""
        # OpenCV usa BGR, PIL usa RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb_frame)

    def detect_cards(self, frame, force=False):
        """
        Detecta cartas en un frame usando Gemini

        Args:
            frame: Imagen BGR de OpenCV
            force: Forzar deteccion ignorando cooldown

        Returns:
            Lista de cartas detectadas [{"card": "knight", "confidence": 0.9}]
        """
        current_time = time.time()

        # Verificar cooldown
        if not force and (current_time - self.last_detection_time) < self.detection_cooldown:
            return []

        self.last_detection_time = current_time

        try:
            # Convertir frame a PIL
            pil_image = self._frame_to_pil(frame)

            # Crear prompt para Gemini
            prompt = """Analyze this Clash Royale game screenshot.

Look at the cards being played or recently deployed in the arena (troops, spells, buildings).
Also look at the opponent's cards if visible.

List ONLY the card names you can clearly identify that were JUST played or are being played.
Use these exact card names (lowercase with underscores):
knight, archers, fireball, hog_rider, giant, golem, pekka, wizard, witch, valkyrie,
musketeer, mini_pekka, prince, baby_dragon, skeleton_army, goblin_barrel, arrows,
zap, lightning, rocket, freeze, rage, clone, mirror, graveyard, poison, tornado,
electro_wizard, bandit, night_witch, mega_knight, royal_ghost, magic_archer,
lumberjack, inferno_dragon, miner, princess, ice_wizard, sparky, lava_hound,
balloon, bowler, executioner, hunter, goblin_gang, bats, wall_breakers,
royal_hogs, three_musketeers, barbarians, minion_horde, elite_barbarians,
skeleton_barrel, goblin_giant, ram_rider, fisherman, phoenix, monk,
mighty_miner, golden_knight, skeleton_king, archer_queen, cannon, tesla,
inferno_tower, bomb_tower, tombstone, furnace, goblin_hut, x_bow, mortar

Respond with ONLY a comma-separated list of card names, nothing else.
If no cards are being played right now, respond with: none
Example response: hog_rider, fireball, knight"""

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

                # Verificar que es una carta válida
                if card_name in CARDS:
                    detected.append({
                        "card": card_name,
                        "confidence": 0.85  # Gemini no da confidence, usamos valor fijo
                    })
                    print(f"Gemini detectó: {card_name}")

            self.last_detected_cards = detected
            return detected

        except Exception as e:
            print(f"Error en detección Gemini: {e}")
            return []

    def detect_cards_from_pil(self, pil_image):
        """
        Detecta cartas desde una imagen PIL directamente
        """
        # Convertir PIL a frame OpenCV
        frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return self.detect_cards(frame, force=True)

    def get_card_info(self, card_name):
        """Obtiene información de una carta"""
        if card_name in CARDS:
            return CARDS[card_name]
        return None

    def clear_cooldown(self):
        """Limpia el cooldown de detección"""
        self.last_detection_time = 0


def test_gemini():
    """Prueba el detector Gemini con una captura de pantalla"""
    from capture import ScreenCapture

    print("=" * 50)
    print("  Test Detector Gemini")
    print("=" * 50)

    # Capturar pantalla
    print("\nCapturando pantalla...")
    capture = ScreenCapture()
    frame = capture.capture()

    # Guardar captura
    cv2.imwrite("test_gemini_capture.png", frame)
    print("Captura guardada: test_gemini_capture.png")

    # Detectar cartas
    print("\nEnviando a Gemini para análisis...")
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
