## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -60,6 +60,53 @@
 # A '**' at the start of a line: how extract_field spots the next heading.
 _HEADING_START = re.compile(r"^\*\*", re.M)
 
+# Reasoning models may wrap their working in <think></think>. Most providers return
+# it in a separate field and leave `content` clean, but that is per-provider
+# behaviour and the router load-balances across several, so the same model can
+# answer either way between two calls. It matters because the reasoning holds a full
+# draft of the character, headings included -- an observed gpt-oss-120b trace had all
+# eleven -- and extract_field takes the FIRST match, so an un-stripped draft would
+# beat the real answer and parse cleanly while being wrong.
+_REASONING_BLOCK = re.compile(r"<think>.*?</think>", re.S | re.I)
+_REASONING_UNCLOSED = re.compile(r"<think>.*\Z", re.S | re.I)
+
+# Typographic variants seen where the prompt uses a plain ASCII character.
+# gpt-oss-120b wrote "Self-told" with U+2011 NON-BREAKING HYPHEN, which made an exact
+# find() miss the heading outright and cost a parse retry.
+# Every entry maps one character to exactly one character, so translating is
+# length-preserving: an offset found in the normalised copy indexes the original
+# unchanged, which is what lets the extracted value keep its real characters.
+_MATCH_EQUIV = {
+    0x2010: "-",  # HYPHEN
+    0x2011: "-",  # NON-BREAKING HYPHEN
+    0x2012: "-",  # FIGURE DASH
+    0x2013: "-",  # EN DASH
+    0x2014: "-",  # EM DASH
+    0x2015: "-",  # HORIZONTAL BAR
+    0x2212: "-",  # MINUS SIGN
+    0x00AD: "-",  # SOFT HYPHEN
+    0x00A0: " ",  # NO-BREAK SPACE
+    0x2007: " ",  # FIGURE SPACE
+    0x2009: " ",  # THIN SPACE
+    0x202F: " ",  # NARROW NO-BREAK SPACE
+}
+
+
+def strip_reasoning(response: str) -> str:
+    """
+    Remove <think></think> blocks. A no-op on any response without them, which is
+    every response on record. An unclosed <think> means the reasoning was cut off
+    before an answer existed, so everything from it onward goes too.
+    """
+    if not response or "<think>" not in response.lower():
+        return response
+    return _REASONING_UNCLOSED.sub("", _REASONING_BLOCK.sub("", response))
+
+
+def _normalise_for_match(text: str) -> str:
+    """Fold dash and space variants to ASCII. Length-preserving -- see _MATCH_EQUIV."""
+    return text.translate(_MATCH_EQUIV)
+
 
 def extract_field(response: str, field_name: str) -> Optional[str]:
     """
@@ -72,18 +119,26 @@
     bold ("teacher **and** coach") was silently truncated at the first inner marker.
     No response on record contains mid-line '**', so this is defensive rather than a
     change to how any existing run parses.
+
+    Matching tolerates dash and space variants (see _MATCH_EQUIV) and strips <think>
+    reasoning blocks (see strip_reasoning). Both were replayed against every
+    historical extraction on record and left all of them byte-identical.
     """
     if not response:
         return None
-    marker = f"**{field_name}**"
-    start = response.find(marker)
+    response = strip_reasoning(response)
+    # Search a dash/space-folded copy but slice the original: the two are the same
+    # length, so offsets carry over and the value keeps its real characters.
+    haystack = _normalise_for_match(response)
+    marker = _normalise_for_match(f"**{field_name}**")
+    start = haystack.find(marker)
     if start < 0:
         return None
     start += len(marker)
     # Skip leading newlines/CR
     while start < len(response) and response[start] in ("\n", "\r"):
         start += 1
-    nxt = _HEADING_START.search(response, start)
+    nxt = _HEADING_START.search(haystack, start)
     content = response[start:nxt.start()] if nxt else response[start:]
     return content.strip()
 
```
