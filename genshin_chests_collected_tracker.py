#!/bin/python3
import os
import re
import sqlite3

os.makedirs("./db_files", exist_ok=True)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class DBOperations:
    db_name = os.path.join(BASE_DIR, "db_files", "collected_chests_tracker.db")

    def __init__(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS chests (
            id INTEGER PRIMARY KEY, 
            video_title TEXT NOT NULL,
            chest_number INTEGER
        )
        """
        self.conn = sqlite3.connect(DBOperations.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def get_all_rows(self) -> list:
        query = "SELECT * FROM chests"
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        table = [columns] + self.cursor.fetchall()
        return table

    def add_entry(self, video_title: str, chest_count: int = 0) -> None:
        add_query = """
            INSERT INTO chests (video_title, chest_number)
            VALUES(?, ?)
        """
        self.cursor.execute(add_query, (video_title, chest_count))
        self.conn.commit()

    def update_chest_count(self, entry_id: int, new_chest_count: int) -> None:
        update_query = """
            UPDATE chests
            SET chest_number = ?
            WHERE id = ?
        """
        self.cursor.execute(update_query, (new_chest_count, entry_id))
        if self.cursor.rowcount == 0:
            raise ValueError("No entry found with given ID.")
        self.conn.commit()

    def delete_entry(self, entry_id: int) -> None:
        delete_query = """
            DELETE FROM chests WHERE id = ?
        """
        self.cursor.execute(delete_query, (entry_id,))
        self.conn.commit()

    def finished_ops(self) -> None:
        self.conn.close()


class IOinteractions:
    def print_table(self, table):
        str_rows = [
            [str(item) if item is not None else "null" for item in row] for row in table
        ]
        str_cols = str_rows[0]

        col_widths = (
            [
                max(len(col), *(len(row[i]) for row in str_rows[1:]))
                for i, col in enumerate(str_cols)
            ]
            if len(str_rows) > 1
            else [len(col) for col in (str_cols)]
        )

        format_divider = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

        def format_row(row):
            return (
                "| "
                + " | ".join(row[i].ljust(col_widths[i]) for i in range(len(row)))
                + " |"
            )

        os.system("cls" if os.name == "nt" else "clear")
        print("Tracked Chests: ")
        print(format_divider)
        print(format_row(str_cols))
        print(format_divider)
        for row in str_rows[1:]:
            print(format_row(row))
        print(format_divider)

    def initial_menu(self, opts):
        prompt = "What would you like to do?"
        for option in opts:
            prompt += f"\n{option[0]}. {option[1]}"
        prompt += "\n"
        while True:
            try:
                user_selection = int(input(prompt))
                if user_selection not in [item[0] for item in opts]:
                    raise ValueError
                return user_selection
            except ValueError:
                print("Invalid selection. You must choose one of the given options")

    def add_new_menu(self):
        prompt = "Please type in the video title. Video title must be alphanumeric and only _ is allowed: "
        while True:
            title = input(prompt).strip()
            is_valid = re.fullmatch(r"[\w\.\-]+", title)
            if is_valid:
                return title
            print("Invalid input.")

    def update_chest_count_menu(self):
        id_prompt = "Please provide the id number of the video you want to update the chest count for: "
        chest_count_prompt = "Please provide the updated chest count: "
        while True:
            try:
                id_input = int(input(id_prompt))
                chest_count_input = int(input(chest_count_prompt))
                return (id_input, chest_count_input)
            except ValueError:
                print("ID and Chest Count must be an integer.")

    def delete_entry_menu(self):
        id_prompt = "Please provide the id number of the entry you want to delete: "
        while True:
            try:
                id_input = int(input(id_prompt))
                return id_input
            except ValueError:
                print("ID must be an integer.")


def main():
    db = DBOperations()
    io = IOinteractions()

    options = [
        (1, "Add a new entry"),
        (2, "Update a chest count"),
        (3, "Delete an entry"),
        (4, "Exit"),
    ]

    try:
        while True:
            current_table = db.get_all_rows()
            io.print_table(current_table)
            action_selected = io.initial_menu(options)
            try:
                if action_selected == 1:
                    video_title = io.add_new_menu()
                    db.add_entry(video_title)
                    continue
                if action_selected == 2:
                    entry_id, new_count = io.update_chest_count_menu()
                    db.update_chest_count(entry_id, new_count)
                    continue
                if action_selected == 3:
                    entry_id = io.delete_entry_menu()
                    db.delete_entry(entry_id)
                    continue
                if action_selected == 4:
                    db.finished_ops()
                    return
            except Exception as e:
                print(f"Error: {e}")
                input("Press enter to continue...")
    except KeyboardInterrupt:
        db.finished_ops()
        print("\n")
        return


if __name__ == "__main__":
    main()


# import sys

# conn = sqlite3.connect("collectd_chests_tracker.db")
# cursor = conn.cursor()

# cursor.execute(
#     "CREATE TABLE IF NOT EXISTS chests (id INTEGER PRIMARY KEY, chest_number INTEGER)"
# )
# cursor.execute("SELECT chest_number FROM chests WHERE id = 1")

# row = cursor.fetchone()
# if row:
#     print(f"Current collected chest number: {row[0]}")
# else:
#     print("No data currently stored. Please update the collected chest number.")

# want_to_add_new = input(
#     "Do you want to update the collected chest number?(y/n) "
# ).lower()

# if want_to_add_new == "y":
#     try:
#         new_chest_number = int(
#             input("Please input the updated collected chest number: ")
#         )
#         cursor.execute(
#             """
#             INSERT INTO chests (id, chest_number)
#             VALUES(1, ?)
#             ON CONFLICT(ID) DO UPDATE SET chest_number = excluded.chest_number
#         """,
#             (new_chest_number,),
#         )
#         conn.commit()
#         cursor.execute("SELECT chest_number FROM chests WHERE id = 1")
#         row = cursor.fetchone()
#         print(
#             f"Chest collection number updated successfully.Current collected chest number: {row[0]}"
#         )
#     except ValueError:
#         print("Invalid input. Please enter an integer.")
# else:
#     print("No updates made.")

# input("Press Enter to exit")
# conn.close()
# sys.exit()
