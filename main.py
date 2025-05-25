import re
from transformers import pipeline

# 1. Load Pipelines
# Grammar/spelling corrector
corrector = pipeline(
              'text2text-generation',
              'pszemraj/flan-t5-large-grammar-synthesis',
            )

# Sentiment analyzer
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment"
)

# 2. Clean Text
def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+|@\S+|#\S+", "", text)  # Remove URLs, handles, hashtags
    text = re.sub(r"[^\w\s,.!?]", "", text)        # Remove emojis/special chars
    text = re.sub(r"\s+", " ", text).strip()       # Normalize whitespace
    return text

# 3. Full Pipeline: Correct → Clean → Analyze
def analyze_text(raw_input):
    # Grammar + spelling correction
    corrected = corrector(raw_input)[0]["generated_text"]

    # Clean it
    cleaned = clean_text(corrected)

    # Sentiment prediction
    LABELS = {
        "LABEL_0": "NEGATIVE",
        "LABEL_1": "NEUTRAL",
        "LABEL_2": "POSITIVE"
    }

    raw_sentiment = sentiment_pipeline(cleaned)[0]
    label = LABELS.get(raw_sentiment["label"], raw_sentiment["label"])

    return {
        "original": raw_input,
        "corrected": corrected,
        "cleaned": cleaned,
        "sentiment": label,
        "confidence": round(raw_sentiment["score"], 3)
    }

# 🔍 Test Example
text = "i wnt to bok a flite to delhi nxt monday 😠"
result = analyze_text(text)

# 📤 Output
print("Original  :", result["original"])
print("Corrected :", result["corrected"])
print("Cleaned   :", result["cleaned"])
print("Sentiment :", result["sentiment"])
print("Confidence:", result["confidence"])



# from transformers import pipeline

# corrector = pipeline(
#               'text2text-generation',
#               'pszemraj/flan-t5-large-grammar-synthesis',
#               )
# raw_text = 'i wnt to bok a flite to delhi nxt monday'
# results = corrector(raw_text)
# print(results)
