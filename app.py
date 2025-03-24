import json
from flask import Flask, render_template, request, redirect, jsonify
import firebase_admin
from firebase_admin import credentials, db
import os

# Flask setup
app = Flask(__name__)

# Firebase Admin SDK setup
cred = credentials.Certificate("/etc/secrets/firebase.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://giannantonio-fundraiser-default-rtdb.firebaseio.com/"  # Replace with your DB URL
})

GOAL_AMOUNT = 20000

def get_donations():
    ref = db.reference("/donations")
    data = ref.get() or {}
    entries = []
    total = 0

    for key, value in data.items():
        try:
            amount = float(value.get("amount", 0))
            total += amount
            entries.append({
                "id": key,
                "name": value.get("name", ""),
                "company": value.get("company", ""),
                "amount": amount,
                "password": value.get("password", "")
            })
        except Exception:
            continue

    return total, entries

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        company = request.form.get("company", "").strip()
        amount = request.form.get("amount", "").strip()
        password = request.form.get("password", "").strip()

        if name and amount:
            try:
                amount = float(amount)
                ref = db.reference("/donations")
                ref.push({
                    "name": name,
                    "company": company,
                    "amount": amount,
                    "password": password
                })
            except ValueError:
                pass
        return redirect("/")

    total, entries = get_donations()
    percentage = int(min((total / GOAL_AMOUNT) * 100, 100))
    latest_donor = entries[-1]["name"] if entries else "No donations yet"
    latest_company = entries[-1]["company"] if entries and entries[-1]["company"] else "N/A"

    return render_template("index.html", total=total, goal=GOAL_AMOUNT,
                           percentage=percentage, latest_donor=latest_donor,
                           latest_company=latest_company, entries=entries)

@app.route("/edit", methods=["POST"])
def edit_donation():
    data = request.json
    donation_id = data["id"]
    name = data["name"].strip()
    company = data["company"].strip()
    amount = data["amount"]
    password = data["password"].strip()

    ref = db.reference(f"/donations/{donation_id}")
    donation = ref.get()

    if donation and donation.get("password", "") == password:
        try:
            ref.update({
                "name": name,
                "company": company,
                "amount": float(amount)
            })
            return jsonify(success=True)
        except ValueError:
            return jsonify(success=False, error="Invalid amount")
    else:
        return jsonify(success=False, error="Incorrect password")

@app.route("/delete/<donation_id>", methods=["POST"])
def delete_donation(donation_id):
    data = request.json
    password = data.get("password", "").strip()

    ref = db.reference(f"/donations/{donation_id}")
    donation = ref.get()

    if donation and donation.get("password", "") == password:
        ref.delete()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Incorrect password")

if __name__ == "__main__":
    app.run(debug=True)



# from flask import Flask, render_template, request, redirect, jsonify
# import csv
# import json

# app = Flask(__name__)
# CSV_FILE = "donations.csv"
# GOAL_AMOUNT = 20000  # Fundraising goal

# def read_donations():
#     """Read donations from the CSV file."""
#     total = 0
#     entries = []
#     try:
#         with open(CSV_FILE, "r", newline="") as f:
#             reader = csv.reader(f)
#             for i, row in enumerate(reader):
#                 if len(row) == 4:  # Ensure correct row format
#                     name, company, amount, password = row
#                     try:
#                         amount = float(amount)
#                         total += amount
#                         entries.append({
#                             "id": i,
#                             "name": name,
#                             "company": company,
#                             "amount": amount,
#                             "password": password
#                         })
#                     except ValueError:
#                         continue  # Skip invalid data
#     except FileNotFoundError:
#         pass
#     return total, entries

# def save_donation(name, company, amount, password):
#     """Save a new donation to the CSV file."""
#     with open(CSV_FILE, "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([name, company, amount, password])

# def write_donations(entries):
#     """Rewrite the entire donation file (used for edits & deletes)."""
#     with open(CSV_FILE, "w", newline="") as f:
#         writer = csv.writer(f)
#         for entry in entries:
#             writer.writerow([entry["name"], entry["company"], entry["amount"], entry["password"]])

# @app.route("/", methods=["GET", "POST"])
# def index():
#     """Render the donation page and handle new donations."""
#     if request.method == "POST":
#         name = request.form.get("name", "").strip()
#         company = request.form.get("company", "").strip()
#         amount = request.form.get("amount", "").strip()
#         password = request.form.get("password", "").strip()

#         if name and amount:
#             try:
#                 amount = float(amount)
#                 save_donation(name, company, amount, password)
#             except ValueError:
#                 pass  # Ignore invalid inputs
#         return redirect("/")

#     total, entries = read_donations()
#     percentage = int(min((total / GOAL_AMOUNT) * 100, 100))  # Cap progress at 100%
#     latest_donor = entries[-1]["name"] if entries else "No donations yet"
#     latest_company = entries[-1]["company"] if entries and entries[-1]["company"] else "N/A"

#     return render_template("index.html", total=total, goal=GOAL_AMOUNT, percentage=percentage, latest_donor=latest_donor, latest_company=latest_company, entries=entries)

# @app.route("/edit", methods=["POST"])
# def edit_donation():
#     """Edit a donation after verifying the password."""
#     data = request.json
#     donation_id = int(data["id"])
#     new_name = data["name"].strip()
#     new_company = data["company"].strip()
#     new_amount = data["amount"].strip()
#     password = data["password"].strip()

#     total, entries = read_donations()
    
#     for entry in entries:
#         if entry["id"] == donation_id and entry["password"] == password:
#             try:
#                 entry["name"] = new_name
#                 entry["company"] = new_company
#                 entry["amount"] = float(new_amount)
#                 write_donations(entries)
#                 return jsonify(success=True)
#             except ValueError:
#                 return jsonify(success=False, error="Invalid amount")

#     return jsonify(success=False, error="Incorrect password")

# @app.route("/delete/<int:id>", methods=["POST"])
# def delete_donation(id):
#     """Delete a donation after verifying the password."""
#     data = request.json
#     password = data.get("password", "").strip()

#     total, entries = read_donations()
#     updated_entries = [entry for entry in entries if not (entry["id"] == id and entry["password"] == password)]

#     if len(updated_entries) < len(entries):  # If an entry was removed
#         write_donations(updated_entries)
#         return jsonify(success=True)
    
#     return jsonify(success=False, error="Incorrect password")

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)
