from datetime import date, timedelta
#Adds a renter and makes sure it made it properly
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

#Adds a renter then searches for it
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

#Adds a renter then deletes it and verifies its done correctly
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

#Adds a renter then updates it and verifies its done correctly 
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

#Adds multiple renters then creates a list of them and verifies all the renters are in the list
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

#Adds renter, equipment then rentals then creates a list of them and verifies all the rentals are in the list
def test_view_all_rentals(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()

    renter_response1 = client.post("/renters", json={
                    "name": "RenterA",
                    "email": "rentera@example.com"
                })
    renter_response2 = client.post("/renters", json={
                    "name": "RenterB",
                    "email": "renterB@example.com"
                })
    assert renter_response1.status_code == 201
    assert renter_response2.status_code == 201
    renter1 = renter_response1.get_json()
    renter2 = renter_response2.get_json()
    renter_ID1 = renter1["id"]
    renter_ID2 = renter2["id"]

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
    assert first.status_code == 201
    assert second.status_code == 201
    equipment1 = first.get_json()
    equipment2 = second.get_json()
    equipment_ID1 = equipment1["id"]
    equipment_ID2 = equipment2["id"]


    response1 = client.post("/rentals", json={
            "equipment_id": equipment_ID1,
            "renter_id": renter_ID2,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": equipment_ID2,
            "renter_id": renter_ID1,
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

#Adds renter, equipment then rentals then searches for a rental based on renter
def test_filter_rental_records_renter(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()
    renter_response1 = client.post("/renters", json={
                    "name": "RenterA",
                    "email": "rentera@example.com"
                })
    renter_response2 = client.post("/renters", json={
                    "name": "RenterB",
                    "email": "renterB@example.com"
                })
    assert renter_response1.status_code == 201
    assert renter_response2.status_code == 201
    renter1 = renter_response1.get_json()
    renter2 = renter_response2.get_json()
    renter_ID1 = renter1["id"]
    renter_ID2 = renter2["id"]

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
    assert first.status_code == 201
    assert second.status_code == 201
    equipment1 = first.get_json()
    equipment2 = second.get_json()
    equipment_ID1 = equipment1["id"]
    equipment_ID2 = equipment2["id"]


    response1 = client.post("/rentals", json={
            "equipment_id": equipment_ID1,
            "renter_id": renter_ID2,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": equipment_ID2,
            "renter_id": renter_ID1,
            "due_date": due_date_str,
            "deposit_amount": 75.0
            })
    assert response1.status_code == 201
    assert response2.status_code == 201
    rental1 = response1.get_json()

    response_list = client.get(f"/rentals?renter_id={renter_ID2}")
    assert response_list.status_code == 200
    rentals_list = response_list.get_json()

    assert len(rentals_list) == 1
    assert rental1 in rentals_list   

#Adds renter, equipment then rentals then searches for a rental based on equipment ID
def test_filter_rental_records_ID(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()
    renter_response1 = client.post("/renters", json={
                    "name": "RenterA",
                    "email": "rentera@example.com"
                })
    renter_response2 = client.post("/renters", json={
                    "name": "RenterB",
                    "email": "renterB@example.com"
                })
    assert renter_response1.status_code == 201
    assert renter_response2.status_code == 201
    renter1 = renter_response1.get_json()
    renter2 = renter_response2.get_json()
    renter_ID1 = renter1["id"]
    renter_ID2 = renter2["id"]

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
    assert first.status_code == 201
    assert second.status_code == 201
    equipment1 = first.get_json()
    equipment2 = second.get_json()
    equipment_ID1 = equipment1["id"]
    equipment_ID2 = equipment2["id"]


    response1 = client.post("/rentals", json={
            "equipment_id": equipment_ID1,
            "renter_id": renter_ID2,
            "due_date": due_date_str,
            "deposit_amount": 50.0
            })
    response2 = client.post("/rentals", json={
            "equipment_id": equipment_ID2,
            "renter_id": renter_ID1,
            "due_date": due_date_str,
            "deposit_amount": 75.0
            })
    assert response1.status_code == 201
    assert response2.status_code == 201
    rental1 = response1.get_json()

    response_list = client.get(f"/rentals?equipment_id={equipment_ID1}")
    assert response_list.status_code == 200
    rentals_list = response_list.get_json()

    assert len(rentals_list) == 1
    assert rental1 in rentals_list   

#Adds renter, equipment then rental then checks out equipment and verifies its done correctly
def test_check_out_equipment(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()
    renter_response1 = client.post("/renters", json={
                    "name": "RenterA",
                    "email": "rentera@example.com"
                })
    assert renter_response1.status_code == 201
    renter1 = renter_response1.get_json()
    renter_ID1 = renter1["id"]
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
                "renter_id": renter_ID1,
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

#Adds renter, equipment then rental then returns equipment and verifies its done correctly
def test_return_equipment(client):
    due_date_str = (date.today() + timedelta(days=7)).isoformat()
    renter_response1 = client.post("/renters", json={
                    "name": "RenterA",
                    "email": "rentera@example.com"
                })
    assert renter_response1.status_code == 201
    renter1 = renter_response1.get_json()
    renter_ID1 = renter1["id"]   

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
                "renter_id": renter_ID1,
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


#_____________STEP3_TEST___________
#Verifies that out-of-service items cannot be rented.
def test_enhancement_checkout_blocks_out_of_service(client):
    item = client.post("/equipment", json={
        "name": "Defect Boat", 
        "category": "Water", 
        "total_units": 1
    }).get_json()
    
    client.patch(f"/equipment/{item['id']}/status", json={"is_available": False})

    response = client.post("/rentals", json={"equipment_id": item["id"], "renter_id": 100})
    
    assert response.status_code == 400
    assert response.get_json()["error"] == "Equipment is out of service"

#Verifies that items with zero available stock cannot be double-booked.
def test_enhancement_checkout_blocks_negative_stock(client):
    
    item = client.post("/equipment", json={
        "name": "Defect Boat", 
        "category": "Water", 
        "total_units": 1
    }).get_json()

    client.post("/rentals", json={"equipment_id": item["id"], "renter_id": 100})

    second_checkout = client.post("/rentals", json={"equipment_id": item["id"], "renter_id": 200})
    
    assert second_checkout.status_code == 400
    assert second_checkout.get_json()["error"] == "Equipment is out of stock / completely checked out"
    
    availability = client.get(f"/equipment/{item['id']}/availability").get_json()
    assert availability["available_units"] == 0