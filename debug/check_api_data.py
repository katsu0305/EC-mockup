#!/usr/bin/env python3
import json

data = json.load(open("work/data/products.json", encoding="utf-8"))
item = data["items"][0]

print(f"Keys: {list(item.keys())}")
print(f"\nFull item:")
print(json.dumps(item, indent=2, ensure_ascii=False))
