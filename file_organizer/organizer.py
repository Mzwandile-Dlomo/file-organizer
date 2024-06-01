import os
import shutil
import json
import filetype
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def load_rules():
    rules_path = os.path.join(os.path.dirname(__file__), 'rules.json')
    with open(rules_path, 'r') as file:
        return json.load(file)

def load_undo_log():
    undo_log_path = os.path.join(os.path.expanduser('~'), '.undo_log.json')
    if os.path.exists(undo_log_path):
        with open(undo_log_path, 'r') as file:
            return json.load(file)
    return {}

def save_undo_log(undo_log):
    undo_log_path = os.path.join(os.path.expanduser('~'), '.undo_log.json')
    with open(undo_log_path, 'w') as file:
        json.dump(undo_log, file)

def log_operation(operation):
    log_path = os.path.join(os.path.expanduser('~'), 'operation_log.txt')
    with open(log_path, 'a') as log_file:
        log_file.write(f"{datetime.now()}: {operation}\n")

def organize_files(directory, rules):
    print(f"Organizing files in directory: {directory}")
    undo_log = load_undo_log()
    undo_log['last_operation'] = []

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            print(f"Processing file: {filename}")
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
                    print(f"Moved {filename} to {category}")
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


class Watcher(FileSystemEventHandler):
    def __init__(self, directory, rules):
        self.directory = directory
        self.rules = rules
        print(f"Initialized watcher for directory: {self.directory}")


    def on_created(self, event):
        print("Attempting")
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            organize_files(self.directory, self.rules)


def main():
    directory = os.path.join(os.path.expanduser("~"), "Downloads")
    rules = load_rules()

    print(f"Starting to watch directory: {directory}")
    print(directory)
    event_handler = Watcher(directory, rules)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    
    try:
        observer.start()
        print("Observer started")
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        print("Observer stopped")
    observer.join()

if __name__ == "__main__":
    main()