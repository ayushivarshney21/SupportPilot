"""SupportPilot - AI Ticket Resolution Agent (Milestone 1)
Web application: ticket intake, classification, severity and priority."""
import json
from flask import Flask, request, redirect, url_for, render_template, abort, send_from_directory
import config
import database
from pipeline import process_ticket

app = Flask(__name__)
database.init_db()

DEPARTMENTS = ["Sales", "Marketing", "Finance", "Human Resources", "Engineering", "Operations", "Legal"]


@app.get("/")
def index():
    return render_template("submit.html", departments=DEPARTMENTS, form={})


@app.post("/submit")
def submit():
    form = {k: request.form.get(k, "").strip() for k in
            ("employee", "email", "department", "title", "description")}
    if not all(form.values()):
        return render_template("submit.html", departments=DEPARTMENTS, form=form,
                               error="All fields are required."), 400
    ticket = database.ingest(form["employee"], form["email"], form["title"],
                             form["description"], form["department"])
    print("Ingested ticket JSON:\n", json.dumps(ticket, indent=2))
    result = process_ticket(ticket["title"] + ". " + ticket["description"])
    database.save_ticket(ticket, result)
    return redirect(url_for("show_ticket", ticket_id=ticket["ticket_id"]))


@app.get("/ticket/<ticket_id>")
def show_ticket(ticket_id):
    return render_template("ticket.html", t=database.get_ticket(ticket_id) or abort(404))


@app.get("/tickets")
def tickets():
    return render_template("queue.html", tickets=database.all_tickets(), stats=database.stats())


@app.get("/model")
def model_page():
    lines = config.REPORT_PATH.read_text().splitlines() if config.REPORT_PATH.exists() else []
    metrics = dict(l.split(": ", 1) for l in lines[:2] if ": " in l)
    return render_template("model.html", metrics=metrics, report="\n".join(lines[3:]),
                           has_matrix=config.CONFUSION_PATH.exists())


@app.get("/model/confusion-matrix.png")
def confusion_matrix_image():
    return send_from_directory(config.MODEL_DIR, config.CONFUSION_PATH.name)


if __name__ == "__main__":
    app.run(debug=True)
