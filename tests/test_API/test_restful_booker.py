import datetime
import requests
from .conftest import BASE_URL, faker
from .constants import ENDPOINT_BOOKING


class TestBooker:

    def test_get_booking(self, requester, booking_data, booking_id):
        # Запрос на получения бронирования по ID
        response = requester.send_request(
            method="get",
            endpoint=f"{ENDPOINT_BOOKING}/{booking_id}",
            expected_status=200
        )

        get_booking_JSON = response.json()
        assert get_booking_JSON == booking_data, "Ошибка схемы не совпадают" #вместо сравнения каждого поля сравниваем схемы



    def test_full_booking_update(self, requester, booking_id):
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
        response = requester.send_request(
            method="put",
            endpoint=f"{ENDPOINT_BOOKING}/{booking_id}",
            data=new_body,
            expected_status=200
        )
        # Сравнение схем
        response_data = response.json()
        assert response_data == new_body, "Ошибка, схемы не совпадают"

    def test_partial_resource_update(self, requester, booking_data, booking_id):
        """Частичное обновление ресурса"""
        new_body = {
            "firstname": "Николай",
            "lastname": "Ялдонов"
        }
        response = requester.send_request(
            method="patch",
            endpoint=f"{ENDPOINT_BOOKING}/{booking_id}",
            data=new_body,
            expected_status=200
        )
        response_data = response.json()

        assert response_data["firstname"] == new_body["firstname"], "Ошибка имена не совпадают"
        assert response_data["lastname"] == new_body["lastname"], "Ошибка фамилия не совпадают"
        assert response_data["totalprice"] == booking_data["totalprice"], "Ошибка цена не совпадают"
        assert response_data["depositpaid"] == booking_data["depositpaid"], "Ошибка депозит не совпадают"
        assert response_data["bookingdates"]["checkin"] == booking_data["bookingdates"]["checkin"], "Ошибка Дата заезда не совпадают"
        assert response_data["bookingdates"]["checkout"] == booking_data["bookingdates"]["checkout"], "Ошибка Дата выезда не совпадают"
        assert response_data["additionalneeds"] == booking_data["additionalneeds"], "Ошибка пожелания не совпадают"

    def test_no_required_field(self, requester):
        """отсутсвие обязаительных полей"""
        checkin_date = faker.date_between(start_date=datetime.date.today(), end_date="+10d")
        checkout_date = faker.date_between(start_date=checkin_date + datetime.timedelta(days=1), end_date="+10d")
        body = {
            "firstname": " ",
            "lastname": " ",
            "totalprice": faker.random_int(100, 100_000),
            "depositpaid": faker.boolean(),
            "bookingdates": {
                "checkin": checkin_date.strftime('%Y-%m-%d'),
                "checkout": checkout_date.strftime('%Y-%m-%d')
            },
            "additionalneeds": faker.word()
        }
        requester.send_request(
            method="post",
            endpoint=f"{ENDPOINT_BOOKING}",
            data=body,
            expected_status=400
        )

    def test_invalid_data_type(self, requester):
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
        requester.send_request(
            method="post",
            endpoint=f"{ENDPOINT_BOOKING}",
            data=body,
            expected_status=400
        )

    def test_updating_nonexistent_resource(self, requester, booking_data):
        requester.send_request(
            method="put",
            endpoint=f"{ENDPOINT_BOOKING}/999999999999999999",
            data=booking_data,
            expected_status=405
        )

    def test_update_without_authorization(self, booking_id):
        new_body = {
            "firstname": "Николай",
            "lastname": "Ялдонов"
        }
        response = requests.patch(f"{BASE_URL}{ENDPOINT_BOOKING}/{booking_id}", json=new_body)
        assert response.status_code == 403, "Ошибка, ожидалось что без авторизации обновления не будет"

    def test_empty_data_transfer(self, requester, booking_id):
        new_body = {
            "firstname": " ",
            "lastname": "Ялдонов"
        }
        requester.send_request(
            method="put",
            endpoint=f"{ENDPOINT_BOOKING}/{booking_id}",
            data=new_body,
            expected_status=400
        )
        # response_put = auth_session.put(f"{BASE_URL}/booking/{post_booking}", json=new_body)
        # assert response_put.status_code == 400, "Ошибка, ожидали предупреждение что обязательные поля не могут быть пустыми"

    def test_delete_no_authorization(self, booking_id):
        response = requests.delete(f"{BASE_URL}{ENDPOINT_BOOKING}/{booking_id}")
        assert response.status_code == 403, "Ошибка, удаление без авторизации невозможно"
