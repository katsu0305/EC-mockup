#!/usr/bin/env python3
import re

tmpl = """
<div class="item-image">
                <{if !$item.multi_image.has_item && $item.is_option_image}>
                <div class="main-image clearfix"><img src="/view/images/common/noimage.png" alt="" class="item-image"></div>
                <{/if}>
                
                <{if $item.multi_image.has_item || $item.is_option_image}>
                    <ul class="gallery">
                        <{section name=i loop=$item.multi_image.list}>
                            <li><img src="<{$item.multi_image.list[i].image_L}>" class="item-image" alt=""></li>
                        <{/section}>
                    </ul>
                    <ul class="choice-btn">
                        <{section name=i loop=$item.multi_image.list}>
                            <li><img src="<{$item.multi_image.list[i].image_L}>" class="item-image" alt="" loading="lazy"></li>
                        <{/section}>
                    </ul>
                <{else}>
                    <div class="main-image clearfix"><img src="<{$item.image_L}>" alt="" class="item-image"></div>
                <{/if}>
            </div>
"""

# Test specific patterns
cond = "item.is_option_image"
pattern = r"<\{\s*if\s+\$" + re.escape(cond) + r"[^}]*\}>.*?<\{/if\}>"

print(f"Pattern: {pattern}")
matches = list(re.finditer(pattern, tmpl, re.DOTALL))
print(f"Matches: {len(matches)}")
for m in matches:
    print(f"  {m.group(0)[:100]}")

print(f"\nChecking first if block:")
first_if = '<{if !$item.multi_image.has_item && $item.is_option_image}>'
print(f"Contains '$item.is_option_image': {'item.is_option_image' in first_if}")
print(f"Matches pattern? {bool(re.search(pattern, first_if))}")

# Check second if
second_if = '<{if $item.multi_image.has_item || $item.is_option_image}>'
print(f"\nSecond if contains '$item.is_option_image': {'item.is_option_image' in second_if}")
print(f"Matches pattern? {bool(re.search(pattern, second_if))}")
