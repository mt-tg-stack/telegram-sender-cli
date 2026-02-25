def parse_targets(text: str) -> list[int | str]:
    targets: list[int | str] = []
    for t in text.split(","):
        t = t.strip()
        if not t:
            continue
        try:
            targets.append(int(t))
        except ValueError:
            targets.append(t)
    return targets
