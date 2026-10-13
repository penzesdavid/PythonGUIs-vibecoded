"""
Damareen Kártyajáték - Játéklogika modul
Dusza Árpád Országos Programozói Emlékverseny 2025/2026 - I. forduló
"""

import os
import math
from typing import Dict, List, Optional, Tuple


class Card:
    """Kártya adatmodell"""
    def __init__(self, name: str, damage: int, hp: int, element: str, is_boss: bool = False):
        self.name: str = name
        self.damage: int = int(damage)
        self.max_hp: int = int(hp)
        self.hp: int = int(hp)
        self.element: str = element.lower().strip()
        self.is_boss: bool = is_boss

    def clone(self) -> 'Card':
        c = Card(self.name, self.damage, self.max_hp, self.element, self.is_boss)
        c.hp = self.max_hp
        return c

    def reset_hp(self):
        self.hp = self.max_hp

    def __repr__(self):
        return f"Card({self.name}, {self.damage}/{self.max_hp}, {self.element}{', VEZÉR' if self.is_boss else ''})"


class Dungeon:
    """Kazamata adatmodell"""
    def __init__(self, dtype: str, name: str, plain_card_names: List[str],
                 boss_card_name: Optional[str] = None, reward_type: Optional[str] = None):
        self.dtype: str = dtype.lower().strip()  # 'egyszeru', 'kis', 'nagy'
        self.name: str = name
        self.plain_card_names: List[str] = plain_card_names
        self.boss_card_name: Optional[str] = boss_card_name
        self.reward_type: Optional[str] = reward_type.lower().strip() if reward_type else None

    def get_all_cards(self, game_state: 'GameState') -> List[Card]:
        cards: List[Card] = []
        for name in self.plain_card_names:
            if name in game_state.world_cards:
                cards.append(game_state.world_cards[name].clone())
        if self.boss_card_name and self.boss_card_name in game_state.boss_cards:
            cards.append(game_state.boss_cards[self.boss_card_name].clone())
        return cards


# Elem-kapcsolatok a 7. oldali ábra alapján
# Szomszédos (erős / 2x): levego-fold, levego-viz, fold-tuz, viz-tuz
# Átlós / Ellentétes (gyenge / 0.5x, lefelé kerekítve): levego-tuz, fold-viz
# Azonos: 1x
EROS_PAROK = {
    ('levego', 'fold'), ('fold', 'levego'),
    ('levego', 'viz'), ('viz', 'levego'),
    ('fold', 'tuz'), ('tuz', 'fold'),
    ('viz', 'tuz'), ('tuz', 'viz')
}

GYENGE_PAROK = {
    ('levego', 'tuz'), ('tuz', 'levego'),
    ('fold', 'viz'), ('viz', 'fold')
}


def calculate_damage(attacker_elem: str, defender_elem: str, base_dmg: int) -> Tuple[int, float, str]:
    """
    Kiszámítja a tényleges sebzést a két elem kapcsolata alapján.
    Visszatér: (tényleges_sebzés, szorzó, leírás)
    """
    pair = (attacker_elem.lower().strip(), defender_elem.lower().strip())
    if pair in EROS_PAROK:
        return base_dmg * 2, 2.0, "erős (2x)"
    elif pair in GYENGE_PAROK:
        return base_dmg // 2, 0.5, "gyenge (0.5x)"
    else:
        return base_dmg, 1.0, "semleges (1x)"


class BattleResult:
    """Egy harc kimenetelének és lépéseinek tárolója"""
    def __init__(self, winner: str, reward_line: str, log_lines: List[str], event_steps: List[dict]):
        self.winner: str = winner  # 'jatekos' vagy 'kazamata'
        self.reward_line: str = reward_line
        self.log_lines: List[str] = log_lines
        self.event_steps: List[dict] = event_steps


class GameState:
    """A játék állapotát és logikáját kezelő osztály"""
    def __init__(self):
        self.world_cards: Dict[str, Card] = {}
        self.boss_cards: Dict[str, Card] = {}
        self.dungeons: Dict[str, Dungeon] = {}
        self.player_collection: Dict[str, Card] = {}
        self.player_deck: List[str] = []

    def add_plain_card(self, name: str, damage: int, hp: int, element: str):
        card = Card(name, int(damage), int(hp), element, is_boss=False)
        self.world_cards[name] = card

    def add_boss_card(self, boss_name: str, base_name: str, upgrade_type: str):
        if base_name not in self.world_cards:
            raise ValueError(f"Ismeretlen alap kártya: {base_name}")
        base = self.world_cards[base_name]
        dmg = base.damage * 2 if upgrade_type.lower() == 'sebzes' else base.damage
        hp = base.max_hp * 2 if upgrade_type.lower() == 'eletero' else base.max_hp
        boss = Card(boss_name, dmg, hp, base.element, is_boss=True)
        self.boss_cards[boss_name] = boss

    def add_dungeon(self, dtype: str, name: str, card_names: List[str],
                    boss_name: Optional[str] = None, reward_type: Optional[str] = None):
        dungeon = Dungeon(dtype, name, card_names, boss_name, reward_type)
        self.dungeons[name] = dungeon

    def add_to_collection(self, card_name: str):
        if card_name not in self.world_cards:
            raise ValueError(f"A kártya nem található a világban: {card_name}")
        if card_name not in self.player_collection:
            self.player_collection[card_name] = self.world_cards[card_name].clone()

    def get_max_deck_size(self) -> int:
        """A pakli legfeljebb a gyűjtemény fele, felfelé kerekítve."""
        coll_size = len(self.player_collection)
        return math.ceil(coll_size / 2) if coll_size > 0 else 0

    def set_deck(self, card_names: List[str]):
        max_size = self.get_max_deck_size()
        if len(card_names) > max_size:
            raise ValueError(f"A pakli mérete ({len(card_names)}) meghaladja a maximumot ({max_size})!")
        for cname in card_names:
            if cname not in self.player_collection:
                raise ValueError(f"A kártya nincs a gyűjteményben: {cname}")
        self.player_deck = list(card_names)

    def can_challenge_dungeon(self, dungeon_name: str) -> Tuple[bool, str]:
        if dungeon_name not in self.dungeons:
            return False, f"Ismeretlen kazamata: {dungeon_name}"
        if not self.player_deck:
            return False, "Nincs összeállítva aktív pakli a harchoz!"
        
        dungeon = self.dungeons[dungeon_name]
        if dungeon.dtype == 'nagy':
            # Nagy kazamata esetén kell lennie olyan sima kártyának a világban, ami nincs meg
            available_world_cards = [
                c.name for c in self.world_cards.values()
                if c.name not in self.player_collection
            ]
            if not available_world_cards:
                return False, "Már minden sima kártya megvan a gyűjteményedben, a Nagy kazamata nem indítható!"
        
        return True, "Rendben"

    def execute_battle(self, dungeon_name: str) -> BattleResult:
        if dungeon_name not in self.dungeons:
            raise ValueError(f"Kazamata nem létezik: {dungeon_name}")
        dungeon = self.dungeons[dungeon_name]

        # Kazamata lapok előkészítése
        kazamata_queue = dungeon.get_all_cards(self)
        # Játékos pakli lapok előkészítése (a gyűjteményben elért aktuális fejlesztésekkel)
        player_queue = [self.player_collection[cname].clone() for cname in self.player_deck]

        active_kazamata: Optional[Card] = None
        active_player: Optional[Card] = None
        last_played_player_card_name: Optional[str] = None

        log_lines: List[str] = [f"harc kezdodik;{dungeon.name}"]
        event_steps: List[dict] = []
        round_num = 1

        while True:
            # === 1. AKCIÓ: KAZAMATA ===
            if active_kazamata is None:
                if not kazamata_queue:
                    # Nincs több kazamata lap
                    break
                active_kazamata = kazamata_queue.pop(0)
                log_lines.append(
                    f"{round_num}.kor;kazamata;kijatszik;{active_kazamata.name};{active_kazamata.damage};{active_kazamata.hp};{active_kazamata.element}"
                )
                event_steps.append({
                    'round': round_num,
                    'actor': 'kazamata',
                    'action': 'kijatszik',
                    'card': active_kazamata.name,
                    'damage': active_kazamata.damage,
                    'hp': active_kazamata.hp,
                    'element': active_kazamata.element
                })
            else:
                # Kazamata támad a játékos lapjára
                dmg, mult, desc = calculate_damage(active_kazamata.element, active_player.element, active_kazamata.damage)
                active_player.hp = max(0, active_player.hp - dmg)
                log_lines.append(
                    f"{round_num}.kor;kazamata;tamad;{active_kazamata.name};{dmg};{active_player.name};{active_player.hp}"
                )
                event_steps.append({
                    'round': round_num,
                    'actor': 'kazamata',
                    'action': 'tamad',
                    'attacker': active_kazamata.name,
                    'damage': dmg,
                    'multiplier': mult,
                    'defender': active_player.name,
                    'defender_hp': active_player.hp
                })

                if active_player.hp == 0:
                    active_player = None
                    if not player_queue:
                        # Játékos elvesztette a harcot
                        # "Ha az utolsó körben a kazamata nyer, akkor abban a körben csak egyetlen akció születik"
                        log_lines.append("jatekos vesztett")
                        event_steps.append({
                            'round': round_num,
                            'event': 'game_over',
                            'winner': 'kazamata'
                        })
                        return BattleResult('kazamata', 'jatekos vesztett', log_lines, event_steps)

            # === 2. AKCIÓ: JÁTÉKOS ===
            if active_player is None:
                if not player_queue:
                    log_lines.append("jatekos vesztett")
                    event_steps.append({
                        'round': round_num,
                        'event': 'game_over',
                        'winner': 'kazamata'
                    })
                    return BattleResult('kazamata', 'jatekos vesztett', log_lines, event_steps)
                
                active_player = player_queue.pop(0)
                last_played_player_card_name = active_player.name
                log_lines.append(
                    f"{round_num}.kor;jatekos;kijatszik;{active_player.name};{active_player.damage};{active_player.hp};{active_player.element}"
                )
                event_steps.append({
                    'round': round_num,
                    'actor': 'jatekos',
                    'action': 'kijatszik',
                    'card': active_player.name,
                    'damage': active_player.damage,
                    'hp': active_player.hp,
                    'element': active_player.element
                })
            else:
                # Játékos támad a kazamata lapjára
                dmg, mult, desc = calculate_damage(active_player.element, active_kazamata.element, active_player.damage)
                active_kazamata.hp = max(0, active_kazamata.hp - dmg)
                log_lines.append(
                    f"{round_num}.kor;jatekos;tamad;{active_player.name};{dmg};{active_kazamata.name};{active_kazamata.hp}"
                )
                event_steps.append({
                    'round': round_num,
                    'actor': 'jatekos',
                    'action': 'tamad',
                    'attacker': active_player.name,
                    'damage': dmg,
                    'multiplier': mult,
                    'defender': active_kazamata.name,
                    'defender_hp': active_kazamata.hp
                })

                if active_kazamata.hp == 0:
                    active_kazamata = None
                    if not kazamata_queue:
                        # Kazamata összes lapja elesett -> JÁTÉKOS NYERT!
                        reward_line = self._apply_win_reward(dungeon, last_played_player_card_name or active_player.name)
                        log_lines.append(f"jatekos nyert;{reward_line}")
                        event_steps.append({
                            'round': round_num,
                            'event': 'game_over',
                            'winner': 'jatekos',
                            'reward': reward_line
                        })
                        return BattleResult('jatekos', reward_line, log_lines, event_steps)

            round_num += 1

        # Biztonsági visszatérés
        return BattleResult('kazamata', 'jatekos vesztett', log_lines, event_steps)

    def _apply_win_reward(self, dungeon: Dungeon, winning_card_name: str) -> str:
        """Feldolgozza és érvényesíti a harc nyereményét a játékos gyűjteményében."""
        if dungeon.dtype in ('egyszeru', 'kis'):
            if dungeon.reward_type == 'sebzes':
                if winning_card_name in self.player_collection:
                    self.player_collection[winning_card_name].damage += 1
                return f"sebzes;{winning_card_name}"
            elif dungeon.reward_type == 'eletero':
                if winning_card_name in self.player_collection:
                    self.player_collection[winning_card_name].max_hp += 2
                    self.player_collection[winning_card_name].hp += 2
                return f"eletero;{winning_card_name}"
            return f"eletero;{winning_card_name}"
        elif dungeon.dtype == 'nagy':
            # 1 sima kártyát kap a gyűjteményébe a világból - az első olyat, ami még nincs meg
            reward_card_name = None
            for card in self.world_cards.values():
                if card.name not in self.player_collection:
                    reward_card_name = card.name
                    self.player_collection[card.name] = card.clone()
                    break
            return f"{reward_card_name}" if reward_card_name else "Nincs tobb lap"
        return ""

    def export_world(self) -> List[str]:
        lines: List[str] = []
        for card in self.world_cards.values():
            lines.append(f"kartya;{card.name};{card.damage};{card.max_hp};{card.element}")
        for boss in self.boss_cards.values():
            lines.append(f"vezer;{boss.name};{boss.damage};{boss.max_hp};{boss.element}")
        for dun in self.dungeons.values():
            cards_str = ",".join(dun.plain_card_names)
            if dun.dtype == 'egyszeru':
                lines.append(f"kazamata;egyszeru;{dun.name};{cards_str};{dun.reward_type}")
            elif dun.dtype == 'kis':
                lines.append(f"kazamata;kis;{dun.name};{cards_str};{dun.boss_card_name};{dun.reward_type}")
            elif dun.dtype == 'nagy':
                lines.append(f"kazamata;nagy;{dun.name};{cards_str};{dun.boss_card_name}")
        return lines

    def export_player(self) -> List[str]:
        lines: List[str] = []
        for card in self.player_collection.values():
            lines.append(f"gyujtemeny;{card.name};{card.damage};{card.max_hp};{card.element}")
        for card_name in self.player_deck:
            lines.append(f"pakli;{card_name}")
        return lines

    def parse_in_file(self, filepath: str, working_dir: Optional[str] = None):
        """Feldolgozza az in.txt bemeneti fájlt és végrehajtja a parancsokat."""
        if working_dir is None:
            working_dir = os.path.dirname(os.path.abspath(filepath))

        with open(filepath, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(';')]
                cmd = parts[0].lower()

                if cmd == 'uj kartya':
                    # uj kartya;Aragorn;2;5;tuz
                    _, name, dmg, hp, elem = parts
                    self.add_plain_card(name, int(dmg), int(hp), elem)

                elif cmd == 'uj vezer':
                    # uj vezer;Darth ObiWan;ObiWan;sebzes
                    _, boss_name, base_name, utype = parts
                    self.add_boss_card(boss_name, base_name, utype)

                elif cmd == 'uj kazamata':
                    # uj kazamata;egyszeru;Teszt1a Kazamata;Sadan;eletero
                    # uj kazamata;kis;Teszt2a Kazamata;Aragorn,Eowyn,ObiWan;Darth ObiWan;eletero
                    # uj kazamata;nagy;Teszt3 Kazamata;Aragorn,Eowyn,ObiWan,Kira,Tul'Arak;Darth ObiWan
                    dtype = parts[1].lower()
                    dname = parts[2]
                    if dtype == 'egyszeru':
                        cards = [parts[3]]
                        reward = parts[4]
                        self.add_dungeon(dtype, dname, cards, boss_name=None, reward_type=reward)
                    elif dtype == 'kis':
                        cards = [c.strip() for c in parts[3].split(',')]
                        boss_name = parts[4]
                        reward = parts[5]
                        self.add_dungeon(dtype, dname, cards, boss_name=boss_name, reward_type=reward)
                    elif dtype == 'nagy':
                        cards = [c.strip() for c in parts[3].split(',')]
                        boss_name = parts[4]
                        self.add_dungeon(dtype, dname, cards, boss_name=boss_name, reward_type=None)

                elif cmd == 'uj jatekos':
                    # Elválasztó elem
                    pass

                elif cmd == 'felvetel gyujtemenybe':
                    # felvetel gyujtemenybe;Aragorn
                    card_name = parts[1]
                    self.add_to_collection(card_name)

                elif cmd == 'uj pakli':
                    # uj pakli;Corky,Kira
                    card_names = [c.strip() for c in parts[1].split(',') if c.strip()]
                    self.set_deck(card_names)

                elif cmd == 'harc':
                    # harc;Teszt1a Kazamata;out.harc01.txt
                    dname = parts[1]
                    out_filename = parts[2]
                    out_path = os.path.join(working_dir, out_filename)
                    result = self.execute_battle(dname)
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.write("\n".join(result.log_lines) + "\n")

                elif cmd == 'export vilag':
                    # export vilag;out.vilag01.txt
                    out_filename = parts[1]
                    out_path = os.path.join(working_dir, out_filename)
                    lines = self.export_world()
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.write("\n".join(lines) + "\n")

                elif cmd == 'export jatekos':
                    # export jatekos;out.jatekos02.txt
                    out_filename = parts[1]
                    out_path = os.path.join(working_dir, out_filename)
                    lines = self.export_player()
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.write("\n".join(lines) + "\n")

    @staticmethod
    def get_default_game_state() -> 'GameState':
        """
        Létrehozza a versenykiírás 2. pontjában (10-11. oldal) specifikált alapértelmezett
        világot, kazamatákat és játékos gyűjteményt a Játék módhoz (--ui).
        """
        gs = GameState()

        # 1. Sima kártyák (11 darab a kiírás sorrendjében)
        plain_cards_def = [
            ("Arin", 2, 5, "fold"),
            ("Liora", 2, 4, "levego"),
            ("Nerun", 3, 3, "tuz"),
            ("Selia", 2, 6, "viz"),
            ("Torak", 3, 4, "fold"),
            ("Emera", 2, 5, "levego"),
            ("Vorn", 2, 7, "viz"),
            ("Kael", 3, 5, "tuz"),
            ("Myra", 2, 6, "fold"),
            ("Thalen", 3, 5, "levego"),
            ("Isara", 2, 6, "viz")
        ]
        for name, dmg, hp, elem in plain_cards_def:
            gs.add_plain_card(name, dmg, hp, elem)

        # 2. Vezérkártyák (2 darab)
        # Lord Torak: Torakból sebzés duplázással (3*2=6, 4)
        gs.add_boss_card("Lord Torak", "Torak", "sebzes")
        # Priestess Selia: Seliából életerő duplázással (2, 6*2=12)
        gs.add_boss_card("Priestess Selia", "Selia", "eletero")

        # 3. Kazamaták (3 darab)
        # Barlangi Portya: Egyszerű, Nerun, sebzés
        gs.add_dungeon("egyszeru", "Barlangi Portya", ["Nerun"], boss_name=None, reward_type="sebzes")
        # Osi Szentely: Kis kazamata, Arin, Emera, Selia, Lord Torak, életerő
        gs.add_dungeon("kis", "Osi Szentely", ["Arin", "Emera", "Selia"], boss_name="Lord Torak", reward_type="eletero")
        # A melyseg kiralynoje: Nagy kazamata, Liora, Arin, Selia, Nerun, Torak, Priestess Selia
        gs.add_dungeon("nagy", "A melyseg kiralynoje", ["Liora", "Arin", "Selia", "Nerun", "Torak"], boss_name="Priestess Selia")

        # 4. Játékos kezdeti gyűjteménye (10 lap - Vorn kivételével mind)
        player_cards = ["Arin", "Liora", "Selia", "Nerun", "Torak", "Emera", "Kael", "Myra", "Thalen", "Isara"]
        for cname in player_cards:
            gs.add_to_collection(cname)

        # Alapértelmezett kezdő pakli (legfeljebb gyűjtemény fele: ceil(10/2) = 5 lap)
        default_deck = ["Arin", "Liora", "Selia", "Nerun", "Torak"]
        gs.set_deck(default_deck)

        return gs
