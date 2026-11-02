from datetime import date
from flask import Blueprint, jsonify
from app import store

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


#show only rentals that have not been returned
@reports_bp.route("/current-rentals", methods=["GET"])
def current_rentals_report():
    results = []
    for rental in store.rentals.values():
        if rental.return_date is None:
            results.append(rental.to_dict())
    return jsonify(results)


#show unreturned rentals whose due date has passed
@reports_bp.route("/overdue-rentals", methods=["GET"])
def overdue_rentals_report():
    results = []
    today = date.today()
    for rental in store.rentals.values():
        if rental.return_date is None and rental.due_date < today:
            results.append(rental.to_dict())
    return jsonify(results)