import re
from src.domain.models import DocumentChunk


class ConstitutionLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _parse_text(self, text: str) -> list[DocumentChunk]:
        chunks = []
        current_chapter = "Brak"

        lines = text.split("\n")

        current_article_num = None
        current_article_content = []

        for line in lines:
            # Wykrywanie rozdziału
            chapter_match = re.search(r"Rozdział\s+([IVXLCDM]+)", line)
            if chapter_match:
                current_chapter = line.strip()
                continue

            # Wykrywanie artykułu
            article_match = re.search(r"Art\.\s+(\d+)\.", line)
            if article_match:
                # Dodaj poprzedni artykuł do listy, jeśli istnieje
                if current_article_num:
                    chunks.append(
                        DocumentChunk(
                            content="\n".join(current_article_content).strip(),
                            metadata={
                                "article": current_article_num,
                                "chapter": current_chapter,
                                "tags": [current_chapter.lower()],
                            },
                        )
                    )

                current_article_num = article_match.group(1)
                current_article_content = [line]
            else:
                if current_article_num:
                    current_article_content.append(line)

        # Dodaj ostatni artykuł
        if current_article_num:
            chunks.append(
                DocumentChunk(
                    content="\n".join(current_article_content).strip(),
                    metadata={
                        "article": current_article_num,
                        "chapter": current_chapter,
                        "tags": [current_chapter.lower()],
                    },
                )
            )

        return chunks
