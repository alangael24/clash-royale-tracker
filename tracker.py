"""
Modulo de rastreo de elixir y ciclo de cartas
Logica principal del tracker de Clash Royale
"""

import time
from collections import deque
from config import CARDS, ELIXIR_CONFIG


class ElixirTracker:
    """
    Rastrea el elixir estimado del rival
    El elixir se genera a una tasa constante y se consume al jugar cartas
    """

    def __init__(self):
        self.elixir = ELIXIR_CONFIG["starting_elixir"]
        self.max_elixir = ELIXIR_CONFIG["max_elixir"]
        self.elixir_rate = ELIXIR_CONFIG["normal_rate"]  # Segundos por 1 elixir
        self.last_update = time.time()
        self.is_running = False
        self.double_elixir = False
        self.triple_elixir = False

    def start(self):
        """Inicia el rastreo de elixir"""
        self.elixir = ELIXIR_CONFIG["starting_elixir"]
        self.last_update = time.time()
        self.is_running = True

    def stop(self):
        """Detiene el rastreo"""
        self.is_running = False

    def reset(self):
        """Reinicia el tracker"""
        self.elixir = ELIXIR_CONFIG["starting_elixir"]
        self.last_update = time.time()
        self.double_elixir = False
        self.triple_elixir = False

    def set_double_elixir(self, enabled=True):
        """Activa/desactiva modo 2x elixir"""
        self.double_elixir = enabled
        self.triple_elixir = False
        if enabled:
            self.elixir_rate = ELIXIR_CONFIG["double_rate"]
        else:
            self.elixir_rate = ELIXIR_CONFIG["normal_rate"]

    def set_triple_elixir(self, enabled=True):
        """Activa/desactiva modo 3x elixir"""
        self.triple_elixir = enabled
        self.double_elixir = False
        if enabled:
            self.elixir_rate = ELIXIR_CONFIG["triple_rate"]
        else:
            self.elixir_rate = ELIXIR_CONFIG["normal_rate"]

    def update(self):
        """
        Actualiza el elixir basado en el tiempo transcurrido
        Debe llamarse regularmente (cada frame)
        """
        if not self.is_running:
            return self.elixir

        current_time = time.time()
        elapsed = current_time - self.last_update

        # Calcular elixir generado
        elixir_gained = elapsed / self.elixir_rate
        self.elixir = min(self.max_elixir, self.elixir + elixir_gained)
        self.last_update = current_time

        return self.elixir

    def spend_elixir(self, amount):
        """
        Resta elixir cuando el rival juega una carta

        Args:
            amount: Cantidad de elixir a restar

        Returns:
            True si se pudo restar, False si no habia suficiente
        """
        self.update()  # Actualizar primero
        if self.elixir >= amount:
            self.elixir -= amount
            return True
        else:
            # El rival jugo una carta pero no tenia suficiente elixir?
            # Esto puede pasar si nuestra estimacion esta mal
            # Ajustamos a 0 y continuamos
            self.elixir = 0
            return False

    def card_played(self, card_name):
        """
        Registra que una carta fue jugada y resta su elixir

        Args:
            card_name: Nombre interno de la carta (ej: "knight")

        Returns:
            Costo de elixir de la carta, o None si no se reconoce
        """
        if card_name in CARDS:
            cost = CARDS[card_name]["elixir"]
            self.spend_elixir(cost)
            return cost
        return None

    def get_elixir(self):
        """Obtiene el elixir actual (actualizado)"""
        return self.update()

    def get_elixir_int(self):
        """Obtiene el elixir redondeado hacia abajo"""
        return int(self.get_elixir())


class CardCycleTracker:
    """
    Rastrea el ciclo de cartas del rival
    En CR, cada jugador tiene 8 cartas, 4 en mano en cualquier momento
    """

    def __init__(self):
        self.known_cards = set()  # Cartas que sabemos que tiene el rival
        self.play_history = deque(maxlen=50)  # Historial de cartas jugadas
        self.current_cycle = []  # Orden del ciclo actual
        self.hand_size = 4  # Cartas en mano
        self.deck_size = 8  # Cartas en mazo

    def reset(self):
        """Reinicia el tracker de ciclo"""
        self.known_cards.clear()
        self.play_history.clear()
        self.current_cycle.clear()

    def card_played(self, card_name):
        """
        Registra que una carta fue jugada

        Args:
            card_name: Nombre interno de la carta
        """
        if card_name not in CARDS:
            return

        # Agregar a cartas conocidas
        self.known_cards.add(card_name)

        # Agregar al historial
        self.play_history.append({
            "card": card_name,
            "timestamp": time.time()
        })

        # Actualizar ciclo
        self._update_cycle(card_name)

    def _update_cycle(self, card_name):
        """Actualiza el ciclo de cartas"""
        # Si la carta ya esta en el ciclo, significa que volvio a la mano
        if card_name in self.current_cycle:
            # Encontrar la posicion y rotar el ciclo
            idx = self.current_cycle.index(card_name)
            # La carta jugada va al final del ciclo
            self.current_cycle.pop(idx)
            self.current_cycle.append(card_name)
        else:
            # Nueva carta detectada
            self.current_cycle.append(card_name)

    def get_known_cards(self):
        """Devuelve todas las cartas conocidas del rival"""
        return list(self.known_cards)

    def get_cards_in_hand(self):
        """
        Estima que cartas tiene el rival en mano
        Basado en las ultimas cartas jugadas y el ciclo
        """
        if len(self.current_cycle) < self.deck_size:
            # No conocemos todas las cartas aun
            # Devolver las que probablemente no esten en mano
            recent_played = []
            for item in list(self.play_history)[-4:]:
                recent_played.append(item["card"])

            # Cartas que no se han jugado recientemente probablemente estan en mano
            in_hand = [c for c in self.known_cards if c not in recent_played]
            return in_hand[:4]  # Maximo 4 en mano

        # Si conocemos las 8 cartas, calcular exactamente
        # Las primeras 4 del ciclo estan en mano
        return self.current_cycle[:self.hand_size]

    def get_next_card(self):
        """
        Predice la proxima carta que entrara a la mano del rival
        """
        if len(self.current_cycle) >= self.deck_size:
            # La carta en posicion 4 sera la proxima en entrar a mano
            return self.current_cycle[self.hand_size] if len(self.current_cycle) > self.hand_size else None
        return None

    def get_last_played(self, count=4):
        """Devuelve las ultimas N cartas jugadas"""
        recent = list(self.play_history)[-count:]
        return [item["card"] for item in recent]

    def deck_complete(self):
        """Verifica si hemos identificado las 8 cartas del rival"""
        return len(self.known_cards) >= self.deck_size

    def get_deck_progress(self):
        """Devuelve progreso de identificacion del mazo (0-8)"""
        return min(len(self.known_cards), self.deck_size)


class GameTracker:
    """
    Tracker principal que combina elixir y ciclo de cartas
    """

    def __init__(self):
        self.elixir_tracker = ElixirTracker()
        self.cycle_tracker = CardCycleTracker()
        self.is_active = False
        self.match_start_time = None
        self.total_cards_played = 0

    def start_match(self):
        """Inicia un nuevo partido"""
        self.elixir_tracker.start()
        self.cycle_tracker.reset()
        self.is_active = True
        self.match_start_time = time.time()
        self.total_cards_played = 0

    def end_match(self):
        """Termina el partido actual"""
        self.elixir_tracker.stop()
        self.is_active = False

    def reset(self):
        """Reinicia todo el tracker"""
        self.elixir_tracker.reset()
        self.cycle_tracker.reset()
        self.is_active = False
        self.match_start_time = None
        self.total_cards_played = 0

    def card_detected(self, card_name):
        """
        Procesa una carta detectada

        Args:
            card_name: Nombre de la carta detectada

        Returns:
            Dict con informacion de la carta y estado actual
        """
        if not self.is_active:
            return None

        if card_name not in CARDS:
            return None

        # Registrar en ambos trackers
        elixir_cost = self.elixir_tracker.card_played(card_name)
        self.cycle_tracker.card_played(card_name)
        self.total_cards_played += 1

        return {
            "card": card_name,
            "card_info": CARDS[card_name],
            "elixir_spent": elixir_cost,
            "current_elixir": self.elixir_tracker.get_elixir_int(),
            "known_cards": len(self.cycle_tracker.known_cards)
        }

    def update(self):
        """Actualiza el estado del tracker (llamar cada frame)"""
        if self.is_active:
            self.elixir_tracker.update()

    def set_elixir_mode(self, mode):
        """
        Cambia el modo de elixir

        Args:
            mode: "normal", "double", o "triple"
        """
        if mode == "double":
            self.elixir_tracker.set_double_elixir(True)
        elif mode == "triple":
            self.elixir_tracker.set_triple_elixir(True)
        else:
            self.elixir_tracker.set_double_elixir(False)

    def get_status(self):
        """Obtiene el estado actual del tracker"""
        return {
            "is_active": self.is_active,
            "elixir": self.elixir_tracker.get_elixir(),
            "elixir_int": self.elixir_tracker.get_elixir_int(),
            "elixir_mode": "triple" if self.elixir_tracker.triple_elixir else
                          "double" if self.elixir_tracker.double_elixir else "normal",
            "known_cards": self.cycle_tracker.get_known_cards(),
            "cards_in_hand": self.cycle_tracker.get_cards_in_hand(),
            "next_card": self.cycle_tracker.get_next_card(),
            "last_played": self.cycle_tracker.get_last_played(),
            "deck_complete": self.cycle_tracker.deck_complete(),
            "deck_progress": self.cycle_tracker.get_deck_progress(),
            "total_cards_played": self.total_cards_played,
            "match_duration": time.time() - self.match_start_time if self.match_start_time else 0
        }


def test_tracker():
    """Prueba el tracker con datos simulados"""
    print("Probando tracker...")

    tracker = GameTracker()
    tracker.start_match()

    # Simular algunas cartas jugadas
    test_cards = ["knight", "fireball", "hog_rider", "arrows",
                  "knight", "valkyrie", "musketeer", "golem"]

    for card in test_cards:
        result = tracker.card_detected(card)
        if result:
            print(f"Carta: {card}, Elixir gastado: {result['elixir_spent']}, "
                  f"Elixir rival: {result['current_elixir']}")
        time.sleep(0.5)  # Simular tiempo entre cartas

    # Mostrar estado final
    status = tracker.get_status()
    print("\n--- Estado Final ---")
    print(f"Cartas conocidas: {status['known_cards']}")
    print(f"En mano: {status['cards_in_hand']}")
    print(f"Elixir estimado: {status['elixir_int']}")
    print(f"Mazo completo: {status['deck_complete']}")


if __name__ == "__main__":
    test_tracker()
