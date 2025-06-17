import os
import csv
from typing import Dict, List, Tuple, Optional
from pathlib import Path


def load_annotations(annotations_file: str) -> Dict[str, str]:
    """
    Reads the CSV at `annotations_file` and returns a mapping
    from image basename (no extension) -> ground-truth answer.
    Header lookup is case-insensitive, expecting 'filename' & 'solution'.
    """
    if not os.path.exists(annotations_file):
        raise FileNotFoundError(f"Annotations file not found: {annotations_file}")
    
    annotations: Dict[str, str] = {}
    
    try:
        with open(annotations_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Read and normalize headers
            try:
                headers = [h.strip().lower() for h in next(reader)]
            except StopIteration:
                raise ValueError(f"Empty CSV file: {annotations_file}")
            
            # Find required columns (case-insensitive)
            filename_col = None
            solution_col = None
            
            for i, header in enumerate(headers):
                if header in ['filename', 'file', 'image', 'img']:
                    filename_col = i
                elif header in ['solution', 'answer', 'truth', 'ground_truth', 'idiom']:
                    solution_col = i
            
            if filename_col is None:
                raise ValueError(
                    f"Could not find filename column in {annotations_file}. "
                    f"Expected one of: filename, file, image, img. Found: {headers}"
                )
            
            if solution_col is None:
                raise ValueError(
                    f"Could not find solution column in {annotations_file}. "
                    f"Expected one of: solution, answer, truth, ground_truth, idiom. Found: {headers}"
                )
            
            # Read data rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                if len(row) <= max(filename_col, solution_col):
                    print(f"⚠️  Row {row_num}: Not enough columns, skipping")
                    continue
                
                filename = row[filename_col].strip()
                solution = row[solution_col].strip()
                
                if not filename or not solution:
                    print(f"⚠️  Row {row_num}: Empty filename or solution, skipping")
                    continue
                
                # Remove file extension from filename for consistent matching
                key = os.path.splitext(filename)[0]
                annotations[key] = solution
        
        print(f"📊 Loaded {len(annotations)} annotations from {annotations_file}")
        return annotations
        
    except Exception as e:
        raise ValueError(f"Error reading annotations file {annotations_file}: {e}")


def list_image_paths(images_dir: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    Returns a sorted list of full file paths for all image files
    in `images_dir` matching the given extensions.
    """
    if not os.path.exists(images_dir):
        raise FileNotFoundError(f"Images directory not found: {images_dir}")
    
    if extensions is None:
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
    
    # Normalize extensions to lowercase
    extensions = [ext.lower() for ext in extensions]
    
    all_files = []
    
    try:
        for filename in os.listdir(images_dir):
            file_lower = filename.lower()
            if any(file_lower.endswith(ext) for ext in extensions):
                full_path = os.path.join(images_dir, filename)
                all_files.append(full_path)
        
        all_files.sort()
        print(f"📁 Found {len(all_files)} image files in {images_dir}")
        
        if len(all_files) == 0:
            print(f"⚠️  No image files found in {images_dir}")
            print(f"   Supported extensions: {extensions}")
        
        return all_files
        
    except Exception as e:
        raise ValueError(f"Error listing images in {images_dir}: {e}")


def load_dataset(
    images_dir: str,
    annotations_file: str
) -> List[Tuple[str, str]]:
    """
    Combines raw images + annotations into a list of (image_path, answer).
    Matches on filename without extension, so '001.png' pairs with key '001'.
    """
    print(f"🔄 Loading dataset...")
    print(f"   Images: {images_dir}")
    print(f"   Annotations: {annotations_file}")
    
    # Load annotations
    try:
        ann_map = load_annotations(annotations_file)
    except Exception as e:
        print(f"❌ Failed to load annotations: {e}")
        raise
    
    # Get image paths
    try:
        image_paths = list_image_paths(images_dir)
    except Exception as e:
        print(f"❌ Failed to list images: {e}")
        raise
    
    if not image_paths:
        raise ValueError(f"No images found in {images_dir}")
    
    # Match images with annotations
    dataset: List[Tuple[str, str]] = []
    matched_keys = set()
    
    for img_path in image_paths:
        filename = os.path.basename(img_path)
        key = os.path.splitext(filename)[0]  # Remove extension
        
        if key in ann_map:
            dataset.append((img_path, ann_map[key]))
            matched_keys.add(key)
        else:
            print(f"⚠️  No annotation found for image '{filename}' (key: '{key}')")
    
    # Check for annotations without matching images
    unmatched_annotations = set(ann_map.keys()) - matched_keys
    if unmatched_annotations:
        print(f"⚠️  {len(unmatched_annotations)} annotations have no matching images:")
        for key in sorted(list(unmatched_annotations)[:5]):  # Show first 5
            print(f"      {key}")
        if len(unmatched_annotations) > 5:
            print(f"      ... and {len(unmatched_annotations) - 5} more")
    
    if not dataset:
        raise ValueError(
            f"No matching image-annotation pairs found!\n"
            f"  Images found: {len(image_paths)}\n"
            f"  Annotations found: {len(ann_map)}\n"
            f"  Make sure image filenames (without extensions) match annotation keys."
        )
    
    print(f"✅ Successfully matched {len(dataset)} image-annotation pairs")
    return dataset


def validate_dataset(images_dir: str, annotations_file: str) -> Dict[str, any]:
    """
    Validate dataset without loading it fully. Returns validation info.
    """
    validation_info = {
        "images_dir_exists": os.path.exists(images_dir),
        "annotations_file_exists": os.path.exists(annotations_file),
        "image_count": 0,
        "annotation_count": 0,
        "matched_count": 0,
        "errors": []
    }
    
    try:
        if validation_info["images_dir_exists"]:
            image_paths = list_image_paths(images_dir)
            validation_info["image_count"] = len(image_paths)
        else:
            validation_info["errors"].append(f"Images directory not found: {images_dir}")
    
        if validation_info["annotations_file_exists"]:
            annotations = load_annotations(annotations_file)
            validation_info["annotation_count"] = len(annotations)
            
            if validation_info["images_dir_exists"]:
                # Check matches
                image_keys = {os.path.splitext(os.path.basename(p))[0] for p in image_paths}
                annotation_keys = set(annotations.keys())
                matched_keys = image_keys.intersection(annotation_keys)
                validation_info["matched_count"] = len(matched_keys)
        else:
            validation_info["errors"].append(f"Annotations file not found: {annotations_file}")
            
    except Exception as e:
        validation_info["errors"].append(str(e))
    
    return validation_info


if __name__ == "__main__":
    # Sanity check with validation
    print("🧪 Testing data loading...")
    
    images_dir = "data/raw/images"  # Point to your images
    annotations_file = "data/raw/annotations.csv"
    
    # First validate
    print("\n1️⃣ Validating dataset...")
    validation = validate_dataset(images_dir, annotations_file)
    
    print(f"   Images directory exists: {validation['images_dir_exists']}")
    print(f"   Annotations file exists: {validation['annotations_file_exists']}")
    print(f"   Image count: {validation['image_count']}")
    print(f"   Annotation count: {validation['annotation_count']}")
    print(f"   Matched pairs: {validation['matched_count']}")
    
    if validation["errors"]:
        print("   Errors:")
        for error in validation["errors"]:
            print(f"     - {error}")
    
    # Try to load if validation looks good
    if validation["matched_count"] > 0:
        print("\n2️⃣ Loading dataset...")
        try:
            dataset = load_dataset(images_dir, annotations_file)
            print(f"✅ Successfully loaded {len(dataset)} samples")
            
            # Show first few samples
            print("\n📋 Sample data:")
            for i, (img_path, answer) in enumerate(dataset[:3]):
                print(f"   {i+1}. {os.path.basename(img_path)} → {answer}")
            
            if len(dataset) > 3:
                print(f"   ... and {len(dataset) - 3} more")
                
        except Exception as e:
            print(f"❌ Failed to load dataset: {e}")
    else:
        print("\n⚠️  Cannot load dataset - no matched pairs found")
        print("   Make sure your images and annotations are properly set up")