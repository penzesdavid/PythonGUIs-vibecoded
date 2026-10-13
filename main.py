"""
Damareen Kártyajáték - Főprogram és belépési pont
Dusza Árpád Országos Programozói Emlékverseny 2025/2026 - I. forduló

Használat:
  1. Teszt mód:
     python main.py <teszt_mappa_eleresi_utja>
     Például: python main.py c:\\tesztek\\teszteset_01\\
     A program beolvassa az in.txt fájlt és legenerálja az out.*.txt fájlokat.

  2. Játék mód (GUI):
     python main.py --ui
     Elindítja a Tkinter grafikus felületet az előre definiált világgal.
"""

import sys
import os
from game_logic import GameState


def print_usage():
    print("Damareen Kártyajáték - Dusza Árpád 2025/2026")
    print("Használat:")
    print("  python main.py --ui                  -> Játék mód indítása asztali felülettel (CustomTkinter GUI)")
    print("  python main.py --streamlit           -> Játék mód indítása böngészős felülettel (Streamlit GUI)")
    print("  python main.py <teszt_mappa_eleres> -> Teszt mód indítása (in.txt feldolgozása a mappában)")
    print("Példa:")
    print("  python main.py c:\\tesztek\\teszteset_01\\")


def main():
    if len(sys.argv) < 2:
        # Ha paraméter nélkül indítják, játék módban (GUI) indul el a kényelem kedvéért
        print("Nem adott meg paramétert. Játék mód (--ui) indítása...")
        import gui
        gui.start_gui()
        return

    arg = sys.argv[1].strip()

    if arg in ('--streamlit', '-st', '--web', '/st', '/streamlit'):
        # Játék mód: Streamlit böngészős GUI
        import subprocess
        st_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", st_app_path])
        return

    if arg in ('--ui', '-ui', '/ui'):
        # Játék mód (CustomTkinter GUI)
        import gui
        gui.start_gui()
        return

    if arg in ('--help', '-h', '/?', '-help'):
        print_usage()
        return

    # Teszt mód: a paraméter a teszt mappa abszolút vagy relatív elérési útja
    target_dir = os.path.abspath(arg)
    if os.path.isfile(target_dir):
        # Ha közvetlenül az in.txt-t adták át
        in_path = target_dir
        target_dir = os.path.dirname(target_dir)
    else:
        in_path = os.path.join(target_dir, "in.txt")

    if not os.path.exists(in_path):
        print(f"Hiba: A megadott helyen nem található in.txt fájl: {in_path}", file=sys.stderr)
        sys.exit(1)

    try:
        gs = GameState()
        gs.parse_in_file(in_path, working_dir=target_dir)
        # Tiszta csendes kilépés, ahogy a versenykiírás kéri:
        # "Teszt módban 'tiszta' konzolos alkalmazásként kell működnie az alkalmazásnak,
        # azaz ne várjon felhasználói interakcióra, és futás után automatikusan záródjon be."
        sys.exit(0)
    except Exception as e:
        print(f"Hiba a teszt futtatása során: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
