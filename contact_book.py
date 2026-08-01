import json 
def main():
    
    contacts = load_contacts()
    while True:
        print("\n --- Contact Book ---")
        print("1. Add Contact")
        print("2. View Contacts")
        print("3. Delete Contact")
        print("4. Exit")
        
        choice = input("choose an option: ")
        
        if choice == "1":
            try:
                add_contact(contacts)
            except DuplicateContactError as e:
                print(e)
            
        elif choice == "2":
            view_contacts(contacts)

        elif choice == "3":
            name = input("Enter contact name to delete: ").strip()
            delete_contact(contacts, name)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice, try again.")

def add_contact(contacts):
    name = input("Enter contact name: ").strip()
    
    if not name:
        print("Name cannot be empty.")
        return
    
    if name in contacts:
        raise DuplicateContactError(name)
    
    phone = input("Enter phone number: ").strip()
    
    if not phone:
        print("phone number cannot be empty.")
        return
    
    
    contacts[name] = phone
    save_contacts(contacts) 
    
    print(f"{name} added successfully. ")
    
class DuplicateContactError(Exception):
    def __init__(self, name):
        self.name = name 
        super().__init__(f"Contact '{name}' already exists")
    
def view_contacts(contacts):
    if not contacts:
        print(f"No contacts saved yet")
    else:
        for name, phone in contacts.items():
            print(f"Name: {name}, Phone: {phone}")
            
def load_contacts(filename="contacts.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("No contacts file found. Starting with an empty contact book.")
        return {}
    except json.JSONDecodeError:
        print("contacts file contains invalid json")
        return {}
        
def save_contacts(contacts, filename="contacts.json"):
    with open(filename, "w") as file:
        json.dump(contacts, file, indent=4)
    print("contact book updated.")
    
def delete_contact(contacts, name):
    try:
        del contacts[name]
        save_contacts(contacts)    
        print(f"{name} deleted successfully.")
    except KeyError:
        print(f"Contact '{name}' not found.")
        
            
    
if __name__ == "__main__":
    main()
