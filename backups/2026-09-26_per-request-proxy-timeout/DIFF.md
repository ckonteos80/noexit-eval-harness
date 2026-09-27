## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -67,5 +67,17 @@
 # ── Request timeout (seconds) ──
 REQUEST_TIMEOUT = 180
 
+# ── Proxy-side read timeout (seconds) ──
+# The proxy Space decides how long it waits on the upstream provider. It uses 60s
+# when we send nothing, which is fine for dialogue but too short for generation
+# once a slower or reasoning-capable model is in play. Sent per request as
+# "timeout"; the proxy clamps it to [1, 600]. Every other call type omits the
+# field entirely and keeps the proxy's own default.
+PROXY_TIMEOUT_GENERATION = 300
+
+# The harness must outlast the proxy so the proxy's timeout fires first and we get
+# a real error back, rather than the client giving up on a call that is still running.
+PROXY_TIMEOUT_MARGIN = 30
+
 # ── Parsing retry config ──
 PARSE_RETRY_ATTEMPTS = 2
```

## providers.py

```diff
--- providers.py (previous)
+++ providers.py (this version)
@@ -47,6 +47,8 @@
     provider        : provider routing used ("hf"/"openai") — None for the extractor
     temperature     : temperature used — None for the extractor
     max_tokens      : max_tokens setting used — None for the extractor
+    proxy_timeout   : per-request read timeout asked of the proxy; None when the
+                      field was omitted and the proxy's own default applied
     endpoint        : which URL was hit
     """
     content: str
@@ -63,6 +65,7 @@
     provider: Optional[str] = None
     temperature: Optional[float] = None
     max_tokens: Optional[int] = None
+    proxy_timeout: Optional[float] = None
     endpoint: Optional[str] = None
 
     def to_dict(self) -> dict:
@@ -82,6 +85,7 @@
             "provider": self.provider,
             "temperature": self.temperature,
             "max_tokens": self.max_tokens,
+            "proxy_timeout": self.proxy_timeout,
             "endpoint": self.endpoint,
         }
 
@@ -94,6 +98,7 @@
     max_tokens: int,
     provider: Optional[str] = None,
     retry_attempts: int = 2,
+    proxy_timeout: Optional[float] = None,
 ) -> CallResult:
     """
     POST to the noexit proxy, mirroring APIRequestHandler.SendOpenAIRequest.
@@ -120,6 +125,17 @@
         "provider": provider,
     }
 
+    # Only sent when a non-default wait is wanted. Omitting it leaves the proxy on
+    # its own 60s, which is what every call type except generation wants.
+    if proxy_timeout is not None:
+        payload["timeout"] = proxy_timeout
+
+    # Outlast the proxy on purpose: its timeout should fire first and come back as a
+    # real error, rather than this client giving up on a call that is still running.
+    client_timeout = config.REQUEST_TIMEOUT
+    if proxy_timeout is not None:
+        client_timeout = max(client_timeout, proxy_timeout + config.PROXY_TIMEOUT_MARGIN)
+
     headers = {
         "Content-Type": "application/json",
         "Accept": "application/json",
@@ -137,7 +153,7 @@
                 config.PROXY_URL,
                 json=payload,
                 headers=headers,
-                timeout=config.REQUEST_TIMEOUT,
+                timeout=client_timeout,
             )
         except requests.exceptions.RequestException as e:
             last_error = f"Connection error: {e}"
@@ -176,6 +192,7 @@
                     provider=provider,
                     temperature=temperature,
                     max_tokens=max_tokens,
+                    proxy_timeout=proxy_timeout,
                     endpoint=config.PROXY_URL,
                 )
             except (KeyError, IndexError, ValueError) as e:
```
