from datetime import date
from unittest.mock import patch

def create_rental(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak", "category": "Water", "total_units": 2
    })
    assert equipment.status_code == 201
    equipment_id = equipment.get_json()["id"]

    renter = client.post("/renters", json={
        "name": "Renter A", "email": "renterA@example.com"
    })
    assert renter.status_code == 201
    renter_id = renter.get_json()["id"]

    rental = client.post("/rentals", json={
        "equipment_id": equipment_id, "renter_id": renter_id
    })
    assert rental.status_code == 201
    return rental.get_json()["id"], equipment_id, renter_id

# --- Member B: Notification Failure & Non-Trigger Paths ---
def test_return_succeeds_when_notification_fails_stub(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.rentals.send_notification",
        lambda recipient, subject, message: False,
    )
    rental_id, equipment_id, renter_id = create_rental(client)

    response = client.put(f"/rentals/{rental_id}/return")

    assert response.status_code == 200
    assert response.headers["X-Return-Notification"] == "not-sent"
    assert response.get_json()["return_date"] == date.today().isoformat()
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 2


def test_notification_not_sent_on_invalid_return_or_non_return_routes_mock(client):
    with patch("app.routes.rentals.send_notification") as mock_send:
        #Non-trigger: checkout and extend do not send return confirmation
        rental_id, equipment_id, renter_id = create_rental(client)
        extend_res = client.put(f"/rentals/{rental_id}/extend", json={"days": 3})
        assert extend_res.status_code == 200
        mock_send.assert_not_called()

        #Failure path: returning an unknown rental does not send notification
        missing_res = client.put("/rentals/967/return")
        assert missing_res.status_code == 404
        mock_send.assert_not_called()

        #Failure path: returning an already-returned rental does not re-send
        first_return = client.put(f"/rentals/{rental_id}/return")
        assert first_return.status_code == 200
        assert mock_send.call_count == 1

        duplicate_return = client.put(f"/rentals/{rental_id}/return")
        assert duplicate_return.status_code == 400
        assert mock_send.call_count == 1

# --- Coverage-Directed Tests ---

