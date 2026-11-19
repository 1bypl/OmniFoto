# Changelog

Wszystkie istotne zmiany w projekcie są dokumentowane w tym pliku.
Format oparty na konwencji [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/).

## [1.0.0] - 2026-11-19

### Dodane
- Równoległe wyszukiwanie w wielu darmowych źródłach: Wallhaven, Wikimedia Commons, NASA Images, Reddit, Unsplash, Pexels, Pixabay, Openverse oraz dane demo offline.
- Animowany licznik, pasek postępu z czasem wyszukiwania i statystykami per źródło.
- Widoki kafelków i listy, pulsująca dotąd jakość (obecnie 🟢/🟡/🔴 z pełnym opisem).
- Plakietki urządzeń 🖥 PC / 💻 LAP / 📱 TEL / 📟 TAB oraz ikony animacji i wygaszacza.
- Ulubione, ostatnio przeglądane, najlepsze (filtr czasu) i kategorie tematyczne.
- Własne kolekcje: tworzenie, import plików/folderów, import/eksport JSON, usuwanie i wyświetlanie jako galeria.
- Pokaz slajdów z nawigacją klawiaturą, automatycznym odtwarzaniem, zoomem kółkiem myszy, przesuwaniem przeciąganiem i etykietą szczegółów pod kursorem.
- Sześć motywów, przełącznik skórek jednym kliknięciem, siedem języków interfejsu.
- Tryb prywatny (brak ciasteczek i historii na dysku), nagłówek DNT, opcjonalne proxy/Tor.
- Instalatory dla Fedory (RPM) i Debiana/Ubuntu (.deb).
- Zrzuty ekranu w `docs/screenshots/`.

### Zmienione
- Silnik zapytań: krótka fraza trafia do API, pełne zapytanie (cyfry wersji, „KDE", „by night") decyduje o rankingu.
- Dopisywanie słów do zapytania doprecyzowuje wyniki zamiast je resetować (przycisk ⊕).
- Kategoria stała się miękką wskazówką zamiast twardego filtra.
- Wyłączono domyślnie scraperzy HTML i Flickr jako źródła niskiej jakości.

### Naprawione
- Przezroczystość maskotki i napisu pod logo.
- Rozciąganie paska wyszukiwania na połowę okna (sztywny rozmiar w pionie).
- Przesyłanie sygnałów z wątku roboczego bezpośrednio do GUI (kolejka Qt).
- Blokowanie nowego wyszukiwania przez poprzednie oraz zawieszanie przy szybkich zapytaniach.
- Wyświetlanie kolekcji lokalnych w głównym widoku.

[1.0.0]: https://github.com/1bypl/OmniFoto/releases/tag/v1.0.0

---

Copyright (C) 2026 1bypl — GPL-3.0-or-later
