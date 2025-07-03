import sqlite3
from flask import Flask, g, render_template
from datetime import date

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("sqlite.db")
    return g.db


def close_db():
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods = ["GET"])
def database():
    db = get_db()
    today = str(date.today())

    cur = db.execute("SELECT * FROM events")

    table = cur.fetchall()
    close_db()
    tag = ["ID", "event", "date", "place"]
    return render_template("a7-1.html", message = "日本のまつり", tag = tag, table = table, today = today)

@app.route("/", methods = ["POST"])

if __name__ == "__main__":
    app.debug = True
    app.run(host="localhost")