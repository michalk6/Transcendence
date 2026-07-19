# Wstęp
Ten folder zawiera aplikację kliencką (Interfejs UI + Silnik Gry). 
Projekt opiera się na architekturze separacji: framework UI odpowiada wyłącznie za "otoczkę" (menu, logowanie, rankingi), podczas gdy logika samej rozgrywki żyje we własnym, niezależnym środowisku.

---

## Struktura katalogów

### 1. Poziom główny (`/frontend`)
Miejsce wyłącznie na pliki instalacyjne i konfiguracyjne. **Nie umieszczamy tu kodu źródłowego.**
* `package.json` – Lista zależności (bibliotek) oraz skrypty startowe.
* `vite.config.js` – Konfiguracja środowiska deweloperskiego i budowania aplikacji.
* `index.html` – Główny punkt wejścia, do którego wstrzykiwany jest nasz kod.

### 2. Katalog `/src` (Kod źródłowy)
Cały kod aplikacji znajduje się tutaj i dzieli się na pięć kluczowych obszarów:

#### `/assets`
Zasoby statyczne ładowane przez przeglądarkę lub silnik gry.
* **Zawartość:** Grafiki, sprite'y postaci, tilesety (tła), pliki audio (mp3/ogg), ikony i niestandardowe czcionki.

#### `/components`
Małe, wielokrotnego użytku klocki budujące interfejs użytkownika.
* **Zawartość:** Przyciski, pola formularzy, modale, powiadomienia, paski zdrowia wyświetlane nad canvasem.
* **Zasada:** Komponenty powinny być "głupie" – przyjmują dane i je wyświetlają. Nie zawierają ciężkiej logiki biznesowej ani logiki gry.

#### `/game`
**Serce rozgrywki. Ten folder to czarna skrzynka.** 
Kod znajdujący się tutaj nie "wie" o istnieniu Reacta czy Vue. Komunikuje się z UI tylko za pomocą zdarzeń (Events) lub globalnego stanu.
* `/scenes` – Ekrany wewnątrz silnika (np. `BootScene`, `MainMenu`, `LevelOne`).
* `/entities` – Klasy reprezentujące obiekty na mapie (np. `Player`, `Enemy`, `Bullet`).
* `gameConfig.js` – Plik startowy z konfiguracją silnika (rozmiar okna, fizyka, grawitacja).

#### `/store`
Globalny magazyn danych (stan aplikacji). 
* **Zawartość:** Informacje o zalogowanym graczu (nick, ID, tokeny), punktacja, stan połączenia WebSocket, ustawienia dźwięku.
* **Cel:** Most komunikacyjny. Kiedy w grze gracz zdobędzie punkt, aktualizuje wartość w `store`. Interfejs (UI) nasłuchuje na tę zmianę i automatycznie odświeża licznik na ekranie.

#### `/views`
Główne ekrany (strony) aplikacji, pomiędzy którymi przełącza się użytkownik.
* **Zawartość:** `LoginView`, `RegisterView`, `LobbyView`, `GameView`.
* **Zasada:** Widoki pełnią rolę kontenerów. Pobierają dane ze `/store` i składają w całość elementy z `/components`. Widok `GameView` jest specjalny – jego jedynym zadaniem jest wyrenderowanie pustego miejsca (np. `div` z odpowiednim ID), do którego wstrzykiwany jest silnik z folderu `/game`.

---

## Złote zasady naszego frontendu
1. **Brak pętli zależności:** `/game` nie importuje NICZEGO z `/components` ani `/views`.
2. **Jeden punkt styku:** Z silnikiem gry rozmawiamy wyłącznie poprzez przekazywanie danych konfiguracyjnych na starcie oraz przez globalny `/store`.
3. **Czysty kod:** Jeśli jakaś funkcja nie dotyczy renderowania widoku, przenieś ją do osobnego pliku pomocniczego (tzw. utils).












----


../frontend
npm install
npm run dev