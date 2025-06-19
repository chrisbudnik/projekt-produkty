# Pogoda + Giełda AI
Projekt zaliczeniowy z przedmiotu: `Tworzenie produktów opartych o dane` (2025)<br>
*Uniwersytet im. Adama Mickiewicza W Poznaniu*

Autorzy:
- Krzysztof Budnik
- Bartosz Michnik


## Uruchomienie aplikacji
Do instalacji pakietów wykorzystano *uv package manager*.
Warto upewnić się, że został zainstalowany w systemie.
- `pip install uv`

Uruchomienie aplikacji lokalnie:
- `uv sync`
- `streamlit run src/app.py`

lub:
- `make run`

Wersja oparta o Docker:
- `make build` + `make run-docker` lub,
- `make compose`

Aplikacja będzie dostępna pod adresem:
- `http://localhost:8501` (lokalne uruchomienie)
- `http://0.0.0.0:8051` (docker)

## Funkcje AI
Aplikacja pozwala na wykorzystanie modeli językowych (LLM) do analizy danych i tworzenia uproszczonych rekomendacji.
W karcie `Ustawienia` (nawigacja za pomocą paska bocznego), należy przekopiować w odpowiednie pole klucz API, a
następnie zaakceptować.

## Lokalizacja
W celu wybrania lokalizacji, należy zaznaczyć na mapie odpowiedni punkt - wybór trzeba potwierdzić przyciskiem 
umiejscowionym poniżej mapki (przy pierwszej selekcji może pojawić się niestandardowo nisko).