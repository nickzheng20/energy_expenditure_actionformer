import os
import json
import shutil

def copy_files_from_json(json_file: str, source_folder: str, destination_folder: str, file_type='mp4'):

    os.makedirs(destination_folder, exist_ok=True)

    print(f"file_type: {file_type}")

    # Read the JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found: {json_file}")
        exit(1)
    except json.JSONDecodeError:
        print("Invalid JSON format")
        exit(1)

    # Get all keys under 'database'
    file_keys = data.get('database', {}).keys()

    # Copy files based on keys
    for file_name in file_keys:
        file_name = file_name + f'.{file_type}'
        source_path = os.path.join(source_folder, file_name)
        dest_path = os.path.join(destination_folder, file_name)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"Copied: {source_path} -> {dest_path}")
        else:
            print(f"File not found, skipped: {source_path}")

    print("File copying completed!")


def extract_video_names(in_folder_path, out_folder_path):
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.mpeg', '.webm'}
    video_paths = []
    total_files_len = len([file for file in os.listdir(in_folder_path) if os.path.splitext(file)[1].lower() in video_extensions])
    print(f"Total files: {total_files_len}")
    for i, file_name in enumerate(os.listdir(in_folder_path)):
        file_path = os.path.join(out_folder_path, file_name)
        if os.path.splitext(file_name)[1].lower() in video_extensions:
            print(f"Writing video file {i}/{total_files_len}: {file_path}")
            video_paths.append(file_path)
        else:
            print(f"Skipping non-video file: {file_name}")

    with open('video_paths.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(video_paths))

def check_directory_difference(dir1, dir2):

    num_files_dir1 = len(os.listdir(dir1))
    num_files_dir2 = len(os.listdir(dir2))

    print(f"Number of files in {dir1}: {num_files_dir1}")
    print(f"Number of files in {dir2}: {num_files_dir2}")

    files_dir1 = set(os.path.splitext(file)[0] for file in os.listdir(dir1))
    files_dir2 = set(os.path.splitext(file)[0] for file in os.listdir(dir2))

    only_in_dir1 = files_dir1 - files_dir2
    only_in_dir2 = files_dir2 - files_dir1

    print(f"Files only in {dir1}: {only_in_dir1}")
    print(f"Files only in {dir2}: {only_in_dir2}")

    return only_in_dir1, only_in_dir2


