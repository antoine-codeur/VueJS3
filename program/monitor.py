import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TreeUpdateHandler(FileSystemEventHandler):
    def __init__(self, root_dir, exclusions_file, output_file):
        self.root_dir = root_dir
        self.exclusions_file = exclusions_file
        self.output_file = output_file
        self.last_update_time = 0
        self.update_delay = 3  # Délai minimal entre les mises à jour (en secondes)
        self.update_tree()  # Mise à jour initiale

    def on_created(self, event):
        """Déclenché lors de la création d'un fichier ou dossier."""
        self.schedule_update()

    def on_deleted(self, event):
        """Déclenché lors de la suppression d'un fichier ou dossier."""
        self.schedule_update()

    def on_moved(self, event):
        """Déclenché lors du déplacement/renommage d'un fichier ou dossier."""
        self.schedule_update()

    def schedule_update(self):
        """Planifie une mise à jour si le délai minimal est écoulé."""
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_delay:
            self.update_tree()
            self.last_update_time = current_time

    def update_tree(self):
        """ Met à jour le fichier tree.txt en fonction de l'arborescence actuelle et des exclusions. """
        exclusions = read_exclusions(self.exclusions_file)
        tree = generate_tree(self.root_dir, exclusions)
        write_tree_to_file(tree, self.output_file)

def read_exclusions(file_path):
    exclusions = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                if clean_line and not clean_line.startswith('#'):
                    exclusions.append(clean_line)
    except FileNotFoundError:
        print("Le fichier d'exclusion n'existe pas.")
    return exclusions

def generate_tree(directory, exclusions):
    tree = []
    for root, dirs, files in os.walk(directory):
        path = root[len(directory):].lstrip(os.sep)
        parts = path.split(os.sep)
        if any(part in exclusions or os.path.join(*parts[:i+1]) in exclusions for i, part in enumerate(parts)):
            dirs[:] = []
            continue
        if parts:  # Vérifie s'il y a des parties dans le chemin
            indent = ' ' * 4 * (len(parts) - 1)  # Ne pas indenter pour le premier niveau
            tree.append(f"{indent}{os.path.basename(root)}/")
        else:
            indent = ''
        for f in files:
            if f not in exclusions and not os.path.join(path, f) in exclusions:
                tree.append(f"{indent}    {f}")
    return '\n'.join(tree)

def write_tree_to_file(tree, file_path):
    with open(file_path, 'w') as file:
        file.write(tree)

def main():
    root_directory = '.'  # Utilise le répertoire courant
    exclusions_file = 'exclude_dirs.txt'
    output_file = 'tree.txt'

    event_handler = TreeUpdateHandler(root_directory, exclusions_file, output_file)
    observer = Observer()
    observer.schedule(event_handler, path=root_directory, recursive=True)
    observer.start()
    try:
        while True:
            pass  # Maintient le script en exécution
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()