#check new equipment is saved
def test_add_equipment(client):
    response = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 2
    })

    assert response.status_code == 201
    item = response.get_json()
    assert item["name"] == "Kayak"
    assert item["category"] == "Water"
    assert item["total_units"] == 2
    assert item["available_units"] == 2

    saved = client.get(f"/equipment/{item['id']}")
    assert saved.status_code == 200
    assert saved.get_json() == item


#check the list shows both items with different ids
def test_equipment_list_contains_added_items(client):
    first = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 1
    }).get_json()

    second = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    }).get_json()
    response = client.get("/equipment")

    assert response.status_code == 200
    items = response.get_json()
    assert len(items) == 2
    assert first in items
    assert second in items
    assert first["id"] != second["id"]


#check an unknown id
def test_get_unknown_equipment_returns_404(client):
    response = client.get("/equipment/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Equipment not found"


#check changes are saved, category stay the same
def test_update_equipment_saves_changes(client):
    item = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    }).get_json()

    response = client.put(f"/equipment/{item['id']}", json={
        "name": "Large Tent",
        "total_units": 3,
        "available_units": 3
    })

    assert response.status_code == 200
    saved = client.get(f"/equipment/{item['id']}").get_json()
    assert saved["name"] == "Large Tent"
    assert saved["total_units"] == 3
    assert saved["available_units"] == 3
    assert saved["category"] == "Camping"


#check deleted equipment is no longer stored
def test_delete_equipment_removes_item(client):
    item = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 1
    }).get_json()

    response = client.delete(f"/equipment/{item['id']}")

    assert response.status_code == 204
    assert client.get(f"/equipment/{item['id']}").status_code == 404
    assert client.get("/equipment").get_json() == []