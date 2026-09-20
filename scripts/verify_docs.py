from __future__ import annotations

from pathlib import Path


def main() -> None:
    files = {
        "README.md": Path("README.md").read_text(encoding="utf-8"),
        "docs/PROTOCOL.md": Path("docs/PROTOCOL.md").read_text(encoding="utf-8"),
        "docs/METHODOLOGY.md": Path("docs/METHODOLOGY.md").read_text(encoding="utf-8"),
        "docs/BACKENDS.md": Path("docs/BACKENDS.md").read_text(encoding="utf-8"),
    }
    required_readme = [
        "jevbench validate",
        "jevbench dry-run",
        "jevbench run",
        "jevbench compare",
        "docker compose",
        "host.docker.internal",
        "SemIf",
        "kev",
    ]
    for token in required_readme:
        assert token in files["README.md"], f"README missing {token!r}"
    for primitive in ("choice", "noul", "score"):
        assert primitive in files["docs/PROTOCOL.md"]
    methodology = files["docs/METHODOLOGY.md"].lower()
    for metric in ("brier", "ece", "option-order", "selective"):
        assert metric in methodology
    for backend in ("HTTP", "command", "replay", "oracle"):
        assert backend in files["docs/BACKENDS.md"]
    print("documentation verification passed")


if __name__ == "__main__":
    main()
