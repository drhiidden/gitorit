from diff_simplifier import simplify_diff

sample_diff = """diff --git a/src/main.py b/src/main.py
index 83db48f..f9a2021 100644
--- a/src/main.py
+++ b/src/main.py
@@ -10,5 +10,6 @@ def hello():
     print("world")
     # some context
-    return False
+    return True
+    # new line
"""

print(simplify_diff(sample_diff))
