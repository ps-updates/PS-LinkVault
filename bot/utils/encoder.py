# Cleaned & Refactored by @Mak0912 (TG)

import base64

def encode(data: str) -> str:
    base64_bytes = base64.urlsafe_b64encode(data.encode("utf-8"))
    return base64_bytes.decode("utf-8").rstrip("=")

def decode(encoded: str) -> str:
    padded = encoded + "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(padded).decode("utf-8")
