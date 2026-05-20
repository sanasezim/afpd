from models import AnalysisResult, Product

SUSPICIOUS_KEYWORDS = {
    "реплика", "копия", "1:1", "аналог", "подделка", "реплики",
    "люкс реплика", "premium copy", "mirror", "зеркало", "fake"
}

def analyze_product(product: Product) -> AnalysisResult:
    score = 0
    flags = []
    good = []

    if product.price is not None:
        if product.price < 3000:
            score += 30
            flags.append(f"Very low price: {product.price:,} ₸ (high risk)")
        elif product.price < 8000:
            score += 15
            flags.append(f"Below average price: {product.price:,} ₸")
        else:
            good.append(f"Reasonable price: {product.price:,} ₸")
    else:
        score += 20
        flags.append("Price not found")

    if product.rating is not None:
        if product.rating < 4.0:
            score += 25
            flags.append(f"Low rating: {product.rating}")
        elif product.rating >= 4.6:
            good.append(f"High rating: {product.rating}")
        else:
            flags.append(f"Average rating: {product.rating}")
    else:
        score += 20
        flags.append("Rating not found")

    if product.reviews == 0:
        score += 35
        flags.append("No reviews - Very high risk")
    elif product.reviews < 10:
        score += 20
        flags.append(f"Very few reviews: {product.reviews}")
    elif product.reviews > 50:
        good.append(f"Good number of reviews: {product.reviews}")
    else:
        flags.append(f"Moderate reviews: {product.reviews}")

    suspicious_found = False
    if product.name:
        name_lower = product.name.lower()
        for word in SUSPICIOUS_KEYWORDS:
            if word in name_lower:
                suspicious_found = True
                flags.append(f"Suspicious keyword: {word}")
                break

    if suspicious_found:
        score += 30

    if product.rating and product.rating >= 4.5 and product.reviews < 8:
        score += 15
        flags.append("Possible fake reviews (high rating + few reviews)")

    score = min(score, 100)

    if score < 35:
        verdict = "Low Risk - Likely Original"
        level = "LOW"
        emoji = "🟢"
    elif score < 65:
        verdict = "Medium Risk - Be Careful"
        level = "MEDIUM"
        emoji = "🟡"
    else:
        verdict = "HIGH RISK OF FAKE / SCAM"
        level = "HIGH"
        emoji = "🔴"

    return AnalysisResult(
        product=product,
        risk_score=score,
        verdict=verdict,
        emoji=emoji,
        risk_level=level,
        flags=flags,
        good=good
    )
