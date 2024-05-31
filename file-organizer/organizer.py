import os
import shutil
import json
import filetype
from datetime import datetime


def load_rules():
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    with open(rules_path, 'r') as file:
        return json.load(file)

def load_undo_log():
    undo_log_path = os.path.join(os.path.expanduser('~'), '.file_organizer_undo_log.json')
    if os.path.exists(undo_log_path):
        with open(undo_log_path, 'r') as file:
            return json.load(file)
    return {}

def save_undo_log(undo_log):
    undo_log_path = os.path.join(os.path.expanduser('~'), '.file_organizer_undo_log.json')
    with open(undo_log_path, 'w') as file:
        json.dump(undo_log, file)

def log_operation(operation):
    log_path = os.path.join(os.path.expanduser('~'), 'file_organizer_operation_log.txt')
    with open(log_path, 'a') as log_file:
        log_file.write(f"{datetime.now()}: {operation}\n")

def organize_files(directory, rules):
    undo_log = load_undo_log()
    undo_log['last_operation'] = []

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            kind = filetype.guess(filepath)
            if kind:
                extension = kind.extension
            else:
                extension = filename.split('.')[-1].lower()
            
            moved = False

            for category, extensions in rules.items():
                if extension in extensions:
                    category_dir = os.path.join(directory, category)
                    if not os.path.exists(category_dir):
                        os.makedirs(category_dir)
                    new_filepath = os.path.join(category_dir, filename)
                    shutil.move(filepath, new_filepath)
                    undo_log['last_operation'].append((new_filepath, filepath))
                    log_operation(f"Moved {filename} to {category}")
                    moved = True
                    break

            if not moved:
                uncategorized_dir = os.path.join(directory, 'uncategorized')
                if not os.path.exists(uncategorized_dir):
                    os.makedirs(uncategorized_dir)
                new_filepath = os.path.join(uncategorized_dir, filename)
                shutil.move(filepath, new_filepath)
                undo_log['last_operation'].append((new_filepath, filepath))
                log_operation(f"Moved {filename} to uncategorized")

    save_undo_log(undo_log)

def undo_last_operation(directory):
    undo_log = load_undo_log()
    if 'last_operation' in undo_log:
        for new_filepath, old_filepath in undo_log['last_operation']:
            if os.path.exists(new_filepath):
                shutil.move(new_filepath, old_filepath)
                log_operation(f"Moved {os.path.basename(new_filepath)} back to original location")
        del undo_log['last_operation']
        save_undo_log(undo_log)
    else:
        print("No operations to undo.")

def add_custom_rule():
    category = input("Enter the new category name: ")
    extensions = input("Enter the file extensions (comma-separated): ").split(',')
    extensions = [ext.strip().lower() for ext in extensions]

    rules = load_rules()
    rules[category] = extensions

    rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    with open(rules_path, 'w') as file:
        json.dump(rules, file)

    log_operation(f"Added custom rule: {category} - {extensions}")

def main():
    directory = input("Enter the directory to organize: ")
    
    while True:
        print("\nOptions:")
        print("1. Organize files")
        print("2. Undo last operation")
        print("3. Add custom rule")
        print("4. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            rules = load_rules()
            organize_files(directory, rules)
            print("Files organized successfully.")
        elif choice == '2':
            undo_last_operation(directory)
            print("Last operation undone.")
        elif choice == '3':
            add_custom_rule()
            print("Custom rule added successfully.")
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()