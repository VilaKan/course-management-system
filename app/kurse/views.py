from flask import Blueprint, render_template

kurse_bp = Blueprint("kurse", __name__, template_folder="pages")

@kurse_bp.route("/kurse")
def kurse_list():
    # Hier später echte Kursdaten einfügen
    kurse = []
    return render_template("list.html", kurse=kurse)
