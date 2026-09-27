## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -20,10 +20,18 @@
 # stopped serving it. Qwen3-8B is ungated with 2 live providers (nscale, featherless-ai).
 MODEL_DIALOGUE = "Qwen/Qwen3-8B"
 MODEL_ADDRESSING = "Qwen/Qwen3-8B"
-# Generation runs once per session (cost/latency don't matter as much here), so it
-# gets Qwen's flagship instead -- same family/license as the models above, chosen
-# to address vague/disconnected character-gen content flagged in human eval.
-MODEL_GENERATION = "Qwen/Qwen3-235B-A22B-Instruct-2507"
+# Generation runs once per session, so quality matters more here than cost or
+# latency -- it gets a reasoning model. The reasoning itself is returned by the
+# provider in a separate field and deliberately ignored: providers.py reads only
+# choices[0].message.content, and assembly.strip_reasoning covers the providers
+# that inline it as <think> instead.
+# Chosen over Qwen/Qwen3-235B-A22B-Thinking-2507, which is the stronger model but
+# unreachable through this path: the HF router returns 504 at roughly 120s and
+# that prompt needs longer. gpt-oss-120b answered the same prompt in 2.7s.
+# reasoning_effort stays at the provider default -- the proxy cannot forward it.
+# TEMP_GENERATION deliberately stays at 0.95 so the model is the only variable
+# that moved in this version.
+MODEL_GENERATION = "openai/gpt-oss-120b"
 # Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
 MODEL_NARRATOR = MODEL_DIALOGUE
 
```
