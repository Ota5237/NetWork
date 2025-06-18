import sqlite3
import os
from ultralytics import YOLO
from flask import Flask, render_template, request, g
from PIL import Image

app = Flask(__name__)
model = YOLO("yolo11x.pt")

def get_db():
    if "db" not in g:
        # gはリクエストごとに用意されるFlaskのオブジェクト
        # gに"db"が含まれていない場合にデータベースへの接続が行われる．
        g.db = sqlite3.connect("sqlite.db")
        # データベースへの接続
    return g.db

def close_db():
    db = g.pop("db", None)
    # gから"db"を取り出す．
    if db is not None:
        # gに"db"が含まれていた場合にはデータベースとの接続を終了する．
        db.close()
        # データベースの接続終了

@app.route("/", methods=["GET", "POST"])
# POSTメソッドでのアクセスは以下が実行される．
def upload():
    if request.method == "POST":
        file = request.files["file"]
        save_path = os.path.join("static", file.filename)
        file.save(save_path)

        results = model(save_path)

    # 認識した元画像
        boxes = results[0].boxes
    # 認識した物体領域を取得する．

        obj_names = []
        for box in boxes:
            cls_id = int(box.cls[0].item())
            name = model.names.get(cls_id, str(cls_id))
            obj_names.append(name)
        objects = ", ".join(obj_names)

        try:
            with Image.open(save_path) as im:
                exif = im.getexif()
            exif_dict = exif.get_ifd(0x8769)
            gps_dict = exif.get_ifd(0x8825)

            dd_lat = gps_dict[2][0] + float(gps_dict[2][1]) / 60 + float(gps_dict[2][2]) / 3600
            dd_lon = gps_dict[4][0] + float(gps_dict[4][1]) / 60 + float(gps_dict[4][2]) / 3600

            if gps_dict[1] == "S":
                dd_lat = -dd_lat
            if gps_dict[3] == "W":
                dd_lon = -dd_lon
            
            date = exif_dict[0x9003]
            location = "{}, {}".format(dd_lat, dd_lon)
        except:
            date = ""
            location = ""


        db = get_db()
        db.execute(
        "INSERT INTO images (file_name, object, date, place) VALUES (?, ?, ?, ?)",
        (file.filename, objects, date, location)
        )

        db.commit()

    db = get_db()
    data = db.execute("SELECT * FROM images").fetchall()
    return render_template("kento.html", data=data)


if __name__ == "__main__":
    app.debug = True
    app.run(host="localhost")