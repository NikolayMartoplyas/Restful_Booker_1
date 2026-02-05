import datetime

import pytest
import requests
from faker import Faker
from .constants import BASE_URL, HEADERS, AUTH_DATE, ENDPOINT_AUTH, ENDPOINT_BOOKING
from custom_requester.custom_requester import CustomRequester

faker = Faker("ru_RU")
@pytest.fixture(scope="session")
def requester(auth_session):
    """Создание сессии"""
    return CustomRequester(session=auth_session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def auth_session():
    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.post(f'{BASE_URL}{ENDPOINT_AUTH}', json=AUTH_DATE)
    assert response.status_code == 200, f"Ошибка получения токена, получили статус {response.status_code}"
    token = response.json().get("token")
    assert token is not None, "Токен отсутствует"
    session.headers.update({"Cookie": f"token={token}"})
    return session

@pytest.fixture()
def booking_id(requester, booking_data):
    # Создание бронирования
    response = requester.send_request(
        method="POST",
        endpoint=ENDPOINT_BOOKING,
        data=booking_data,
        expected_status=200
    )
    # response = auth_session.post(f"{BASE_URL}{ENDPOINT_BOOKING}", json=booking_data)
    # assert response.status_code == 200, f"Бронирование не создано, статус код = {response.status_code}"

    # Полуение ID
    id = response.json().get("bookingid")
    assert id is not None, "Ошибка идентификатор брони не найден"

    # Сравнение схем
    # get_booking = auth_session.get(f"{BASE_URL}/booking/{id}")
    # schem_response = get_booking.json()
    # assert schem_response == booking_data, "Ошибка схемы не совпадают"
    yield id

    # Удаляем Бронирование
    requester.send_request(
        method="delete",
        endpoint=f"{ENDPOINT_BOOKING}/{id}",
        expected_status=201
    )
    # auth_session.delete(f"{BASE_URL}/booking/{id}")

@pytest.fixture()
def booking_data():
    checkin_date = faker.date_between(start_date=datetime.date.today(), end_date="+10d")
    checkout_date = faker.date_between(start_date=checkin_date + datetime.timedelta(days=1), end_date="+10d")
    return {
        "firstname": faker.first_name(),
        "lastname": faker.last_name(),
        "totalprice": faker.random_int(100, 100_000),
        "depositpaid": faker.boolean(),
        "bookingdates": {
            "checkin": checkin_date.strftime('%Y-%m-%d'),
            "checkout": checkout_date.strftime('%Y-%m-%d')
        },
        "additionalneeds": faker.word()
    }

