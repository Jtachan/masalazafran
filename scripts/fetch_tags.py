"""Fetching all the tags (among all recipes)."""
import re
import tomllib
import tomli_w
from pathlib import Path

TERMINAL_PRINT = True
OVERRIDE_CONFIG = True

def extract_tags(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    match = re.search(r"^---\s*\ntags:\s*\n((?:\s+-\s+.+\n)*?)---", content, re.MULTILINE)
    if not match:
        return []
    return re.findall(r"^\s+-\s+(.+)$", match.group(1), re.MULTILINE)

def collect_all_tags(recipes_dir: str = "recipes") -> set[str]:
    root = Path(recipes_dir)
    tags = set()
    for md_file in root.rglob("*.md"):
        if md_file.name == "index.md":
            continue
        tags.update(extract_tags(md_file))
    return tags

def update_config(tags: set[str]):
    zensical_cfg = Path("zensical.toml")
    config = tomllib.loads(zensical_cfg.read_text(encoding="utf-8"))
    config["project"]["extra"]["tags"] = {
        tag: tag.lower() for tag in tags
    }
    zensical_cfg.write_text(tomli_w.dumps(config), encoding="utf-8")

def print_tags(tags: set[str]):
    print(f"Tags:\n")
    for tag in tags:
        print(f'{tag} = "{tag.lower()}"')

if __name__ == "__main__":
    all_tags = collect_all_tags()
    if TERMINAL_PRINT:
        print_tags(all_tags)
    if OVERRIDE_CONFIG:
        update_config(all_tags)