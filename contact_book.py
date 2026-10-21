"""Contact Book - a simple command-line contact manager with JSON storage."""

import csv
import json
import re

CONTACTS_FILE = "contacts.json"
CSV_FILE = "contacts.csv"
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9 \-]{6,18}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class DuplicateContactError(Exception):
    """Raised when a contact with the same name already exists."""

    def __init__(self, name):
        self.name = name
        super().__init__(f"Contact '{name}' already exists.")


# ---------- Storage ----------

def load_contacts(filename=CONTACTS_FILE):
    """Load contacts from JSON. Old files ({name: phone}) are upgraded automatically."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("No contacts file found. Starting with an empty contact book.")
        return {}
    except json.JSONDecodeError:
        print("Contacts file contains invalid JSON. Starting with an empty contact book.")
        return {}

    contacts = {}
    for name, value in data.items():
        if isinstance(value, str):  # old format: just a phone number
            value = {"phone": value, "email": ""}
        contacts[name] = value
    return contacts


def save_contacts(contacts, filename=CONTACTS_FILE):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4, ensure_ascii=False)


# ---------- Helpers ----------

def find_name(contacts, name):
    """Return the stored name matching `name` (case-insensitive), or None."""
    for stored in contacts:
        if stored.lower() == name.lower():
            return stored
    return None


def ask_phone(prompt="Enter phone number: ", allow_blank=False):
    while True:
        phone = input(prompt).strip()
        if allow_blank and not phone:
            return ""
        if PHONE_PATTERN.match(phone):
            return phone
        print("Invalid phone number. Use digits, optionally starting with + (e.g. +923001234567).")


def ask_email(prompt="Enter email (optional, press Enter to skip): "):
    while True:
        email = input(prompt).strip()
        if not email or EMAIL_PATTERN.match(email):
            return email
        print("Invalid email address. Try again or press Enter to skip.")


def print_contact(name, info):
    line = f"Name: {name} | Phone: {info['phone']}"
    if info.get("email"):
        line += f" | Email: {info['email']}"
    print(line)


# ---------- Actions ----------

def add_contact(contacts):
    name = input("Enter contact name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    if find_name(contacts, name):
        raise DuplicateContactError(name)

    phone = ask_phone()
    email = ask_email()

    contacts[name] = {"phone": phone, "email": email}
    save_contacts(contacts)
    print(f"{name} added successfully.")


def view_contacts(contacts):
    if not contacts:
        print("No contacts saved yet.")
        return
    print(f"\n{len(contacts)} contact(s):")
    for name in sorted(contacts, key=str.lower):
        print_contact(name, contacts[name])


def search_contacts(contacts):
    query = input("Search by name, phone or email: ").strip().lower()
    if not query:
        print("Search text cannot be empty.")
        return
    matches = [
        name for name, info in contacts.items()
        if query in name.lower()
        or query in info["phone"]
        or query in info.get("email", "").lower()
    ]
    if not matches:
        print("No matching contacts found.")
        return
    for name in sorted(matches, key=str.lower):
        print_contact(name, contacts[name])


def update_contact(contacts):
    name = find_name(contacts, input("Enter contact name to update: ").strip())
    if not name:
        print("Contact not found.")
        return

    info = contacts[name]
    print("Press Enter to keep the current value.")
    phone = ask_phone(f"New phone [{info['phone']}]: ", allow_blank=True)
    email = ask_email(f"New email [{info.get('email') or 'none'}]: ")

    if phone:
        info["phone"] = phone
    if email:
        info["email"] = email
    save_contacts(contacts)
    print(f"{name} updated successfully.")


def delete_contact(contacts):
    name = find_name(contacts, input("Enter contact name to delete: ").strip())
    if not name:
        print("Contact not found.")
        return
    confirm = input(f"Delete '{name}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return
    del contacts[name]
    save_contacts(contacts)
    print(f"{name} deleted successfully.")


def export_csv(contacts, filename=CSV_FILE):
    if not contacts:
        print("No contacts to export.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Phone", "Email"])
        for name in sorted(contacts, key=str.lower):
            info = contacts[name]
            writer.writerow([name, info["phone"], info.get("email", "")])
    print(f"Exported {len(contacts)} contact(s) to {filename}.")


# ---------- Menu ----------

MENU = """
--- Contact Book ---
1. Add Contact
2. View Contacts
3. Search Contacts
4. Update Contact
5. Delete Contact
6. Export to CSV
7. Exit"""


def main():
    contacts = load_contacts()
    actions = {
        "1": add_contact,
        "2": view_contacts,
        "3": search_contacts,
        "4": update_contact,
        "5": delete_contact,
        "6": export_csv,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "7":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice, try again.")
            continue

        try:
            action(contacts)
        except DuplicateContactError as error:
            print(error)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
