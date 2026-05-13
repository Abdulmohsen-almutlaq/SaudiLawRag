import asyncio
import aiohttp
import json
import csv
from collections import defaultdict

BASE = "https://laws-gateway.moj.gov.sa/apis/legislations/v1/statute"

HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en,ar;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://laws.moj.gov.sa",
    "Referer": "https://laws.moj.gov.sa/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}

CONCURRENCY = 5  # max parallel requests


# ── CALL 1: Fetch single page ──────────────────────────
async def fetch_page(session: aiohttp.ClientSession, page: int) -> list[dict]:
    payload = {
        "pageNumber": page,
        "pageSize": 50,
        "detailsKeyword": "",
        "LegalStatue": None,
        "classificationId": None,
        "sortingBy": 7,
        "statuteIssueDateFrom": None,
        "statuteIssueDateTo": None,
        "statuteName": "",
        "statutePublishDateFrom": None,
        "statutePublishDateTo": None,
        "statuteType": None,
        "keyword": "",
        "isSearch": False,
        "identityNumber": ""
    }
    async with session.post(f"{BASE}/section-search", json=payload) as res:
        text = await res.text()
        if "<html>" in text or not text.strip():
            print(f"  ⚠️  Blocked on page {page}")
            return []
        data = await res.json(content_type=None)
        return data["model"]["collection"], data["model"]["totalPages"]


async def get_all_laws(session: aiohttp.ClientSession) -> list[dict]:
    # First request to get total pages
    collection, total_pages = await fetch_page(session, 1)
    print(f"  Page 1/{total_pages} fetched")

    # Fetch remaining pages in parallel
    tasks = [fetch_page(session, p) for p in range(2, total_pages + 1)]
    sem = asyncio.Semaphore(CONCURRENCY)

    async def bounded(task):
        async with sem:
            return await task

    results = await asyncio.gather(*[bounded(t) for t in tasks])

    for result, _ in results:
        collection.extend(result)
        print(f"  Page fetched → {len(collection)} total")

    # Deduplicate by serial
    seen = set()
    unique = []
    for item in collection:
        if item["serial"] not in seen:
            seen.add(item["serial"])
            unique.append({
                "serial":      item["serial"],
                "statuteId":   item["statuteId"],
                "title":       item["statuteName"].strip(),
                "type":        item["legalType"].strip(),
                "status":      item["legalStatueName"],
                "issueDate":   item.get("issueDate", ""),
                "publishDate": item.get("publishDate", ""),
                "summary":     item.get("summary", ""),
            })
    return unique


# ── CALL 2: Fetch single detail ────────────────────────
async def fetch_detail(session: aiohttp.ClientSession, sem: asyncio.Semaphore, law: dict) -> dict:
    async with sem:
        async with session.get(
            f"{BASE}/get-Statute-gateway-Detail",
            params={"serial": law["serial"]}
        ) as res:
            text = await res.text()
            if "<html>" in text or not text.strip():
                return law  # return as-is if blocked
            data = await res.json(content_type=None)
            detail = data.get("model", {})
            if detail:
                law["articlesCount"] = detail.get("articlesCount", "")
                law["chaptersCount"] = detail.get("chaptersCount", "")
                law["articles"]      = detail.get("articles", [])
            return law


async def get_all_details(session: aiohttp.ClientSession, laws: list[dict]) -> list[dict]:
    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [fetch_detail(session, sem, law) for law in laws]
    results = await asyncio.gather(*tasks)
    print(f"  Details fetched: {sum(1 for r in results if 'articlesCount' in r)}/{len(results)}")
    return results


# ── Main ───────────────────────────────────────────────
async def main():
    async with aiohttp.ClientSession(headers=HEADERS) as session:

        print("CALL 1 — Fetching all laws in parallel...")
        all_laws = await get_all_laws(session)
        print(f"✅ Total unique laws: {len(all_laws)}\n")

        print("CALL 2 — Fetching details in parallel...")
        all_laws = await get_all_details(session, all_laws)

    # ── Save JSON ──────────────────────────────────────
    with open("laws.json", "w", encoding="utf-8") as f:
        json.dump(all_laws, f, ensure_ascii=False, indent=2)
    print("\n✅ Saved to laws.json")


    # ── Summary ────────────────────────────────────────
    by_type = defaultdict(int)
    for l in all_laws:
        by_type[l["type"]] += 1

    print(f"\n{'─'*40}")
    print(f"Total          : {len(all_laws)}")
    print(f"Active  (ساري) : {sum(1 for l in all_laws if 'ساري' in l['status'])}")
    print(f"Cancelled(ملغي): {sum(1 for l in all_laws if 'ملغي' in l['status'])}")
    print(f"By type        : {dict(by_type)}")


if __name__ == "__main__":
    asyncio.run(main())