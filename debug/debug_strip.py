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
    
    # section / if タグを除去
    result = re.sub(r"<\{section[^}]*\}>.*?<\{/section\}>", "", result, flags=re.DOTALL)
    result = re.sub(r"<\{else\}>.*?(?=<\{/if\}>)", "", result, flags=re.DOTALL)
    result = re.sub(r"<\{/if\}>", "", result)
    result = re.sub(r"<\{if[^}]*\}>", "", result)
    
    return result

# Test
with open("../ECsite/original/05_商品詳細/detail.html", encoding="utf-8") as f:
    tmpl = f.read()

start = tmpl.find('<div class="item-image">')
end = tmpl.find('</div>', start) + 6
item_image_section = tmpl[start:end]

result = _strip_conditional_blocks(item_image_section, {})

print("=== After strip ===")
if "noimage.png" in result:
    print("❌ noimage.png is still present!")
    for i, line in enumerate(result.split('\n')):
        if "noimage" in line:
            print(f"  Line {i}: {line.strip()[:100]}")
else:
    print("✓ noimage.png removed!")

if "item.image_L" in result:
    print("✓ item.image_L placeholder is present")
    for i, line in enumerate(result.split('\n')):
        if "item.image_L" in line:
            print(f"  Line {i}: {line.strip()[:100]}")


