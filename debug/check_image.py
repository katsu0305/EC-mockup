#!/usr/bin/env python3
import json
from pathlib import Path

# Check products.json
data = json.load(open("work/data/products.json", encoding="utf-8"))
item = data["items"][0]
print(f"System Code: {item.get('system_code')}")
print(f"Product Name: {item.get('product_name')}")
print(f"Keys in item: {list(item.keys())}")

# Check if image exists
from src.config.loader import load_config
cfg = load_config()
system_code = item.get("system_code")
rel = f"item/{system_code}_01.jpg"
local = cfg.app_work_dir / "images" / rel
print(f"\nImage resolution:")
print(f"  Local path: {local}")
print(f"  Exists: {local.exists()}")
print(f"  MAKESHOP_PUBLIC_BASE_URL: {cfg.makeshop_public_base_url}")

# Simulate _resolve_image_url
if local.exists():
    result = f"../../work/images/{rel}"
elif cfg.makeshop_public_base_url:
    result = f"{cfg.makeshop_public_base_url.rstrip('/')}/{rel}"
else:
    result = "assets/images/no-image.png"

print(f"  Resolved URL: {result}")
