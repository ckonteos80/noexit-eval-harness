## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -29,8 +29,8 @@
 # unreachable through this path: the HF router returns 504 at roughly 120s and
 # that prompt needs longer. gpt-oss-120b answered the same prompt in 2.7s.
 # reasoning_effort stays at the provider default -- the proxy cannot forward it.
-# TEMP_GENERATION deliberately stays at 0.95 so the model is the only variable
-# that moved in this version.
+# TEMP_GENERATION was held at 0.95 for that swap so the model was the only
+# variable; it moves in this version instead -- see the note at TEMP_GENERATION.
 MODEL_GENERATION = "openai/gpt-oss-120b"
 # Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
 MODEL_NARRATOR = MODEL_DIALOGUE
@@ -39,7 +39,15 @@
 TEMP_DIALOGUE = 0.5     # CharacterController.temp
 TEMP_ADDRESSING = 0.5   # CharacterController.temp (same field)
 TEMP_NARRATOR = 0.5     # CharacterController.temp (same field)
-TEMP_GENERATION = 0.95  # CharacterGenerator.temperature
+# Lowered from 0.95 after the first gpt-oss-120b run collapsed into shared
+# sentence templates -- six frames appeared verbatim in both characters.
+# Two effects pull against each other and this value is the test of which wins:
+# high temperature degrades long reasoning chains, so lowering it should improve
+# rule-following and coherence; low temperature increases determinism, so lowering
+# it should make the model reach for the same high-probability frames MORE often.
+# Prediction recorded before the run: deaths become more rule-abiding, duplication
+# gets worse. If both improve instead, 0.95 was simply wrong for a reasoning model.
+TEMP_GENERATION = 0.6   # CharacterGenerator.temperature
 
 # ── Max tokens (from Inspector / code) ──
 MAX_TOKENS_DIALOGUE = 75
```
