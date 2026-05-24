import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


BASE_URL = "https://www.aidedd.org"
SPANISH_LIST_URL = f"{BASE_URL}/magic-item/es/"
ENGLISH_LIST_URL = f"{BASE_URL}/magic-item/"
REQUEST_DELAY = 1.5  # seconds between requests to avoid rate limiting
TRANSLATE_DELAY = 1.0  # seconds between translations


class Enricher:
    def __init__(self, items_path: Path):
        self.items_path = Path(items_path)
        self.client = httpx.Client(timeout=30, headers={"User-Agent": "ObjetosMagicosMCP/1.0"})
        self.es_to_en: dict[str, str] = {}
        self.en_to_slug: dict[str, str] = {}
        self.translator = GoogleTranslator(target="es")

    def build_mapping(self) -> dict[str, str]:
        """Fetch both listing pages and build spanish_name -> english_slug mapping."""
        print("Fetching Spanish listing page...")
        es_html = self.client.get(SPANISH_LIST_URL).text
        print("Fetching English listing page...")
        en_html = self.client.get(ENGLISH_LIST_URL).text

        es_soup = BeautifulSoup(es_html, "html.parser")
        en_soup = BeautifulSoup(en_html, "html.parser")

        for tr in es_soup.select("table#liste tbody tr"):
            name_td = tr.select_one("td.item a")
            en_td = tr.select_one("td.colV")
            if name_td and en_td:
                self.es_to_en[name_td.get_text(strip=True)] = en_td.get_text(strip=True)

        for tr in en_soup.select("table#liste tbody tr"):
            link = tr.select_one("td.item a")
            if link:
                name = link.get_text(strip=True)
                href = link.get("href", "")
                slug = href.rstrip("/").split("/")[-1]
                self.en_to_slug[name] = slug

        direct = {}
        missing = 0
        for spanish_es, english in self.es_to_en.items():
            slug = self.en_to_slug.get(english)
            if slug:
                direct[spanish_es] = slug
            else:
                missing += 1
        print(f"Built mapping: {len(direct)} Spanish->slug entries, {missing} missing")
        return direct

    def enrich(self, dry_run: bool = False) -> list[dict[str, Any]]:
        items = json.loads(self.items_path.read_text(encoding="utf-8"))
        mapping = self.build_mapping()

        to_enrich = [i for i in items if not i.get("es_ogl", True)]
        print(f"\nItems to enrich: {len(to_enrich)}")

        if dry_run:
            self._dry_run(to_enrich, mapping)
            return items

        enriched = 0
        for idx, item in enumerate(to_enrich):
            spanish_name = item["nombre"]
            slug = mapping.get(spanish_name)

            if not slug:
                print(f"[{idx + 1}/{len(to_enrich)}] SKIP '{spanish_name}' - no slug found")
                continue

            print(f"[{idx + 1}/{len(to_enrich)}] {spanish_name} -> {slug}")

            en_desc = self._fetch_description(slug)
            if not en_desc:
                print(f"  WARNING: empty description")
                continue

            es_desc = self._translate(en_desc)
            if not es_desc:
                print(f"  WARNING: translation failed")
                continue

            item["descripcion"] = es_desc
            item["traducido"] = True
            item["nombre_en"] = self.es_to_en.get(spanish_name, "")
            enriched += 1

        print(f"\nEnriched {enriched}/{len(to_enrich)} items")
        self.items_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return items

    def _fetch_description(self, slug: str) -> str | None:
        url = f"{BASE_URL}/magic-item/{slug}"
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"  ERROR fetching {url}: {e}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        desc_div = soup.find("div", class_="description")
        if not desc_div:
            return None

        text = desc_div.get_text("\n", strip=True)
        return text

    def _translate(self, text: str) -> str | None:
        if len(text) > 4500:
            parts = self._split_text(text, 4500)
            translated_parts = []
            for part in parts:
                result = self._translate_chunk(part)
                if result:
                    translated_parts.append(result)
                time.sleep(TRANSLATE_DELAY)
            return "\n".join(translated_parts)
        return self._translate_chunk(text)

    def _translate_chunk(self, text: str) -> str | None:
        try:
            result = self.translator.translate(text)
            time.sleep(TRANSLATE_DELAY)
            return result
        except Exception as e:
            print(f"  TRANSLATION ERROR: {e}")
            return None

    def _split_text(self, text: str, max_len: int) -> list[str]:
        paragraphs = text.split("\n")
        chunks = []
        current = ""
        for p in paragraphs:
            if len(current) + len(p) + 1 > max_len and current:
                chunks.append(current)
                current = p
            else:
                current = p if not current else current + "\n" + p
        if current:
            chunks.append(current)
        return chunks

    def _dry_run(self, to_enrich: list[dict], mapping: dict[str, str]):
        found = 0
        for item in to_enrich:
            slug = mapping.get(item["nombre"])
            en_name = self.es_to_en.get(item["nombre"], "?")
            if slug:
                print(f"  {item['nombre']} -> [{en_name}] -> {slug}")
                found += 1
            else:
                print(f"  {item['nombre']} -> [{en_name}] -> NO SLUG")
        print(f"\n  {found}/{len(to_enrich)} resolved")
