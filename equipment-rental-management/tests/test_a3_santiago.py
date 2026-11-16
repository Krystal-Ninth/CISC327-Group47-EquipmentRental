from datetime import date
from unittest.mock import patch

#creates generic rental 
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
#Checks the return when a notification fails to send 
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

#Checks that a notification is not sent during non-return actions or failed return requests 
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

#Tests that when Equipment is out of stock it gives an error
def test_checkout_out_of_stock_equipment(client):
    rental_id, equipment_id, renter_id = create_rental(client)

    second = client.post("/rentals", json={
        "equipment_id": equipment_id, "renter_id": renter_id
    })
    assert second.status_code == 201

    third = client.post("/rentals", json={
            "equipment_id": equipment_id, "renter_id": renter_id
        })
    assert third.status_code == 400
    assert third.get_json() == {"error": "Equipment is out of stock / completely checked out"}

#test that updating and deleting an unknown renter gives an error
def test_update_and_delete_unknown_renter(client):
    update_res = client.put("/renters/967", json={"name": "idk"})
    assert update_res.status_code == 404
    assert update_res.get_json() == {"error": "Renter not found"}

    delete_res = client.delete("/renters/967")
    assert delete_res.status_code == 404
    assert delete_res.get_json() == {"error": "Renter not found"}


#tests adding and deleting renters on web page
def test_renters_web_page_add_and_delete(client):
    added = client.post(
        "/ui/renters",
        data={"name": "Michael Jordan ", "email": "jordan@example.com"},
        follow_redirects=True,
    )
    assert added.status_code == 200
    assert b"Michael Jordan" in added.data

    renters = client.get("/renters").get_json()
    assert len(renters) == 1
    renter_id = renters[0]["id"]

    deleted = client.post(f"/ui/renters/{renter_id}/delete", follow_redirects=True)
    assert deleted.status_code == 200
    assert b"Michael Jordan" not in deleted.data
    assert client.get("/renters").get_json() == []

#test web page that a valid web checkout and tests the missing equipment branch
def test_rentals_web_page_checkout_and_missing_equipment(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak", "category": "Water", "total_units": 2
    }).get_json()
    renter = client.post("/renters", json={
        "name": "Renter A", "email": "renterA@example.com"
    }).get_json()

    invalid_post = client.post(
        "/ui/rentals",
        data={"equipment_id": 967, "renter_id": renter["id"]},
        follow_redirects=True,
    )
    assert invalid_post.status_code == 200
    assert client.get("/rentals").get_json() == []

    valid_post = client.post(
        "/ui/rentals",
        data={"equipment_id": equipment["id"], "renter_id": renter["id"]},
        follow_redirects=True,
    )
    assert valid_post.status_code == 200
    rentals = client.get("/rentals").get_json()
    assert len(rentals) == 1
    assert client.get(f"/equipment/{equipment['id']}").get_json()["available_units"] == 1
