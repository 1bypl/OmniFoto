# 🐸 OmniFoto

**Lokalna przeglądarka i wyszukiwarka tapet** — nowoczesny, prywatny i przejrzysty program działający wyłącznie na komputerze użytkownika.

OmniFoto łączy wygodę znaną z serwisów z tapetami (kafelki, lista, podgląd, ulubione, pokaz slajdów) z bezpieczeństwem aplikacji desktopowej: **bez śledzenia, bez reklam, bez telemetrii, bez zapisywania historii w trybie prywatnym**.

> Autor: **1bypl** • https://github.com/1bypl  
> Licencja: **GPL-3.0-or-later** (pełny tekst w pliku `LICENSE`)  
> Wersja: **1.0.0**  
> Systemy: **Fedora 45 KDE** (testowane), Debian, Ubuntu; Windows — planowany

## Zrzuty ekranu

| Widok | Podgląd |
| --- | --- |
| Wyniki — kafelki | ![Kafelki](docs/screenshots/01-wyniki-kafelki.png) |
| Wyniki — lista | ![Lista](docs/screenshots/02-wyniki-lista.png) |
| Szczegóły tapety | ![Szczegóły](docs/screenshots/03-szczegoly-i-podglad.png) |
| Pokaz slajdów | ![Slideshow](docs/screenshots/04-pokaz-slajdow.png) |
| Ustawienia | ![Ustawienia](docs/screenshots/05-ustawienia.png) |
| Własne kolekcje | ![Kolekcje](docs/screenshots/06-kolekcje.png) |
| O programie | ![O programie](docs/screenshots/07-o-programie.png) |

---

## Spis treści

1. [Najważniejsze funkcje](#najważniejsze-funkcje)
2. [Szczera uwaga o wyszukiwaniu i prywatności](#szczera-uwaga-o-wyszukiwaniu-i-prywatności)
3. [Instalacja na Fedorze 45](#instalacja-na-fedorze-45)
4. [Uruchomienie](#uruchomienie)
5. [Zbudowanie pakietu RPM](#zbudowanie-pakietu-rpm)
6. [Korzystanie z programu](#korzystanie-z-programu)
7. [Źródła i klucze API](#źródła-i-klucze-api)
8. [Obsługiwane formaty i rozdzielczości](#obsługiwane-formaty-i-rozdzielczości)
9. [Struktura projektu](#struktura-projektu)
10. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
11. [Licencja](#licencja)

---

## Najważniejsze funkcje

### 🔍 Inteligentne wyszukiwanie
- Wpisanie frazy uruchamia równoległe przeszukiwanie **wielu baz jednocześnie** (wątki w tle — interfejs się nie zacina): Wallhaven (wielostronnicowo), **Wikimedia Commons, NASA Images, Flickr**, Reddit, Unsplash/Pexels/Pixabay (z kluczem), Google/Bing (best-effort) i dane demo. Jedno zapytanie potrafi zebrać **setki surowych wyników** — przycisk **„＋ Więcej"** doładowuje kolejne 80.
- **Animowany licznik** pokazuje, ile wyników znaleziono i z ilu źródeł, na bieżąco podczas skanowania.
- **Aktywny pasek postępu** w kolorze wybranego motywu.
- Jeśli któreś źródło nie odpowie albo jest nieaktualne — program **po cichu pomija je i szuka dalej** w innych bazach.
- **Dopisywanie słów działa zamiast psuć wyniki**: do API idzie krótka fraza główna (2–3 słowa, bez cyfr wersji i słów typu „dla", „tapety"), natomiast pełne zapytanie — z `45`, `KDE`, `by night` — służy do **oceny i ustawienia wyników**. Dzięki temu `Fedora 45` → `Fedora 45-Glassy.png`, `Debian 13` → `Debian 13 (Trixie)`, a `New York by night` → nocne panoramy wieżowców.
- Polskie słowa i odmiany (`las`, `laptopa`, `zwierzęta`, `kosmos`) są tłumaczone na angielskie, literówki korygowane (`parot → parrot`), a nazwa źródła (`nasa mars`) staje się wskazówką, nie częścią zapytania. Wikimedia wykonuje kilka prostych zapytań `intitle:` i scala wyniki, a rezultaty bez trafnego tytułu/tagu są odrzucane. Wyniki z różnych źródeł są przeplatane; kategoria to miękka wskazówka.
- **Bardzo płytki pasek narzędzi (ok. 58 px)**: czas, wyniki per źródło i suma zmieściły się w jednym wierszu z filtrami; animowany pasek ma 3 px.
- **Doprecyzowywanie zamiast resetu**: przycisk **⊕** (domyślnie włączony) dodaje nowe wyniki do poprzednich, więc `Fedora 45` → `Fedora 45 KDE` nie czyści ekranu — trafniejsze obrazy wędrują na górę. Przycisk **🔄** wymusza świeże zapytanie do wszystkich źródeł bez zmiany frazy i ustawień.
- **Nieblokujące wyszukiwanie**: każde zapytanie ma własny wątek i numer — wpisanie nowej frazy zawsze działa, nawet gdy poprzednie źródło jeszcze odpowiada. Stare wyniki są odrzucane; sygnały trafiają do GUI wyłącznie przez kolejkę Qt (stabilność).
- Wyniki można sortować według: trafności, **jakości, rozdzielczości, daty, rozmiaru pliku, formatu, popularności (ocen) i liczby pobrań**.
- Filtr czasu: **wszystko / dzisiaj / tydzień / miesiąc / rok** (zakładka „Najlepsze”).

### 🎨 Nowoczesny interfejs
- Widok **kafelek** lub **listy** (przełączanie jednym kliknięciem).
- Każdy kafelek zawiera: miniaturę, tytuł, rozdzielczość, format, rozmiar, tagi oraz **czytelną kropkę jakości** 🟢 (wysoka, ≥ 6 MP) / 🟡 (średnia, ≥ 2 MP) / 🔴 (niska).
- **Czytelne plakietki urządzeń** dobierane automatycznie na podstawie proporcji: 🖥 PC, 💻 LAP, 📱 TEL, 📟 TAB (po najechaniu widzisz pełną nazwę). Jeśli tapeta pasuje do trzech urządzeń — zobaczysz trzy plakietki.
- Dodatkowe ikony: 🎞️ tapeta animowana, 🌙 wygaszacz ekranu.
- **Złota gwiazdka** ⭐ dodaje do Ulubionych, zielony przycisk **⬇ Pobierz**, **👁 Podejrzyj** otwiera podgląd. Prawy przycisk myszy na kafelku dodaje tapetę do kolekcji.
- **📚 Własne kolekcje**: twórz je, importuj z pliku JSON, **dodawaj pojedyncze pliki graficzne lub całe foldery** (przyciski „📁 Nowa z folderu" i „🖼 Dodaj pliki/folder"), eksportuj i usuwaj w oknie „Kolekcje". Kolekcję możesz też otworzyć jako galerię. Miniatury lokalnych zdjęć są dekodowane od razu do mniejszego rozmiaru, a pokaz slajdów używa lekkich wersji zamiast plików 8K — dzięki temu otwieranie folderu i galerii jest szybkie.
- **🎨 Przełącznik skórek** w prawym górnym rogu — jeden klik zmienia wygląd na kolejny motyw.
- **Panel szczegółów** po prawej: pełne metadane (autor, data, źródło, ocena, pobrania, tagi, opis z „Czytaj więcej”), link do źródła i otwarcie w przeglądarce.

### 🖼️ Podgląd i pokaz slajdów
- Pojedyncze zdjęcie lub cała galeria w trybie **slideshow**. Przycisk „▶ Pokaz slajdów" znajduje się też w panelu szczegółów.
- Nawigacja: **← poprzednia, → następna, +/− powiększenie, Esc zamknięcie** (oraz przyciski na ekranie). **Kółko myszy** przybliża/oddala, **przeciąganie myszką** przesuwa powiększony obraz, a ruchoma etykieta pod kursorem pokazuje tytuł, rozdzielczość, format i rozmiar. Przycisk **⏵ Auto** włącza automatyczne przechodzenie co 4 sekundy.
- Tapety są wyświetlane w pamięci — **program nie zapisuje ich na dysku bez Twojej zgody**. Pobranie następuje dopiero po kliknięciu „Pobierz” i wybraniu pliku.

### 🗂️ Kategorie i nawigacja
- Kategorie tematyczne: gry, technologia, systemy operacyjne, muzyka, natura, krajobrazy, abstrakcje, motoryzacja, zwierzęta, architektura.
- Menu po lewej, nad którym znajduje się maskotka — **niebieska żabka Azureus z albumem zdjęć**.
- Zakładki: **Ulubione, Kategorie, Najlepsze, Ostatnio przeglądane, Ustawienia, O programie**.
- W ustawieniach możesz **samodzielnie dodawać, edytować i usuwać kategorie oraz źródła**.

### 🔒 Prywatność
- Brak ciasteczek (pusty magazyn cookies przy każdym żądaniu).
- Nagłówek **Do Not Track: 1**, losowy, zwykły User-Agent, brak referrera.
- **Historia i ulubione nie są zapisywane na dysku**, gdy włączony jest tryb prywatny (domyślnie włączony).
- Opcjonalne **proxy / Tor SOCKS5** w ustawieniach (domyślnie `127.0.0.1:9050`).
- Brak reklam, telemetrii i ukrytych usług.

### 🌍 Języki i skórki
- Języki: **polski, angielski, francuski, niemiecki, rosyjski, hiszpański, włoski**.
- Motywy: **Azureus (niebieski), Ciemny nowoczesny, Jasny, Zielony las, Fioletowy, Pomarańczowy zachód**.

---

## Szczera uwaga o wyszukiwaniu i prywatności

Chcę być z Tobą szczery — to ważne przy nauce i przy narzędziu „do poważnych zadań”:

1. **Część serwisów udostępnia oficjalne API** (Wallhaven, Reddit — bez klucza; Unsplash, Pexels, Pixabay — z darmowym kluczem). Tam wyszukiwanie jest niezawodne i zwraca dokładne metadane.
2. **Żródła takie jak Grafika Google, Obrazy Bing, WallpaperFlare, DeviantArt nie mają prostego, otwartego API.** OmniFoto czyta ich publicznie dostępne strony w sposób „best-effort”. Gdy serwis zmieni układ strony albo zablokuje automatyczne zapytania, dane źródło zwróci 0 wyników — a program przejdzie do pozostałych. **Nie omijamy blokad ani zabezpieczeń.**
3. **„Incognito” w OmniFoto oznacza, że aplikacja nie śledzi Cię i nie zostawia śladów u siebie.** Pełną anonimowość w sieci daje dopiero uruchomienie Tor / proxy i włączenie go w Ustawieniach (wymagany moduł `PySocks`). Nie obiecuję „niewidzialności” samą zmianą ustawienia.

Dodatkowo w pakiecie jest **dostawca danych demo offline** — dzięki niemu program działa i ma co pokazać nawet bez internetu i bez kluczy API.

---

## Instalacja na Fedorze 45

### Krok 1 — zależności systemowe

Otwórz terminal i wpisz:

```bash
sudo dnf update
sudo dnf install python3 python3-pip python3-pyside6 python3-pysocks rpm-build rpmdevtools
```

`python3-pyside6` to QT (interfejs graficzny), `python3-pysocks` jest potrzebny tylko do Tor/proxy.

### Krok 2 — pobranie kodu

Jeśli masz już ten folder — przejdź do kroku 3. Inaczej:

```bash
git clone https://github.com/1bypl/OmniFoto.git
cd OmniFoto
```

### Krok 3 — uruchomienie bez instalacji

```bash
chmod +x run.sh
./run.sh
```

To najszybszy sposób, żeby zobaczyć program w działaniu. Nic nie jest instalowane w systemie.

### Krok 4 — (opcjonalnie) instalacja „na stałe”

```bash
mkdir -p ~/.local/share/applications ~/.local/share/icons ~/.local/bin

# skrót uruchamiający z dowolnego miejsca
cat > ~/.local/bin/omnifoto <<EOF
#!/usr/bin/env bash
cd "$(pwd)"
exec python3 -m omnifoto "\$@"
EOF
chmod +x ~/.local/bin/omnifoto

cp packaging/omnifoto.desktop ~/.local/share/applications/
cp omnifoto/assets/app_icon.svg ~/.local/share/icons/omnifoto.svg
```

> W powyższym skrypcie `cd "$(pwd)"` zostanie zapisany jako bieżący katalog w momencie kopiowania — czyli folder projektu. Dzięki temu skrót zadziała z menu KDE.

Potem OmniFoto pojawi się w menu aplikacji KDE (po wylogowaniu i zalogowaniu lub po odświeżeniu menu). Upewnij się, że `~/.local/bin` jest w zmiennej `PATH`.

### Debian / Ubuntu

```bash
sudo apt install python3 python3-pip python3-pyside6.qtwidgets python3-pyside6.qtsvg python3-pyside6.qtnetwork
./run.sh
```

---

## Uruchomienie

| Sposób | Polecenie |
| --- | --- |
| Przez skrypt | `./run.sh` |
| Przez moduł Pythona | `python3 -m omnifoto` |
| Po zbudowaniu RPM | `omnifoto` (z menu lub terminala) |

Program zapisuje ustawienia w:
`~/.config/OmniFoto/settings.json`

---

## Zbudowanie pakietu RPM (Fedora)

Przygotowałem plik spec oraz skrypt, który robi wszystko za Ciebie:

```bash
cd packaging
chmod +x build_rpm.sh
./build_rpm.sh
```

Skrypt:
1. doinstaluje narzędzia `rpm-build`, `rpmdevtools`,
2. przygotuje drzewo `~/rpmbuild`,
3. spakuje źródła,
4. zbuduje pakiet `omnifoto-1.0.0-1.fc45.noarch.rpm`.

Gotowy pakiet znajdziesz w `~/rpmbuild/RPMS/noarch/`. Instalacja:

```bash
sudo dnf install ~/rpmbuild/RPMS/noarch/omnifoto-1.0.0-1.fc45.noarch.rpm
```

---

## Korzystanie z programu

1. **Wpisz frazę** w pole na górze i naciśnij Enter — zobaczysz licznik i pasek postępu.
2. **Zmień sortowanie / przedział czasu** w drugim wierszu — wyniki przesortują się od razu.
3. **Kliknij kafelek** lub „👁 Podejrzyj”, aby otworzyć pokaz slajdów. Panel po prawej pokaże szczegóły.
4. **⭐ Gwiazdka** dodaje do Ulubionych (menu po lewej).
5. **⬇ Pobierz** — wybierasz folder i nazwę pliku. Bez tego kliknięcia nic nie jest zapisywane.
6. **Ustawienia** — motyw, język, tryb prywatny, własne kategorie, własne źródła, klucze API, proxy/Tor.

Skróty w pokazie slajdów: `←` / `→` nawigacja, `+` / `-` powiększenie, `Esc` wyjście.

---

## Źródła i klucze API

Domyślnie włączone: **Wallhaven, Wikimedia Commons, NASA Images, Flickr, Reddit, WallpaperFlare, Grafika Google, Obrazy Bing, dane demo**. Openverse jest domyślnie wyłączony (bywa przeciążony) — możesz go włączyć w ustawieniach.

Żeby włączyć pełne możliwości banków zdjęć, dodaj darmowe klucze w **Ustawienia → Klucze API**:

| Serwis | Gdzie uzyskać klucz |
| --- | --- |
| Unsplash | https://unsplash.com/developers |
| Pexels | https://www.pexels.com/api/ |
| Pixabay | https://pixabay.com/api/docs/ |

Klucze są przechowywane lokalnie w `~/.config/OmniFoto/settings.json` i nigdzie nie są wysyłane poza oficjalne endpointy danego serwisu.

W ustawieniach możesz też **dodać własne źródło** (nazwa, URL, typ: `api` / `scrape`), **edytować** je i **usunąć**.

---

## Obsługiwane formaty i rozdzielczości

**Formaty:** JPEG/JPG, PNG, WebP (także animowany), AVIF, HEIC/HEIF, SVG.  
Rzeczywista obsługa AVIF/HEIC zależy od wtyczek Qt w systemie — pozostałe działają domyślnie.

**Rozdzielczości desktopowe:** 1920×1080, 2560×1440, 3840×2160 (4K), 5120×2880 (5K), 7680×4320 (8K), 1920×1200, 2560×1600, 3440×1440 (21:9), 5120×1440 (32:9).

**Rozdzielczości mobilne:** 1080×2400, 1080×2340, 1440×3200, 1179×2556 (iPhone), 1290×2796, 2048×2732 (iPad).

---

## Struktura projektu

```
OmniFoto/
├── omnifoto/
│   ├── app.py              # start aplikacji
│   ├── constants.py        # źródła, formaty, motywy, ustawienia domyślne
│   ├── models.py           # model Wallpaper, wyliczenia
│   ├── i18n.py             # 7 języków
│   ├── settings.py         # ustawienia JSON (XDG)
│   ├── privacy.py          # anonimowy klient HTTP
│   ├── utils.py            # sortowanie, filtrowanie, parsowanie
│   ├── search/             # dostawcy + SearchManager
│   ├── ui/                 # okna, widoki, motywy, animacje
│   └── assets/             # maskotka SVG i ikona
├── packaging/              # .desktop, spec RPM, skrypt buildu
├── tests/                  # testy automatyczne
├── run.sh
├── LICENSE                 # GPL-3.0
├── info.txt
└── README.md
```

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
| --- | --- |
| `Brak biblioteki PySide6` | `sudo dnf install python3-pyside6` |
| program nie widać w menu KDE | `update-desktop-database ~/.local/share/applications` i wyloguj się |
| `libgssapi_krb5.so.2: cannot open` | `sudo dnf install krb5-libs` |
| Brak wyników z internetu | sprawdź połączenie, włącz więcej źródeł lub dodaj klucze API; demo zawsze działa |
| Chcę wyczyścić ustawienia | usuń `~/.config/OmniFoto/settings.json` |
| Tor nie działa | zainstaluj `python3-pysocks` i upewnij się, że Tor nasłuchuje na 9050 |

---

## Licencja

OmniFoto jest wolnym oprogramowaniem: możesz je rozpowszechniać i modyfikować na warunkach **GNU General Public License w wersji 3 lub (opcjonalnie) późniejszej**.

Copyright (C) 2026 1bypl

Pełny tekst licencji znajduje się w pliku [`LICENSE`](LICENSE).  
Program jest dostarczany **bez jakiejkolwiek gwarancji** — używasz go na własną odpowiedzialność.

🐸 **OmniFoto — Twoje tapety, Twoje zasady.**
