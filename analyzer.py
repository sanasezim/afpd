from models import AnalysisResult, Product

def analyze_product(product: Product) -> AnalysisResult:
    flags = []
    good = []
    score = 0

    # Price Analysis
    if product.price:
        if product.price < 5000:
            score += 35
            flags.append(f"💸 Very low price: {product.price:,} ₸")
        elif product.price < 15000:
            score += 15
            flags.append(f"💸 Price below average: {product.price:,} ₸")
        else:
            good.append(f"💰 Good price: {product.price:,} ₸")

    # Rating & Reviews
    if product.rating:
        if product.rating < 3.8:
            score += 30
            flags.append(f"⭐ Low rating: {product.rating}")
        elif product.rating >= 4.5:
            good.append(f"⭐ Excellent rating: {product.rating}")
    else:
        score += 25
        flags.append("⭐ No rating found")

    if product.reviews == 0:
        score += 40
        flags.append("📝 No reviews — High risk of fake")
    elif product.reviews < 15:
        score += 20
        flags.append(f"📝 Few reviews: {product.reviews}")
    else:
        good.append(f"📝 Good number of reviews: {product.reviews}")

    score = min(score, 100)

    if score < 30:
        emoji, verdict, level = "🟢", "Low Risk - Likely Original", "LOW"
    elif score < 60:
        emoji, verdict, level = "🟡", "Medium Risk - Be Careful", "MEDIUM"
    else:
        emoji, verdict, level = "🔴", "HIGH RISK OF FAKE!", "HIGH"

    return AnalysisResult(product, score, verdict, emoji, level, flags, good)