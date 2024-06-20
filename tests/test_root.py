from fastapi.testclient import TestClient

def test_auth_header(client: TestClient):
    # 1. Set user data for authentication
    auth_data = {
        "username": "mrdigital",
        "password": "mrdigital"
    }

    # 2. Make a request to obtain the access token
    response = client.post("/token", data=auth_data)

    # 3. Check if the request was successful
    assert response.status_code == 200

    # 4. Get the access token from the response body
    token = response.json()["access_token"]

    # 5. Return the authorization header to be used in tests
    return {"Authorization": f"Bearer {token}"}

def test_read_clients_authenticated(client: TestClient):
    # 1. Set user data for authentication
    headers = test_auth_header(client)

    # 2. Make a GET request to the protected endpoint
    response = client.get("/clients/", headers=headers)

    # 3. Verify that the request was successful
    assert response.status_code == 200

    # 4. Assertions
    clients = response.json()
    assert isinstance(clients, list)
    # 5. Example: Check if there is at least one returned customer
    assert len(clients) > 0


def test_read_products_authenticated(client: TestClient):
    # 1. Get authorization header using token
    headers = test_auth_header(client)

    # 2. Make a GET request to the protected endpoint
    response = client.get("/products/", headers=headers)

    # 3. Verify that the request was successful
    assert response.status_code == 200

    # 4. Assertions
    products = response.json()
    assert isinstance(products, list)
    # 5. Example: Check if there is at least one product returned
    assert len(products) > 0


def test_read_orders_authenticated(client: TestClient):
    # 1. Get authorization header using token
    headers = test_auth_header(client)

    # 2. Make a GET request to the protected endpoint
    response = client.get("/", headers=headers)

    # 3. Verify that the request was successful
    assert response.status_code == 200

    # 4. Assertions
    orders = response.json()
    assert isinstance(orders, list)

    # Example: Check if there is at least one returned order
    assert len(orders) > 0


