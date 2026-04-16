import sqlite3
from flask import Flask, jsonify, request, g, render_template

app = Flask(__name__)
DATABASE = "items.db"


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            description TEXT
        )
        """
    )
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Web interface route
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# CRUD routes  –  /items
# ---------------------------------------------------------------------------

# CREATE  POST /items
@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True)
    if not data or not data.get("name"):
        return jsonify({"error": "Field 'name' is required"}), 400

    db = get_db()
    cursor = db.execute(
        "INSERT INTO items (name, description) VALUES (?, ?)",
        (data["name"], data.get("description")),
    )
    db.commit()
    return jsonify({"id": cursor.lastrowid, "name": data["name"], "description": data.get("description")}), 201


# READ ALL  GET /items
@app.route("/items", methods=["GET"])
def get_items():
    rows = get_db().execute("SELECT * FROM items").fetchall()
    return jsonify([dict(row) for row in rows])


# READ ONE  GET /items/<id>
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    row = get_db().execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(dict(row))


# UPDATE  PUT /items/<id>
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    db = get_db()
    row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True) or {}
    name = data.get("name", row["name"])
    description = data.get("description", row["description"])

    db.execute(
        "UPDATE items SET name = ?, description = ? WHERE id = ?",
        (name, description, item_id),
    )
    db.commit()
    return jsonify({"id": item_id, "name": name, "description": description})


# DELETE  DELETE /items/<id>
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    db = get_db()
    row = db.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        return jsonify({"error": "Item not found"}), 404

    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    db.commit()
    return jsonify({"message": f"Item {item_id} deleted"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=80, debug=True)
