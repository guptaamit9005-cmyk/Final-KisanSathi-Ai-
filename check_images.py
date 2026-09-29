
from pathlib import Path
from PIL import Image


DATASET = Path("dataset")

VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
}

images = [
    p
    for p in DATASET.rglob("*")
    if p.is_file()
    and p.suffix.lower() in VALID_EXTENSIONS
]

print("=" * 60)
print("AGRIVISION AI - IMAGE CHECK")
print("=" * 60)

print(f"\nTotal image files: {len(images)}\n")

bad_images = []

for image_path in images:

    try:
        with Image.open(image_path) as img:
            img.verify()

        print(f"OK  | {image_path}")

    except Exception as error:

        print(f"BAD | {image_path}")
        print(f"     {error}")

        bad_images.append(image_path)


print("\n" + "=" * 60)

if bad_images:

    print(
        f"BAD IMAGES FOUND: {len(bad_images)}"
    )

    print("\nProblem files:")

    for image in bad_images:
        print(image)

else:

    print("ALL IMAGES ARE VALID.")

print("=" * 60)

