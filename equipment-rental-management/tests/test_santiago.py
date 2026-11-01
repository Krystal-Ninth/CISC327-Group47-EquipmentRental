from datetime import date, timedelta
def test_add_renter(client):
    response = client.post("/renters", json={
        "name": "RenterA",
        "email": "rentera@example.com"
    })

    assert response.status_code == 201
    renter = response.get_json()
    assert renter["id"] == 1
    assert renter["name"] == "RenterA"
    assert renter["email"] == "rentera@example.com"
    assert renter["membership_date"] == date.today().isoformat()

def test_view_renter_ID(client):
    response = client.post("/renters", json={
        "name": "RenterA",
        "email": "rentera@example.com"
    })

    assert response.status_code == 201
    renter = response.get_json()
    assert renter["id"] == 1
    assert renter["name"] == "RenterA"
    assert renter["email"] == "rentera@example.com"
    assert renter["membership_date"] == date.today().isoformat()

    saved = client.get(f"/renters/{renter['id']}")
    assert saved.status_code == 200
    assert saved.get_json() == renter    

def test_delete_renter(client):
    response = client.post("/renters", json={
            "name": "RenterA",
            "email": "rentera@example.com"
        })
    
    assert response.status_code == 201
    renter = response.get_json()
    renter_ID = renter["id"]
    delete_response = client.delete(f"/renters/{renter_ID}")
    assert delete_response.status_code in [200, 204]
    verify_response = client.get(f"/renters/{renter_ID}")
    assert verify_response.status_code == 404

def test_update_renter(client):
    response = client.post("/renters", json={
                "name": "RenterA",
                "email": "rentera@example.com"
            })
        
    assert response.status_code == 201
    renter = response.get_json()
    renter_ID = renter["id"]

    updated_response = client.put(f"/renters/{renter_ID}", json={
                "name": "RenterB",
                "email": "renterB@example.com"
            })
    assert updated_response.status_code == 200
    updated_renter = updated_response.get_json()
    assert updated_renter["id"] == renter_ID
    assert updated_renter["name"] == "RenterB"
    assert updated_renter["email"] == "renterB@example.com"
    assert updated_renter["membership_date"] == date.today().isoformat()

    saved = client.get(f"/renters/{renter_ID}")
    assert saved.status_code == 200
    assert saved.get_json() == updated_renter 

def test_view_renter_list(client):
    response1 = client.post("/renters", json={
                "name": "RenterA",
                "email": "rentera@example.com"
            })
    response2 = client.post("/renters", json={
                    "name": "RenterB",
                    "email": "renterB@example.com"
                })
    assert response1.status_code == 201
    assert response2.status_code == 201
    renter1 = response1.get_json()
    renter2 = response2.get_json()

    response_list = client.get("/renters")
    assert response_list.status_code == 200
    renters_list = response_list.get_json()

    assert isinstance(renters_list, list)
    assert len(renters_list) >= 2
    assert renter1 in renters_list
    assert renter2 in renters_list

def test_view_all_rentals(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()

    first = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 1
    })
    second = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    })

    response1 = client.post("/rentals", json={
            "equipment_id": 1,
            "renter_id": 1,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": 2,
            "renter_id": 2,
            "due_date": due_date_str,
            "deposit_amount": 75.0
            })
    assert response1.status_code == 201
    assert response2.status_code == 201
    rental1 = response1.get_json()
    rental2 = response2.get_json()

    response_list = client.get("/rentals")
    assert response_list.status_code == 200
    rentals_list = response_list.get_json()

    assert isinstance(rentals_list, list)
    assert len(rentals_list) >= 2
    assert rental1 in rentals_list
    assert rental2 in rentals_list    

def test_filter_rental_records_renter(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()

    first = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 1
    })
    second = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    })

    response1 = client.post("/rentals", json={
            "equipment_id": 1,
            "renter_id": 1,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": 2,
            "renter_id": 2,
            "due_date": due_date_str,
            "deposit_amount": 75.0
            })
    assert response1.status_code == 201
    assert response2.status_code == 201
    rental1 = response1.get_json()

    response_list = client.get("/rentals?renter_id=1")
    assert response_list.status_code == 200
    rentals_list = response_list.get_json()

    assert len(rentals_list) == 1
    assert rental1 in rentals_list   

def test_filter_rental_records_ID(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()

    first = client.post("/equipment", json={
        "name": "Kayak",
        "category": "Water",
        "total_units": 1
    })
    second = client.post("/equipment", json={
        "name": "Tent",
        "category": "Camping",
        "total_units": 2
    })

    response1 = client.post("/rentals", json={
            "equipment_id": 1,
            "renter_id": 1,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": 2,
            "renter_id": 2,
            "due_date": due_date_str,
            "deposit_amount": 75.0
            })
    assert response1.status_code == 201
    assert response2.status_code == 201
    rental1 = response1.get_json()

    response_list = client.get("/rentals?equipment_id=1")
    assert response_list.status_code == 200
    rentals_list = response_list.get_json()

    assert len(rentals_list) == 1
    assert rental1 in rentals_list   

def test_check_out_equipment(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()

    first = client.post("/equipment", json={
            "name": "Kayak",
            "category": "Water",
            "total_units": 5
        })
    
    assert first.status_code == 201
    equipment = first.get_json()
    equipment_ID = equipment["id"]

    response1 = client.post("/rentals", json={
                "equipment_id": equipment_ID,
                "renter_id": 1,
                "due_date": due_date_str,
                "deposit_amount": 50.0
                })
    
    assert response1.status_code == 201
    rental = response1.get_json()
    assert rental["equipment_id"] == equipment_ID
    assert rental["renter_id"] == 1

    availability_response = client.get(f"/equipment/{equipment_ID}/availability")
    assert availability_response.status_code == 200

    availability = availability_response.get_json()
    assert availability["total_units"] == 5
    assert availability["available_units"] == 4

def test_return_equipment(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()
    first = client.post("/equipment", json={
            "name": "Kayak",
            "category": "Water",
            "total_units": 1
        })
    
    assert first.status_code == 201
    equipment = first.get_json()
    equipment_ID = equipment["id"]

    response1 = client.post("/rentals", json={
                "equipment_id": equipment_ID,
                "renter_id": 1,
                "due_date": due_date_str,
                "deposit_amount": 50.0
                })
    
    assert response1.status_code == 201
    rental = response1.get_json()
    rental_ID = rental["id"]

    pre_return_availability = client.get(f"/equipment/{equipment_ID}/availability").get_json()
    assert pre_return_availability["available_units"] == 0

    return_response = client.put(f"/rentals/{rental_ID}/return")
    assert return_response.status_code == 200

    rental_data = return_response.get_json()
    assert rental_data["return_date"] == date.today().isoformat()

    post_return_availability = client.get(f"/equipment/{equipment_ID}/availability").get_json()
    assert post_return_availability["available_units"] == 1

    