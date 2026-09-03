"""Scanning recipes and updating DB.

The update happens only for recipes that do not appear at the current database.
Some keys are not input (like the nationality). These must be manually updated.
"""

import json
from pathlib import Path
import dataclasses as dtc
import pprint

ROOT_PATH = Path(__file__).resolve().parent / "recipes"
DB_PATH = ROOT_PATH / "db.json"


@dtc.dataclass
class Entry:
    recipe: str  # NAME of the recipe (titled). E.G.: "Pizza", "Focaccia", "Apple Cake".
    section: str  # SECTION containing the recipe. E.G.: "dough", "sauces", "sweets".
    nationality: str = (
        ""  # COUNTRY of the dish, or empty string. E.G.: "Spanish", "Indian", "Italian"
    )
    image: str = ""
    annotation: str = ""

    def to_dict(self) -> dict:
        return dtc.asdict(self)


if __name__ == "__main__":
    with open(DB_PATH, "r", encoding="utf-8") as fh:
        recipes: list[dict] = json.load(fh)
    all_recipe_names = {r["recipe"] for r in recipes}
    nav = {}

    for file in ROOT_PATH.glob("*/*.md"):
        nav.setdefault((section := file.parent.name).title(), []).append(
            f"{section}/{file.name}"
        )

        name = file.name.split(".")[0].replace("_", " ").title()
        if name.startswith("Abuela"):
            name = name.replace("Abuela", "Abuela's")
        if file.name == "index.md" or name in all_recipe_names:
            continue
        recipes.append(Entry(recipe=name, section=section).to_dict())

    recipes.sort(key=lambda r: r["recipe"])

    empty_entry = Entry("", "").to_dict()
    for recipe in recipes:
        for k, v in empty_entry.items():
            if k not in recipe:
                recipe[k] = v

    with open(DB_PATH, "w", encoding="utf-8") as fh:
        json.dump(recipes, fh, indent=3)

    final_nav = [{"Home": "index.md"}]
    for section_title in sorted(nav):
        # Sorting contents alphabetically, with the file 'index.md' as first.
        section_content = [f for f in nav[section_title] if "index.md" in f]
        section_content.extend(
            [f for f in sorted(nav[section_title]) if "index.md" not in f]
        )
        final_nav.append({section_title: section_content})

    print(
        "New navigation:\n",
        pprint.pformat(final_nav).replace(":", "=").replace("'", '"'),
    )
