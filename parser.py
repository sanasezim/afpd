import re
import requests
from cache import cache

OZON_DOMAINS = ("ozon.ru", "ozon.kz", "ozon.by")

def detect_ozon(url: str) -> bool:
    return any(d in url.lower() for d in OZON_DOMAINS)

def parse_ozon(url: str) -> tuple:
    if url in cache:
        return cache[url], None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        r = requests.get(url, headers=headers, timeout=15)
        html = r.text

        # === ЦЕНА ===
        price = None
        price_patterns = [
            r'"finalPrice":\s*"?(\d+)',
            r'"price":\s*"?(\d+)',
            r'"cardPrice":\s*"?(\d+)',
            r'(\d{3,7})\s*[₽₸]',
            r'(\d{1,3}(?:\s\d{3})*)\s*[₽₸]'
        ]
        for pat in price_patterns:
            m = re.search(pat, html)
            if m:
                price_str = re.sub(r'\D', '', m.group(1))
                if price_str:
                    price = int(price_str)
                    break

        # === РЕЙТИНГ ===
        rating = None
        rating_patterns = [
            r'"ratingValue":\s*"?([\d.]+)',
            r'"rating":\s*"?([\d.]+)',
            r'ratingValue["\s:]+([\d.]+)'
        ]
        for pat in rating_patterns:
            m = re.search(pat, html)
            if m:
                try:
                    rating = float(m.group(1))
                    if 1 <= rating <= 5:
                        break
                except:
                    pass

        # === КОЛИЧЕСТВО ОТЗЫВОВ (улучшено) ===
        reviews = 0
        review_patterns = [
            r'"reviewCount":\s*(\d+)',
            r'"feedbackCount":\s*(\d+)',
            r'(\d+)\s*отзыв',           # Новый паттерн
            r'(\d+)\s*отзыва',
            r'(\d+)\s*отзывов',
            r'rating[^"]*"[^"]*(\d+)\s*отзыв'
        ]
        for pat in review_patterns:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                try:
                    reviews = int(m.group(1))
                    break
                except:
                    pass

        # Название
        name = ""
        m = re.search(r'<title>([^<]+)', html)
        if m:
            name = m.group(1).split('—')[0].split('|')[0].strip()[:120]

        result = {
            "name": name,
            "price": price,
            "rating": rating,
            "reviews": reviews,
        }

        cache[url] = result
        return result, None

    except Exception as e:
        return None, f"Ошибка загрузки: {str(e)[:80]}"