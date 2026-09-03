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


WORLD_MD_FLAGS_MAP = {
    "Spanish": ":flag_es:",
    "Italian": ":flag_it:",
    "French": ":flag_fr:",
    "Greek": ":flag_gr:",
    "Indian": ":flag_in:",
    "Japanese": ":flag_jp:",
    "Mexican": ":flag_mx:",
    "Czech": ":flag_cz:",
}


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


def update_recipe_db() -> tuple[dict, dict]:
    """Scan all recipe Markdown files and updates the database file."""
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

    return recipes, nav


def print_navigation(nav: dict):
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


def create_index_table(
    recipes_db: dict, section: str = ""
) -> tuple[list[str], list[tuple]]:
    """Defines the data of an index table as a dictionary."""
    headers = ["Recipe", "Origin", "Section"] if section == "" else ["Recipe", "Origin"]
    table_rows = []

    for r in recipes_db:
        if section != "" and r["section"] != section:
            continue

        r_name = r["recipe"]
        if r["annotation"] != "":
            r_name += f" {r['annotation']}"

        r_link = r["recipe"].lower().replace(" ", "_") + ".md"
        if section == "":
            r_link = f"{r['section']}/{r_link}"

        r_entry = f"[{r_name}]({r_link})"

        r_flag = WORLD_MD_FLAGS_MAP.get(r["nationality"], "--")
        if r_flag != "--":
            r_flag = f"{r['nationality']} {r_flag}"

        row_data = (
            (r_entry, r_flag, r["section"]) if section == "" else (r_entry, r_flag)
        )
        table_rows.append(row_data)

    return headers, table_rows


if __name__ == "__main__":
    db_data, nav_data = update_recipe_db()
    print_navigation(nav_data)
