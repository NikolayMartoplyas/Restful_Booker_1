import datetime
from http.client import responses

import requests

from  conftest import BASE_URL, faker
class TestBooker:

    def test_get_booking(self, auth_session, booking_data, post_booking):
        # Запрос на получения бронирования по ID
        get_booking_id = auth_session.get(f"{BASE_URL}/booking/{post_booking}")
        assert get_booking_id.status_code == 200, "Ошибка не удалось получить бронирование"
        get_booking_JSON = get_booking_id.json()
        assert get_booking_JSON == booking_data, "Ошибка схемы не совпадают" #вместо сравнения каждого поля сравниваем схемы

        # assert get_booking_JSON["firstname"] == booking_data["firstname"], "Ошибка имена не совпадают"
        # assert get_booking_JSON["lastname"] == booking_data["lastname"], "Ошибка фамилия не совпадают"
        # assert get_booking_JSON["totalprice"] == booking_data["totalprice"], "Ошибка цена не совпадают"
        # assert get_booking_JSON["depositpaid"] == booking_data["depositpaid"], "Ошибка депозит не совпадают"
        # assert get_booking_JSON["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"], "Ошибка Дата заезда не совпадают"
        # assert get_booking_JSON["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"], "Ошибка Дата выезда не совпадают"
        # assert get_booking_JSON["additionalneeds"] == booking_data["additionalneeds"], "Ошибка пожелания не совпадают"

        # Удаляем Бронирование
        dellete_booking = auth_session.delete(f"{BASE_URL}/booking/{post_booking}")
        assert dellete_booking.status_code == 201, f"Ошибка получили статус {dellete_booking.status_code}"

        # Проверяем что получить удаленный ресурс невозможно
        get_booking = auth_session.get(f"{BASE_URL}/booking/{post_booking}")
        assert get_booking.status_code == 404, "Ошибка пользователь найден, ожидали что пользователя не найдет"

    def test_full_booking_update(self, auth_session, booking_data, post_booking):
        # Создание нового тела запроса для обновления ресурса
        checkin_date = faker.date_between(start_date=datetime.date.today(), end_date="+10d")
        checkout_date = faker.date_between(start_date=checkin_date + datetime.timedelta(days=1), end_date="+10d")
        new_body = {
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

        #Обновление ресурса
        response_put = auth_session.put(f"{BASE_URL}/booking/{post_booking}", json=new_body)
        assert response_put.status_code == 200, "Ошибка не удалось обновить ресурс"

        # Сравнение схем
        response_data = response_put.json()
        assert response_data == new_body, "Ошибка, схемы не совпадают"

    def test_partial_resource_update(self, auth_session, booking_data, post_booking):
        new_body = {
            "firstname": "Николай",
            "lastname": "Ялдонов"
        }
        response = auth_session.patch(f"{BASE_URL}/booking/{post_booking}", json=new_body)
        assert response.status_code == 200, "Ошибка, не удалось обновить ресурс"
        response_data = response.json()

        assert response_data["firstname"] == new_body["firstname"], "Ошибка имена не совпадают"
        assert response_data["lastname"] == new_body["lastname"], "Ошибка фамилия не совпадают"
        assert response_data["totalprice"] == booking_data["totalprice"], "Ошибка цена не совпадают"
        assert response_data["depositpaid"] == booking_data["depositpaid"], "Ошибка депозит не совпадают"
        assert response_data["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"], "Ошибка Дата заезда не совпадают"
        assert response_data["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"], "Ошибка Дата выезда не совпадают"
        assert response_data["additionalneeds"] == booking_data["additionalneeds"], "Ошибка пожелания не совпадают"

    def test_no_required_field(self, auth_session):
        checkin_date = faker.date_between(start_date=datetime.date.today(), end_date="+10d")
        checkout_date = faker.date_between(start_date=checkin_date + datetime.timedelta(days=1), end_date="+10d")
        body = {
            "firstname": faker.first_name(),
            "lastname": "",
            "totalprice": faker.random_int(100, 100_000),
            "depositpaid": faker.boolean(),
            "bookingdates": {
                "checkin": checkin_date.strftime('%Y-%m-%d'),
                "checkout": checkout_date.strftime('%Y-%m-%d')
            },
            "additionalneeds": faker.word()
        }
        response = auth_session.post(f"{BASE_URL}/booking", json=body)
        assert response.status_code == 400, f"Ошибка ожидали что бронирование не создастся из за отсутсвия обязательных полей"

    def test_invalid_data_type(self, auth_session):
        checkin_date = faker.date_between(start_date=datetime.date.today(), end_date="+10d")
        checkout_date = faker.date_between(start_date=checkin_date + datetime.timedelta(days=1), end_date="+10d")
        body = {
            "firstname": faker.first_name(),
            "lastname": 2233,
            "totalprice": faker.random_int(100, 100_000),
            "depositpaid": faker.boolean(),
            "bookingdates": {
                "checkin": checkin_date.strftime('%Y-%m-%d'),
                "checkout": checkout_date.strftime('%Y-%m-%d')
            },
            "additionalneeds": faker.word()
        }
        response = auth_session.post(f"{BASE_URL}/booking", json=body)
        assert response.status_code == 400, f"Ошибка ожидали что бронирование не создастся из за отсутсвия обязательных полей"

    def test_updating_nonexistent_resource(self, auth_session, booking_data):
        response_put = auth_session.put(f"{BASE_URL}/booking/999999999999999999999", json=booking_data)
        assert response_put.status_code == 405, "Ошибка, ожидали что ресурс не сущевствует"

    def test_update_without_authorization(self, post_booking, auth_session):
        new_body = {
            "firstname": "Николай",
            "lastname": "Ялдонов"
        }
        response = requests.patch(f"{BASE_URL}/booking/{post_booking}", json=new_body)
        assert response.status_code == 403, "Ошибка, ожидалось что без авторизации обновления не будет"

    def test_empty_data_transfer(self, auth_session, post_booking):
        new_body = {
            "firstname": " ",
            "lastname": "Ялдонов"
        }
        response_put = auth_session.put(f"{BASE_URL}/booking/{post_booking}", json=new_body)
        assert response_put.status_code == 400, "Ошибка, ожидали предупреждение что обязательные поля не могут быть пустыми"

    def test_delete_no_authorization(self, post_booking):
        response = requests.delete(f"{BASE_URL}/booking/{post_booking}")
        assert response.status_code == 403, "Ошибка, удаление без авторизации невозможно"
