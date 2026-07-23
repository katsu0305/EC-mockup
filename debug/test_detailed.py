#!/usr/bin/env python3
import re

def _strip_with_detailed_debug(tmpl: str):
    result = tmpl
    
    # Step 1: false_conditions
    false_conditions = {
        "member.is_logged_in", "cart.has_item", "shop.is_member_entry_enabled",
        "item.review.has_item", "category.image_url",
        "item.multi_image.has_item", "item.is_option_image", "item.add_image.has_item", "item.icon.has_item",
    }
    
    print("=== Step 1: false_conditions ===")
    for cond in false_conditions:
        pattern1 = r"<\{\s*if\s+\$" + re.escape(cond) + r"[^}]*\}>.*?<\{/if\}>"
        pattern2 = r"<\{\s*if\s+!\$" + re.escape(cond) + r"[^}]*\}>(.*?)<\{/if\}>"
        
        old_result = result
        result = re.sub(pattern1, "", result, flags=re.DOTALL)
        if old_result != result:
            print(f"  Pattern 1 ({cond}) matched and removed")
        
        old_result = result
        result = re.sub(pattern2, r"\1", result, flags=re.DOTALL)
        if old_result != result:
            print(f"  Pattern 2 (! {cond}) matched")
    
    print(f"After false_conditions: item.image_L? {('item.image_L' in result)}")
    print()
    
    # Step 2: else extraction
    print("=== Step 2: else extraction ===")
    pattern_else = r"<\{\s*if\s+[^}]+\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>"
    old_result = result
    result = re.sub(pattern_else, r"\1", result, flags=re.DOTALL)
    if old_result != result:
        print(f"  Else extraction matched")
    
    print(f"After else extraction: item.image_L? {('item.image_L' in result)}")
    
    # Find any remaining if blocks
    if_blocks = list(re.finditer(r"<\{\s*if\s+[^}]+\}>", result))
    print(f"  Remaining if blocks: {len(if_blocks)}")
    for ib in if_blocks[:3]:  # Show first 3
        print(f"    {ib.group(0)[:60]}")
    print()
    
    # Step 3: remove other if
    print("=== Step 3: remove other if blocks ===")
    old_len = len(result)
    pattern_if = r"<\{\s*if\s+[^}]+\}>.*?<\{/if\}>"
    result = re.sub(pattern_if, "", result, flags=re.DOTALL)
    print(f"  Removed {old_len - len(result)} characters")
    print(f"After if removal: item.image_L? {('item.image_L' in result)}")
    
    # Find what was removed
    print(f"\nDid the pattern match something with item.image_L?")
    test_result = tmpl
    matches = list(re.finditer(pattern_if, test_result, re.DOTALL))
    for i, m in enumerate(matches):
        if "item.image_L" in m.group(0):
            print(f"  Match {i} contains item.image_L: YES")
            print(f"    Content: {m.group(0)[:200]}")
        else:
            print(f"  Match {i} contains item.image_L: NO")

# Test
with open("../ECsite/original/05_商品詳細/detail.html", encoding="utf-8") as f:
    full_tmpl = f.read()

start = full_tmpl.find('<div class="item-image">')
end = full_tmpl.find('<!--追加商品画像-->')
item_image_section = full_tmpl[start:end]

_strip_with_detailed_debug(item_image_section)
