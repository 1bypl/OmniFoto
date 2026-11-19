# Wysłanie OmniFoto na GitHub

Gotowy folder źródłowy znajduje się w **`github_release/`**. Zawiera kompletny kod, dokumentację, instalatory, testy i zrzuty ekranu — bez plików cache.

## Sposób 1 — z poziomu terminala

```bash
cd /home/daka/Pulpit/OmniFoto/github_release

git init
git add .
git commit -m "OmniFoto 1.0.0 — pierwsze wydanie"

git remote add origin https://github.com/1bypl/OmniFoto.git
git branch -M main
git push -u origin main
```

Jeśli repozytorium już istnieje i ma zawartość:

```bash
git remote add origin https://github.com/1bypl/OmniFoto.git
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## Sposób 2 — przez GitHub Desktop / stronę WWW

1. Utwórz nowe repozytorium `OmniFoto` na koncie **1bypl** (licencja GPL-3.0, opis: „Lokalna przeglądarka tapet").
2. Przeciągnij zawartość folderu `github_release/` do okna „Upload files".
3. Kliknij **Commit changes**.

## Przed wysłaniem — lista kontrolna

- ✅ `README.md` z zrzutami ekranu (ścieżki `docs/screenshots/...`)
- ✅ `LICENSE` — pełny tekst GPL-3.0
- ✅ `info.txt`, `CHANGELOG.md`, `CONTRIBUTING.md`
- ✅ katalog `omnifoto/` z kodem i maskotką SVG
- ✅ `packaging/` — instalatory Fedora i Debian
- ✅ `tests/` — 20 testów automatycznych
- ✅ brak `__pycache__`, plików `.pyc` i lokalnych ustawień

## Po wysłaniu

Możesz dodać tag wydania:

```bash
git tag -a v1.0.0 -m "OmniFoto 1.0.0"
git push origin v1.0.0
```

---

Copyright (C) 2026 1bypl — https://github.com/1bypl
