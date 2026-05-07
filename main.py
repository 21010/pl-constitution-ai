import uvicorn
import os

if __name__ == "__main__":
    os.makedirs("./data/chroma", exist_ok=True)

    print("Uruchamianie serwera RAG Konstytucja...")
    print("Dokumentacja API dostępna pod adresem: http://localhost:8000/docs")
    print("Interfejs WWW dostępny pod adresem: http://localhost:8000")

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["src", "web"])
