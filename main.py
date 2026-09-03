"""Main file for the 'macros' plugin."""

import json

WORLD_FLAGS_MAP = {
    "Spanish": ":flag_es:",
    "Italian": ":flag_it:",
    "French": ":flag_fr:",
    "Greek": ":flag_gr:",
    "Indian": ":flag_in:",
    "Japanese": ":flag_jp:",
    "Mexican": ":flag_mx:",
    "Czech": ":flag_cz:",
}


with open("recipes/db.json", "r", encoding="utf-8") as db_file:
    recipes_db = json.load(db_file)


def define_env(env):
    """Macros hook function."""

    @env.macro
    def load_index_table(section: str = "") -> str:
        """Creates an index table base on the recipe's section."""
        headers = (
            ["Recipe", "Origin", "Section"] if section == "" else ["Recipe", "Origin"]
        )
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

            r_flag = WORLD_FLAGS_MAP.get(r["nationality"], "--")
            if r_flag != "--":
                r_flag = f"{r['nationality']} {r_flag}"

            row_data = (
                [r_entry, r_flag, r["section"]] if section == "" else [r_entry, r_flag]
            )
            table_rows.append([f"<td>{d}</td>" for d in row_data])

        headers = "".join([f"<th>{h}</th>" for h in headers])
        table_rows = "\n".join(f"<tr>{r}</tr>" for r in table_rows)

        return f"<table>{headers}{table_rows}</table>"
