"""
Automatikus teszt a game_logic.py ellenőrzésére a PDF-ben megadott mintapéldával.
"""

import os
import shutil
import tempfile
import unittest
from game_logic import GameState, calculate_damage


class TestDamareenLogic(unittest.TestCase):
    def test_damage_multipliers(self):
        # Erős (2x)
        dmg, mult, _ = calculate_damage("levego", "fold", 2)
        self.assertEqual(dmg, 4)
        self.assertEqual(mult, 2.0)

        dmg, mult, _ = calculate_damage("fold", "levego", 3)
        self.assertEqual(dmg, 6)

        dmg, mult, _ = calculate_damage("levego", "viz", 2)
        self.assertEqual(dmg, 4)

        dmg, mult, _ = calculate_damage("fold", "tuz", 3)
        self.assertEqual(dmg, 6)

        dmg, mult, _ = calculate_damage("viz", "tuz", 4)
        self.assertEqual(dmg, 8)

        # Gyenge (0.5x, lefelé kerekítve)
        dmg, mult, _ = calculate_damage("levego", "tuz", 2)
        self.assertEqual(dmg, 1)
        self.assertEqual(mult, 0.5)

        dmg, mult, _ = calculate_damage("levego", "tuz", 3)
        self.assertEqual(dmg, 1)  # 3 // 2 = 1

        dmg, mult, _ = calculate_damage("fold", "viz", 2)
        self.assertEqual(dmg, 1)

        # Semleges (1x)
        dmg, mult, _ = calculate_damage("levego", "levego", 2)
        self.assertEqual(dmg, 2)
        self.assertEqual(mult, 1.0)

        dmg, mult, _ = calculate_damage("fold", "fold", 5)
        self.assertEqual(dmg, 5)

    def test_pdf_example_flow(self):
        temp_dir = tempfile.mkdtemp()
        try:
            in_content = """uj kartya;Aragorn;2;5;tuz
uj kartya;Sadan;2;4;levego
uj kartya;Corky;2;4;fold
uj kartya;Kira;2;7;levego
uj kartya;Eowyn;2;5;viz
uj kartya;ObiWan;2;2;fold
uj kartya;Tul'Arak;2;4;fold
uj vezer;Darth ObiWan;ObiWan;sebzes
uj kazamata;egyszeru;Teszt1a Kazamata;Sadan;eletero
uj kazamata;egyszeru;Teszt1b Kazamata;Aragorn;sebzes
uj kazamata;kis;Teszt2a Kazamata;Aragorn,Eowyn,ObiWan;Darth ObiWan;eletero
uj kazamata;kis;Teszt2b Kazamata;Sadan,Eowyn,Kira;Darth ObiWan;sebzes
uj kazamata;nagy;Teszt3 Kazamata;Aragorn,Eowyn,ObiWan,Kira,Tul'Arak;Darth ObiWan
export vilag;out.vilag01.txt
uj jatekos
felvetel gyujtemenybe;Aragorn
felvetel gyujtemenybe;Sadan
felvetel gyujtemenybe;Corky
felvetel gyujtemenybe;Kira
uj pakli;Corky,Kira
harc;Teszt1a Kazamata;out.harc01.txt
export jatekos;out.jatekos02.txt
"""
            in_file_path = os.path.join(temp_dir, "in.txt")
            with open(in_file_path, "w", encoding="utf-8") as f:
                f.write(in_content)

            gs = GameState()
            gs.parse_in_file(in_file_path, working_dir=temp_dir)

            # 1. out.vilag01.txt ellenőrzése
            vilag_path = os.path.join(temp_dir, "out.vilag01.txt")
            self.assertTrue(os.path.exists(vilag_path))
            with open(vilag_path, "r", encoding="utf-8") as f:
                vilag_lines = [l.strip() for l in f if l.strip()]

            expected_vilag = [
                "kartya;Aragorn;2;5;tuz",
                "kartya;Sadan;2;4;levego",
                "kartya;Corky;2;4;fold",
                "kartya;Kira;2;7;levego",
                "kartya;Eowyn;2;5;viz",
                "kartya;ObiWan;2;2;fold",
                "kartya;Tul'Arak;2;4;fold",
                "vezer;Darth ObiWan;4;2;fold",
                "kazamata;egyszeru;Teszt1a Kazamata;Sadan;eletero",
                "kazamata;egyszeru;Teszt1b Kazamata;Aragorn;sebzes",
                "kazamata;kis;Teszt2a Kazamata;Aragorn,Eowyn,ObiWan;Darth ObiWan;eletero",
                "kazamata;kis;Teszt2b Kazamata;Sadan,Eowyn,Kira;Darth ObiWan;sebzes",
                "kazamata;nagy;Teszt3 Kazamata;Aragorn,Eowyn,ObiWan,Kira,Tul'Arak;Darth ObiWan"
            ]
            self.assertEqual(vilag_lines, expected_vilag)

            # 2. out.harc01.txt ellenőrzése
            harc_path = os.path.join(temp_dir, "out.harc01.txt")
            self.assertTrue(os.path.exists(harc_path))
            with open(harc_path, "r", encoding="utf-8") as f:
                harc_lines = [l.strip() for l in f if l.strip()]

            expected_harc = [
                "harc kezdodik;Teszt1a Kazamata",
                "1.kor;kazamata;kijatszik;Sadan;2;4;levego",
                "1.kor;jatekos;kijatszik;Corky;2;4;fold",
                "2.kor;kazamata;tamad;Sadan;4;Corky;0",
                "2.kor;jatekos;kijatszik;Kira;2;7;levego",
                "3.kor;kazamata;tamad;Sadan;2;Kira;5",
                "3.kor;jatekos;tamad;Kira;2;Sadan;2",
                "4.kor;kazamata;tamad;Sadan;2;Kira;3",
                "4.kor;jatekos;tamad;Kira;2;Sadan;0",
                "jatekos nyert;eletero;Kira"
            ]
            self.assertEqual(harc_lines, expected_harc)

            # 3. out.jatekos02.txt ellenőrzése
            jatekos_path = os.path.join(temp_dir, "out.jatekos02.txt")
            self.assertTrue(os.path.exists(jatekos_path))
            with open(jatekos_path, "r", encoding="utf-8") as f:
                jatekos_lines = [l.strip() for l in f if l.strip()]

            expected_jatekos = [
                "gyujtemeny;Aragorn;2;5;tuz",
                "gyujtemeny;Sadan;2;4;levego",
                "gyujtemeny;Corky;2;4;fold",
                "gyujtemeny;Kira;2;9;levego",
                "pakli;Corky",
                "pakli;Kira"
            ]
            self.assertEqual(jatekos_lines, expected_jatekos)
            print("Minden teszt sikeresen lefutott, a kimenetek 100%-ban megegyeznek a kiírással!")

        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
