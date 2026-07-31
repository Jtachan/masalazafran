"""Scanning recipes and updating DB.

The update happens only for recipes that do not appear at the current database.
Some keys are not input (like the nationality). These must be manually updated.
"""

import json
from pathlib import Path
import dataclasses as dtc

ROOT_PATH = Path(__file__).resolve().parent / "recipes"
DB_PATH = ROOT_PATH / "db.json"


@dtc.dataclass
class Entry:
    recipe: str  # NAME of the recipe (titled). E.G.: "Pizza", "Focaccia", "Apple Cake".
    section: str  # SECTION containing the recipe. E.G.: "dough", "sauces", "sweets".
    nationality: str = (
        ""  # COUNTRY of the dish, or empty string. E.G.: "Spanish", "Indian", "Italian"
    )

    def to_dict(self) -> dict:
        return dtc.asdict(self)


if __name__ == "__main__":
    with open(DB_PATH, "r", encoding="utf-8") as fh:
        recipes: list[dict] = json.load(fh)
    all_recipe_names = {r["recipe"] for r in recipes}

    for file in ROOT_PATH.glob("*/*.md"):
        name = file.name.split(".")[0].replace("_", " ").title()
        if name.startswith("Abuela"):
            name = name.replace("Abuela", "Abuela's")
        if file.name == "index.md" or name in all_recipe_names:
            continue
        recipes.append(Entry(recipe=name, section=file.parent.name).to_dict())

    recipes.sort(key=lambda r: r["recipe"])
    with open(DB_PATH, "w", encoding="utf-8") as fh:
        json.dump(recipes, fh, indent=3)
