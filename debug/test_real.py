#!/usr/bin/env python3
import re

def _strip_conditional_blocks(tmpl: str, vars_: dict[str, str]) -> str:
    """
    <{if ...}> ブロックを評価して不要なブランチを除去する。
    """
    result = tmpl
    
    # 明示的に false の条件リスト
    false_conditions = {
        "member.is_logged_in", "cart.has_item", "shop.is_member_entry_enabled",
        "item.review.has_item", "category.image_url",
        "item.multi_image.has_item", "item.is_option_image", "item.add_image.has_item", "item.icon.has_item",
    }
    
    for cond in false_conditions:
        # <{if $cond}>...</{if}> を除去
        result = re.sub(
            r"<\{\s*if\s+\$" + re.escape(cond) + r"[^}]*\}>.*?<\{/if\}>",
            "",
            result,
            flags=re.DOTALL,
        )
        # <{if !$cond}>...</{if}> → ... を残す（negation）
        result = re.sub(
            r"<\{\s*if\s+!\$" + re.escape(cond) + r"[^}]*\}>(.*?)<\{/if\}>",
            r"\1",
            result,
            flags=re.DOTALL,
        )
    
    # 複合条件（&&、||）を含む if ブロック：else があればそれを取り、なければ除去
    result = re.sub(
        r"<\{\s*if\s+[^}]+\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>",
        r"\1",
        result,
        flags=re.DOTALL,
    )
    
    # その他の if ブロック（else なし）：除去
    result = re.sub(
        r"<\{\s*if\s+[^}]+\}>.*?<\{/if\}>",
        "",
        result,
        flags=re.DOTALL,
    )
    
    # section ループを除去
    result = re.sub(r"<\{section[^}]*\}>.*?<\{/section\}>", "", result, flags=re.DOTALL)
    
    # 残りの if / else / elseif タグ除去
    result = re.sub(r"<\{else\}>.*?(?=<\{/if\}>)", "", result, flags=re.DOTALL)
    result = re.sub(r"<\{/if\}>", "", result)
    result = re.sub(r"<\{if[^}]*\}>", "", result)
    
    return result

# Test - extract the full item-image section correctly
with open("../ECsite/original/05_商品詳細/detail.html", encoding="utf-8") as f:
    full_tmpl = f.read()

# Find '<div class="item-image">' and matching closing '</div>'
start = full_tmpl.find('<div class="item-image">')
if start >= 0:
    # Count div depth to find the matching close
    depth = 0
    pos = start
    while pos < len(full_tmpl):
        open_tag = full_tmpl.find('<div', pos)
        close_tag = full_tmpl.find('</div>', pos)
        
        if open_tag < close_tag and open_tag >= 0 and close_tag >= 0:
            depth += 1
            pos = open_tag + 4
        elif close_tag >= 0:
            depth -= 1
            pos = close_tag + 6
            if depth == 0:
                end = pos
                break
        else:
            break
    
    item_image_section = full_tmpl[start:end]
    print(f"Extracted section length: {len(item_image_section)}")
    print(f"Contains item.image_L before: {('item.image_L' in item_image_section)}")
    
    result = _strip_conditional_blocks(item_image_section, {})
    
    print(f"\n=== After strip ===")
    print(f"Contains item.image_L: {('item.image_L' in result)}")
    print(f"Contains noimage.png: {('noimage.png' in result)}")
    
    if "item.image_L" in result:
        print("✓ item.image_L found!")
        for i, line in enumerate(result.split('\n')):
            if "item.image_L" in line:
                print(f"  {line.strip()}")


