"""Scanning recipes and updating DB.

The update happens only for recipes that do not appear at the current database.
Some keys are not input (like the nationality). These must be manually updated.
"""

import dataclasses as dtc
import json
import pprint
from pathlib import Path

import tomli_w
import tomllib

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


def update_navigation(nav: dict):
    """Terminal print of the navigation for `zensical.toml` (already formatted)."""
    final_nav = [{"Home": ["index.md", "all_recipes.md"]}]
    for section_title in sorted(nav):
        # Sorting contents alphabetically, with the file 'index.md' as first.
        section_content = [f for f in nav[section_title] if "index.md" in f]
        section_content.extend(
            [f for f in sorted(nav[section_title]) if "index.md" not in f]
        )
        final_nav.append({section_title: section_content})

    with open("zensical.toml", "rb") as fh:
        zensical_cfg = tomllib.load(fh)

    zensical_cfg["project"]["nav"] = final_nav
    with open("zensical.toml", "wb") as fh:
        tomli_w.dump(zensical_cfg, fh)

    print(
        "New navigation:\n",
        pprint.pformat(final_nav).replace(":", "=").replace("'", '"'),
    )


def update_recipe_db() -> dict:
    """Scan all recipe Markdown files and updates the database file `recipes/db.json`.

    Returns
    -------
    recipes : dict
        All database entries as a dictionary. Each entry contains the same
        fields as in the `Entry` dataclass.
    """
    with open(DB_PATH, "r", encoding="utf-8") as fh:
        recipes_db: list[dict] = json.load(fh)
    all_recipe_names = {r["recipe"] for r in recipes_db}
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
        recipes_db.append(Entry(recipe=name, section=section).to_dict())

    recipes_db.sort(key=lambda r: r["recipe"])

    empty_entry = Entry("", "").to_dict()
    for recipe in recipes_db:
        for k, v in empty_entry.items():
            if k not in recipe:
                recipe[k] = v

    with open(DB_PATH, "w", encoding="utf-8") as fh:
        json.dump(recipes_db, fh, indent=3)
    update_navigation(nav)

    return recipes_db


def create_md_index_table(recipes_db: dict, section: str = "") -> str:
    """Creates an index table in Markdown (containing the links)."""
    headers = ["Recipe", "Origin", "Section"] if section == "" else ["Recipe", "Origin"]

    md_table = "|" + "|".join(headers) + "|\n"
    md_table += "|:---" * len(headers) + "|\n"

    for r in recipes_db:
        if section != "" and r["section"] != section:
            continue

        r_name = r["recipe"]
        if r["annotation"] != "":
            r_name += f" ({r['annotation']})"

        r_link = r["recipe"].lower().replace("'s", "").replace(" ", "_") + ".md"
        if section == "":
            r_link = f"{r['section']}/{r_link}"

        r_entry = f"[{r_name}]({r_link})"

        r_flag = WORLD_MD_FLAGS_MAP.get(r["nationality"], "--")
        if r_flag != "--":
            r_flag = f"{r['nationality']} {r_flag}"

        row_data = (
            (r_entry, r_flag, r["section"]) if section == "" else (r_entry, r_flag)
        )
        md_table += "|" + "|".join(row_data) + "|\n"

    return md_table


def update_index_md_files(recipes_db: dict):
    """Iterates over all the folders and updates the indexes for the recipes."""
    section_titles = {
        "doughs": "Doughs: Bread & Pasta",
        "drinks": "Drinks",
        "preserves": "Preserves & Jams",
        "sauces": "Sauces",
        "sides": "Side Dishes, Tapas and Accompaniments",
        "stews": "Stews",
        "sweets": "Sweets",
    }

    # Iterating over all section index files...
    for idx_file in ROOT_PATH.glob("*/index.md"):
        section = idx_file.parent.name
        md_table = create_md_index_table(recipes_db, section)

        with open(idx_file, "w", encoding="utf-8") as fh:
            fh.write(
                f"---\ntitle: {section.title()}\n---\n\n"
                f"# {section_titles[section]}\n\n{md_table}"
            )

    # Updating the main index...
    md_table = create_md_index_table(recipes_db)
    with open(ROOT_PATH / "all_recipes.md", "w", encoding="utf-8") as fh:
        fh.write(
            f"---\ntitle: Recipe Index\n---\n\n"
            f"# All Recipes\n\nTotal recipes: {len(recipes_db)}\n\n{md_table}"
        )


if __name__ == "__main__":
    recipes = update_recipe_db()
    update_index_md_files(recipes)
