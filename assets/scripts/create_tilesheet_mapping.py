from typing import Optional
import os
from PIL import Image


def main() -> None:
    base_dir = r"X:\Coding\Personal\Python\Games\untitled_rpg\assets\graphics"
    files = {
        f"{base_dir}\\16x16 Dungeon Autotile Remix Walls.png": "wall",
        f"{base_dir}\\16x16 Dungeon Autotile Remix Floors.png": "floor",
    }
    for filepath, base_name in files.items():
        _d, _f = os.path.split(filepath)
        _n, _e = os.path.splitext(_f)
        out_file = os.path.join(_d, _n + ".txt")
        create_mapping(filepath, base_name, out_file=out_file)


def create_mapping(
    filename: str,
    name: str,
    tile_width: Optional[int] = 32,
    tile_height: Optional[int] = None,
    out_file: Optional[str] = None,
) -> list:
    if name[-1] == "_":
        name = name[:-1]

    if not tile_height:
        tile_height = tile_width

    lines = []
    image = Image.open(filename)
    image_width, image_height = image.size
    index = 0
    cols = int(image_width // tile_width)
    rows = int(image_height // tile_height)
    for col in range(cols):
        for row in range(rows):
            x = col * tile_width
            y = row * tile_height
            lines.append(
                " ".join(
                    [
                        str(_)
                        for _ in [name + f"_{index}", x, y, tile_width, tile_height]
                    ]
                )
                + "\n"
            )
            index += 1

    if out_file:
        with open(out_file, "w") as fp:
            fp.writelines(lines)

    return lines


if __name__ == "__main__":
    main()
