# Konstytucja RP - Inteligentny System RAG 🇵🇱

System typu **RAG (Retrieval-Augmented Generation)** umożliwiający zadawanie pytań w języku naturalnym do tekstu Konstytucji Rzeczypospolitej Polskiej. Aplikacja wyszukuje odpowiednie artykuły, analizuje ich treść i generuje precyzyjną odpowiedź wraz z podaniem źródeł prawnych.

## Cel Projektu
Głównym celem aplikacji jest ułatwienie obywatelom dostępu do informacji zawartych w Konstytucji RP poprzez interaktywny czat. System gwarantuje odpowiedzi oparte wyłącznie na autentycznym tekście ustawy zasadniczej, eliminując ryzyko halucynacji modelu LLM.

## Architektura i Etapy Pracy

System składa się z dwóch głównych potoków (pipelines) zaprojektowanych zgodnie z zasadami **SOLID** i **CUPID**:

### 1. Pipeline Indeksowania (Indexing)
* **Scraping:** Automatyczne pobieranie aktualnego tekstu Konstytucji ze strony prezydent.pl.
* **Tagowanie AI:** Każdy artykuł jest analizowany przez model Gemini w celu wygenerowania słów kluczowych (tagów), co poprawia późniejszą precyzję wyszukiwania.
* **Embeddingi:** Tekst jest zamieniany na wektory matematyczne przy użyciu modelu `text-embedding-004`.
* **Vector Store:** Wektory wraz z metadanymi trafiają do bazy **ChromaDB**.

### 2. Pipeline Zapytań (Querying)
* **Query Refinement:** Pytanie użytkownika jest przekształcane przez LLM na profesjonalne zapytanie prawnicze (rozszerzanie zapytania).
* **Retrieval:** Wyszukiwanie top-k najbardziej relewantnych fragmentów Konstytucji w bazie wektorowej.
* **Augmentation & Generation:** Konstrukcja promptu zawierającego znaleziony kontekst i generowanie finalnej odpowiedzi przez model Gemini.

## Technologie
* **Język:** Python 3.13+
* **LLM & Embeddings:** Google Gemini API
* **Baza Wektorowa:** ChromaDB
* **API Framework:** FastAPI
* **Frontend:** Vanilla JS / HTML / CSS
* **Inne:** Pydantic (walidacja), BeautifulSoup4 (scraping), tqdm (monitoring postępu)

## Instalacja i Uruchomienie

### Wymagania
* Klucz API Google Gemini (dostępny bezpłatnie w [Google AI Studio](https://aistudio.google.com/))

### Kroki instalacji
1. Sklonuj repozytorium:
    ```bash
    git clone <url-repozytorium>
    cd project
    ```

2.  Stwórz środowisko wirtualne i zainstaluj zależności:
    ```bash
    uv sync
    ```

3.  Skonfiguruj zmienne środowiskowe:
    Stwórz plik `.env` w głównym katalogu i dodaj swój klucz API:
    ```env
    GEMINI_API_KEY=twój_klucz_api
    ```

### Uruchomienie
1.  **Indeksowanie danych:** (Wymagane tylko przy pierwszym uruchomieniu)
    Możesz uruchomić proces poprzez API lub skrypt (jeśli dostępny). System pobierze Konstytucję i przygotuje bazę wektorową.

2.  **Start Serwera:**
    ```bash
    uv run .\main.py
    ```
    
    Aplikacja będzie dostępna pod adresem: [http://localhost:8000](http://localhost:8000)

## Testy
Aby uruchomić testy jednostkowe weryfikujące poprawność logiki biznesowej:
```bash
python -m unittest discover tests
```
