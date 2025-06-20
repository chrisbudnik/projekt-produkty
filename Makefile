hello:
	echo "Hello World"

test:
	pytest

build:
	docker build --no-cache --platform=linux/amd64 -t weather-stocks-app .

compose:
	docker compose up --build


run-docker:
	docker run -p 8051:8051 weather-stocks-app 

run:	
	set UV_LINK_MODE=copy && uv run streamlit run src/app.py


clean:
	rm -rf src/__pycache__/
	rm -rf src/ui/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf src/.pytest_cache/
	rm -rf src/projekt_produkty.egg-info/
	rm -rf temp/
	rm -rf config/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/


