from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)
app.secret_key = "bloodbank"

# =========================
# BLOOD PRICE LIST
# =========================
BLOOD_PRICES = {
    "A+": 1200, "A-": 1500,
    "B+": 1200, "B-": 1500,
    "AB+": 1800, "AB-": 2200,
    "O+": 1000, "O-": 2000
}

# =========================
# SQL SERVER CONNECTION
# =========================
conn = pyodbc.connect(
    "DRIVER={SQL Server};"
    "SERVER=localhost\SQLEXPRESS;"
    "DATABASE=blood_bank;"
 )

# =========================
# HOME PAGE
# =========================
@app.route("/")
def index():
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, blood_group, contact FROM donors")
    donors = cursor.fetchall()

    cursor.execute("SELECT blood_group, units, amount FROM blood_stock")
    stock = cursor.fetchall()

    cursor.execute("""
        SELECT blood_group, SUM(units)
        FROM monthly_donations
        WHERE donation_date >= DATEADD(DAY, -30, GETDATE())
        GROUP BY blood_group
    """)
    monthly_donations = cursor.fetchall()

    cursor.execute("""
        SELECT blood_group, SUM(units), SUM(total_amount)
        FROM monthly_issued
        WHERE issue_date >= DATEADD(DAY, -30, GETDATE())
        GROUP BY blood_group
    """)
    monthly_issued = cursor.fetchall()

    return render_template(
        "index.html",
        donors=donors,
        stock=stock,
        monthly_donations=monthly_donations,
        monthly_issued=monthly_issued
    )

# =========================
# ADD DONOR
# =========================
@app.route("/add_donor", methods=["POST"])
def add_donor():
    cursor = conn.cursor()

    name = request.form["name"]
    age = request.form["age"]
    blood_group = request.form["blood_group"].upper()
    contact = request.form["contact"]

    price = BLOOD_PRICES.get(blood_group, 1000)

    cursor.execute(
        "INSERT INTO donors (name, age, blood_group, contact) VALUES (?, ?, ?, ?)",
        (name, age, blood_group, contact)
    )

    cursor.execute("SELECT units FROM blood_stock WHERE blood_group = ?", (blood_group,))
    stock = cursor.fetchone()

    if stock:
        cursor.execute(
            "UPDATE blood_stock SET units = units + 1 WHERE blood_group = ?",
            (blood_group,)
        )
    else:
        cursor.execute(
            "INSERT INTO blood_stock (blood_group, units, amount) VALUES (?, ?, ?)",
            (blood_group, 1, price)
        )

    cursor.execute(
        "INSERT INTO monthly_donations (blood_group, units, donation_date) VALUES (?, ?, GETDATE())",
        (blood_group, 1)
    )

    conn.commit()
    return redirect(url_for("index"))

# =========================
# DELETE DONOR
# =========================
@app.route("/delete_donor", methods=["POST"])
def delete_donor():
    cursor = conn.cursor()
    donor_id = request.form["donor_id"]
    cursor.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
    conn.commit()
    return redirect(url_for("index"))

# =========================
# ADD STOCK
# =========================
@app.route("/add_stock", methods=["POST"])
def add_stock():
    cursor = conn.cursor()

    blood_group = request.form["blood_group"].upper()
    units = int(request.form["units"])
    price = BLOOD_PRICES.get(blood_group, 1000)

    cursor.execute("SELECT units FROM blood_stock WHERE blood_group = ?", (blood_group,))
    stock = cursor.fetchone()

    if stock:
        cursor.execute(
            "UPDATE blood_stock SET units = units + ? WHERE blood_group = ?",
            (units, blood_group)
        )
    else:
        cursor.execute(
            "INSERT INTO blood_stock (blood_group, units, amount) VALUES (?, ?, ?)",
            (blood_group, units, price)
        )

    cursor.execute(
        "INSERT INTO monthly_donations (blood_group, units, donation_date) VALUES (?, ?, GETDATE())",
        (blood_group, units)
    )

    conn.commit()
    return redirect(url_for("index"))

# =========================
# ISSUE BLOOD WITH PRICE
# =========================
@app.route("/give_blood", methods=["POST"])
def give_blood():
    cursor = conn.cursor()

    blood_group = request.form["blood_group"].upper()
    units = int(request.form["units"])

    cursor.execute(
        "SELECT units, amount FROM blood_stock WHERE blood_group = ?",
        (blood_group,)
    )
    stock = cursor.fetchone()

    if not stock or stock.units < units:
        return "Not enough stock"

    total_amount = stock.amount * units

    cursor.execute(
        "UPDATE blood_stock SET units = units - ? WHERE blood_group = ?",
        (units, blood_group)
    )

    # Delete blood group if units become 0 or less
    cursor.execute(
        "DELETE FROM blood_stock WHERE blood_group = ? AND units <= 0",
        (blood_group,)
    )

    cursor.execute(
        "INSERT INTO monthly_issued (blood_group, units, total_amount, issue_date) VALUES (?, ?, ?, GETDATE())",
        (blood_group, units, total_amount)
    )

    conn.commit()
    return redirect(url_for("index"))

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)
