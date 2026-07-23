import json
with open('work/data/products.json', encoding='utf-8') as f:
    d = json.load(f)
items = d['items']
zero_price = [p for p in items if not p.get('sell_price')]
print(f'合計: {len(items)} 件, 0円: {len(zero_price)} 件')
for p in items[:5]:
    print(p['product_name'][:30], '| sell_price:', p.get('sell_price'))
