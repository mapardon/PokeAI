MIN_HP, MAX_HP = 150, 200
MIN_STAT, MAX_STAT = 60, 140
MIN_POW, MAX_POW = 50, 100

MAX_ROUNDS = 50

NB_POKEMON = 3
NB_MOVES = 3

TYPES = ['BUG', 'DARK', 'DRAGON', 'ELECTRIC', 'FAIRY', 'FIGHTING', 'FIRE', 'FLYING', 'GHOST', 'GRASS', 'GROUND', 'ICE',
         'STEEL', 'NORMAL', 'POISON', 'PSYCHIC', 'ROCK', 'WATER']

#  {offensive: {defensive: multiplier}}
TYPE_CHART = {'NORMAL': {'ROCK': 0.5, 'GHOST': 0, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'FIRE': {'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 2, 'BUG': 2, 'ROCK': 0.5, 'DRAGON': 0.5, 'STEEL': 2, 'NORMAL': 1, 'ELECTRIC': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'WATER': {'FIRE': 2, 'WATER': 0.5, 'GRASS': 0.5, 'GROUND': 2, 'ROCK': 2, 'DRAGON': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'GHOST': 1, 'DARK': 1, 'STEEL': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'ELECTRIC': {'WATER': 2, 'ELECTRIC': 0.5, 'GRASS': 0.5, 'GROUND': 0, 'FLYING': 2, 'DRAGON': 0.5, 'NORMAL': 1, 'FIRE': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1, 'STEEL': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'GRASS': {'FIRE': 0.5, 'WATER': 2, 'GRASS': 0.5, 'POISON': 0.5, 'GROUND': 2, 'FLYING': 0.5, 'BUG': 0.5, 'ROCK': 2, 'DRAGON': 0.5, 'STEEL': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'ICE': {'FIRE': 0.5, 'WATER': 0.5, 'GRASS': 2, 'ICE': 0.5, 'GROUND': 2, 'FLYING': 2, 'DRAGON': 2, 'STEEL': 0.5, 'NORMAL': 1, 'ELECTRIC': 1, 'FIGHTING': 1, 'POISON': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'FIGHTING': {'NORMAL': 2, 'ICE': 2, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 0.5, 'BUG': 0.5, 'ROCK': 2, 'GHOST': 0, 'DARK': 2, 'STEEL': 2, 'FAIRY': 0.5, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'FIGHTING': 1, 'GROUND': 1, 'DRAGON': 1, 'NOTYPE': 1},
              'POISON': {'GRASS': 2, 'POISON': 0.5, 'GROUND': 0.5, 'ROCK': 0.5, 'GHOST': 0.5, 'STEEL': 0, 'FAIRY': 2, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'ICE': 1, 'FIGHTING': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'DRAGON': 1, 'DARK': 1, 'NOTYPE': 1},
              'GROUND': {'FIRE': 2, 'ELECTRIC': 2, 'GRASS': 0.5, 'POISON': 2, 'FLYING': 0, 'BUG': 0.5, 'ROCK': 2, 'STEEL': 2, 'NORMAL': 1, 'WATER': 1, 'ICE': 1, 'FIGHTING': 1, 'GROUND': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'FLYING': {'ELECTRIC': 0.5, 'GRASS': 2, 'FIGHTING': 2, 'BUG': 2, 'ROCK': 0.5, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ICE': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'PSYCHIC': {'FIGHTING': 2, 'POISON': 2, 'PSYCHIC': 0.5, 'DARK': 0, 'STEEL': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DRAGON': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'BUG': {'FIRE': 0.5, 'GRASS': 2, 'FIGHTING': 0.5, 'POISON': 0.5, 'FLYING': 0.5, 'PSYCHIC': 2, 'GHOST': 0.5, 'DARK': 2, 'STEEL': 0.5, 'FAIRY': 0.5, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'ICE': 1, 'GROUND': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1, 'NOTYPE': 1},
              'ROCK': {'FIRE': 2, 'ICE': 2, 'FIGHTING': 0.5, 'GROUND': 0.5, 'FLYING': 2, 'BUG': 2, 'STEEL': 0.5, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'POISON': 1, 'PSYCHIC': 1, 'ROCK': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'GHOST': {'NORMAL': 0, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1, 'STEEL': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'DRAGON': {'DRAGON': 2, 'STEEL': 0.5, 'FAIRY': 0, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'DARK': 1, 'NOTYPE': 1},
              'DARK': {'FIGHTING': 0.5, 'PSYCHIC': 2, 'GHOST': 2, 'DARK': 0.5, 'FAIRY': 0.5, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'BUG': 1, 'ROCK': 1, 'DRAGON': 1, 'STEEL': 1, 'NOTYPE': 1},
              'STEEL': {'FIRE': 0.5, 'WATER': 0.5, 'ELECTRIC': 0.5, 'ICE': 2, 'ROCK': 2, 'STEEL': 0.5, 'FAIRY': 2, 'NORMAL': 1, 'GRASS': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'GHOST': 1, 'DRAGON': 1, 'DARK': 1, 'NOTYPE': 1},
              'FAIRY': {'FIRE': 0.5, 'FIGHTING': 2, 'POISON': 0.5, 'DRAGON': 2, 'DARK': 2, 'STEEL': 1, 'NORMAL': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'ROCK': 1, 'GHOST': 1, 'FAIRY': 1, 'NOTYPE': 1},
              'NOTYPE': {'ROCK': 1, 'GHOST': 1, 'STEEL': 1, 'NORMAL': 1, 'FIRE': 1, 'WATER': 1, 'ELECTRIC': 1, 'GRASS': 1, 'ICE': 1, 'FIGHTING': 1, 'POISON': 1, 'GROUND': 1, 'FLYING': 1, 'PSYCHIC': 1, 'BUG': 1, 'DRAGON': 1, 'DARK': 1, 'FAIRY': 1, 'NOTYPE': 1}}

TYPES_INDEX = {
    'NORMAL': 0,
    'FIRE': 1,
    'WATER': 2,
    'ELECTRIC': 3,
    'GRASS': 4,
    'ICE': 5,
    'FIGHTING': 6,
    'POISON': 7,
    'GROUND': 8,
    'FLYING': 9,
    'PSYCHIC': 10,
    'BUG': 11,
    'ROCK': 12,
    'GHOST': 13,
    'DRAGON': 14,
    'DARK': 15,
    'STEEL': 16,
    'FAIRY': 17,
    'NOTYPE': 18
}

MOVES = {
    'light_normal': ('NORMAL', 50),
    'heavy_normal': ('NORMAL', 100),
    'light_fire': ('FIRE', 50),
    'heavy_fire': ('FIRE', 100),
    'light_water': ('WATER', 50),
    'heavy_water': ('WATER', 100),
    'light_electric': ('ELECTRIC', 50),
    'heavy_electric': ('ELECTRIC', 100),
    'light_grass': ('GRASS', 50),
    'heavy_grass': ('GRASS', 100),
    'light_ice': ('ICE', 50),
    'heavy_ice': ('ICE', 100),
    'light_fighting': ('FIGHTING', 50),
    'heavy_fighting': ('FIGHTING', 100),
    'light_poison': ('POISON', 50),
    'heavy_poison': ('POISON', 100),
    'light_ground': ('GROUND', 50),
    'heavy_ground': ('GROUND', 100),
    'light_flying': ('FLYING', 50),
    'heavy_flying': ('FLYING', 100),
    'light_psychic': ('PSYCHIC', 50),
    'heavy_psychic': ('PSYCHIC', 100),
    'light_bug': ('BUG', 50),
    'heavy_bug': ('BUG', 100),
    'light_rock': ('ROCK', 50),
    'heavy_rock': ('ROCK', 100),
    'light_ghost': ('GHOST', 50),
    'heavy_ghost': ('GHOST', 100),
    'light_dragon': ('DRAGON', 50),
    'heavy_dragon': ('DRAGON', 100),
    'light_dark': ('DARK', 50),
    'heavy_dark': ('DARK', 100),
    'light_steel': ('STEEL', 50),
    'heavy_steel': ('STEEL', 100),
    'light_fairy': ('FAIRY', 50),
    'heavy_fairy': ('FAIRY', 100),
    'light_notype': ('NOTYPE', 50),
    'heavy_notype': ('NOTYPE', 100)
}
