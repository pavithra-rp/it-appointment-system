import pytest
from datetime import datetime


async def get_auth_headers(client):
    # register user
    await client.post(
        "/register",
        json={
            "name": "Admin User",
            "email": "admin@example.com",
            "password": "123456",
            "role": "admin"
        }
    )

    # login
    res = await client.post(
        "/login",
        json={
            "email": "admin@example.com",
            "password": "123456"
        }
    )

    token = res.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_book_appointment(client):
    headers = await get_auth_headers(client)

    response = await client.post(
        "/appointments",
        json={
            "title": "Server Issue",
            "description": "Need help with server",
            "team": "IT",
            "appointment_date": datetime(2026, 4, 20, 10, 0).isoformat()
        },
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Appointment created"


@pytest.mark.asyncio
async def test_duplicate_appointment(client):
    headers = await get_auth_headers(client)

    payload = {
        "title": "Server Issue",
        "description": "Need help with server",
        "team": "IT",
        "appointment_date": datetime(2026, 4, 20, 10, 0).isoformat()
    }

    # first booking
    await client.post("/appointments", json=payload, headers=headers)

    # duplicate booking
    response = await client.post("/appointments", json=payload, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "This time slot is already booked"


@pytest.mark.asyncio
async def test_get_appointments(client):
    headers = await get_auth_headers(client)

    response = await client.get("/appointments", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_status_invalid_role(client):
    # create normal user
    await client.post(
        "/register",
        json={
            "name": "User",
            "email": "user@example.com",
            "password": "123456",
            "role": "user"
        }
    )

    login = await client.post(
        "/login",
        json={
            "email": "user@example.com",
            "password": "123456"
        }
    )

    token = login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.put(
        "/appointments/1",
        json={"status": "approved"},
        headers=headers
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_status_invalid_value(client):
    headers = await get_auth_headers(client)

    response = await client.put(
        "/appointments/1",
        json={"status": "pending"},
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status"


@pytest.mark.asyncio
async def test_update_status_not_found(client):
    headers = await get_auth_headers(client)

    response = await client.put(
        "/appointments/999",
        json={"status": "approved"},
        headers=headers
    )

    # router order: status -> role -> appointment
    # so here status valid + admin role -> then appointment check
    assert response.status_code == 404