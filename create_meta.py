from pathlib import Path
from yaml import safe_dump
import csv

def create_meta(csv_path):
     with open(csv_path) as _file:
        for csv_line in list(csv.reader(_file, delimiter=",")):
            meta = {
            "title": csv_line[0],
            "author": csv_line[1],
            "translator": csv_line[2],
            "publisher": csv_line[3],
            "volumes": csv_line[4],
            "total_pages": csv_line[5],
            "language": csv_line[6],
            "copyright": csv_line[7],
            "publish_date": csv_line[8],
            "page_per_image": csv_line[10]
            }
            title = csv_line[0]
            meta_path = Path(f"./data/{title}")
            meta_path.mkdir(parents=True, exist_ok=True)
            with open(Path(f"{meta_path}/meta.yml"), 'w') as file:
                safe_dump(meta, file, encoding='utf-8')
            

if __name__ == "__main__":
    csv_path = Path("./non-bdrc.csv")
    create_meta(csv_path)