import json, os
from PIL import Image

ann = json.load(open("bdd100k_labels_images_det_coco.json"))
for item in ann:
    img_name = item['image_id'] + '.jpg'
    w,h = Image.open(f"images/{img_name}").size
    lines = []
    for obj in item['objects']:
        cls = map_bdd_to_yolo(obj['category'])
        x1,y1,x2,y2 = obj['bbox']  # adjust if COCO bbox (x,y,w,h)
        # convert to x_center y_center w h normalized
        xc = (x1 + x2) / 2 / w
        yc = (y1 + y2) / 2 / h
        w_norm = (x2 - x1) / w
        h_norm = (y2 - y1) / h
        lines.append(f"{cls} {xc} {yc} {w_norm} {h_norm}")
    with open(f"labels/{img_name.replace('.jpg','.txt')}","w") as f:
        f.write("\n".join(lines))
