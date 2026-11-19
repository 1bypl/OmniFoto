# Wkład w OmniFoto 🐸

Dziękuję za zainteresowanie projektem! OmniFoto jest na licencji **GPL-3.0-or-later**, więc każdy może go używać, modyfikować i rozpowszechniać na tych samych warunkach.

## Jak zacząć

```bash
git clone https://github.com/1bypl/OmniFoto.git
cd OmniFoto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m omnifoto
```

Na Fedorze zamiast venv można użyć pakietów systemowych:

```bash
sudo dnf install python3-pyside6 python3-pysocks
./run.sh
```

## Uruchamianie testów

```bash
python3 -m unittest discover -s tests -v
```

Testy logiki (modele, ustawienia, wyszukiwanie) nie wymagają interfejsu graficznego.

## Struktura kodu

| Katalog | Zawartość |
| --- | --- |
| `omnifoto/search/` | dostawcy wyników (api / scrape / demo) i `SearchManager` |
| `omnifoto/ui/` | okna, widoki, motywy, animacje |
| `omnifoto/assets/` | maskotka SVG i ikona aplikacji |
| `packaging/` | instalatory RPM i DEB, plik `.desktop`, generator zrzutów |
| `tests/` | testy automatyczne |

## Dodanie nowego źródła tapet

1. Utwórz klasę dziedziczącą po `SearchProvider` w `omnifoto/search/`.
2. Zaimplementuj `search(query, limit, **kwargs) -> list[Wallpaper]`.
3. Zarejestruj klasę w `PROVIDERS` w `omnifoto/search/manager.py`.
4. Dodaj wpis do `DEFAULT_SOURCES` w `omnifoto/constants.py`.
5. Dodaj test w `tests/`.

Dostawca musi być odporny na błędy sieci — `SearchManager` pomija źródła, które nie odpowiadają.

## Zasady

- Brak telemetrii, śledzenia i reklam.
- Żadnych ukrytych połączeń — tylko jawnie pokazane w ustawieniach źródła i opcjonalne proxy.
- Kod i komentarze w języku angielskim, interfejs tłumaczony w `omnifoto/i18n.py`.
- Zmiany interfejsu powinny być zgodne z motywami i skalowaniem Qt.

## Zrzuty ekranu

```bash
QT_QPA_PLATFORM=offscreen python3 packaging/make_screenshots.py
```

Pliki trafią do `docs/screenshots/`.

---

Copyright (C) 2026 1bypl — https://github.com/1bypl
