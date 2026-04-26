from analyzer import GitAnalyzer

analyzer = GitAnalyzer("/home/drugo/projects/HALETHEIA/apps/2-open-core/gitorit")
commits = analyzer.extract_commits(include_diffs=True)
for c in commits[:2]:
    print(f"Commit: {c.short_hash}")
    print(f"Message: {c.message}")
    print("Diff:")
    print(c.simplified_diff)
    print("-" * 40)
