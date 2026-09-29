from pathlib import Path
from PIL import Image

ROOT = Path("dataset")

valid_extensions = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
}

bad_files = []

for file in ROOT.rglob("*"):

    if not file.is_file():
        continue

    if file.suffix.lower() not in valid_extensions:
        print("SKIP:", file)
        continue

    try:

        with Image.open(file) as img:
            img.verify()

    except Exception as e:

        bad_files.append(file)

        print("\nBAD IMAGE:")
        print(file)
        print("ERROR:", e)


print("\n====================")

if bad_files:

    print(
        f"Found {len(bad_files)} bad image(s)."
    )

else:

    print(
        "All image files look valid."
    )