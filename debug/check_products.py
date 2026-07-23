import json

with open('work/data/products.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'商品数: {len(data["items"])}')
item = data["items"][0]
print(f'\n最初の商品キー: {list(item.keys())}')
print(f'\ncategories フィールド: {item.get("categories", "NOT FOUND")}')

# categories が存在する商品の例を表示
for i, item in enumerate(data["items"]):
    if item.get("categories"):
        print(f'\n商品 {i}: {item["product_name"][:30]}')
        print(f'  categories: {item["categories"]}')
        break
