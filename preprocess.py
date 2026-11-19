import re

# Basic filler words
STOP_WORDS = {
    "my", "is", "me", "asap", "i", "am", "are", "the",
    "a", "an", "to", "of", "in", "on", "it", "this", "that", "and"
}

# Email noise: greetings, sign-offs, dates, forwarding words
NOISE_WORDS = {
    "hi", "hello", "dear", "regards", "kind", "best", "thanks", "thank",
    "sincerely", "greetings", "good", "morning", "afternoon", "evening",
    "sent", "re", "fw", "fwd", "cc", "subject", "pm", "importance",
    "high", "br", "com", "wrote",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "you", "we", "our", "your", "us", "by", "at", "as", "or", "if",
    "will", "would", "can", "could", "also", "be", "been", "was", "were",
    "has", "have", "had", "for", "with", "from", "please", "hesitate",
}

# Legal / confidentiality footers: everything AFTER these phrases is cut off
FOOTER_MARKERS = [
    "information confidential", "confidential legally privileged",
    "intended solely", "views expressed", "please consider environment",
    "opinions expressed", "notice intended", "this email",
]

MAX_WORDS = 40


def preprocess_text(text, remove_noise=True):
    text = str(text).lower()

    # 1. Cut off the legal footer
    if remove_noise:
        for marker in FOOTER_MARKERS:
            pos = text.find(marker)
            if pos > 20:
                text = text[:pos]

    # 2. Remove punctuation, numbers, symbols
    text = re.sub(r"[^a-z\s]", " ", text)

    # 3. Remove stop words (and email noise words)
    bad = STOP_WORDS | NOISE_WORDS if remove_noise else STOP_WORDS
    words = [w for w in text.split() if w not in bad and len(w) > 1]

    # 4. Remove immediate repeats ("accounts accounts" -> "accounts")
    deduped = []
    for w in words:
        if not deduped or deduped[-1] != w:
            deduped.append(w)

    # 5. Keep the first MAX_WORDS words (the issue is usually at the start)
    if remove_noise:
        deduped = deduped[:MAX_WORDS]

    return " ".join(deduped)


if __name__ == "__main__":
    s = "URGENT!!! My VPN is NOT connecting!!! Please help me ASAP!!!"
    print(preprocess_text(s, remove_noise=False))  
    print(preprocess_text(s))                      