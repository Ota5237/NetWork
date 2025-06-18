import os
from flask import Flask, render_template, request, g
import cv2
from ultralytics import YOLO
import sqlite3
from PIL import Image


model = YOLO("yolo11x.pt")
app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("sqlite.db")
    return g.db


def close_db():
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def input():
    return render_template("a5-2.html")

@app.route("/", methods=["POST"])
def upload():
    file = request.files["file"]
    save_name = os.path.join(file.filename)
    save_path = os.path.join("static", file.filename)
    file.save(save_path)

    try:
        with Image.open(save_path) as im:
            exif = im.getexif()

        exif_dict = exif.get_ifd(0x8769)  # Exif情報の取得
        gps_dict = exif.get_ifd(0x8825)  # GPS情報の取得

        dd_lat = gps_dict[2][0] + float(gps_dict[2][1]) / 60 + float(gps_dict[2][2]) / 3600
        dd_lon = gps_dict[4][0] + float(gps_dict[4][1]) / 60 + float(gps_dict[4][2]) / 3600

        if gps_dict[1] == 'S':
            dd_lat = -dd_lat
        if gps_dict[3] == 'W':
            dd_lon = -dd_lon
        date = exif_dict[0x9003]
        place = "{}, {}".format(dd_lat, dd_lon)
    except:
        date = "None"
        place = "None"

    inImage = cv2.imread(save_path)
    results = model(inImage, conf=0.2)
    boxes = results[0].boxes

    object_list = ""

    for box in boxes:
        id = int(box.cls[0])
        object_name = model.names[id]
        if object_list == "":
            object_list = object_name
        else:
            object_list += ", " + object_name
    
    if object_list == "":
        object_list = "None"

    db = get_db()
    db.execute("INSERT INTO images (file_name, date, place, object) VALUES(:file, :date, :place, :object)", {"file": save_name, "date": date, "place": place, "object": object_list})
    db.commit()

    cur = db.execute("SELECT * FROM images")
    table = cur.fetchall()
    close_db()
    tag = ["id", "file name", "date", "place", "object"]

    return render_template("a5-2.html", tag=tag, table=table)

if __name__ == "__main__":
    app.debug = True
    app.run(host="localhost")
