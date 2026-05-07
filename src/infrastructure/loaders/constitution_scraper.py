import os
import requests
from bs4 import BeautifulSoup
import re
from src.domain.models import DocumentChunk


from src.domain.interfaces import IDocumentLoader

class ConstitutionScraper(IDocumentLoader):
    BASE_URL = "https://www.prezydent.pl"
    START_URL = "https://www.prezydent.pl/prawo/konstytucja-rp"

    def __init__(self, raw_dir: str = "data/raw", processed_dir: str = "data/processed"):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def load_documents(self) -> list[DocumentChunk]:
        """Implementacja interfejsu IDocumentLoader."""
        return self.scrape_all()

    def get_chapters_links(self) -> list[dict[str, str]]:
        """Pobiera listę linków do rozdziałów i ich tytuły."""
        print(f"Pobieranie strony głównej: {self.START_URL}")
        response = self.session.get(self.START_URL)
        response.raise_for_status()

        # Zapisz surową stronę główną
        with open(os.path.join(self.raw_dir, "main_page.html"), "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")

        chapters = []
        links = soup.select("ul.pageslist-list li h3 a")
        print(f"Znaleziono {len(links)} potencjalnych linków w ul.pageslist-list")

        if not links:
            links = soup.select("ul.aside-menu li ul li a")
            print(f"Znaleziono {len(links)} linków w menu bocznym (aside-menu)")

        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href")
            if href and "rozdzial-" in href:
                full_url = self.BASE_URL + href if href.startswith("/") else href
                if not any(c["url"] == full_url for c in chapters):
                    print(f"Dodano rozdział: {title} -> {full_url}")
                    chapters.append({"title": title, "url": full_url})
        return chapters

    def scrape_chapter(self, chapter_title: str, url: str) -> list[DocumentChunk]:
        """Pobiera artykuły z konkretnego rozdziału i zapisuje surowy HTML."""
        print(f"Scrapowanie rozdziału: {chapter_title} z {url}")
        response = self.session.get(url)
        response.raise_for_status()

        # Zapisz surowy HTML rozdziału
        safe_title = re.sub(r"[^\w\s-]", "", chapter_title).strip().replace(" ", "_")
        with open(os.path.join(self.raw_dir, f"{safe_title}.html"), "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")

        # Nowy kontener na podstawie analizy HTML
        content_div = soup.select_one("div.articles-single__description")
        if not content_div:
            content_div = soup.select_one("div.module-content")

        if not content_div:
            print(f"BŁĄD: Nie znaleziono kontenera artykułów na stronie {url}")
            return []

        chunks = []
        paragraphs = content_div.find_all("p")
        print(f"Znaleziono {len(paragraphs)} paragrafów w kontenerze")

        for p in paragraphs:
            text = p.get_text("\n", strip=True)
            if not text:
                continue

            lines = text.split("\n")
            first_line = lines[0].strip()

            article_match = re.match(r"^Art\.\s*(\d+)\.?$", first_line, re.IGNORECASE)

            if article_match:
                article_num = article_match.group(1)
                content = "\n".join(lines)
                chunks.append(self._create_chunk(article_num, chapter_title, [content]))
            else:
                if chunks:
                    chunks[-1].content += "\n" + text

        print(f"Wyodrębniono {len(chunks)} artykułów z rozdziału {chapter_title}")
        return chunks

    def _create_chunk(self, article_num: str, chapter_title: str, text_lines: list[str]) -> DocumentChunk:
        content = "\n".join(text_lines)
        return DocumentChunk(
            content=content,
            metadata={
                "article": article_num,
                "chapter": chapter_title,
                "tags": [],  # Tagi zostaną wygenerowane przez AI w IndexerService
            },
        )

    def scrape_all(self) -> list[DocumentChunk]:
        """Główna metoda pobierająca całą konstytucję."""
        all_chunks = []
        chapters = self.get_chapters_links()
        for chapter in chapters:
            chapter_chunks = self.scrape_chapter(chapter["title"], chapter["url"])
            all_chunks.extend(chapter_chunks)
        return all_chunks
