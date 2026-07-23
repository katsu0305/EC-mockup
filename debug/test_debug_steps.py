#!/usr/bin/env python3
import re

def _strip_conditional_blocks_debug(tmpl: str) -> str:
    """
    ステップバイステップでデバッグ
    """
    result = tmpl
    
    false_conditions = {
        "member.is_logged_in", "cart.has_item", "shop.is_member_entry_enabled",
        "item.review.has_item", "category.image_url",
        "item.multi_image.has_item", "item.is_option_image", "item.add_image.has_item", "item.icon.has_item",
    }
    
    print("=== Step 1: Process false conditions ===")
    for cond in false_conditions:
        result = re.sub(
            r"<\{\s*if\s+\$" + re.escape(cond) + r"[^}]*\}>.*?<\{/if\}>",
            "",
            result,
            flags=re.DOTALL,
        )
        result = re.sub(
            r"<\{\s*if\s+!\$" + re.escape(cond) + r"[^}]*\}>(.*?)<\{/if\}>",
            r"\1",
            result,
            flags=re.DOTALL,
        )
    print(f"After false_conditions: item.image_L present? {('item.image_L' in result)}")
    
    print("\n=== Step 2: Process else blocks ===")
    result = re.sub(
        r"<\{\s*if\s+[^}]+\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>",
        r"\1",
        result,
        flags=re.DOTALL,
    )
    print(f"After else extraction: item.image_L present? {('item.image_L' in result)}")
    print(f"  Snippet: {result[result.find('item.image_L')-50 :  result.find('item.image_L')+100] if 'item.image_L' in result else 'NOT FOUND'}")
    
    print("\n=== Step 3: Remove remaining if blocks ===")
    result = re.sub(
        r"<\{\s*if\s+[^}]+\}>.*?<\{/if\}>",
        "",
        result,
        flags=re.DOTALL,
    )
    print(f"After if removal: item.image_L present? {('item.image_L' in result)}")
    
    print("\n=== Step 4: Remove section blocks ===")
    result = re.sub(r"<\{section[^}]*\}>.*?<\{/section\}>", "", result, flags=re.DOTALL)
    print(f"After section removal: item.image_L present? {('item.image_L' in result)}")
    
    return result

# Test
with open("../ECsite/original/05_商品詳細/detail.html", encoding="utf-8") as f:
    full_tmpl = f.read()

start = full_tmpl.find('<div class="item-image">')
# Extract until "<!--追加商品画像-->"
end = full_tmpl.find('</div>', full_tmpl.find('<!--追加商品画像-->'))
item_image_section = full_tmpl[start:end+6]

_strip_conditional_blocks_debug(item_image_section)
