# Pogoda + Giełda AI

Projekt zaliczeniowy z przedmiotu: `Tworzenie produktów opartych o dane` <br>
Uniwersytet im. Adama Mickiewicza W Poznaniu

Autorzy:
- Krzysztof Budnik
- Bartosz Michnik


## Uruchomienie aplikacji

Konfiguracja środowiska - nalezy utworzyć plik `src/.env`, który będzie zawierać:

```bash
OPENAI_API_KEY=xxx
OPENAI_ORG_ID=org-xxx
OPENAI_PROJECT_ID=xxx
```

środowisko lokalne:

- `pip install uv`
- `uv sync`
- `uv tool --with plotly,mplfinance streamlit`
- `uvx streamlit run src/app.py`

