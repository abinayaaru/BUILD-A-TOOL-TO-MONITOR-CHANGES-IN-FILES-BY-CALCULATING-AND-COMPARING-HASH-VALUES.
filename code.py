import hashlib
import json
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler("file_monitor.log"), logging.StreamHandler()]
)

def calculate_file_hash(file_path, algorithm='sha256'):
    """
    Calculates the hash of the given file using the specified algorithm.
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error calculating hash for {file_path}: {e}")
        return None

def load_stored_hashes(file_path):
    """
    Loads stored hash values from a JSON file.
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def save_hashes(hashes, file_path):
    """
    Saves hash values to a JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(hashes, f, indent=4)

def monitor_files(files, hash_file='file_hashes.json', interval=5):
    """
    Monitors specified files for changes using hash comparison.
    """
    stored_hashes = load_stored_hashes(hash_file)

    try:
        while True:
            for file in files:
                current_hash = calculate_file_hash(file)

                if current_hash is None:
                    continue

                if file not in stored_hashes:
                    logging.info(f"New file added for monitoring: {file}")
                    stored_hashes[file] = current_hash
                elif stored_hashes[file] != current_hash:
                    logging.warning(f"Change detected in: {file}")
                    stored_hashes[file] = current_hash
                else:
                    logging.info(f"No changes in: {file}")

            save_hashes(stored_hashes, hash_file)
            time.sleep(interval)

    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")

if __name__ == "__main__":
    # Replace with your own file paths
    files_to_monitor = ['test1.txt', 'test2.txt']
    
    # Optional: create files with initial content if they don’t exist
    for file in files_to_monitor:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write("Initial content")

    monitor_files(files_to_monitor)
