"""
Modulo de deteccion de cartas para Clash Royale Tracker
Usa OpenCV template matching para identificar cartas jugadas
"""

import cv2
import numpy as np
import os
from pathlib import Path
from config import CARDS, DETECTION_THRESHOLD, SCREEN_CONFIG


class CardDetector:
    """
    Detecta cartas de Clash Royale en capturas de pantalla
    usando template matching de OpenCV
    """

    def __init__(self, cards_folder="cards"):
        self.cards_folder = Path(cards_folder)
        self.templates = {}  # {nombre_carta: imagen_template}
        self.last_detections = []  # Ultimas cartas detectadas
        self.detection_cooldown = {}  # Evitar detectar la misma carta multiples veces

        # Cargar templates de cartas
        self._load_templates()

    def _load_templates(self):
        """Carga todas las imagenes de cartas como templates"""
        if not self.cards_folder.exists():
            print(f"AVISO: Carpeta de cartas '{self.cards_folder}' no existe.")
            print("Necesitas agregar imagenes de las cartas para la deteccion.")
            return

        # Formatos de imagen soportados
        extensions = [".png", ".jpg", ".jpeg"]

        # Tamaño objetivo para redimensionar templates
        target_width = SCREEN_CONFIG["card_width"]
        target_height = SCREEN_CONFIG["card_height"]

        for card_file in self.cards_folder.iterdir():
            if card_file.suffix.lower() in extensions:
                card_name = card_file.stem.lower()

                # Verificar que la carta existe en nuestra base de datos
                if card_name in CARDS:
                    template = cv2.imread(str(card_file))
                    if template is not None:
                        # Redimensionar al tamaño configurado
                        template = cv2.resize(template, (target_width, target_height))
                        # Convertir a escala de grises para mejor matching
                        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                        self.templates[card_name] = {
                            "color": template,
                            "gray": template_gray,
                            "size": (target_height, target_width)
                        }
                        print(f"Template cargado: {card_name}")
                else:
                    print(f"AVISO: Carta '{card_name}' no encontrada en la base de datos")

        print(f"Total templates cargados: {len(self.templates)}")

    def detect_cards(self, frame, threshold=None):
        """
        Detecta cartas en un frame de pantalla

        Args:
            frame: Imagen BGR de OpenCV
            threshold: Umbral de confianza (usa el default si no se especifica)

        Returns:
            Lista de cartas detectadas con su posicion y confianza
            [{"card": "knight", "confidence": 0.85, "position": (x, y)}]
        """
        if threshold is None:
            threshold = DETECTION_THRESHOLD

        if not self.templates:
            return []

        # Convertir frame a escala de grises
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        detections = []
        current_time = cv2.getTickCount()

        for card_name, template_data in self.templates.items():
            template = template_data["gray"]
            h, w = template_data["size"]

            # Template matching
            result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)

            # Encontrar todas las coincidencias sobre el umbral
            locations = np.where(result >= threshold)

            for pt in zip(*locations[::-1]):  # Swap x,y
                confidence = result[pt[1], pt[0]]

                # Verificar cooldown para evitar duplicados
                cooldown_key = f"{card_name}_{pt[0]//50}_{pt[1]//50}"  # Grid de 50px
                if cooldown_key in self.detection_cooldown:
                    last_time = self.detection_cooldown[cooldown_key]
                    # Cooldown de 2 segundos
                    if (current_time - last_time) / cv2.getTickFrequency() < 2.0:
                        continue

                self.detection_cooldown[cooldown_key] = current_time

                detections.append({
                    "card": card_name,
                    "confidence": float(confidence),
                    "position": (pt[0], pt[1]),
                    "size": (w, h)
                })

        # Eliminar duplicados cercanos (non-maximum suppression simple)
        detections = self._remove_duplicates(detections)

        self.last_detections = detections
        return detections

    def _remove_duplicates(self, detections, distance_threshold=30):
        """
        Elimina detecciones duplicadas que estan muy cerca
        Mantiene la de mayor confianza
        """
        if not detections:
            return []

        # Ordenar por confianza (mayor primero)
        detections = sorted(detections, key=lambda x: x["confidence"], reverse=True)

        filtered = []
        for det in detections:
            x1, y1 = det["position"]
            is_duplicate = False

            for existing in filtered:
                x2, y2 = existing["position"]
                distance = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

                if distance < distance_threshold and det["card"] == existing["card"]:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(det)

        return filtered

    def detect_in_region(self, frame, region):
        """
        Detecta cartas solo en una region especifica del frame

        Args:
            frame: Frame completo
            region: (x, y, width, height) de la region a analizar

        Returns:
            Lista de detecciones con posiciones ajustadas al frame completo
        """
        x, y, w, h = region
        roi = frame[y:y+h, x:x+w]

        detections = self.detect_cards(roi)

        # Ajustar posiciones al frame completo
        for det in detections:
            px, py = det["position"]
            det["position"] = (px + x, py + y)

        return detections

    def draw_detections(self, frame, detections=None):
        """
        Dibuja rectangulos alrededor de las cartas detectadas
        Util para debug y visualizacion
        """
        if detections is None:
            detections = self.last_detections

        frame_copy = frame.copy()

        for det in detections:
            x, y = det["position"]
            w, h = det["size"]
            card = det["card"]
            conf = det["confidence"]

            # Color verde para detecciones
            color = (0, 255, 0)

            # Dibujar rectangulo
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)

            # Etiqueta con nombre y confianza
            label = f"{card}: {conf:.2f}"
            cv2.putText(frame_copy, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame_copy

    def get_card_info(self, card_name):
        """Obtiene informacion de una carta (nombre, elixir)"""
        if card_name in CARDS:
            return CARDS[card_name]
        return None

    def clear_cooldowns(self):
        """Limpia los cooldowns de deteccion"""
        self.detection_cooldown.clear()


class ManualCardInput:
    """
    Alternativa manual para registrar cartas
    Util si la deteccion automatica no funciona bien
    """

    def __init__(self):
        self.registered_cards = []

    def register_card(self, card_name):
        """Registra una carta manualmente"""
        if card_name in CARDS:
            self.registered_cards.append({
                "card": card_name,
                "timestamp": cv2.getTickCount()
            })
            return True
        return False

    def get_recent_cards(self, seconds=10):
        """Obtiene cartas registradas en los ultimos N segundos"""
        current_time = cv2.getTickCount()
        cutoff = current_time - (seconds * cv2.getTickFrequency())

        recent = [c for c in self.registered_cards if c["timestamp"] > cutoff]
        return recent

    def clear(self):
        """Limpia el historial"""
        self.registered_cards.clear()


def create_sample_templates():
    """
    Crea templates de ejemplo (placeholders) para testing
    En produccion, necesitas capturas reales de las cartas
    """
    cards_folder = Path("cards")
    cards_folder.mkdir(exist_ok=True)

    # Crear imagen placeholder para algunas cartas
    sample_cards = ["knight", "fireball", "hog_rider", "golem", "arrows"]

    for card_name in sample_cards:
        # Crear imagen gris de 64x76 como placeholder
        img = np.zeros((76, 64, 3), dtype=np.uint8)
        img[:] = (100, 100, 100)  # Gris

        # Agregar texto del nombre
        cv2.putText(img, card_name[:4], (5, 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        filepath = cards_folder / f"{card_name}.png"
        cv2.imwrite(str(filepath), img)
        print(f"Placeholder creado: {filepath}")


def test_detector():
    """Funcion de prueba para el detector"""
    print("Probando detector de cartas...")

    # Crear templates de ejemplo si no existen
    if not Path("cards").exists() or not list(Path("cards").glob("*.png")):
        print("Creando templates de ejemplo...")
        create_sample_templates()

    detector = CardDetector()

    if not detector.templates:
        print("No hay templates cargados. Agrega imagenes de cartas a la carpeta 'cards/'")
        return

    # Crear imagen de prueba
    test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    test_frame[:] = (50, 50, 50)

    # Detectar (no encontrara nada en una imagen vacia, pero prueba que funcione)
    detections = detector.detect_cards(test_frame)
    print(f"Detecciones encontradas: {len(detections)}")


if __name__ == "__main__":
    test_detector()
