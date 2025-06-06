import os
import csv
from typing import Dict, List, Tuple


def load_annotations(annotations_file: str) -> Dict[str, str]:
    """
    Reads the CSV at `annotations_file` and returns a mapping
    from image basename (no extension) -> ground-truth answer.
    Header lookup is case-insensitive, expecting 'filename' & 'solution'.
    """
    annotations: Dict[str, str] = {}
    with open(annotations_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = [h.strip().lower() for h in next(reader)]
        try:
            idx_img = headers.index('filename')
            idx_ans = headers.index('solution')
        except ValueError:
            raise ValueError(
                f"CSV {annotations_file} must have columns 'filename' and 'solution' (case-insensitive)"
            )

        for row in reader:
            key = row[idx_img].strip()
            answer = row[idx_ans].strip()
            if key and answer:
                annotations[key] = answer
    return annotations


def list_image_paths(images_dir: str, extensions: List[str] = None) -> List[str]:
    """
    Returns a sorted list of full file paths for all image files
    in `images_dir` matching the given extensions.
    """
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg']

    all_files = []
    for fname in os.listdir(images_dir):
        lower = fname.lower()
        if any(lower.endswith(ext) for ext in extensions):
            all_files.append(os.path.join(images_dir, fname))

    all_files.sort()
    return all_files


def load_dataset(
    images_dir: str,
    annotations_file: str
) -> List[Tuple[str, str]]:
    """
    Combines raw images + annotations into a list of (image_path, answer).
    Matches on filename without extension, so '001.png' pairs with key '001'.
    """
    ann_map = load_annotations(annotations_file)
    image_paths = list_image_paths(images_dir)

    dataset: List[Tuple[str, str]] = []
    for img_path in image_paths:
        fname = os.path.basename(img_path)
        key, _ = os.path.splitext(fname)           # strip '.png'
        if key in ann_map:
            dataset.append((img_path, ann_map[key]))
        else:
            print(f"[load_data] WARNING: no annotation for image '{fname}', skipping.")
    return dataset


if __name__ == "__main__":
    # Sanity check
    ROOT = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(ROOT, "raw", "img")      # <-- point at your 'img' folder
    ann_file   = os.path.join(ROOT, "raw", "annotations.csv")

    data = load_dataset(images_dir, ann_file)
    print(f"Loaded {len(data)} image–answer pairs.")
    for img_path, ans in data[:5]:
        print(f"  • {os.path.basename(img_path)}  →  {ans}")
