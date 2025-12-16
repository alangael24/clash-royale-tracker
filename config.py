"""
Configuracion del Clash Royale Tracker
Contiene datos de cartas y configuraciones de pantalla
"""

# Todas las cartas de Clash Royale con su costo de elixir
# Formato: "nombre_interno": {"name": "Nombre Display", "elixir": costo}
CARDS = {
    # Tropas - Comunes
    "knight": {"name": "Caballero", "elixir": 3},
    "archers": {"name": "Arqueras", "elixir": 3},
    "goblins": {"name": "Duendes", "elixir": 2},
    "giant": {"name": "Gigante", "elixir": 5},
    "minions": {"name": "Esbirros", "elixir": 3},
    "balloon": {"name": "Globo Bombástico", "elixir": 5},
    "witch": {"name": "Bruja", "elixir": 5},
    "barbarians": {"name": "Bárbaros", "elixir": 5},
    "golem": {"name": "Gólem", "elixir": 8},
    "skeletons": {"name": "Esqueletos", "elixir": 1},
    "valkyrie": {"name": "Valquiria", "elixir": 4},
    "skeleton_army": {"name": "Ejército de Esqueletos", "elixir": 3},
    "bomber": {"name": "Bombardero", "elixir": 2},
    "musketeer": {"name": "Mosquetera", "elixir": 4},
    "baby_dragon": {"name": "Bebé Dragón", "elixir": 4},
    "prince": {"name": "Príncipe", "elixir": 5},
    "wizard": {"name": "Mago", "elixir": 5},
    "mini_pekka": {"name": "Mini P.E.K.K.A", "elixir": 4},
    "spear_goblins": {"name": "Duendes con Lanza", "elixir": 2},
    "giant_skeleton": {"name": "Esqueleto Gigante", "elixir": 6},
    "hog_rider": {"name": "Montapuercos", "elixir": 4},
    "minion_horde": {"name": "Horda de Esbirros", "elixir": 5},
    "ice_wizard": {"name": "Mago de Hielo", "elixir": 3},
    "royal_giant": {"name": "Gigante Real", "elixir": 6},
    "guards": {"name": "Guardias", "elixir": 3},
    "princess": {"name": "Princesa", "elixir": 3},
    "dark_prince": {"name": "Príncipe Oscuro", "elixir": 4},
    "three_musketeers": {"name": "Tres Mosqueteras", "elixir": 9},
    "lava_hound": {"name": "Sabueso de Lava", "elixir": 7},
    "ice_spirit": {"name": "Espíritu de Hielo", "elixir": 1},
    "fire_spirit": {"name": "Espíritu de Fuego", "elixir": 1},
    "miner": {"name": "Minero", "elixir": 3},
    "sparky": {"name": "Chispitas", "elixir": 6},
    "bowler": {"name": "Lanzarrocas", "elixir": 5},
    "lumberjack": {"name": "Leñador", "elixir": 4},
    "inferno_dragon": {"name": "Dragón Infernal", "elixir": 4},
    "electro_wizard": {"name": "Mago Eléctrico", "elixir": 4},
    "battle_ram": {"name": "Ariete de Batalla", "elixir": 4},
    "goblin_gang": {"name": "Pandilla de Duendes", "elixir": 3},
    "dart_goblin": {"name": "Duende con Dardos", "elixir": 3},
    "bats": {"name": "Murciélagos", "elixir": 2},
    "bandit": {"name": "Bandida", "elixir": 3},
    "night_witch": {"name": "Bruja Nocturna", "elixir": 4},
    "mega_knight": {"name": "Megacaballero", "elixir": 7},
    "skeleton_barrel": {"name": "Barril de Esqueletos", "elixir": 3},
    "flying_machine": {"name": "Máquina Voladora", "elixir": 4},
    "cannon_cart": {"name": "Carro de Cañón", "elixir": 5},
    "royal_ghost": {"name": "Fantasma Real", "elixir": 3},
    "magic_archer": {"name": "Arquero Mágico", "elixir": 4},
    "royal_hogs": {"name": "Puercos Reales", "elixir": 5},
    "zappies": {"name": "Zappies", "elixir": 4},
    "rascals": {"name": "Rufianes", "elixir": 5},
    "royal_recruits": {"name": "Reclutas Reales", "elixir": 7},
    "hunter": {"name": "Cazador", "elixir": 4},
    "goblin_giant": {"name": "Duende Gigante", "elixir": 6},
    "electro_dragon": {"name": "Dragón Eléctrico", "elixir": 5},
    "ram_rider": {"name": "Montacarneros", "elixir": 5},
    "wall_breakers": {"name": "Rompemuros", "elixir": 2},
    "fisherman": {"name": "Pescador", "elixir": 3},
    "elixir_golem": {"name": "Gólem de Elixir", "elixir": 3},
    "battle_healer": {"name": "Sanadora de Batalla", "elixir": 4},
    "skeleton_dragons": {"name": "Dragones Esqueléticos", "elixir": 4},
    "mother_witch": {"name": "Madre Bruja", "elixir": 4},
    "electro_spirit": {"name": "Espíritu Eléctrico", "elixir": 1},
    "electro_giant": {"name": "Gigante Eléctrico", "elixir": 7},
    "phoenix": {"name": "Fénix", "elixir": 4},
    "monk": {"name": "Monje", "elixir": 5},
    "mighty_miner": {"name": "Minero Poderoso", "elixir": 4},
    "golden_knight": {"name": "Caballero Dorado", "elixir": 4},
    "skeleton_king": {"name": "Rey Esqueleto", "elixir": 4},
    "archer_queen": {"name": "Reina Arquera", "elixir": 5},
    "little_prince": {"name": "Principito", "elixir": 3},

    # Edificios
    "cannon": {"name": "Cañón", "elixir": 3},
    "goblin_hut": {"name": "Choza de Duendes", "elixir": 5},
    "mortar": {"name": "Mortero", "elixir": 4},
    "inferno_tower": {"name": "Torre Infernal", "elixir": 5},
    "bomb_tower": {"name": "Torre Bomba", "elixir": 4},
    "barbarian_hut": {"name": "Choza de Bárbaros", "elixir": 7},
    "tesla": {"name": "Tesla", "elixir": 4},
    "elixir_collector": {"name": "Recolector de Elixir", "elixir": 6},
    "x_bow": {"name": "Ballesta", "elixir": 6},
    "tombstone": {"name": "Lápida", "elixir": 3},
    "furnace": {"name": "Horno", "elixir": 4},
    "goblin_cage": {"name": "Jaula de Duende", "elixir": 4},
    "goblin_drill": {"name": "Taladro de Duendes", "elixir": 4},

    # Hechizos
    "fireball": {"name": "Bola de Fuego", "elixir": 4},
    "arrows": {"name": "Flechas", "elixir": 3},
    "rage": {"name": "Furia", "elixir": 2},
    "rocket": {"name": "Cohete", "elixir": 6},
    "goblin_barrel": {"name": "Barril de Duendes", "elixir": 3},
    "freeze": {"name": "Congelación", "elixir": 4},
    "mirror": {"name": "Espejo", "elixir": 1},  # El costo real depende de la carta copiada
    "lightning": {"name": "Rayo", "elixir": 6},
    "zap": {"name": "Descarga", "elixir": 2},
    "poison": {"name": "Veneno", "elixir": 4},
    "graveyard": {"name": "Cementerio", "elixir": 5},
    "the_log": {"name": "El Tronco", "elixir": 2},
    "tornado": {"name": "Tornado", "elixir": 3},
    "clone": {"name": "Clonación", "elixir": 3},
    "earthquake": {"name": "Terremoto", "elixir": 3},
    "barbarian_barrel": {"name": "Barril de Bárbaro", "elixir": 2},
    "heal_spirit": {"name": "Espíritu Sanador", "elixir": 1},
    "giant_snowball": {"name": "Bola de Nieve", "elixir": 2},
    "royal_delivery": {"name": "Entrega Real", "elixir": 3},
    "pekka": {"name": "P.E.K.K.A", "elixir": 7},
    "ice_golem": {"name": "Gólem de Hielo", "elixir": 2},
    "mega_minion": {"name": "Megaesbirro", "elixir": 3},
    "executioner": {"name": "Verdugo", "elixir": 5},
}

# Configuracion de tiempos de elixir (en segundos)
ELIXIR_CONFIG = {
    "normal_rate": 2.8,      # Segundos por 1 elixir en tiempo normal
    "double_rate": 1.4,      # Segundos por 1 elixir en 2x
    "triple_rate": 0.9,      # Segundos por 1 elixir en 3x
    "max_elixir": 10,        # Maximo elixir
    "starting_elixir": 5,    # Elixir inicial
}

# Configuracion de la pantalla de captura
# NOTA: Estos valores deben ajustarse segun tu resolucion
SCREEN_CONFIG = {
    # Region donde aparecen las cartas del rival cuando las juega
    # Formato: (x, y, width, height)
    # Ajustado para tu pantalla - Clash Royale esta a la derecha
    "capture_region": (343, 28, 557, 1000),  # Solo la ventana del juego (incluye cartas)

    # Zona de la arena donde detectar cartas jugadas (relativo a capture_region)
    "arena_top": 120,        # Y superior de la arena
    "arena_bottom": 650,    # Y inferior de la arena
    "arena_left": 27,       # X izquierdo de la arena
    "arena_right": 529,     # X derecho de la arena

    # Tamano esperado de las cartas en el juego (para template matching)
    "card_width": 65,
    "card_height": 80,

    # FPS de captura (mayor = mas responsivo pero mas CPU)
    "capture_fps": 10,
}

# Umbral de confianza para deteccion de cartas (0.0 - 1.0)
# Mas bajo = mas detecciones (puede haber falsos positivos)
# Mas alto = menos detecciones (mas preciso)
DETECTION_THRESHOLD = 0.55

# Colores para la interfaz (formato RGB)
COLORS = {
    "elixir_purple": "#9B30FF",
    "elixir_bg": "#2D2D2D",
    "card_known": "#4CAF50",
    "card_unknown": "#757575",
    "text_white": "#FFFFFF",
    "bg_dark": "#1E1E1E",
    "highlight": "#FFD700",
}
