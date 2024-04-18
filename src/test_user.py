from requests import get, post, delete, put
import unittest


class TestUserRestfulApiPost(unittest.TestCase):
    def test_correct(self):
        address = 'http://127.0.0.1:8080/api/users'
        data = dict(login="Alex", age=19, email="email_test_10@yandex.ru", hashed_password="123")

        response = post(address, json=data)

        self.assertEqual(response.status_code, 200)

    def test_correct_two(self):
        address = 'http://127.0.0.1:8080/api/users'
        data = dict(login="Oleg", age=19, email="email_test_11@yandex.ru", hashed_password="123")

        response = post(address, json=data)

        self.assertEqual(response.status_code, 200)

    def test_email_not_enique(self):
        address = 'http://127.0.0.1:8080/api/users'
        data = dict(login="Alex", age=19, email="email_test_10@yandex.ru", hashed_password="123")

        response = post(address, json=data)

        self.assertEqual(response.status_code, 500)

    def test_not_full_param(self):
        address = 'http://127.0.0.1:8080/api/users'
        data = dict(login="Alex", email="email_test_12@yandex.ru", hashed_password="123")

        response = post(address, json=data)

        self.assertEqual(response.status_code, 400)

    def test_dict_is_empty(self):
        address = 'http://127.0.0.1:8080/api/users'
        data = dict()

        response = post(address, json=data)

        self.assertEqual(response.status_code, 400)


class TestUserRestfulApiGet(unittest.TestCase):
    def test_correct_one_user(self):
        address = 'http://127.0.0.1:8080/api/users/1'
        response = get(address)

        self.assertEqual(response.status_code, 200)

    def test_non_existent_id(self):
        address = 'http://127.0.0.1:8080/api/users/100'
        response = get(address)

        self.assertEqual(response.status_code, 404)

    def test_not_specified_id(self):
        address = 'http://127.0.0.1:8080/api/users/'
        response = get(address)

        self.assertEqual(response.status_code, 404)

    def test_correct_all(self):
        address = 'http://127.0.0.1:8080/api/users'
        response = get(address)

        self.assertEqual(response.status_code, 200)


class TestUserRestfulApiPut(unittest.TestCase):
    def test_correct(self):
        address = 'http://127.0.0.1:8080/api/users/1'
        data = dict(login="Alex_two", age=21, email="email_test_3@yandex.ru")

        response = put(address, json=data)

        self.assertEqual(response.status_code, 200)

    def test_non_existent_param(self):
        address = 'http://127.0.0.1:8080/api/users/1'
        data = dict(loggggin="Alex_two")

        response = put(address, json=data)

        self.assertEqual(response.status_code, 400)

    def test_non_existent_id(self):
        address = 'http://127.0.0.1:8080/api/users/100'
        data = dict(login="Alex_two", age=21, email="email_test_10@yandex.ru")

        response = put(address, json=data)

        self.assertEqual(response.status_code, 500)

    def test_not_specified_id(self):
        address = 'http://127.0.0.1:8080/api/users/'
        data = dict(login="Alex_two", age=21, email="email_test_10@yandex.ru")

        response = put(address, json=data)

        self.assertEqual(response.status_code, 404)


class TestUserRestfulApiDelete(unittest.TestCase):
    def test_correct(self):
        address = 'http://127.0.0.1:8080/api/users/3'

        response = delete(address)

        self.assertEqual(response.status_code, 200)

    def test_non_existent_id(self):
        address = 'http://127.0.0.1:8080/api/users/100'

        response = delete(address)

        self.assertEqual(response.status_code, 404)

    def test_not_specified_id(self):
        address = 'http://127.0.0.1:8080/api/users/'

        response = delete(address)

        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
