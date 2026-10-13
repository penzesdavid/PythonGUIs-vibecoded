"""
Damareen Kártyajáték - Modern Streamlit Webes Felület
Dusza Árpád Országos Programozói Emlékverseny 2025/2026 - I. forduló
Design téma: Obszidián & Misztikus Arany (Dark Obsidian & Arcane Gold)
"""

import os
import io
import math
import tempfile
import streamlit as st
from typing import Optional, List, Dict

from game_logic import GameState, Card, Dungeon, calculate_damage, BattleResult, EROS_PAROK, GYENGE_PAROK

# =============================================================================
# OLDAL KONFIGURÁCIÓ ÉS DESIGN
# =============================================================================
st.set_page_config(
    page_title="Damareen – Fantasy Kártyajáték",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elem színek és ikonok
ELEM_CONFIG = {
    'fold': {
        'name': 'Föld',
        'icon': '🌱',
        'color': '#2ecc71',
        'bg_gradient': 'linear-gradient(135deg, #143823 0%, #1e5631 100%)',
        'border': '#27ae60'
    },
    'levego': {
        'name': 'Levegő',
        'icon': '🌪️',
        'color': '#bb86fc',
        'bg_gradient': 'linear-gradient(135deg, #2b153b 0%, #43235b 100%)',
        'border': '#8e44ad'
    },
    'viz': {
        'name': 'Víz',
        'icon': '💧',
        'color': '#3498db',
        'bg_gradient': 'linear-gradient(135deg, #102a43 0%, #1a4268 100%)',
        'border': '#2980b9'
    },
    'tuz': {
        'name': 'Tűz',
        'icon': '🔥',
        'color': '#e74c3c',
        'bg_gradient': 'linear-gradient(135deg, #3d1210 0%, #5e1c18 100%)',
        'border': '#c0392b'
    }
}

# Globális prémium CSS stílusok
CUSTOM_CSS = """
<style>
/* Fő háttér és kontraszt */
.stApp {
    background-color: #0c0d14;
    color: #f0f2f8;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Kártya stílusok */
.damareen-card {
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    background: #161825;
    border: 1px solid #2a2d42;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.damareen-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
}

.damareen-card-boss {
    border: 2px solid #d4af37 !important;
    background: linear-gradient(145deg, #1c1c2b 0%, #292415 100%) !important;
    box-shadow: 0 4px 18px rgba(212, 175, 55, 0.2) !important;
}

/* Elemi kártya kiemelések */
.card-fold { border-left: 5px solid #27ae60 !important; }
.card-levego { border-left: 5px solid #8e44ad !important; }
.card-viz { border-left: 5px solid #2980b9 !important; }
.card-tuz { border-left: 5px solid #c0392b !important; }

/* Jelvények */
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 6px;
}
.badge-gold { background: #d4af37; color: #0c0d14; }
.badge-boss { background: linear-gradient(90deg, #d4af37, #f39c12); color: #000; font-weight: 800; }
.badge-owned { background: #143823; color: #2ecc71; border: 1px solid #27ae60; }
.badge-unowned { background: #33193e; color: #bb86fc; border: 1px solid #8e44ad; }
.badge-deck { background: #d4af37; color: #000; font-weight: bold; }

/* Csatatér aktív kártya */
.battle-card {
    background: #141624;
    border-radius: 14px;
    padding: 20px;
    border: 2px solid #2a2d42;
    text-align: center;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.battle-card-player {
    border-color: #3498db;
    box-shadow: 0 0 20px rgba(52, 152, 219, 0.25);
}
.battle-card-enemy {
    border-color: #e74c3c;
    box-shadow: 0 0 20px rgba(231, 76, 60, 0.25);
}

.hp-bar-container {
    background-color: #212438;
    border-radius: 10px;
    height: 14px;
    width: 100%;
    overflow: hidden;
    margin: 8px 0;
}
.hp-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s ease;
}

/* VS indicator */
.vs-badge {
    text-align: center;
    font-size: 28px;
    font-weight: 900;
    color: #d4af37;
    text-shadow: 0 0 12px rgba(212, 175, 55, 0.5);
    padding: 10px 0;
}

.mult-badge {
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.9rem;
    font-weight: bold;
    display: inline-block;
    margin-top: 5px;
}
.mult-strong { background: #e74c3c; color: white; box-shadow: 0 0 10px rgba(231, 76, 60, 0.5); }
.mult-weak { background: #3498db; color: white; }
.mult-neutral { background: #2a2d42; color: #a5a9c2; }

/* Címsorok arany fénye */
h1, h2, h3 {
    color: #f7f8fc !important;
}
.gold-text {
    color: #d4af37 !important;
    font-weight: bold;
}

/* Log konzol doboz */
.log-box {
    background-color: #08090f;
    border: 1px solid #1f2235;
    border-radius: 8px;
    padding: 12px;
    font-family: "Courier New", Courier, monospace;
    font-size: 0.85rem;
    color: #7ef196;
    max-height: 260px;
    overflow-y: auto;
    white-space: pre-wrap;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# ÁLLAPOT INICIALIZÁLÁSA (SESSION STATE)
# =============================================================================
def init_session_state():
    if 'gs' not in st.session_state:
        st.session_state.gs = GameState.get_default_game_state()

    if 'selected_dungeon' not in st.session_state:
        st.session_state.selected_dungeon = "Barlangi Portya"

    # Harci futtatási állapotok
    if 'battle_active' not in st.session_state:
        st.session_state.battle_active = False
    if 'battle_result' not in st.session_state:
        st.session_state.battle_result = None
    if 'battle_step_idx' not in st.session_state:
        st.session_state.battle_step_idx = 0
    if 'battle_log_history' not in st.session_state:
        st.session_state.battle_log_history = []


init_session_state()
gs: GameState = st.session_state.gs


# =============================================================================
# HARCI MEGJELENÍTÉSI SZÁMÍTÁSOK
# =============================================================================
def compute_battle_step_state(game_state: GameState, dungeon_name: str, event_steps: List[dict], step_idx: int):
    dun = game_state.dungeons[dungeon_name]
    kazamata_queue = [c.name for c in dun.get_all_cards(game_state)]
    player_queue = list(game_state.player_deck)

    active_k: Optional[dict] = None
    active_p: Optional[dict] = None
    last_action_desc = "Csapatok a csatatéren! Harc kezdetét veszi..."
    multiplier_desc = "—"
    multiplier_class = "mult-neutral"
    game_over_info: Optional[dict] = None
    current_round = 1

    steps_to_process = event_steps[:step_idx]

    for ev in steps_to_process:
        actor = ev.get('actor')
        action = ev.get('action')
        ev_type = ev.get('event')
        current_round = ev.get('round', current_round)

        if ev_type == 'game_over':
            game_over_info = ev
            continue

        if action == 'kijatszik':
            cname = ev['card']
            dmg = ev['damage']
            hp = ev['hp']
            elem = ev['element']

            if actor == 'kazamata':
                is_boss = (cname in game_state.boss_cards)
                active_k = {
                    'name': cname,
                    'damage': dmg,
                    'hp': hp,
                    'max_hp': hp,
                    'element': elem,
                    'is_boss': is_boss
                }
                if cname in kazamata_queue:
                    kazamata_queue.remove(cname)
                last_action_desc = f"{current_round}. kör: Kazamata kijátszotta a(z) {cname} kártyát!"
            else:
                active_p = {
                    'name': cname,
                    'damage': dmg,
                    'hp': hp,
                    'max_hp': hp,
                    'element': elem,
                    'is_boss': False
                }
                if cname in player_queue:
                    player_queue.remove(cname)
                last_action_desc = f"{current_round}. kör: Játékos kijátszotta a(z) {cname} kártyát!"

        elif action == 'tamad':
            attacker = ev['attacker']
            defender = ev['defender']
            dmg = ev['damage']
            mult = ev['multiplier']
            def_hp = ev['defender_hp']

            if mult == 2.0:
                multiplier_desc = "⚡ ERŐS (2x Sebzés!)"
                multiplier_class = "mult-strong"
            elif mult == 0.5:
                multiplier_desc = "🛡️ GYENGE (0.5x Sebzés)"
                multiplier_class = "mult-weak"
            else:
                multiplier_desc = "⚖️ Semleges (1x)"
                multiplier_class = "mult-neutral"

            if actor == 'kazamata':
                last_action_desc = f"{current_round}. kör: Kazamata támad ({attacker} ➔ {defender}): {dmg} sebzés! ({def_hp} HP maradt)"
                if active_p:
                    active_p['hp'] = def_hp
                    if def_hp == 0:
                        active_p = None
            else:
                last_action_desc = f"{current_round}. kör: Játékos visszatámad ({attacker} ➔ {defender}): {dmg} sebzés! ({def_hp} HP maradt)"
                if active_k:
                    active_k['hp'] = def_hp
                    if def_hp == 0:
                        active_k = None

    return {
        'active_k': active_k,
        'active_p': active_p,
        'kazamata_queue_count': len(kazamata_queue),
        'player_queue_count': len(player_queue),
        'last_action_desc': last_action_desc,
        'multiplier_desc': multiplier_desc,
        'multiplier_class': multiplier_class,
        'game_over_info': game_over_info,
        'round': current_round
    }


# =============================================================================
# OLDALSÁV (SIDEBAR)
# =============================================================================
with st.sidebar:
    st.markdown("## ⚔️ DAMAREEN")
    st.markdown("<span style='color: #a5a9c2; font-size: 0.85rem;'>Fantasy Kártyajáték • Dusza Árpád 2025/2026</span>", unsafe_allow_html=True)
    st.markdown("---")

    # Játékos gyors statisztika
    coll_size = len(gs.player_collection)
    deck_size = len(gs.player_deck)
    max_deck = gs.get_max_deck_size()

    st.markdown(f"""
    <div style='background: #161825; border: 1px solid #2a2d42; border-radius: 10px; padding: 12px; margin-bottom: 16px;'>
        <div style='color: #ffffff; font-weight: bold; font-size: 0.95rem; margin-bottom: 4px;'>
            📦 Gyűjtemény: <span style='color: #2ecc71;'>{coll_size} lap</span>
        </div>
        <div style='color: #ffffff; font-weight: bold; font-size: 0.95rem;'>
            🃏 Aktív pakli: <span style='color: #d4af37;'>{deck_size} / {max_deck} lap</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "Navigáció:",
        [
            "⚔️ Kaland & Harc",
            "🃏 Pakliépítő",
            "📜 Világ Kódex",
            "📖 Szabályzat & Elemek",
            "🧪 In.txt Tesztelő & Export"
        ],
        index=0
    )

    st.markdown("---")
    if st.button("🔄 Játék Alaphelyzetbe Állítása", use_container_width=True):
        st.session_state.gs = GameState.get_default_game_state()
        st.session_state.battle_active = False
        st.session_state.battle_result = None
        st.session_state.battle_step_idx = 0
        st.session_state.battle_log_history = []
        st.success("A játékállapot visszaállt az alapértékekre!")
        st.rerun()

    st.markdown("<div style='text-align: center; color: #656883; font-size: 0.75rem; margin-top: 20px;'>Dusza Árpád Országos Verseny • Streamlit Edition</div>", unsafe_allow_html=True)


# =============================================================================
# 1. NÉZET: KALAND ÉS HARC (BATTLE ARENA)
# =============================================================================
if nav == "⚔️ Kaland & Harc":
    st.markdown("## ⚔️ Kaland & Csatatér")
    st.markdown("Válassz kazamatát, állítsd ki hősies kártyapaklidat, és küzdj meg Damareen veszedelmes teremtményeivel!")

    # 1. Kazamata választó panel
    st.markdown("### 🏰 Kazamata Kiválasztása")
    dungeon_cols = st.columns(3)

    for idx, (dname, dun) in enumerate(gs.dungeons.items()):
        col = dungeon_cols[idx]
        is_selected = (dname == st.session_state.selected_dungeon)
        border_c = "#d4af37" if is_selected else "#2a2d42"
        bg_c = "#23263a" if is_selected else "#161825"

        type_text = "Egyszerű (1 lap)" if dun.dtype == 'egyszeru' else ("Kis (3+1 lap)" if dun.dtype == 'kis' else "Nagy (5+1 lap)")
        reward_text = "+1 Sebzés" if dun.reward_type == 'sebzes' else ("+2 Életerő" if dun.reward_type == 'eletero' else "Új kártya a világból!")

        with col:
            st.markdown(f"""
            <div style='background: {bg_c}; border: 2px solid {border_c}; border-radius: 12px; padding: 14px; margin-bottom: 10px;'>
                <div style='color: #d4af37; font-weight: bold; font-size: 1.1rem; margin-bottom: 4px;'>{dun.name}</div>
                <div style='color: #a5a9c2; font-size: 0.85rem; margin-bottom: 6px;'>Típus: <b>{type_text}</b></div>
                <div style='color: #2ecc71; font-size: 0.85rem; font-weight: bold;'>Jutalom: {reward_text}</div>
                <div style='color: #a5a9c2; font-size: 0.75rem; margin-top: 6px;'>
                    Lapok: {", ".join(dun.plain_card_names)} {f" + ⭐ {dun.boss_card_name}" if dun.boss_card_name else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Kiválasztás: {dun.name}", key=f"sel_dun_{dname}", use_container_width=True):
                st.session_state.selected_dungeon = dname
                st.session_state.battle_active = False
                st.session_state.battle_result = None
                st.session_state.battle_step_idx = 0
                st.rerun()

    # Ellenőrzés: indítható-e a harc
    can_fight, reason = gs.can_challenge_dungeon(st.session_state.selected_dungeon)
    if not can_fight:
        st.warning(f"⚠️ A kiválasztott kazamata nem indítható: **{reason}**")

    st.markdown("---")

    # 2. Csatatér Panel
    st.markdown(f"### 🛡️ Csatatér: **{st.session_state.selected_dungeon}**")

    # Harci gombok sávja
    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 2, 2, 2])

    with ctrl_col1:
        if st.button("⚔️ Új Harc Indítása", disabled=not can_fight, use_container_width=True, type="primary"):
            # Harc végrehajtása a játékmagban
            res = gs.execute_battle(st.session_state.selected_dungeon)
            st.session_state.battle_result = res
            st.session_state.battle_active = True
            st.session_state.battle_step_idx = 1  # Kezdés az 1. akcióval
            st.rerun()

    battle_res: Optional[BattleResult] = st.session_state.battle_result

    with ctrl_col2:
        if battle_res and st.session_state.battle_step_idx < len(battle_res.event_steps):
            if st.button("⏩ Következő Akció", use_container_width=True):
                st.session_state.battle_step_idx += 1
                st.rerun()
        else:
            st.button("⏩ Következő Akció", disabled=True, use_container_width=True)

    with ctrl_col3:
        if battle_res and st.session_state.battle_step_idx < len(battle_res.event_steps):
            if st.button("⏭️ Ugrás a végére", use_container_width=True):
                st.session_state.battle_step_idx = len(battle_res.event_steps)
                st.rerun()
        else:
            st.button("⏭️ Ugrás a végére", disabled=True, use_container_width=True)

    with ctrl_col4:
        if battle_res:
            if st.button("🔄 Újracsatázás", use_container_width=True):
                st.session_state.battle_step_idx = 0
                st.rerun()

    # Csatatér vizualizáció
    if battle_res and st.session_state.battle_step_idx > 0:
        step_state = compute_battle_step_state(
            gs,
            st.session_state.selected_dungeon,
            battle_res.event_steps,
            st.session_state.battle_step_idx
        )

        # Aktuális akció leírás sáv
        st.info(f"**{step_state['last_action_desc']}** (Lépés: {st.session_state.battle_step_idx} / {len(battle_res.event_steps)})")

        arena_p_col, arena_mid_col, arena_e_col = st.columns([4, 2, 4])

        # Játékos lapja (Bal)
        with arena_p_col:
            st.markdown("<h4 style='color: #3498db; text-align: center;'>🛡️ Játékos Lapja</h4>", unsafe_allow_html=True)
            p_card = step_state['active_p']
            if p_card:
                e_data = ELEM_CONFIG.get(p_card['element'], {})
                hp_ratio = max(0.0, min(1.0, p_card['hp'] / max(1, p_card['max_hp'])))
                hp_color = "#2ecc71" if hp_ratio > 0.4 else ("#f39c12" if hp_ratio > 0.2 else "#e74c3c")

                st.markdown(f"""
                <div class='battle-card battle-card-player'>
                    <div>
                        <div style='font-size: 1.3rem; font-weight: bold; color: #ffffff;'>{p_card['name']}</div>
                        <span class='badge' style='background: {e_data.get('border', '#3498db')}; color: white;'>
                            {e_data.get('icon', '')} {e_data.get('name', p_card['element']).upper()}
                        </span>
                    </div>
                    <div style='margin: 16px 0;'>
                        <div style='font-size: 1.1rem; color: #d4af37; font-weight: bold;'>⚔️ Sebzés: {p_card['damage']}</div>
                        <div style='font-size: 1.1rem; color: {hp_color}; font-weight: bold;'>❤️ Élet: {p_card['hp']} / {p_card['max_hp']}</div>
                        <div class='hp-bar-container'>
                            <div class='hp-bar-fill' style='width: {int(hp_ratio * 100)}%; background-color: {hp_color};'></div>
                        </div>
                    </div>
                    <div style='color: #a5a9c2; font-size: 0.85rem;'>
                        Pakli tartalék: <b>{step_state['player_queue_count']}</b> lap
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='battle-card' style='opacity: 0.6;'>
                    <div style='margin: auto;'>
                        <div style='font-size: 1.2rem; color: #a5a9c2;'>💀 Lap Elesett / Nincs Kijátszva</div>
                        <div style='font-size: 0.85rem; color: #656883;'>Következő lap kijátszásra vár...</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Közép: VS & Elem szorzó
        with arena_mid_col:
            st.markdown("<div class='vs-badge'>VS</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='text-align: center;'>
                <div class='mult-badge {step_state['multiplier_class']}'>
                    {step_state['multiplier_desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Kazamata lapja (Jobb)
        with arena_e_col:
            st.markdown("<h4 style='color: #e74c3c; text-align: center;'>💀 Kazamata Ellenfél</h4>", unsafe_allow_html=True)
            k_card = step_state['active_k']
            if k_card:
                e_data = ELEM_CONFIG.get(k_card['element'], {})
                hp_ratio = max(0.0, min(1.0, k_card['hp'] / max(1, k_card['max_hp'])))
                hp_color = "#2ecc71" if hp_ratio > 0.4 else ("#f39c12" if hp_ratio > 0.2 else "#e74c3c")
                boss_badge = "<span class='badge badge-boss'>⭐ VEZÉR</span>" if k_card['is_boss'] else ""

                st.markdown(f"""
                <div class='battle-card battle-card-enemy'>
                    <div>
                        <div style='font-size: 1.3rem; font-weight: bold; color: #ffffff;'>
                            {k_card['name']} {boss_badge}
                        </div>
                        <span class='badge' style='background: {e_data.get('border', '#e74c3c')}; color: white;'>
                            {e_data.get('icon', '')} {e_data.get('name', k_card['element']).upper()}
                        </span>
                    </div>
                    <div style='margin: 16px 0;'>
                        <div style='font-size: 1.1rem; color: #d4af37; font-weight: bold;'>⚔️ Sebzés: {k_card['damage']}</div>
                        <div style='font-size: 1.1rem; color: {hp_color}; font-weight: bold;'>❤️ Élet: {k_card['hp']} / {k_card['max_hp']}</div>
                        <div class='hp-bar-container'>
                            <div class='hp-bar-fill' style='width: {int(hp_ratio * 100)}%; background-color: {hp_color};'></div>
                        </div>
                    </div>
                    <div style='color: #a5a9c2; font-size: 0.85rem;'>
                        Kazamata tartalék: <b>{step_state['kazamata_queue_count']}</b> lap
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='battle-card' style='opacity: 0.6;'>
                    <div style='margin: auto;'>
                        <div style='font-size: 1.2rem; color: #a5a9c2;'>💀 Lap Elesett / Nincs Kijátszva</div>
                        <div style='font-size: 0.85rem; color: #656883;'>Következő ellenség várható...</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Győzelem / Vereség banner
        if step_state['game_over_info'] or st.session_state.battle_step_idx >= len(battle_res.event_steps):
            if battle_res.winner == 'jatekos':
                st.success(f"### 🏆 DIADALMAS GYŐZELEM!\nA kazamata minden teremtménye elesett! Jutalom: **{battle_res.reward_line}**")
            else:
                st.error("### 💀 KESERŰ VERESÉG!\nA kazamata serege legyőzte a hőseidet. Fejlessz lapjaidon vagy változtass a paklid taktikáján!")

        # 3. Harci Protokoll (Napló)
        st.markdown("#### 📜 Hivatalos Harci Eseménynapló (Protokoll formátum)")
        executed_logs = battle_res.log_lines[:min(len(battle_res.log_lines), st.session_state.battle_step_idx + 1)]
        log_text = "\n".join(executed_logs)
        st.markdown(f"<div class='log-box'>{log_text}</div>", unsafe_allow_html=True)

    else:
        # Csatatér készenlétben állapot
        st.markdown("""
        <div style='text-align: center; padding: 50px 20px; background: #131422; border-radius: 14px; border: 1px dashed #2a2d42;'>
            <div style='font-size: 3rem; margin-bottom: 10px;'>🏰</div>
            <div style='font-size: 1.2rem; font-weight: bold; color: #d4af37;'>A Csatatér Készenlétben Áll</div>
            <div style='color: #a5a9c2; max-width: 500px; margin: 8px auto;'>
                Kattints a fenti <b>«⚔️ Új Harc Indítása»</b> gombra a küzdelem megkezdéséhez!
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# 2. NÉZET: PAKLIÉPÍTŐ (DECK BUILDER)
# =============================================================================
elif nav == "🃏 Pakliépítő":
    st.markdown("## 🃏 Pakliépítő Műhely")
    st.markdown("Állítsd össze a harci paklidat! A lapok sorrendje határozza meg, hogy milyen sorrendben szállnak harcba a kazamatában.")

    max_deck = gs.get_max_deck_size()
    curr_deck = len(gs.player_deck)

    # Információs sáv
    st.info(f"💡 **Szabály:** A pakli legfeljebb a gyűjteményed fele lehet, felfelé kerekítve: **ceil({len(gs.player_collection)} / 2) = {max_deck} lap**.")

    col_stats1, col_stats2, col_stats3 = st.columns([3, 3, 2])
    with col_stats1:
        st.metric("📦 Teljes Gyűjtemény", f"{len(gs.player_collection)} lap")
    with col_stats2:
        st.metric("🛡️ Aktuális Pakliméret", f"{curr_deck} / {max_deck} lap")
    with col_stats3:
        if st.button("🗑️ Teljes Pakli Ürítése", use_container_width=True, type="secondary"):
            gs.set_deck([])
            st.rerun()

    st.markdown("---")

    col_coll, col_deck = st.columns(2)

    # BAL: Kártyagyűjtemény
    with col_coll:
        st.markdown("### 📦 Kártyagyűjteményed")
        st.markdown("<small style='color: #a5a9c2;'>Kattints a Hozzáad gombra a kártya pakliba tételéhez.</small>", unsafe_allow_html=True)

        for cname, card in gs.player_collection.items():
            in_deck = (cname in gs.player_deck)
            e_data = ELEM_CONFIG.get(card.element, {})
            e_class = f"card-{card.element}"

            with st.container():
                st.markdown(f"""
                <div class='damareen-card {e_class}'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='font-size: 1.1rem; font-weight: bold; color: #ffffff;'>{card.name}</div>
                        <span class='badge' style='background: {e_data.get('border', '#555')}; color: white;'>
                            {e_data.get('icon', '')} {e_data.get('name', card.element)}
                        </span>
                    </div>
                    <div style='color: #d4af37; font-weight: bold; margin-top: 6px;'>
                        ⚔️ {card.damage} Sebzés &nbsp;|&nbsp; ❤️ {card.max_hp} Életerő
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if in_deck:
                    st.button(f"✅ Pakliban van ({cname})", key=f"coll_in_{cname}", disabled=True, use_container_width=True)
                else:
                    can_add = (curr_deck < max_deck)
                    if st.button(f"➕ Hozzáad: {cname}", key=f"coll_add_{cname}", disabled=not can_add, use_container_width=True):
                        new_deck = list(gs.player_deck) + [cname]
                        gs.set_deck(new_deck)
                        st.rerun()

    # JOBB: Aktív Harci Pakli (Sorrendkezeléssel)
    with col_deck:
        st.markdown("### 🛡️ Aktív Harci Paklid (Bevetési Sorrend)")
        st.markdown("<small style='color: #a5a9c2;'>A csatában a kártyák felülről lefelé haladva indulnak harcba.</small>", unsafe_allow_html=True)

        if not gs.player_deck:
            st.warning("A paklid jelenleg üres! Válassz kártyákat a bal oldali gyűjteményedből.")
        else:
            for idx, cname in enumerate(gs.player_deck):
                card = gs.player_collection[cname]
                e_data = ELEM_CONFIG.get(card.element, {})

                tile_col, btn_up_col, btn_down_col, btn_del_col = st.columns([5, 1, 1, 1])

                with tile_col:
                    st.markdown(f"""
                    <div style='background: #191b29; border: 1px solid #d4af37; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #d4af37; font-weight: 800;'>#{idx+1} {card.name}</span>
                            <span style='color: {e_data.get('color', '#fff')}; font-size: 0.85rem;'>{e_data.get('icon', '')} {e_data.get('name', card.element)}</span>
                        </div>
                        <div style='font-size: 0.8rem; color: #a5a9c2; margin-top: 2px;'>
                            ⚔️ {card.damage} ATK &nbsp;|&nbsp; ❤️ {card.max_hp} HP
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with btn_up_col:
                    if st.button("▲", key=f"deck_up_{idx}", disabled=(idx == 0), help="Előrébb mozgatás"):
                        new_deck = list(gs.player_deck)
                        new_deck[idx], new_deck[idx - 1] = new_deck[idx - 1], new_deck[idx]
                        gs.set_deck(new_deck)
                        st.rerun()

                with btn_down_col:
                    if st.button("▼", key=f"deck_down_{idx}", disabled=(idx == len(gs.player_deck) - 1), help="Hátrébb mozgatás"):
                        new_deck = list(gs.player_deck)
                        new_deck[idx], new_deck[idx + 1] = new_deck[idx + 1], new_deck[idx]
                        gs.set_deck(new_deck)
                        st.rerun()

                with btn_del_col:
                    if st.button("✕", key=f"deck_del_{idx}", help="Eltávolítás a pakliból"):
                        new_deck = list(gs.player_deck)
                        del new_deck[idx]
                        gs.set_deck(new_deck)
                        st.rerun()


# =============================================================================
# 3. NÉZET: VILÁG KÓDEX (CODEX & CARDS)
# =============================================================================
elif nav == "📜 Világ Kódex":
    st.markdown("## 📜 Damareen Világ Kódex")
    st.markdown("A játék teljes univerzumának kártyakészlete, legendás vezérei és kazamatái.")

    search_query = st.text_input("🔍 Keresés kártya neve vagy eleme alapján:", "").strip().lower()

    # 1. Vezérkártyák (Boss cards)
    st.markdown("### ⭐ Legendás Vezérkártyák (Boss lapok)")
    st.markdown("<small style='color: #a5a9c2;'>A vezérkártyák egy alap sima lapból jönnek létre, duplázott sebzéssel vagy duplázott életerővel.</small>", unsafe_allow_html=True)

    boss_cols = st.columns(len(gs.boss_cards))
    for idx, (bname, boss) in enumerate(gs.boss_cards.items()):
        if search_query and (search_query not in boss.name.lower() and search_query not in boss.element.lower()):
            continue
        e_data = ELEM_CONFIG.get(boss.element, {})
        with boss_cols[idx % len(boss_cols)]:
            st.markdown(f"""
            <div class='damareen-card damareen-card-boss'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='font-size: 1.15rem; font-weight: bold; color: #d4af37;'>⭐ {boss.name}</span>
                    <span class='badge' style='background: {e_data.get('border', '#333')}; color: white;'>
                        {e_data.get('icon', '')} {e_data.get('name', boss.element)}
                    </span>
                </div>
                <div style='color: #f7f8fc; font-weight: bold; font-size: 1rem; margin-top: 10px;'>
                    ⚔️ Sebzés: <span style='color: #d4af37;'>{boss.damage}</span><br>
                    ❤️ Életerő: <span style='color: #2ecc71;'>{boss.max_hp}</span>
                </div>
                <div style='color: #a5a9c2; font-size: 0.75rem; margin-top: 8px;'>
                    Különleges kazamata vezér
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Sima lapok (World Cards)
    st.markdown("### ⚔️ Damareen Sima Világkártyái")

    world_card_list = list(gs.world_cards.values())
    filtered_cards = [
        c for c in world_card_list
        if not search_query or (search_query in c.name.lower() or search_query in c.element.lower())
    ]

    card_cols = st.columns(4)
    for idx, card in enumerate(filtered_cards):
        is_owned = card.name in gs.player_collection
        e_data = ELEM_CONFIG.get(card.element, {})
        e_class = f"card-{card.element}"
        status_badge = "<span class='badge badge-owned'>✓ Gyűjteményben</span>" if is_owned else "<span class='badge badge-unowned'>🔒 Megszerezhető</span>"

        with card_cols[idx % 4]:
            st.markdown(f"""
            <div class='damareen-card {e_class}'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 1.1rem; font-weight: bold; color: #ffffff;'>{card.name}</span>
                    <span class='badge' style='background: {e_data.get('border', '#333')}; color: white;'>
                        {e_data.get('icon', '')} {e_data.get('name', card.element)}
                    </span>
                </div>
                <div style='margin: 8px 0;'>
                    <span style='color: #d4af37; font-weight: bold;'>⚔️ {card.damage}</span> &nbsp;|&nbsp;
                    <span style='color: #2ecc71; font-weight: bold;'>❤️ {card.max_hp}</span>
                </div>
                <div>{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # 3. Kazamaták listája
    st.markdown("### 🏰 Kazamaták Összesítése")
    for dname, dun in gs.dungeons.items():
        type_str = "Egyszerű kazamata" if dun.dtype == 'egyszeru' else ("Kis kazamata" if dun.dtype == 'kis' else "Nagy kazamata")
        reward_str = "Győztes lap +1 Sebzést kap" if dun.reward_type == 'sebzes' else (
            "Győztes lap +2 Életerőt kap" if dun.reward_type == 'eletero' else "A játékos megkapja az első hiányzó sima kártyát"
        )

        with st.expander(f"🏰 {dun.name} ({type_str})"):
            st.markdown(f"""
            - **Típus:** `{dun.dtype}`
            - **Sima lapok serege:** {", ".join(dun.plain_card_names)}
            - **Vezér:** {f"⭐ **{dun.boss_card_name}**" if dun.boss_card_name else "*Nincs külön vezér*"}
            - **Győzelmi jutalom:** **{reward_str}**
            """)


# =============================================================================
# 4. NÉZET: SZABÁLYZAT & ELEMEK (RULES & MATRIX)
# =============================================================================
elif nav == "📖 Szabályzat & Elemek":
    st.markdown("## 📖 Szabályzat & Elemi Kölcsönhatások")
    st.markdown("A Damareen világában a 4 őselem kölcsönhatása alapvetően meghatározza a csaták kimenetelét.")

    # Interaktív elem-kalkulátor
    st.markdown("### ⚡ Interaktív Elemkalkulátor")
    calc_c1, calc_c2, calc_c3, calc_c4 = st.columns(4)

    elem_list = ["fold", "levego", "viz", "tuz"]
    elem_labels = {"fold": "🌱 Föld", "levego": "🌪️ Levegő", "viz": "💧 Víz", "tuz": "🔥 Tűz"}

    with calc_c1:
        atk_elem = st.selectbox("Támadó Elem:", elem_list, format_func=lambda x: elem_labels[x], index=1)
    with calc_c2:
        def_elem = st.selectbox("Védekező Elem:", elem_list, format_func=lambda x: elem_labels[x], index=0)
    with calc_c3:
        base_dmg = st.number_input("Alap Sebzés:", min_value=1, max_value=50, value=3)

    final_dmg, mult, desc = calculate_damage(atk_elem, def_elem, base_dmg)

    with calc_c4:
        st.markdown("<div style='margin-top: 24px;'>", unsafe_allow_html=True)
        if mult == 2.0:
            st.success(f"**{final_dmg} sebzés** (⚡ 2.0x Erős!)")
        elif mult == 0.5:
            st.info(f"**{final_dmg} sebzés** (🛡️ 0.5x Gyenge!)")
        else:
            st.markdown(f"**{final_dmg} sebzés** (⚖️ 1.0x Semleges)")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Elemek áttekintése
    st.markdown("### 🌪️ Elemi Rendszer és Szabályok")
    elem_c1, elem_c2, elem_c3, elem_c4 = st.columns(4)

    with elem_c1:
        st.markdown("""
        <div class='damareen-card card-levego'>
            <div style='font-size: 1.2rem; font-weight: bold; color: #bb86fc;'>🌪️ LEVEGŐ</div>
            <div style='color: #2ecc71; margin-top: 6px;'><b>Erős (2x):</b> Föld, Víz</div>
            <div style='color: #e74c3c;'><b>Gyenge (0.5x):</b> Tűz</div>
            <div style='color: #a5a9c2; font-size: 0.8rem; margin-top: 6px;'>Azonos elemmel szemben: 1x</div>
        </div>
        """, unsafe_allow_html=True)

    with elem_c2:
        st.markdown("""
        <div class='damareen-card card-viz'>
            <div style='font-size: 1.2rem; font-weight: bold; color: #3498db;'>💧 VÍZ</div>
            <div style='color: #2ecc71; margin-top: 6px;'><b>Erős (2x):</b> Levegő, Tűz</div>
            <div style='color: #e74c3c;'><b>Gyenge (0.5x):</b> Föld</div>
            <div style='color: #a5a9c2; font-size: 0.8rem; margin-top: 6px;'>Azonos elemmel szemben: 1x</div>
        </div>
        """, unsafe_allow_html=True)

    with elem_c3:
        st.markdown("""
        <div class='damareen-card card-fold'>
            <div style='font-size: 1.2rem; font-weight: bold; color: #2ecc71;'>🌱 FÖLD</div>
            <div style='color: #2ecc71; margin-top: 6px;'><b>Erős (2x):</b> Levegő, Tűz</div>
            <div style='color: #e74c3c;'><b>Gyenge (0.5x):</b> Víz</div>
            <div style='color: #a5a9c2; font-size: 0.8rem; margin-top: 6px;'>Azonos elemmel szemben: 1x</div>
        </div>
        """, unsafe_allow_html=True)

    with elem_c4:
        st.markdown("""
        <div class='damareen-card card-tuz'>
            <div style='font-size: 1.2rem; font-weight: bold; color: #e74c3c;'>🔥 TŰZ</div>
            <div style='color: #2ecc71; margin-top: 6px;'><b>Erős (2x):</b> Föld, Víz</div>
            <div style='color: #e74c3c;'><b>Gyenge (0.5x):</b> Levegő</div>
            <div style='color: #a5a9c2; font-size: 0.8rem; margin-top: 6px;'>Azonos elemmel szemben: 1x</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Szabályzati kivonat
    st.markdown("### 📜 Hivatalos Versenyszabályzat Kivonat")
    st.markdown("""
1. **A harc lefolyása és körök:**
   - Minden harc kezdetekor a lapok életereje alaphelyzetbe áll vissza.
   - Egy kör 2 akcióból áll:
     1. Kazamata cselekszik (új lap kijátszása vagy támadás).
     2. Játékos cselekszik (új lap kijátszása ha az előző elesett, vagy visszatámadás).
   - Ha a kazamata az 1. akcióban legyőzi a játékos utolsó lapját, a játék azonnal véget ér (nincs 2. akció).

2. **Kazamata típusok és nyeremények:**
   - **Egyszerű kazamata (1 sima lap):** A játékos utoljára harcolt győztes lapja a kazamata jutalomtípusától függően **+1 Sebzést** VAGY **+2 Életerőt** kap.
   - **Kis kazamata (3 sima lap + 1 vezér):** A győztes lap a jutalomtípustól függően **+1 Sebzést** VAGY **+2 Életerőt** kap.
   - **Nagy kazamata (5 sima lap + 1 vezér):** A játékos megkapja a világból az **első olyan sima kártyát**, amely még nincs meg a gyűjteményében. Ha már minden lap megvan, nagy kazamata harc nem indítható!

3. **Pakliépítés:**
   - A pakli mérete legfeljebb a gyűjtemény felét teheti ki, felfelé kerekítve (`ceil(méret / 2)`).
   - A pakliban lévő kártyák sorrendje determinisztikusan meghatározza a bevetési sorrendet.
    """)


# =============================================================================
# 5. NÉZET: IN.TXT TESZTELŐ & EXPORTÁLÁS
# =============================================================================
elif nav == "🧪 In.txt Tesztelő & Export":
    st.markdown("## 🧪 In.txt Fájlfeldolgozó & Állapot Exportálás")
    st.markdown("Futtass le komplett verseny teszteseteket (`in.txt`), vagy mentsd le a játék aktuális állapotát!")

    test_tab1, test_tab2 = st.tabs(["📥 In.txt Futtatása & Tesztelés", "📤 Aktuális Állapot Exportálása"])

    with test_tab1:
        st.markdown("### 📥 in.txt fájl feldolgozása")
        st.markdown("Tölts fel egy `in.txt` fájlt vagy illeszd be a tesztparancsokat. A rendszer végrehajtja a parancsokat, és letölthetővé teszi az elkészült `out.*.txt` fájlokat.")

        uploaded_file = st.file_uploader("Válassz in.txt fájlt:", type=["txt"])
        raw_input_text = st.text_area("Vagy illeszd be a szöveges parancsokat:", height=180, placeholder="uj kartya;Aragorn;2;5;tuz\nuj jatekos\nfelvetel gyujtemenybe;Aragorn\n...")

        if st.button("🚀 Teszt Végrehajtása", type="primary"):
            content_to_run = ""
            if uploaded_file is not None:
                content_to_run = uploaded_file.getvalue().decode('utf-8')
            elif raw_input_text.strip():
                content_to_run = raw_input_text.strip()

            if not content_to_run:
                st.error("Kérjük tölts fel egy fájlt vagy illessz be parancsokat!")
            else:
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_path = os.path.join(temp_dir, "in.txt")
                    with open(in_path, "w", encoding="utf-8") as f:
                        f.write(content_to_run)

                    test_gs = GameState()
                    try:
                        test_gs.parse_in_file(in_path, working_dir=temp_dir)
                        st.success("✅ A parancsok sikeresen és hiba nélkül lefutottak!")

                        # Generált out.* fájlok keresése
                        out_files = [fn for fn in os.listdir(temp_dir) if fn.startswith("out.") and fn.endswith(".txt")]
                        if out_files:
                            st.markdown(f"#### 📄 Generált kimeneti fájlok ({len(out_files)} db):")
                            for fn in sorted(out_files):
                                fpath = os.path.join(temp_dir, fn)
                                with open(fpath, "r", encoding="utf-8") as out_f:
                                    out_content = out_f.read()
                                
                                exp_col1, exp_col2 = st.columns([4, 1])
                                with exp_col1:
                                    with st.expander(f"📜 {fn} előnézete"):
                                        st.code(out_content, language="text")
                                with exp_col2:
                                    st.download_button(
                                        label=f"⬇️ {fn}",
                                        data=out_content,
                                        file_name=fn,
                                        mime="text/plain",
                                        key=f"dl_{fn}"
                                    )

                        # Opcionálisan betöltheti ezt az állapotot aktívnak
                        if st.button("🌟 Ennek a tesztállapotnak a betöltése az aktív GUI-ba"):
                            st.session_state.gs = test_gs
                            st.success("Tesztállapot betöltve az aktív játékba!")
                            st.rerun()

                    except Exception as e:
                        st.error(f"Hiba a teszt futtatása közben: {e}")

    with test_tab2:
        st.markdown("### 📤 Aktuális Állapot Exportálása")
        st.markdown("Mentsd le a jelenlegi játékállapotot a versenykiírás szerinti hivatalos szintaxisban!")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            st.markdown("#### 🌍 Világ Export (`out.vilag.txt`)")
            world_lines = gs.export_world()
            world_str = "\n".join(world_lines) + "\n"
            st.text_area("Világ sorai:", world_str, height=200, disabled=True)
            st.download_button(
                label="⬇️ Világ Letöltése (out.vilag.txt)",
                data=world_str,
                file_name="out.vilag.txt",
                mime="text/plain",
                use_container_width=True
            )

        with col_exp2:
            st.markdown("#### 👤 Játékos Export (`out.jatekos.txt`)")
            player_lines = gs.export_player()
            player_str = "\n".join(player_lines) + "\n"
            st.text_area("Játékos sorai:", player_str, height=200, disabled=True)
            st.download_button(
                label="⬇️ Játékos Letöltése (out.jatekos.txt)",
                data=player_str,
                file_name="out.jatekos.txt",
                mime="text/plain",
                use_container_width=True
            )
