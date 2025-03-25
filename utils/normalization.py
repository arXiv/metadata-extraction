def normalize_text(s: str) -> str:
    return s.upper().replace("-", " ").replace("–", " ").replace(",", "").strip()
