<!-- Descrição do Projeto -->
<p align="center">Vendas FastAPI é uma API robusta e segura para gerenciar usuários, clientes, produtos e pedidos. Esta API garante que o primeiro usuário registrado seja um administrador, capaz de gerenciar funções e permissões para outros usuários.</p>

<!-- Tabela de Conteúdos -->
## Tabela de Conteúdos

- [Instalação](#instalação)
- [Utilização](#utilização)
- [Endpoints](#endpoints)
  - [Gerenciamento de Usuários](#gerenciamento-de-usuários)
  - [Gerenciamento de Clientes](#gerenciamento-de-clientes)
  - [Gerenciamento de Produtos](#gerenciamento-de-produtos)
  - [Gerenciamento de Pedidos](#gerenciamento-de-pedidos)
- [Autenticação](#autenticação)
- [Inicialização do Banco de Dados](#inicialização-do-banco-de-dados)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Instalação

1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/vendas-fastapi.git
    cd vendas-fastapi
    ```

2. Crie e ative um ambiente virtual:
    ```sh
    python3 -m venv env
    source env/bin/activate  # No Windows, use `env\Scripts\activate`
    ```

3. Instale as dependências necessárias:
    ```sh
    pip install -r requirements.txt
    ```

4. Configure o banco de dados (atualize o `DATABASE_URL` no arquivo `.env` se necessário):
    ```sh
    alembic upgrade head
    ```

## Utilização

1. Inicie o servidor FastAPI:
    ```sh
    uvicorn main:app --reload
    ```

2. Acesse a documentação interativa da API em `http://127.0.0.1:8000/docs` ou `http://127.0.0.1:8000/redoc`.

## Endpoints

### Lembrando que quando é criado o primeiro usuário ele cria um usuário com o nome de usuário admin e a senha admin para gerenciar as permissões de admin

### Gerenciamento de Usuários

- **Criar Usuário**: `POST /users/`
    ```json
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string"
    }
    ```
    Resposta:
    ```json
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "string"
    }
    ```

- **Atualizar Função do Usuário**: `PUT /users/{user_id}/role/`
    ```json
    {
        "role": "admin"
    }
    ```
    Resposta:
    ```json
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "admin"
    }
    ```

- **Listar Todos os Usuários**: `GET /users/`
    Resposta:
    ```json
    [
        {
            "id": 0,
            "username": "string",
            "email": "user@example.com",
            "role": "string"
        }
    ]
    ```

### Gerenciamento de Clientes

- **Criar Cliente**: `POST /clients/`
    ```json
    {
        "name": "string",
        "email": "user@example.com",
        "cpf": "string"
    }
    ```
    Resposta:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **Listar Todos os Clientes**: `GET /clients/`
    Parâmetros de Consulta:
    - **skip**: Número de resultados a pular (padrão: 0)
    - **limit**: Limitar o número de resultados (padrão: 10, máximo: 100)
    - **name**: Filtrar pelo nome do cliente (opcional)
    - **email**: Filtrar pelo email do cliente (opcional)

    Resposta:
    ```json
    [
        {
            "id": 0,
            "name": "string",
            "email": "string",
            "cpf": "string",
            "owner_id": 0
        }
    ]
    ```

- **Obter Cliente por ID**: `GET /clients/{client_id}`
    Resposta:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **Atualizar Cliente**: `PUT /clients/{client_id}`
    ```json
    {
        "name": "string",
        "email": "string",
        "cpf": "string"
    }
    ```
    Resposta:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **Excluir Cliente**: `DELETE /clients/{client_id}`
    Resposta:
    ```json
    {
        "message": "Cliente excluído com sucesso"
    }
    ```

### Gerenciamento de Produtos

- **Criar Produto**: `POST /products/`
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.264Z",
        "images": "string",
        "available": true
    }
    ```
    Resposta:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.266Z",
        "images": "string",
        "available": true,
        "id": 0
    }
    ```

- **Listar Todos os Produtos**: `GET /products/`
    Parâmetros de Consulta:
    - **skip**: Número de resultados a pular (padrão: 0)
    - **limit**: Limitar o número de resultados (padrão: 10, máximo: 100)
    - **description**: Filtrar pela descrição do produto (opcional)
    - **session**: Filtrar pela sessão do produto (opcional)
    - **available**: Filtrar pela disponibilidade do produto (opcional)

    Resposta:
    ```json
    [
        {
            "description": "string",
            "sale_price": 0,
            "barcode": "string",
            "session": "string",
            "initial_stock": 0,
            "expiration_date": "2024-06-19T19:39:49.321Z",
            "images": "string",
            "available": true,
            "id": 0
        }
    ]
    ```

- **Obter Produto por ID**: `GET /products/{id}`
    Resposta:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:44:42.922Z",
        "images": "string",
        "available": true,
        "id": 0
    }
    ```

- **Atualizar Produto**: `PUT /products/{id}`
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:48:23.502Z",
        "images": "string",
        "available": true
    }
    ```
    Resposta:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:48:23.502Z",
        "images": "string",
        "available": true
    }
    ```

- **Excluir Produto**: `DELETE /products/{id}`
    Resposta:
    ```json
    {
        "message": "Produto excluído com sucesso"
    }
    ```

### Gerenciamento de Pedidos

- **Listar Todos os Pedidos**: `GET /orders/`
    Parâmetros de Consulta:
    - **skip**: Número de resultados a pular (padrão: 0).
    - **limit**: Limitar o número de resultados por página (padrão: 10, máximo: 100).
    - **start_date**: Filtrar pela data de criação - data inicial (opcional - formato YYYY-MM-DD).
    - **end_date**: Filtrar pela data de criação - data final (opcional - formato YYYY-MM-DD).
    - **section**: Filtrar pela seção do produto (opcional).
    - **order_id**: Filtrar pelo ID do pedido (opcional).
    - **status**: Filtrar pelo status do pedido (opcional).
    - **client_id**: Filtrar pelo ID do cliente (opcional).

    Exemplo de Resposta:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```

- **Criar Pedido**: `POST /orders/`
    Exemplo de Requisição:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```
        
    Exemplo de Resposta:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
    ```

- **Listar um Pedido**: `GET /orders/{order_id}`
    Exemplo de Requisição:
    ```json
    {
        "id": 1 
    }
    ```
        
    Exemplo de Resposta:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
    ```

- **Atualizar Pedido**: `PUT /orders/{order_id}`
    Exemplo de Requisição:
    ```json
    {
        "id": 1 
    }
    ```
        
    Exemplo de Resposta:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```

- **Excluir Pedido**: `DELETE /orders/{order_id}`
    Exemplo de Requisição:
    ```json
    {
        "id": "1"
    }
    ```
    
    Exemplo de Resposta:
    ```json
    {
        "message": "Pedido excluído com sucesso"
    }
    ```

## Contribuições
## Sinta-se à vontade para contribuir para este projeto. Para maiores detalhes, envie um e-mail para: gleysonwener3@gmail.com.







# Vendas FastAPI

Vendas FastAPI is a robust and secure API for managing users, clients, products, and orders. 
This API ensures that the first user registered is an administrator, capable of managing roles and permissions for other users.

## Tabela de Conteúdos

- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
  - [User Management](#user-management)
  - [Client Management](#client-management)
  - [Product Management](#product-management)
  - [Order Management](#order-management)
- [Authentication](#authentication)
- [Database Initialization](#database-initialization)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/vendas-fastapi.git
    cd vendas-fastapi
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up the database (update the `DATABASE_URL` in the `.env` file if needed):
    ```sh
    alembic upgrade head
    ```

## Usage

1. Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

2. Access the interactive API documentation at `http://127.0.0.1:8000/docs` or `http://127.0.0.1:8000/redoc`.

## Endpoints

### Remembering that when the first user is created, it creates a user with the username admin and password admin to manage admin permissions

### User Management

- **Create User**: `POST /users/`
    ```json
    {
        "username": "string",
        "email": "user@example.com",
        "password": "string"
    }
    ```
    Response:
    ```json
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "string"
    }
    ```

- **Update User Role**: `PUT /users/{user_id}/role/`
    ```json
    {
        "role": "admin"
    }
    ```
    Response:
    ```json
    {
        "id": 0,
        "username": "string",
        "email": "user@example.com",
        "role": "admin"
    }
    ```

- **List All Users**: `GET /users/`
    Response:
    ```json
    [
        {
            "id": 0,
            "username": "string",
            "email": "user@example.com",
            "role": "string"
        }
    ]
    ```

### Client Management

- **Create Client**: `POST /clients/`
    ```json
    {
        "name": "string",
        "email": "user@example.com",
        "cpf": "string"
    }
    ```
    Response:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **List All Clients**: `GET /clients/`
    Query Parameters:
    - **skip**: Number of results to skip (default: 0)
    - **limit**: Limit the number of results (default: 10, max: 100)
    - **name**: Filter by client name (optional)
    - **email**: Filter by client email (optional)

    Response:
    ```json
    [
        {
            "id": 0,
            "name": "string",
            "email": "string",
            "cpf": "string",
            "owner_id": 0
        }
    ]
    ```

- **Get Client by ID**: `GET /clients/{client_id}`
    Response:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **Update Client**: `PUT /clients/{client_id}`
    ```json
    {
        "name": "string",
        "email": "string",
        "cpf": "string"
    }
    ```
    Response:
    ```json
    {
        "id": 0,
        "name": "string",
        "email": "string",
        "cpf": "string",
        "owner_id": 0
    }
    ```

- **Delete Client**: `DELETE /clients/{client_id}`
    Response:
    ```json
    {
        "message": "Client deleted successfully"
    }
    ```

### Product Management

- **Create Product**: `POST /products/`
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.264Z",
        "images": "string",
        "available": true
    }
    ```
    Response:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:43:38.266Z",
        "images": "string",
        "available": true,
        "id": 0
    }
    ```

- **List All Products**: `GET /products/`
    Query Parameters:
    - **skip**: Number of results to skip (default: 0)
    - **limit**: Limit the number of results (default: 10, max: 100)
    - **description**: Filter by product description (optional)
    - **session**: Filter by product session (optional)
    - **available**: Filter by product availability (optional)

    Response:
    ```json
    [
        {
            "description": "string",
            "sale_price": 0,
            "barcode": "string",
            "session": "string",
            "initial_stock": 0,
            "expiration_date": "2024-06-19T19:39:49.321Z",
            "images": "string",
            "available": true,
            "id": 0
        }
    ]
    ```

- **Get Product by ID**: `GET /products/{id}`
    Response:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:44:42.922Z",
        "images": "string",
        "available": true,
        "id": 0
    }
    ```

- **Update Product**: `PUT /products/{id}`
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:48:23.502Z",
        "images": "string",
        "available": true
    }
    ```
    Response:
    ```json
    {
        "description": "string",
        "sale_price": 0,
        "barcode": "string",
        "session": "string",
        "initial_stock": 0,
        "expiration_date": "2024-06-19T19:48:23.502Z",
        "images": "string",
        "available": true
    }
    ```

- **Delete Product**: `DELETE /products/{id}`
    Response:
    ```json
    {
        "message": "Product deleted successfully"
    }
    ```
    
### Order Management

- **List All Orders**: `GET /orders/`
    Query Parameters:
    - **skip**: Number of results to skip (default: 0).
    - **limit**: Limit the number of results per page (default: 10, max: 100).
    - **start_date**: Filter by creation date - start date (optional - format YYYY-MM-DD).
    - **end_date**: Filter by creation date - end date (optional - format YYYY-MM-DD).
    - **section**: Filter by product section (optional).
    - **order_id**: Filter by order ID (optional).
    - **status**: Filter by order status (optional).
    - **client_id**: Filter by client ID (optional).

    Example Response:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```

- **Create Order**: `POST /orders/`
    Example Request:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```
        
    Example Response:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
    ```

- **Get Order by ID**: `GET /orders/{order_id}`
    Example Request:
    ```json
    {
        "id": 1 
    }
    ```
        
    Example Response:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "id": 0,
        "items": [],
        "total_order_price": 0
    }
    ```

- **Update Order**: `PUT /orders/{order_id}`
    Example Request:
    ```json
    {
        "id": 1 
    }
    ```
        
    Example Response:
    ```json
    {
        "client_id": 0,
        "status": "string",
        "items": [
            {
                "product_id": 0,
                "quantity": 0
            }
        ]
    }
    ```

- **Delete Order**: `DELETE /orders/{order_id}`
    Example Request:
    ```json
    {
        "id": "1"
    }
    ```
    
    Example Response:
    ```json
    {
        "message": "Order deleted successfully"
    }
    ```

## Contributions
## Feel free to contribute to this project. For more details, send an email to: gleysonwener3@gmail.com.
