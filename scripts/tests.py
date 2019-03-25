from rest_framework import status
from rest_framework.test import APITestCase


class ManuscriptsTests(APITestCase):

    def test_list_manuscripts(self):
        url = '/api/manuscripts'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)

    def test_filter_manuscripts(self):
        url = '/api/manuscripts'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        full_list_length = len(response.data)

        url = '/api/manuscripts?display=true'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        filtered_list_length = len(response.data)

        self.assertGreaterEqual(full_list_length, filtered_list_length)


class PagesTests(APITestCase):

    def test_list_pages(self):
        url = '/api/pages'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)


class LettersTests(APITestCase):
    def test_list_letters(self):
        url = '/api/letters'
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)


class CoordinatesTests(APITestCase):
    def test_filter_coordinates(self):
        url = '/api/coordinates?page_id=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)

        url = '/api/coordinates?letter_id=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)

        url = '/api/coordinates?page_id=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)

        url = '/api/coordinates?page_id=1&letter_id=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 0)


class CroppingTests(APITestCase):
    def test_image_crop(self):
        url = '/api/crop?page_url=http://images.syriac.reclaim.hosting/'
        'manuscripts/Add.17224/add17724-57a.jpg&x=879&y=1384&w=111&h=97'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.content), 0)
