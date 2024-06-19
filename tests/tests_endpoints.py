from fastapi.testclient import TestClient

from ..app.main import app

client = TestClient(app)




def test_example():
    assert 1 + 1 == 2


# def test_import_app():
#     from app.main import app
#     assert app is not None

# def test_get_client():
#     # Dados para um novo usuário
#     # new_user = {
#     #     "username": "wener",
#     #     "email": "wener@example.com",
#     #     "password": "wener1234"
#     # }

#     # Realiza a requisição POST para criar o usuário
#     response = client.get("/clients/")

#     # Verifica se a requisição foi bem-sucedida (status code 200) e se o usuário retornado corresponde aos dados enviados
    # assert response.status_code == 200  

# def test_create_user_success():
#     # Dados para um novo usuário
#     new_user = {
#         "username": "wener",
#         "email": "wener@example.com",
#         "password": "wener1234"
#     }

#     # Realiza a requisição POST para criar o usuário
#     response = client.post("http://127.0.0.1:8000/users/", json=new_user)

#     # Verifica se a requisição foi bem-sucedida (status code 200) e se o usuário retornado corresponde aos dados enviados
#     assert response.status_code == 200  

# def test_create_user_success():
#     # Dados para um novo usuário
#     new_user = {
#         "username": "wener",
#         "email": "wener@example.com",
#         "password": "wener1234"
#     }

#     # Realiza a requisição POST para criar o usuário
#     response = client.post("/users/", json=new_user)

#     # Verifica se a requisição foi bem-sucedida (status code 200) e se o usuário retornado corresponde aos dados enviados
#     assert response.status_code == 200
#     assert response.json()["username"] == new_user["username"]
#     assert response.json()["email"] == new_user["email"]

# def test_create_user_username_already_exists():
#     # Dados para um novo usuário com um username que já existe
#     existing_user = {
#         "username": "wener",
#         "email": "wener@example.com",
#         "password": "wener"
#     }

#     # Realiza a primeira requisição POST para criar o usuário com o username que já existe
#     response_existing = client.post("/users/", json=existing_user)

#     # Verifica se a primeira requisição falhou devido ao username já existente
#     assert response_existing.status_code == 400
#     assert "Username already registered" in response_existing.text

# def test_create_user_email_already_exists():
#     # Dados para um novo usuário com um email que já existe
#     existing_email_user = {
#         "username": "wener2",
#         "email": "wener@example.com",  # Email que já está registrado
#         "password": "wener"
#     }

#     # Realiza a segunda requisição POST para criar o usuário com o email que já existe
#     response_existing_email = client.post("/users/", json=existing_email_user)

#     # Verifica se a segunda requisição falhou devido ao email já existente
#     assert response_existing_email.status_code == 400
#     assert "Email already registered" in response_existing_email.text


# def test_example():
#     assert 1 + 1 == 2