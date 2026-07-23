#!/usr/bin/env python3
import re

test_html = '''<div class="item-image">
                <{if !$item.multi_image.has_item && $item.is_option_image}>
                <div class="main-image clearfix"><img src="/view/images/common/noimage.png" alt="" class="item-image"></div>
                <{/if}>
                
                <{if $item.multi_image.has_item || $item.is_option_image}>
                    <ul class="gallery">
                        gallery content
                    </ul>
                <{else}>
                    <div class="main-image clearfix"><img src="<{$item.image_L}>" alt="" class="item-image"></div>
                <{/if}>
            </div>'''

print("=== Original ===")
print(test_html[:200])

# Test pattern
pattern1 = r"<\{\s*if\s+[^}]+\}>.*?<\{/if\}>"
matches = list(re.finditer(pattern1, test_html, re.DOTALL))
print(f"\n=== Matches for pattern ===")
print(f"Found {len(matches)} matches")
for i, m in enumerate(matches):
    print(f"\nMatch {i+1}:")
    print(f"  Start: {m.start()}, End: {m.end()}")
    print(f"  Text: {m.group(0)[:100]}...")

# Test with else
pattern2 = r"<\{\s*if\s+[^}]+\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>"
matches2 = list(re.finditer(pattern2, test_html, re.DOTALL))
print(f"\n=== Matches for pattern2 (with else) ===")
print(f"Found {len(matches2)} matches")
for i, m in enumerate(matches2):
    print(f"\nMatch {i+1}:")
    print(f"  Else content: {m.group(1)[:100]}...")

# Apply replaces in order
result = test_html

# First: else cases
result = re.sub(
    r"<\{\s*if\s+[^}]+\}>.*?<\{\s*else\s*\}>(.*?)<\{/if\}>",
    r"\1",
    result,
    flags=re.DOTALL,
)
print(f"\n=== After else replacement ===")
print("noimage.png still present?" if "noimage.png" in result else "✓ noimage.png gone")

# Second: no-else cases
result = re.sub(
    r"<\{\s*if\s+[^}]+\}>.*?<\{/if\}>",
    "",
    result,
    flags=re.DOTALL,
)
print(f"\n=== After no-else replacement ===")
print("noimage.png still present?" if "noimage.png" in result else "✓ noimage.png gone")
print("\nFinal result:")
print(result)
