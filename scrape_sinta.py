#!/usr/bin/env python3
"""
Ambil daftar publikasi Scopus dari profil SINTA lalu tulis ke data/publications.json.
Dipakai oleh GitHub Actions (dijadwalkan). Tidak butuh API key.

Catatan ketahanan:
- SINTA bisa mengubah struktur HTML sewaktu-waktu. Skrip ini defensif:
  jika parsing gagal atau hasil kosong, ia TIDAK menimpa data lama
  (supaya website tidak tiba-tiba kosong).
"""
import json, re, sys, os, datetime
import urllib.request

SINTA_ID = os.environ.get("SINTA_ID", "6973450")
URL = f"https://sinta.kemdiktisaintek.go.id/authors/profile/{SINTA_ID}"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "publications.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SintaDashboardBot/1.0; +https://github.com)"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def categorize(venue, quartile):
    v = (venue or "").lower()
    if quartile in ("Q1", "Q2", "Q3", "Q4") or "journal" in v or "telecommunication systems" in v or "biomedical signal" in v:
        # jurnal ber-kuartil atau nama jurnal dikenal
        if quartile in ("Q1", "Q2", "Q3", "Q4") or "systems" in v or "journal" in v or "control" in v:
            return "jurnal"
    return "proc"


def parse(html):
    """Ambil blok publikasi Scopus dari HTML profil SINTA."""
    pubs = []
    # Setiap publikasi diawali link record Scopus. Kita pecah per blok <a ...scopus...record...>
    # Pola judul:
    #   <a href="https://www.scopus.com/record/display.uri?eid=EID&...">JUDUL</a>
    # diikuti quartile ("Q1 as Journal" / "no-Q as Conference Proceedin"), nama venue (link sourceid),
    # "Author Order : X of Y", "Creator : ...", tahun, "N cited".
    title_re = re.compile(
        r'<a href="(https://www\.scopus\.com/record/display\.uri\?eid=([^"&]+)[^"]*)"[^>]*>(.*?)</a>',
        re.S,
    )
    # Ambil semua kandidat judul + posisinya
    matches = list(title_re.finditer(html))
    for i, m in enumerate(matches):
        url = m.group(1)
        eid = m.group(2)
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(3))).strip()
        if not title:
            continue
        # potong konteks sampai judul berikutnya untuk cari metadata
        seg = html[m.end(): matches[i + 1].start() if i + 1 < len(matches) else m.end() + 1200]
        seg_text = re.sub(r"<[^>]+>", " ", seg)
        seg_text = re.sub(r"\s+", " ", seg_text)

        # quartile
        q = "Conf"
        qm = re.search(r"\b(Q[1-4])\b", seg_text)
        if qm:
            q = qm.group(1)

        # venue: link sourceid
        vm = re.search(r'sourceid/\d+"[^>]*>(.*?)</a>', seg, re.S)
        venue = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", vm.group(1))).strip() if vm else ""

        # author order
        om = re.search(r"Author Order\s*:\s*([0-9]+ of [0-9]+)", seg_text)
        order = om.group(1) if om else ""

        # year
        ym = re.search(r"\b(20[0-9]{2})\b", seg_text)
        year = ym.group(1) if ym else ""

        # cited
        cm = re.search(r"([0-9]+)\s*cited", seg_text)
        cit = int(cm.group(1)) if cm else 0

        pubs.append({
            "t": title,
            "url": url,
            "eid": eid,
            "v": venue,
            "q": q,
            "ord": order,
            "y": year,
            "cit": cit,
            "cat": categorize(venue, q),
        })

    # dedup by eid, keep first
    seen = set()
    uniq = []
    for p in pubs:
        if p["eid"] in seen:
            continue
        seen.add(p["eid"])
        uniq.append(p)
    return uniq


def parse_stats(html):
    """Ambil ringkasan angka (SINTA score, h-index, dst)."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    stats = {}

    def grab(label):
        m = re.search(r"([0-9]+)\s+" + re.escape(label), text)
        return int(m.group(1)) if m else None

    stats["score"] = grab("SINTA Score Overall")
    stats["score3"] = grab("SINTA Score 3Yr")
    # tabel ringkasan Article/Citation/H-Index dsb sulit dipetakan stabil -> best effort
    return {k: v for k, v in stats.items() if v is not None}


def main():
    try:
        html = fetch(URL)
    except Exception as e:
        print(f"[warn] gagal fetch SINTA: {e}", file=sys.stderr)
        sys.exit(0)  # jangan gagalkan workflow; biarkan data lama

    pubs = parse(html)
    if not pubs:
        print("[warn] tidak ada publikasi ter-parse; data lama dipertahankan", file=sys.stderr)
        sys.exit(0)

    stats = parse_stats(html)

    payload = {
        "url": URL,
        "sinta_id": SINTA_ID,
        "updated": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "stats": stats,
        "pubs": pubs,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"[ok] {len(pubs)} publikasi ditulis ke {OUT}")


if __name__ == "__main__":
    main()
