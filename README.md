# Pogoda + Giełda AI
Projekt zaliczeniowy z przedmiotu: `Tworzenie produktów opartych o dane` <br>
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
- `uvx streamlit run src/app.py`

lub:
- `make run`

Wersja oparta o Docker:
- `make build` + `make run-docker` lub,
- `make compose`

## Funkcje AI
Aplikacja pozwala na wykorzystanie modeli językowych (LLM) do analizy danych i tworzenia uproszczonych rekomendacji.
W karcie `Ustawienia` (nawigacja za pomocą paska bocznego), należy przekopiować w odpowiednie pole klucz API, a
następnie zakceptować.

## Lokalizacja
W celu wybrania lokalizacji, należy wybrać na mapie odpowiedni punkt - wybór trzeba potwierdzić przyciskiem 
umiejscowionym poniżej mapki (przy pierwszej selekcji może pojawić się niestandardowo nisko).