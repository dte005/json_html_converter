import copy
import random
from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class ExtractedSection:
    id: str
    title: str
    content_html: str
    images: list[str] = field(default_factory=list)


@dataclass
class ExtractedDocument:
    header: dict[str, str]
    header_images: list[str]
    sections: list[ExtractedSection]
    approvals: list[dict[str, str]]


class SectionExtractor:
    def __init__(self, soup: BeautifulSoup) -> None:
        self._soup = soup

    def extract(self) -> ExtractedDocument:
        header, header_images = self._extract_header()

        numbered_sections = self._extract_numbered_sections()
        used_ids = {section.id for section in numbered_sections}

        leading_sections: list[ExtractedSection] = []
        for wrapper_selector, title_selector in (
            ("div.document-description", "h2"),
            ("div.things-i-need-wrapper", "h2.things-i-need-header"),
        ):
            section = self._extract_named_section(wrapper_selector, title_selector, used_ids)
            if section is not None:
                leading_sections.append(section)

        trailing_sections: list[ExtractedSection] = []
        approvals_section = self._extract_named_section("div.document-approvals", "h2", used_ids)
        if approvals_section is not None:
            trailing_sections.append(approvals_section)

        sections = leading_sections + numbered_sections + trailing_sections
        approvals = self._extract_approvals()

        return ExtractedDocument(header, header_images, sections, approvals)

    @staticmethod
    def _generate_unique_id(used_ids: set[str]) -> str:
        while True:
            candidate = str(random.randint(1, 999_999))
            if candidate not in used_ids:
                used_ids.add(candidate)
                return candidate

    def _extract_header(self) -> tuple[dict[str, str], list[str]]:
        head = self._soup.select_one("div.document-head")
        if head is None:
            empty = {
                "doc_title": "",
                "document": "",
                "owner": "",
                "collection": "",
                "review_by": "",
                "revised": "",
                "effective": "",
            }
            return empty, []

        title_tag = head.select_one("h1")
        header = {
            "doc_title": title_tag.get_text(strip=True) if title_tag else "",
            "document": self._text_after_label(head, "span.document-number"),
            "owner": self._text_after_label(head, "span.document-owner"),
            "collection": self._text_after_label(head, "span.document-collection"),
            "review_by": self._text_after_label(head, "div.document-review", direct_text_only=True),
            "revised": self._text_after_label(head, "span.document-revised"),
            "effective": self._text_after_label(head, "span.document-effective"),
        }
        images = [img["src"] for img in head.select("img[src]")]
        return header, images

    @staticmethod
    def _text_after_label(scope: Tag, selector: str, direct_text_only: bool = False) -> str:
        tag = scope.select_one(selector)
        if tag is None:
            return ""
        if direct_text_only:
            text = "".join(child for child in tag.children if isinstance(child, str))
        else:
            text = tag.get_text()
        text = text.strip()
        if ":" in text:
            text = text.split(":", 1)[1]
        return text.strip()

    def _extract_numbered_sections(self) -> list[ExtractedSection]:
        sections = []
        for wrapper in self._soup.select("div.document-step.expandable-section-wrapper"):
            badge = wrapper.select_one("span.badge")
            title_tag = wrapper.select_one("h3.step-title")
            content_tag = wrapper.select_one("div.step-description.expandable-section-content")
            if badge is None or title_tag is None or content_tag is None:
                continue
            sections.append(
                ExtractedSection(
                    id=badge.get_text(strip=True),
                    title=title_tag.get_text(strip=True),
                    content_html=content_tag.decode_contents().strip(),
                    images=[img["src"] for img in content_tag.select("img[src]")],
                )
            )
        return sections

    def _extract_named_section(
        self, wrapper_selector: str, title_selector: str, used_ids: set[str]
    ) -> ExtractedSection | None:
        wrapper = self._soup.select_one(wrapper_selector)
        if wrapper is None:
            return None

        images = [img["src"] for img in wrapper.select("img[src]")]

        wrapper_copy = copy.copy(wrapper)
        title_tag = wrapper_copy.select_one(title_selector)
        title = title_tag.get_text(strip=True) if title_tag else ""
        if title_tag is not None:
            title_tag.extract()

        return ExtractedSection(
            id=self._generate_unique_id(used_ids),
            title=title,
            content_html=wrapper_copy.decode_contents().strip(),
            images=images,
        )

    def _extract_approvals(self) -> list[dict[str, str]]:
        wrapper = self._soup.select_one("div.document-approvals")
        if wrapper is None:
            return []

        approvals = []
        for row in wrapper.select("table tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            approvals.append(
                {
                    "date": cells[0].get_text(strip=True),
                    "by": cells[1].get_text(strip=True),
                }
            )
        return approvals
