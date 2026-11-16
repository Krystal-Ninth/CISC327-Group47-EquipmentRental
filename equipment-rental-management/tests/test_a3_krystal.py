from datetime import date
from unittest.mock import patch


def create_checkout(client):
    equipment = client.post("/equipment", json={
        "name": "Kayak", "category": "Water", "total_units": 1
    })
    assert equipment.status_code == 201
    equipment_id = equipment.get_json()["id"]
    renter = client.post("/renters", json={
        "name": "Renter A", "email": "renter@example.com"
    })
    assert renter.status_code == 201
    rental = client.post("/rentals", json={
        "equipment_id": equipment_id, "renter_id": renter.get_json()["id"]
    })
    assert rental.status_code == 201
    return rental.get_json()["id"], equipment_id


def test_return_succeeds_with_notification_stub(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.rentals.send_notification",
        lambda recipient, subject, message: True,
    )
    rental_id, equipment_id = create_checkout(client)

    response = client.put(f"/rentals/{rental_id}/return")

    assert response.status_code == 200
    assert response.headers["X-Return-Notification"] == "sent"
    assert response.get_json()["return_date"] == date.today().isoformat()
    assert client.get("/rentals").get_json() == [response.get_json()]
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 1


def test_return_sends_expected_confirmation(client):
    rental_id, _ = create_checkout(client)

    with patch("app.routes.rentals.send_notification", return_value=True) as send:
        response = client.put(f"/rentals/{rental_id}/return")

    assert response.status_code == 200
    assert response.get_json()["return_date"] == date.today().isoformat()
    assert client.get("/rentals").get_json() == [response.get_json()]
    send.assert_called_once_with(
        "renter@example.com",
        "[Group 47 Equipment Rental] Return confirmed",
        f"Your return for rental #{rental_id} was recorded.",
    )


def test_home_links_to_management_pages(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Equipment Rental Management" in response.data
    for path in (b"/ui/equipment", b"/ui/renters", b"/ui/rentals"):
        assert b'href="' + path + b'"' in response.data


def test_equipment_can_be_added_and_deleted_from_web_page(client):
    added = client.post("/ui/equipment", data={
        "name": "Camp Lantern", "category": "Camping", "total_units": 2
    }, follow_redirects=True)
    assert added.status_code == 200
    assert b"Camp Lantern" in added.data
    items = client.get("/equipment").get_json()
    assert len(items) == 1
    assert items[0]["name"] == "Camp Lantern"
    assert items[0]["available_units"] == 2

    deleted = client.post(
        f"/ui/equipment/{items[0]['id']}/delete", follow_redirects=True
    )
    assert deleted.status_code == 200
    assert b"Camp Lantern" not in deleted.data
    assert client.get("/equipment").get_json() == []


def test_web_return_restores_stock_only_once(client):
    rental_id, equipment_id = create_checkout(client)

    for _ in range(2):
        response = client.post(f"/ui/rentals/{rental_id}/return")
        assert response.status_code == 302
        assert response.headers["Location"] == "/ui/rentals"
        rental = client.get("/rentals").get_json()[0]
        assert rental["return_date"] == date.today().isoformat()
        assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 1


def test_update_unknown_equipment_does_not_create_record(client):
    response = client.put("/equipment/999", json={"name": "Tent"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Equipment not found"}
    assert client.get("/equipment").get_json() == []


def test_delete_unknown_equipment_leaves_existing_item(client):
    created = client.post("/equipment", json={"name": "Tent", "category": "Camping"})
    assert created.status_code == 201

    response = client.delete("/equipment/999")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Equipment not found"}
    assert client.get("/equipment").get_json() == [created.get_json()]


def test_return_unknown_rental_does_not_create_record(client):
    response = client.put("/rentals/999/return")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Rental not found"}
    assert client.get("/rentals").get_json() == []


def test_returning_same_rental_twice_does_not_restore_stock_twice(client):
    rental_id, equipment_id = create_checkout(client)
    first = client.put(f"/rentals/{rental_id}/return")
    assert first.status_code == 200

    response = client.put(f"/rentals/{rental_id}/return")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Rental already returned"}
    assert client.get("/rentals").get_json() == [first.get_json()]
    assert client.get(f"/equipment/{equipment_id}").get_json()["available_units"] == 1
