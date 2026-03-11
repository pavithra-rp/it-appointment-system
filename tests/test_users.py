import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "user1@example.com",
            "password": "123456",
            "role": "user"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully."


@pytest.mark.asyncio
async def test_duplicate_user(client):

    await client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "duplicate@example.com",
            "password": "123456",
            "role": "user"
        }
    )

    response = await client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "duplicate@example.com",
            "password": "123456",
            "role": "user"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Already user exists."


@pytest.mark.asyncio
async def test_login_success(client):

    await client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "login@example.com",
            "password": "123456",
            "role": "user"
        }
    )

    response = await client.post(
        "/login",
        json={
            "email": "login@example.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_password(client):

    await client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "wrongpass@example.com",
            "password": "123456",
            "role": "user"
        }
    )

    response = await client.post(
        "/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client):
    response = await client.post("/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out"