"""
Damareen Kártyajáték - Modern Grafikus Felület (CustomTkinter GUI)
Dusza Árpád Országos Programozói Emlékverseny 2025/2026 - I. forduló
Design téma: Obszidián & Misztikus Arany (Obsidian & Arcane Gold)
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, List, Dict
from game_logic import GameState, Card, Dungeon, calculate_damage, BattleResult

# CustomTkinter globális beállítások
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Téma színpaletta: Obszidián & Misztikus Arany
THEME = {
    'bg_app': '#0c0d14',
    'bg_sidebar': '#11121d',
    'bg_card': '#191b29',
    'bg_card_highlight': '#23263a',
    'bg_card_inner': '#131420',
    'border_subtle': '#2a2d42',
    'border_gold': '#d4af37',
    
    # Kiemelő színek
    'gold': '#d4af37',
    'gold_hover': '#f39c12',
    'gold_light': '#f9e79f',
    'crimson': '#e74c3c',
    'emerald': '#2ecc71',
    'cyan': '#3498db',
    'purple': '#9b59b6',
    
    # Szövegszínek
    'text_primary': '#ffffff',
    'text_secondary': '#a5a9c2',
    'text_muted': '#656883',
    
    # Elemek
    'elem_fold': '#27ae60',
    'elem_fold_bg': '#143823',
    'elem_levego': '#8e44ad',
    'elem_levego_bg': '#33193e',
    'elem_viz': '#2980b9',
    'elem_viz_bg': '#152e42',
    'elem_tuz': '#c0392b',
    'elem_tuz_bg': '#421714',
}

ELEM_ICONS = {
    'fold': '🌱',
    'levego': '🌪️',
    'viz': '💧',
    'tuz': '🔥'
}

ELEM_NAMES = {
    'fold': 'Föld',
    'levego': 'Levegő',
    'viz': 'Víz',
    'tuz': 'Tűz'
}


class DamareenModernGUI(ctk.CTk):
    def __init__(self, game_state: Optional[GameState] = None):
        super().__init__()

        self.title("Damareen – Fantasy Kártyajáték (Dusza Árpád 2025/2026)")
        self.geometry("1180x820")
        self.minsize(1040, 740)
        self.configure(fg_color=THEME['bg_app'])

        # Játékállapot
        self.gs: GameState = game_state if game_state else GameState.get_default_game_state()

        # Harci állapotok
        self.current_battle_result: Optional[BattleResult] = None
        self.current_event_index: int = 0
        self.selected_dungeon_name: str = "Barlangi Portya"
        self.is_auto_playing: bool = False
        self.auto_play_timer = None

        self._init_layout()
        self._select_nav('battle')
        self._update_all_views()

    def _init_layout(self):
        # 1. Bal oldali navigációs Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=THEME['bg_sidebar'])
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # 2. Jobb oldali tartalom terület
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=THEME['bg_app'])
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_views()

    # =========================================================================
    # SIDEBAR ÉS NAVIGÁCIÓ
    # =========================================================================
    def _build_sidebar(self):
        # Logó & Fejléc
        title_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        title_box.pack(fill=tk.X, padx=16, pady=(20, 15))

        logo_lbl = ctk.CTkLabel(title_box, text="⚔️ DAMAREEN", font=ctk.CTkFont(size=20, weight="bold"),
                                text_color=THEME['gold'])
        logo_lbl.pack(anchor='w')

        sub_lbl = ctk.CTkLabel(title_box, text="Fantasy Kártyajáték • I. Forduló",
                               font=ctk.CTkFont(size=11), text_color=THEME['text_secondary'])
        sub_lbl.pack(anchor='w')

        # Gyors Játékos Statisztikák doboz
        self.stats_panel = ctk.CTkFrame(self.sidebar_frame, fg_color=THEME['bg_card'],
                                        corner_radius=10, border_width=1, border_color=THEME['border_subtle'])
        self.stats_panel.pack(fill=tk.X, padx=14, pady=(0, 20))

        self.stat_coll_lbl = ctk.CTkLabel(self.stats_panel, text="Gyűjtemény: 10 lap",
                                          font=ctk.CTkFont(size=12, weight="bold"),
                                          text_color=THEME['text_primary'])
        self.stat_coll_lbl.pack(anchor='w', padx=12, pady=(8, 2))

        self.stat_deck_lbl = ctk.CTkLabel(self.stats_panel, text="Pakli: 5 / 5 lap",
                                          font=ctk.CTkFont(size=12, weight="bold"),
                                          text_color=THEME['gold'])
        self.stat_deck_lbl.pack(anchor='w', padx=12, pady=(0, 8))

        # Navigációs gombok
        nav_items = [
            ('battle', '⚔️ Kaland & Harc'),
            ('deck', '🃏 Pakliépítő'),
            ('codex', '📜 Világ Kódex'),
            ('rules', '📖 Szabályzat & Elemek')
        ]

        self.nav_buttons = {}
        for key, text in nav_items:
            btn = ctk.CTkButton(self.sidebar_frame, text=text,
                                font=ctk.CTkFont(size=13, weight="bold"),
                                anchor='w', height=42, corner_radius=8,
                                fg_color="transparent", text_color=THEME['text_secondary'],
                                hover_color=THEME['bg_card_highlight'],
                                command=lambda k=key: self._select_nav(k))
            btn.pack(fill=tk.X, padx=12, pady=4)
            self.nav_buttons[key] = btn

        # Alsó lábléc és alaphelyzetbe állítás
        footer_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        footer_box.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=16)

        reset_btn = ctk.CTkButton(footer_box, text="🔄 Alaphelyzet",
                                  font=ctk.CTkFont(size=11), height=30,
                                  fg_color=THEME['bg_card'], text_color=THEME['text_muted'],
                                  hover_color=THEME['border_subtle'],
                                  command=self._on_reset_game)
        reset_btn.pack(fill=tk.X, pady=(0, 8))

        dusza_lbl = ctk.CTkLabel(footer_box, text="Dusza Árpád 2025/2026",
                                 font=ctk.CTkFont(size=10), text_color=THEME['text_muted'])
        dusza_lbl.pack()

    def _select_nav(self, key: str):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=THEME['bg_card_highlight'], text_color=THEME['gold'])
            else:
                btn.configure(fg_color="transparent", text_color=THEME['text_secondary'])

        for k, frame in self.views.items():
            if k == key:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

    # =========================================================================
    # NÉZETEK FELÉPÍTÉSE
    # =========================================================================
    def _build_views(self):
        self.views = {
            'battle': ctk.CTkFrame(self.content_frame, fg_color=THEME['bg_app'], corner_radius=0),
            'deck': ctk.CTkFrame(self.content_frame, fg_color=THEME['bg_app'], corner_radius=0),
            'codex': ctk.CTkFrame(self.content_frame, fg_color=THEME['bg_app'], corner_radius=0),
            'rules': ctk.CTkFrame(self.content_frame, fg_color=THEME['bg_app'], corner_radius=0)
        }

        self._build_battle_view()
        self._build_deck_view()
        self._build_codex_view()
        self._build_rules_view()

    # =========================================================================
    # 1. KALAND ÉS HARCI CSATATÉR
    # =========================================================================
    def _build_battle_view(self):
        view = self.views['battle']

        # FELSŐ SÁV: Kazamata választó kártyák
        dungeon_bar = ctk.CTkFrame(view, fg_color=THEME['bg_card'], corner_radius=12,
                                   border_width=1, border_color=THEME['border_subtle'])
        dungeon_bar.pack(fill=tk.X, padx=16, pady=(16, 10))

        dun_hdr_box = ctk.CTkFrame(dungeon_bar, fg_color="transparent")
        dun_hdr_box.pack(fill=tk.X, padx=16, pady=(12, 6))

        ctk.CTkLabel(dun_hdr_box, text="🏰 Válassz Kazamatát a kihíváshoz:",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(side=tk.LEFT)

        self.dun_warning_lbl = ctk.CTkLabel(dun_hdr_box, text="", font=ctk.CTkFont(size=12),
                                            text_color=THEME['crimson'])
        self.dun_warning_lbl.pack(side=tk.RIGHT)

        # 3 Kazamata csempe
        self.dun_tiles_frame = ctk.CTkFrame(dungeon_bar, fg_color="transparent")
        self.dun_tiles_frame.pack(fill=tk.X, padx=12, pady=(0, 12))

        # KÖZÉPSŐ SÁV: Csatatér (Fantasy Battlefield)
        self.arena_frame = ctk.CTkFrame(view, fg_color=THEME['bg_card'], corner_radius=14,
                                        border_width=1, border_color=THEME['border_subtle'])
        self.arena_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)

        # Küzdőtér fejléc
        arena_top = ctk.CTkFrame(self.arena_frame, fg_color="transparent")
        arena_top.pack(fill=tk.X, padx=16, pady=(10, 5))

        self.round_badge = ctk.CTkLabel(arena_top, text="Készenlétben • Válassz kazamatát és indíts harcot",
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        text_color=THEME['text_secondary'])
        self.round_badge.pack(side=tk.LEFT)

        # Csatatér belső doboz: Játékos Kártya | VS & Elem Jelvény | Kazamata Kártya
        combat_inner = ctk.CTkFrame(self.arena_frame, fg_color=THEME['bg_card_inner'], corner_radius=12)
        combat_inner.pack(fill=tk.X, padx=16, pady=8)

        # Játékos Aktív Kártya (Bal)
        self.player_card_widget = self._create_battle_card_ui(combat_inner, "🛡️ JÁTÉKOS LAPJA", is_player=True)
        self.player_card_widget['frame'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Középső Elem-szorzó és VS panel
        mid_panel = ctk.CTkFrame(combat_inner, fg_color="transparent", width=180)
        mid_panel.pack(side=tk.LEFT, padx=5, pady=10)

        vs_text = ctk.CTkLabel(mid_panel, text="VS", font=ctk.CTkFont(size=24, weight="bold"),
                               text_color=THEME['gold'])
        vs_text.pack(pady=4)

        self.multiplier_badge = ctk.CTkLabel(mid_panel, text="—", font=ctk.CTkFont(size=12, weight="bold"),
                                             fg_color=THEME['bg_card'], corner_radius=6,
                                             text_color=THEME['text_muted'], padx=10, pady=6)
        self.multiplier_badge.pack(pady=6)

        # Kazamata Aktív Kártya (Jobb)
        self.enemy_card_widget = self._create_battle_card_ui(combat_inner, "💀 KAZAMATA ELLENFÉL", is_player=False)
        self.enemy_card_widget['frame'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tartalék kártyák előnézete
        reserves_frame = ctk.CTkFrame(self.arena_frame, fg_color="transparent")
        reserves_frame.pack(fill=tk.X, padx=20, pady=(2, 6))

        self.player_reserves_lbl = ctk.CTkLabel(reserves_frame, text="Pakli tartalék: —",
                                                font=ctk.CTkFont(size=11), text_color=THEME['text_muted'])
        self.player_reserves_lbl.pack(side=tk.LEFT)

        self.enemy_reserves_lbl = ctk.CTkLabel(reserves_frame, text="Kazamata tartalék: —",
                                               font=ctk.CTkFont(size=11), text_color=THEME['text_muted'])
        self.enemy_reserves_lbl.pack(side=tk.RIGHT)

        # Harci Vezérlősáv
        controls_bar = ctk.CTkFrame(self.arena_frame, fg_color="transparent")
        controls_bar.pack(fill=tk.X, padx=16, pady=8)

        self.start_battle_btn = ctk.CTkButton(controls_bar, text="⚔️ Harc Indítása",
                                              font=ctk.CTkFont(size=13, weight="bold"),
                                              fg_color=THEME['gold'], text_color='#000000',
                                              hover_color=THEME['gold_hover'], height=38,
                                              corner_radius=8, command=self._on_start_battle)
        self.start_battle_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.step_btn = ctk.CTkButton(controls_bar, text="⏩ Következő Akció",
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      fg_color=THEME['bg_card_highlight'], text_color=THEME['text_primary'],
                                      hover_color=THEME['border_subtle'], height=38,
                                      corner_radius=8, state="disabled", command=self._on_step_battle)
        self.step_btn.pack(side=tk.LEFT, padx=4)

        self.autoplay_btn = ctk.CTkButton(controls_bar, text="▶️ Folyamatos Lejátszás",
                                          font=ctk.CTkFont(size=12),
                                          fg_color=THEME['border_subtle'], text_color=THEME['text_primary'],
                                          hover_color=THEME['bg_card_highlight'], height=38,
                                          corner_radius=8, state="disabled", command=self._on_toggle_autoplay)
        self.autoplay_btn.pack(side=tk.LEFT, padx=4)

        self.skip_btn = ctk.CTkButton(controls_bar, text="⏭️ Azonnali Befejezés",
                                      font=ctk.CTkFont(size=12),
                                      fg_color=THEME['border_subtle'], text_color=THEME['text_secondary'],
                                      hover_color=THEME['bg_card_highlight'], height=38,
                                      corner_radius=8, state="disabled", command=self._on_skip_battle)
        self.skip_btn.pack(side=tk.LEFT, padx=4)

        # ALSÓ SÁV: Modern sötét terminál napló (Protokoll)
        log_frame = ctk.CTkFrame(view, fg_color=THEME['bg_card'], corner_radius=12,
                                border_width=1, border_color=THEME['border_subtle'], height=160)
        log_frame.pack(fill=tk.X, padx=16, pady=(6, 16))
        log_frame.pack_propagate(False)

        log_hdr = ctk.CTkLabel(log_frame, text="📜 Harci Eseménynapló (Protokoll)",
                               font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME['text_secondary'])
        log_hdr.pack(anchor='w', padx=14, pady=(8, 4))

        self.log_textbox = ctk.CTkTextbox(log_frame, fg_color='#090a10', text_color='#d1d4e6',
                                          font=ctk.CTkFont(family="Consolas", size=11),
                                          corner_radius=8, border_width=0)
        self.log_textbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _create_battle_card_ui(self, parent: ctk.CTkFrame, title: str, is_player: bool) -> dict:
        card_box = ctk.CTkFrame(parent, fg_color=THEME['bg_card'], corner_radius=12,
                                border_width=2, border_color=THEME['border_subtle'])

        hdr_lbl = ctk.CTkLabel(card_box, text=title, font=ctk.CTkFont(size=10, weight="bold"),
                               text_color=THEME['text_muted'])
        hdr_lbl.pack(anchor='w', padx=14, pady=(10, 2))

        name_lbl = ctk.CTkLabel(card_box, text="— Nincs kártya —", font=ctk.CTkFont(size=16, weight="bold"),
                                text_color=THEME['text_muted'])
        name_lbl.pack(anchor='w', padx=14, pady=2)

        elem_badge = ctk.CTkLabel(card_box, text="", font=ctk.CTkFont(size=11, weight="bold"),
                                  fg_color="transparent", corner_radius=6, padx=8, pady=2)
        elem_badge.pack(anchor='w', padx=14, pady=4)

        # Statisztika csíkok (ATK és HP)
        stats_frame = ctk.CTkFrame(card_box, fg_color="transparent")
        stats_frame.pack(fill=tk.X, padx=14, pady=6)

        atk_lbl = ctk.CTkLabel(stats_frame, text="⚔️ Sebzés: —", font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=THEME['gold'])
        atk_lbl.pack(side=tk.LEFT)

        hp_lbl = ctk.CTkLabel(stats_frame, text="❤️ Élet: —", font=ctk.CTkFont(size=12, weight="bold"),
                              text_color=THEME['emerald'])
        hp_lbl.pack(side=tk.RIGHT)

        hp_bar = ctk.CTkProgressBar(card_box, height=10, corner_radius=5,
                                    fg_color='#1f202e', progress_color=THEME['emerald'])
        hp_bar.pack(fill=tk.X, padx=14, pady=(2, 12))
        hp_bar.set(0)

        return {
            'frame': card_box,
            'name': name_lbl,
            'elem': elem_badge,
            'atk': atk_lbl,
            'hp': hp_lbl,
            'bar': hp_bar,
            'max_hp': 1
        }

    def _update_battle_card_ui(self, widget: dict, card_name: Optional[str], dmg: int,
                               hp: int, max_hp: int, elem: str, is_boss: bool = False):
        if not card_name:
            widget['frame'].configure(border_color=THEME['border_subtle'])
            widget['name'].configure(text="— Elesett / Nincs —", text_color=THEME['text_muted'])
            widget['elem'].configure(text="", fg_color="transparent")
            widget['atk'].configure(text="⚔️ Sebzés: —")
            widget['hp'].configure(text="❤️ Élet: —")
            widget['bar'].set(0)
            return

        boss_badge = " ⭐ [VEZÉR]" if is_boss else ""
        widget['name'].configure(text=f"{card_name}{boss_badge}",
                                 text_color=THEME['gold'] if is_boss else THEME['text_primary'])

        e_clean = elem.lower().strip()
        icon = ELEM_ICONS.get(e_clean, '')
        hum_name = ELEM_NAMES.get(e_clean, e_clean.capitalize())
        e_color = THEME.get(f'elem_{e_clean}', THEME['border_gold'])
        e_bg = THEME.get(f'elem_{e_clean}_bg', THEME['bg_card_highlight'])

        widget['frame'].configure(border_color=e_color)
        widget['elem'].configure(text=f"{icon} {hum_name}", fg_color=e_bg, text_color=e_color)
        widget['atk'].configure(text=f"⚔️ Sebzés: {dmg}")
        widget['hp'].configure(text=f"❤️ Élet: {hp} / {max_hp}")

        widget['max_hp'] = max(1, max_hp)
        ratio = max(0.0, min(1.0, hp / widget['max_hp']))
        widget['bar'].set(ratio)

        # HP sáv dinamikus színe
        if ratio > 0.4:
            widget['bar'].configure(progress_color=THEME['emerald'])
        elif ratio > 0.2:
            widget['bar'].configure(progress_color=THEME['gold'])
        else:
            widget['bar'].configure(progress_color=THEME['crimson'])

    # =========================================================================
    # 2. PAKLIÉPÍTŐ NÉZET
    # =========================================================================
    def _build_deck_view(self):
        view = self.views['deck']

        # Felső információs sáv
        info_bar = ctk.CTkFrame(view, fg_color=THEME['bg_card'], corner_radius=12,
                                border_width=1, border_color=THEME['border_subtle'])
        info_bar.pack(fill=tk.X, padx=16, pady=(16, 10))

        info_inner = ctk.CTkFrame(info_bar, fg_color="transparent")
        info_inner.pack(fill=tk.X, padx=16, pady=12)

        self.deck_status_title = ctk.CTkLabel(info_inner, text="🃏 Aktuális Paklid: 0 / 0 lap",
                                              font=ctk.CTkFont(size=16, weight="bold"),
                                              text_color=THEME['gold'])
        self.deck_status_title.pack(side=tk.LEFT)

        clear_all_btn = ctk.CTkButton(info_inner, text="🗑️ Pakli Ürítése",
                                      font=ctk.CTkFont(size=12), height=32,
                                      fg_color=THEME['crimson'], hover_color='#b03a2e',
                                      command=self._on_clear_deck)
        clear_all_btn.pack(side=tk.RIGHT)

        rule_lbl = ctk.CTkLabel(info_bar,
                                text="💡 Szabály: A pakli legfeljebb a gyűjteményed felét teheti ki (felfelé kerekítve). A lapok a harcban fentről lefelé sorrendben vesznek részt!",
                                font=ctk.CTkFont(size=12), text_color=THEME['text_secondary'])
        rule_lbl.pack(anchor='w', padx=16, pady=(0, 10))

        # Kétoszlopos elrendezés (Bal: Gyűjtemény csempék, Jobb: Pakli sorrend csempék)
        panes = ctk.CTkFrame(view, fg_color="transparent")
        panes.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        # BAL OSZLOP: Gyűjtemény
        coll_col = ctk.CTkFrame(panes, fg_color=THEME['bg_card'], corner_radius=12,
                                border_width=1, border_color=THEME['border_subtle'])
        coll_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        ctk.CTkLabel(coll_col, text="📦 Teljes Kártyagyűjteményed",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['text_primary']).pack(anchor='w', padx=14, pady=12)

        self.coll_scroll = ctk.CTkScrollableFrame(coll_col, fg_color="transparent")
        self.coll_scroll.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # JOBB OSZLOP: Aktív Pakli sorrend
        deck_col = ctk.CTkFrame(panes, fg_color=THEME['bg_card'], corner_radius=12,
                                border_width=1, border_color=THEME['border_subtle'])
        deck_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        ctk.CTkLabel(deck_col, text="🛡️ Aktív Harci Pakli (Sorrend)",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(anchor='w', padx=14, pady=12)

        self.deck_scroll = ctk.CTkScrollableFrame(deck_col, fg_color="transparent")
        self.deck_scroll.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    # =========================================================================
    # 3. KÓDEX NÉZET
    # =========================================================================
    def _build_codex_view(self):
        view = self.views['codex']

        hdr = ctk.CTkLabel(view, text="📖 Világ Kódex & Kártyatár",
                           font=ctk.CTkFont(size=18, weight="bold"), text_color=THEME['gold'])
        hdr.pack(anchor='w', padx=20, pady=(20, 10))

        self.codex_scroll = ctk.CTkScrollableFrame(view, fg_color="transparent")
        self.codex_scroll.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

    # =========================================================================
    # 4. SZABÁLYOK NÉZET
    # =========================================================================
    def _build_rules_view(self):
        view = self.views['rules']

        hdr = ctk.CTkLabel(view, text="📖 Szabályzat & Elemi Kölcsönhatások",
                           font=ctk.CTkFont(size=18, weight="bold"), text_color=THEME['gold'])
        hdr.pack(anchor='w', padx=20, pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(view, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        # Elemkerék vizuális bemutató panel
        wheel_card = ctk.CTkFrame(scroll, fg_color=THEME['bg_card'], corner_radius=12,
                                  border_width=1, border_color=THEME['border_subtle'])
        wheel_card.pack(fill=tk.X, pady=8)

        ctk.CTkLabel(wheel_card, text="⚡ ELEMI KAPCSOLATOK ÉS SEBZÉS-SZORZÓK",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(anchor='w', padx=16, pady=(12, 6))

        elem_grid = ctk.CTkFrame(wheel_card, fg_color="transparent")
        elem_grid.pack(fill=tk.X, padx=16, pady=8)

        # 4 Elem kártya
        items = [
            ("🌪️ LEVEGŐ", THEME['elem_levego'], "Erős (2x): Föld, Víz\nGyenge (0.5x): Tűz"),
            ("💧 VÍZ", THEME['elem_viz'], "Erős (2x): Levegő, Tűz\nGyenge (0.5x): Föld"),
            ("🌱 FÖLD", THEME['elem_fold'], "Erős (2x): Levegő, Tűz\nGyenge (0.5x): Víz"),
            ("🔥 TŰZ", THEME['elem_tuz'], "Erős (2x): Föld, Víz\nGyenge (0.5x): Levegő")
        ]

        for idx, (title, color, desc) in enumerate(items):
            box = ctk.CTkFrame(elem_grid, fg_color=THEME['bg_card_inner'], corner_radius=8,
                               border_width=1, border_color=color)
            box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
            ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(anchor='w', padx=10, pady=(8, 2))
            ctk.CTkLabel(box, text=desc, font=ctk.CTkFont(size=11),
                         text_color=THEME['text_secondary'], justify=tk.LEFT).pack(anchor='w', padx=10, pady=(0, 8))

        # Részletes szabályok szövegdoboza
        rules_text_frame = ctk.CTkFrame(scroll, fg_color=THEME['bg_card'], corner_radius=12,
                                        border_width=1, border_color=THEME['border_subtle'])
        rules_text_frame.pack(fill=tk.X, pady=8)

        rules_body = """
1. A JÁTÉK CÉLJA ÉS MENETE
   • A cél a kártyagyűjtemény fejlesztése a kazamaták elleni harcokban.
   • A lapok végtelenül fejleszthetők, a játéknak soha nincs vége.

2. HARCI KÖRÖK ÉS AKCIÓK
   • Minden harc kezdetekor a lapok életereje alaphelyzetbe áll vissza.
   • Egy kör két akcióból áll:
     1. Kazamata cselekszik (új lap kijátszása vagy támadás).
     2. Játékos cselekszik (új lap kijátszása ha az előző elesett, vagy visszatámadás).
   • Ha a kazamata az 1. akcióban leüti a játékos utolsó lapját, a harc azonnal véget ér!

3. KAZAMATÁK ÉS NYEREMÉNYEK
   • Egyszerű találkozás (1 sima lap): A győztes lap +1 Sebzést VAGY +2 Életerőt kap.
   • Kis kazamata (3 sima + 1 vezér): A győztes lap +1 Sebzést vagy +2 Életerőt kap.
   • Nagy kazamata (5 sima + 1 vezér): A játékos megkapja a világból az ELSŐ olyan sima lapot,
     amely még nincs a gyűjteményében!
     (Ha már minden sima lap megvan, nagy kazamata harc nem indítható!)

4. PAKLIÉPÍTÉS
   • A pakli mérete legfeljebb a gyűjtemény fele lehet (felfelé kerekítve).
   • A pakliban lévő lapok sorrendje határozza meg a bevetési sorrendet.
"""
        ctk.CTkLabel(rules_text_frame, text="📜 HIVATALOS SZABÁLYZAT KIVONAT",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(anchor='w', padx=16, pady=(12, 4))

        ctk.CTkLabel(rules_text_frame, text=rules_body, font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=THEME['text_primary'], justify=tk.LEFT).pack(anchor='w', padx=16, pady=(0, 16))

    # =========================================================================
    # ÁLLAPOTFRISSÍTÉSEK ÉS KÁRTYAGENERÁLÁS
    # =========================================================================
    def _update_all_views(self):
        self._update_sidebar_stats()
        self._render_dungeon_tiles()
        self._render_deck_builder()
        self._render_codex()

    def _update_sidebar_stats(self):
        coll_cnt = len(self.gs.player_collection)
        deck_cnt = len(self.gs.player_deck)
        max_deck = self.gs.get_max_deck_size()

        self.stat_coll_lbl.configure(text=f"Gyűjtemény: {coll_cnt} lap")
        self.stat_deck_lbl.configure(text=f"Pakli: {deck_cnt} / {max_deck} lap")

    def _render_dungeon_tiles(self):
        for w in self.dun_tiles_frame.winfo_children():
            w.destroy()

        for dname, dun in self.gs.dungeons.items():
            is_sel = (dname == self.selected_dungeon_name)
            border_c = THEME['gold'] if is_sel else THEME['border_subtle']
            bg_c = THEME['bg_card_highlight'] if is_sel else THEME['bg_card_inner']

            tile = ctk.CTkFrame(self.dun_tiles_frame, fg_color=bg_c, corner_radius=10,
                                border_width=2 if is_sel else 1, border_color=border_c)
            tile.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            # Kattintás kezelés
            tile.bind('<Button-1>', lambda e, n=dname: self._on_select_dungeon(n))

            title_lbl = ctk.CTkLabel(tile, text=dun.name, font=ctk.CTkFont(size=13, weight="bold"),
                                     text_color=THEME['gold'] if is_sel else THEME['text_primary'])
            title_lbl.pack(anchor='w', padx=12, pady=(10, 2))
            title_lbl.bind('<Button-1>', lambda e, n=dname: self._on_select_dungeon(n))

            type_str = "Egyszerű (1 lap)" if dun.dtype == 'egyszeru' else ("Kis (3+1 lap)" if dun.dtype == 'kis' else "Nagy (5+1 lap)")
            type_lbl = ctk.CTkLabel(tile, text=type_str, font=ctk.CTkFont(size=11),
                                    text_color=THEME['text_secondary'])
            type_lbl.pack(anchor='w', padx=12, pady=1)
            type_lbl.bind('<Button-1>', lambda e, n=dname: self._on_select_dungeon(n))

            rew_str = "Jutalom: +1 Sebzés" if dun.reward_type == 'sebzes' else (
                "Jutalom: +2 Életerő" if dun.reward_type == 'eletero' else "Jutalom: Új lap a világból!"
            )
            rew_lbl = ctk.CTkLabel(tile, text=rew_str, font=ctk.CTkFont(size=11, weight="bold"),
                                   text_color=THEME['emerald'])
            rew_lbl.pack(anchor='w', padx=12, pady=(2, 10))
            rew_lbl.bind('<Button-1>', lambda e, n=dname: self._on_select_dungeon(n))

        # Jogosultság ellenőrzése
        can_fight, reason = self.gs.can_challenge_dungeon(self.selected_dungeon_name)
        if can_fight:
            self.dun_warning_lbl.configure(text="")
            self.start_battle_btn.configure(state="normal")
        else:
            self.dun_warning_lbl.configure(text=f"⚠️ {reason}")
            self.start_battle_btn.configure(state="disabled")

    def _on_select_dungeon(self, name: str):
        self.selected_dungeon_name = name
        self._render_dungeon_tiles()

    def _render_deck_builder(self):
        # Fejléc frissítése
        max_size = self.gs.get_max_deck_size()
        curr_size = len(self.gs.player_deck)
        self.deck_status_title.configure(text=f"🃏 Aktuális Paklid: {curr_size} / {max_size} lap")

        # 1. Gyűjtemény kártyacsempék
        for w in self.coll_scroll.winfo_children():
            w.destroy()

        for cname, card in self.gs.player_collection.items():
            in_deck = (cname in self.gs.player_deck)
            e_clean = card.element.lower().strip()
            e_color = THEME.get(f'elem_{e_clean}', THEME['border_gold'])
            e_icon = ELEM_ICONS.get(e_clean, '')

            card_tile = ctk.CTkFrame(self.coll_scroll, fg_color=THEME['bg_card_inner'],
                                     corner_radius=10, border_width=1,
                                     border_color=THEME['gold'] if in_deck else THEME['border_subtle'])
            card_tile.pack(fill=tk.X, pady=4, padx=4)

            # Csempe tartalma
            top_box = ctk.CTkFrame(card_tile, fg_color="transparent")
            top_box.pack(fill=tk.X, padx=12, pady=(8, 2))

            name_lbl = ctk.CTkLabel(top_box, text=card.name, font=ctk.CTkFont(size=13, weight="bold"),
                                    text_color=THEME['text_primary'])
            name_lbl.pack(side=tk.LEFT)

            elem_lbl = ctk.CTkLabel(top_box, text=f"{e_icon} {ELEM_NAMES.get(e_clean, card.element)}",
                                    font=ctk.CTkFont(size=11, weight="bold"), text_color=e_color)
            elem_lbl.pack(side=tk.RIGHT)

            bot_box = ctk.CTkFrame(card_tile, fg_color="transparent")
            bot_box.pack(fill=tk.X, padx=12, pady=(2, 8))

            stats_lbl = ctk.CTkLabel(bot_box, text=f"⚔️ {card.damage} ATK   ❤️ {card.max_hp} HP",
                                     font=ctk.CTkFont(size=11), text_color=THEME['text_secondary'])
            stats_lbl.pack(side=tk.LEFT)

            if in_deck:
                badge = ctk.CTkLabel(bot_box, text="PAKLIBAN", font=ctk.CTkFont(size=10, weight="bold"),
                                     text_color=THEME['gold'], fg_color=THEME['bg_card_highlight'],
                                     corner_radius=4, padx=6, pady=2)
                badge.pack(side=tk.RIGHT)
            else:
                add_btn = ctk.CTkButton(bot_box, text="➕ Hozzáad", width=80, height=26,
                                        font=ctk.CTkFont(size=11, weight="bold"),
                                        fg_color=THEME['gold'], text_color='#000000',
                                        hover_color=THEME['gold_hover'], corner_radius=6,
                                        state="normal" if curr_size < max_size else "disabled",
                                        command=lambda n=cname: self._on_add_card(n))
                add_btn.pack(side=tk.RIGHT)

        # 2. Pakli sorrend csempék
        for w in self.deck_scroll.winfo_children():
            w.destroy()

        if not self.gs.player_deck:
            ctk.CTkLabel(self.deck_scroll, text="A paklid jelenleg üres!\nVálassz kártyákat a bal oldali gyűjteményből.",
                         font=ctk.CTkFont(size=12, slant="italic"),
                         text_color=THEME['text_muted']).pack(pady=30)
            return

        for idx, cname in enumerate(self.gs.player_deck):
            card = self.gs.player_collection[cname]
            e_clean = card.element.lower().strip()
            e_color = THEME.get(f'elem_{e_clean}', THEME['border_gold'])
            e_icon = ELEM_ICONS.get(e_clean, '')

            deck_tile = ctk.CTkFrame(self.deck_scroll, fg_color=THEME['bg_card_inner'],
                                     corner_radius=10, border_width=1, border_color=THEME['border_subtle'])
            deck_tile.pack(fill=tk.X, pady=4, padx=4)

            inner = ctk.CTkFrame(deck_tile, fg_color="transparent")
            inner.pack(fill=tk.X, padx=12, pady=8)

            idx_lbl = ctk.CTkLabel(inner, text=f"#{idx+1}", font=ctk.CTkFont(size=13, weight="bold"),
                                   text_color=THEME['gold'], width=30)
            idx_lbl.pack(side=tk.LEFT)

            c_info = ctk.CTkLabel(inner, text=f"{card.name}  ({e_icon} ⚔️{card.damage} ❤️{card.max_hp})",
                                  font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME['text_primary'])
            c_info.pack(side=tk.LEFT, padx=6)

            # Mozgató és törlő gombok
            btn_box = ctk.CTkFrame(inner, fg_color="transparent")
            btn_box.pack(side=tk.RIGHT)

            up_btn = ctk.CTkButton(btn_box, text="▲", width=28, height=26,
                                   font=ctk.CTkFont(size=10), fg_color=THEME['border_subtle'],
                                   hover_color=THEME['bg_card_highlight'], corner_radius=4,
                                   state="normal" if idx > 0 else "disabled",
                                   command=lambda i=idx: self._on_move_deck(i, -1))
            up_btn.pack(side=tk.LEFT, padx=2)

            down_btn = ctk.CTkButton(btn_box, text="▼", width=28, height=26,
                                     font=ctk.CTkFont(size=10), fg_color=THEME['border_subtle'],
                                     hover_color=THEME['bg_card_highlight'], corner_radius=4,
                                     state="normal" if idx < len(self.gs.player_deck) - 1 else "disabled",
                                     command=lambda i=idx: self._on_move_deck(i, 1))
            down_btn.pack(side=tk.LEFT, padx=2)

            del_btn = ctk.CTkButton(btn_box, text="✕", width=28, height=26,
                                    font=ctk.CTkFont(size=10), fg_color=THEME['crimson'],
                                    hover_color='#b03a2e', corner_radius=4,
                                    command=lambda i=idx: self._on_remove_deck(i))
            del_btn.pack(side=tk.LEFT, padx=2)

    def _render_codex(self):
        for w in self.codex_scroll.winfo_children():
            w.destroy()

        # Sima kártyák szekció
        ctk.CTkLabel(self.codex_scroll, text="⚔️ VILÁGKÁRTYÁK (SIMA LAPOK)",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(anchor='w', pady=(4, 8))

        grid_frame = ctk.CTkFrame(self.codex_scroll, fg_color="transparent")
        grid_frame.pack(fill=tk.X, pady=(0, 16))

        for idx, card in enumerate(self.gs.world_cards.values()):
            is_owned = card.name in self.gs.player_collection
            e_clean = card.element.lower().strip()
            e_color = THEME.get(f'elem_{e_clean}', THEME['border_gold'])
            e_icon = ELEM_ICONS.get(e_clean, '')

            tile = ctk.CTkFrame(grid_frame, fg_color=THEME['bg_card'], corner_radius=10,
                                border_width=1, border_color=THEME['emerald'] if is_owned else THEME['border_subtle'])
            tile.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)

            ctk.CTkLabel(tile, text=card.name, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=THEME['text_primary']).pack(anchor='w', padx=10, pady=(8, 2))
            ctk.CTkLabel(tile, text=f"{e_icon} {ELEM_NAMES.get(e_clean, card.element)}",
                         font=ctk.CTkFont(size=10, weight="bold"), text_color=e_color).pack(anchor='w', padx=10)
            ctk.CTkLabel(tile, text=f"⚔️ {card.damage} | ❤️ {card.max_hp}",
                         font=ctk.CTkFont(size=11), text_color=THEME['text_secondary']).pack(anchor='w', padx=10, pady=2)

            status_str = "✓ Megvan" if is_owned else "Megszerezhető"
            status_color = THEME['emerald'] if is_owned else THEME['gold']
            ctk.CTkLabel(tile, text=status_str, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=status_color).pack(anchor='w', padx=10, pady=(2, 8))

        # Vezérkártyák szekció
        ctk.CTkLabel(self.codex_scroll, text="⭐ VEZÉRKÁRTYÁK",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME['gold']).pack(anchor='w', pady=(8, 8))

        boss_frame = ctk.CTkFrame(self.codex_scroll, fg_color="transparent")
        boss_frame.pack(fill=tk.X, pady=(0, 16))

        for boss in self.gs.boss_cards.values():
            e_clean = boss.element.lower().strip()
            e_color = THEME.get(f'elem_{e_clean}', THEME['border_gold'])
            e_icon = ELEM_ICONS.get(e_clean, '')

            tile = ctk.CTkFrame(boss_frame, fg_color=THEME['bg_card'], corner_radius=10,
                                border_width=2, border_color=THEME['gold'])
            tile.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)

            ctk.CTkLabel(tile, text=f"⭐ {boss.name}", font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=THEME['gold']).pack(anchor='w', padx=12, pady=(10, 2))
            ctk.CTkLabel(tile, text=f"{e_icon} {ELEM_NAMES.get(e_clean, boss.element)}",
                         font=ctk.CTkFont(size=11, weight="bold"), text_color=e_color).pack(anchor='w', padx=12)
            ctk.CTkLabel(tile, text=f"⚔️ Sebzés: {boss.damage}  |  ❤️ Élet: {boss.max_hp}",
                         font=ctk.CTkFont(size=11), text_color=THEME['text_primary']).pack(anchor='w', padx=12, pady=(4, 10))

    # =========================================================================
    # HARCI VEZÉRLÉS ÉS ANIMÁCIÓK
    # =========================================================================
    def _on_start_battle(self):
        can_fight, reason = self.gs.can_challenge_dungeon(self.selected_dungeon_name)
        if not can_fight:
            messagebox.showwarning("Nem indítható harc", reason)
            return

        # Harci állapot inicializálása
        self.current_battle_result = self.gs.execute_battle(self.selected_dungeon_name)
        self.current_event_index = 0
        self.is_auto_playing = False

        # Napló ürítése
        self.log_textbox.delete("1.0", tk.END)
        self.log_textbox.insert(tk.END, f"harc kezdodik;{self.selected_dungeon_name}\n")

        # Gombok állapotai
        self.start_battle_btn.configure(state="disabled")
        self.step_btn.configure(state="normal")
        self.autoplay_btn.configure(state="normal", text="▶️ Folyamatos Lejátszás")
        self.skip_btn.configure(state="normal")

        # Kártyák alaphelyzetbe
        self._update_battle_card_ui(self.player_card_widget, None, 0, 0, 1, '')
        self._update_battle_card_ui(self.enemy_card_widget, None, 0, 0, 1, '')
        self.multiplier_badge.configure(text="—", fg_color=THEME['bg_card'], text_color=THEME['text_muted'])
        self.round_badge.configure(text="Csapatok felkészültek! Harc kezdődik...", text_color=THEME['gold'])

        dun = self.gs.dungeons[self.selected_dungeon_name]
        self.enemy_reserves_lbl.configure(text=f"Kazamata tartalék: {len(dun.plain_card_names) + (1 if dun.boss_card_name else 0)} lap")
        self.player_reserves_lbl.configure(text=f"Pakli tartalék: {len(self.gs.player_deck)} lap")

        # Első akció azonnali végrehajtása
        self._on_step_battle()

    def _on_step_battle(self):
        if not self.current_battle_result:
            return

        if self.current_event_index >= len(self.current_battle_result.event_steps):
            self._finish_battle()
            return

        ev = self.current_battle_result.event_steps[self.current_event_index]
        self.current_event_index += 1

        r_num = ev.get('round', 1)
        actor = ev.get('actor')
        action = ev.get('action')
        event_type = ev.get('event')

        if event_type == 'game_over':
            winner = ev.get('winner')
            if winner == 'jatekos':
                self.round_badge.configure(text="🏆 Győzelem! A kazamata serege elesett!", text_color=THEME['gold'])
                self.log_textbox.insert(tk.END, f"jatekos nyert;{ev.get('reward', '')}\n")
            else:
                self.round_badge.configure(text="💀 Vereség! A hősök serege elbukott!", text_color=THEME['crimson'])
                self.log_textbox.insert(tk.END, "jatekos vesztett\n")
            self.log_textbox.see(tk.END)
            self._finish_battle()
            return

        if action == 'kijatszik':
            cname = ev['card']
            dmg = ev['damage']
            hp = ev['hp']
            elem = ev['element']

            if actor == 'kazamata':
                is_boss = (cname in self.gs.boss_cards)
                self._update_battle_card_ui(self.enemy_card_widget, cname, dmg, hp, hp, elem, is_boss)
                self.log_textbox.insert(tk.END, f"{r_num}.kor;kazamata;kijatszik;{cname};{dmg};{hp};{elem}\n")
                self.round_badge.configure(text=f"{r_num}. kör • Kazamata kijátszotta: {cname}", text_color=THEME['text_primary'])
            else:
                self._update_battle_card_ui(self.player_card_widget, cname, dmg, hp, hp, elem, is_boss=False)
                self.log_textbox.insert(tk.END, f"{r_num}.kor;jatekos;kijatszik;{cname};{dmg};{hp};{elem}\n")
                self.round_badge.configure(text=f"{r_num}. kör • Játékos kijátszotta: {cname}", text_color=THEME['text_primary'])

        elif action == 'tamad':
            attacker = ev['attacker']
            defender = ev['defender']
            dmg = ev['damage']
            mult = ev['multiplier']
            def_hp = ev['defender_hp']

            # Elemi szorzó vizuális jelvénye
            if mult == 2.0:
                self.multiplier_badge.configure(text="⚡ ERŐS (2x Sebzés!)", fg_color=THEME['crimson'], text_color='#ffffff')
            elif mult == 0.5:
                self.multiplier_badge.configure(text="🛡️ GYENGE (0.5x Sebzés)", fg_color=THEME['cyan'], text_color='#ffffff')
            else:
                self.multiplier_badge.configure(text="⚖️ Semleges (1x)", fg_color=THEME['border_subtle'], text_color=THEME['text_secondary'])

            if actor == 'kazamata':
                cur_max = self.player_card_widget['max_hp']
                p_card = self.gs.player_collection.get(defender)
                p_elem = p_card.element if p_card else ''
                p_dmg = p_card.damage if p_card else 0
                self._update_battle_card_ui(self.player_card_widget, defender if def_hp > 0 else None,
                                            p_dmg, def_hp, cur_max, p_elem, is_boss=False)
                self.log_textbox.insert(tk.END, f"{r_num}.kor;kazamata;tamad;{attacker};{dmg};{defender};{def_hp}\n")
                self.round_badge.configure(text=f"{r_num}. kör • Kazamata támad ({dmg} sebzés) ➔ {def_hp} HP maradt",
                                           text_color=THEME['crimson'])
            else:
                cur_max = self.enemy_card_widget['max_hp']
                e_card = self.gs.world_cards.get(defender) or self.gs.boss_cards.get(defender)
                e_elem = e_card.element if e_card else ''
                e_dmg = e_card.damage if e_card else 0
                is_boss = (defender in self.gs.boss_cards)
                self._update_battle_card_ui(self.enemy_card_widget, defender if def_hp > 0 else None,
                                            e_dmg, def_hp, cur_max, e_elem, is_boss=is_boss)
                self.log_textbox.insert(tk.END, f"{r_num}.kor;jatekos;tamad;{attacker};{dmg};{defender};{def_hp}\n")
                self.round_badge.configure(text=f"{r_num}. kör • Játékos visszatámad ({dmg} sebzés) ➔ {def_hp} HP maradt",
                                           text_color=THEME['emerald'])

        self.log_textbox.see(tk.END)

        if self.is_auto_playing and self.current_event_index < len(self.current_battle_result.event_steps):
            self.auto_play_timer = self.after(450, self._on_step_battle)
        elif self.current_event_index >= len(self.current_battle_result.event_steps):
            self._finish_battle()

    def _on_toggle_autoplay(self):
        self.is_auto_playing = not self.is_auto_playing
        if self.is_auto_playing:
            self.autoplay_btn.configure(text="⏸️ Szünet")
            self._on_step_battle()
        else:
            self.autoplay_btn.configure(text="▶️ Folyamatos Lejátszás")
            if self.auto_play_timer:
                self.after_cancel(self.auto_play_timer)

    def _on_skip_battle(self):
        self.is_auto_playing = False
        if self.auto_play_timer:
            self.after_cancel(self.auto_play_timer)

        self.log_textbox.delete("1.0", tk.END)
        for line in self.current_battle_result.log_lines:
            self.log_textbox.insert(tk.END, line + "\n")
        self.log_textbox.see(tk.END)
        self._finish_battle()

    def _finish_battle(self):
        self.is_auto_playing = False
        if self.auto_play_timer:
            self.after_cancel(self.auto_play_timer)

        self.step_btn.configure(state="disabled")
        self.autoplay_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        self.start_battle_btn.configure(state="normal")

        if not self.current_battle_result:
            return

        winner = self.current_battle_result.winner
        reward_line = self.current_battle_result.reward_line

        self._update_all_views()

        if winner == 'jatekos':
            messagebox.showinfo("🏆 Győzelem!", f"Gratulálunk, győztél a harcban!\nNyereményed: {reward_line}")
        else:
            messagebox.showwarning("💀 Vereség", "A kazamata serege felülkerekedett.\nFejlessz a lapjaidon vagy próbálkozz másik paklival!")

    # =========================================================================
    # PAKLI KEZELŐK
    # =========================================================================
    def _on_add_card(self, cname: str):
        max_size = self.gs.get_max_deck_size()
        if len(self.gs.player_deck) >= max_size:
            messagebox.showwarning("Pakli Limit", f"A pakli megtelt! Maximum {max_size} kártyát választhatsz.")
            return

        if cname in self.gs.player_deck:
            return

        new_deck = list(self.gs.player_deck) + [cname]
        self.gs.set_deck(new_deck)
        self._update_all_views()

    def _on_remove_deck(self, idx: int):
        new_deck = list(self.gs.player_deck)
        del new_deck[idx]
        self.gs.set_deck(new_deck)
        self._update_all_views()

    def _on_move_deck(self, idx: int, direction: int):
        new_idx = idx + direction
        if 0 <= new_idx < len(self.gs.player_deck):
            new_deck = list(self.gs.player_deck)
            new_deck[idx], new_deck[new_idx] = new_deck[new_idx], new_deck[idx]
            self.gs.set_deck(new_deck)
            self._update_all_views()

    def _on_clear_deck(self):
        if messagebox.askyesno("Megerősítés", "Biztosan kiüríted a teljes paklit?"):
            self.gs.set_deck([])
            self._update_all_views()

    def _on_reset_game(self):
        if messagebox.askyesno("Újrakezdés", "Biztosan visszaállítod az eredeti játékállapotot?"):
            self.gs = GameState.get_default_game_state()
            self._update_all_views()
            messagebox.showinfo("Kész", "A játékállapot visszaállt az alapértékekre.")


def start_gui(game_state: Optional[GameState] = None):
    app = DamareenModernGUI(game_state)
    app.mainloop()
