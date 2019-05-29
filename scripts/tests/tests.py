import random

from rest_framework import status
from rest_framework.test import APITestCase

from scripts.models import Manuscript, Letter


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
        url = '/api/crop?page_url=https://images.syriac.reclaim.hosting/'
        url += 'manuscripts/Add.17224/add17724-57a.jpg&x=879&y=1384&w=111&h=97'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.content), 0)


class LetterEndpointTests(APITestCase):

    fixtures = ['scripts/tests/test_fixtures.json']

    def test_no_params(self):
        url = '/api/letters'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "No Manuscripts Specified!"})

    def test_no_mss(self):
        url = '/api/letters?letter_ids=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "No Manuscripts Specified!"})

    def test_no_letters(self):
        url = '/api/letters?ms_ids=1'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "No Letters Specified!"})

    def test_response(self):

        count = random.choice((1, 3, 5))

        # get a random numer of random Manuscript IDs
        num_ms_ids = random.choice(range(3, 10))
        ms_ids = random.sample(
            list(Manuscript.objects.values_list('id', flat=True)), num_ms_ids)

        # get 3 random Letter IDs
        num_letter_ids = random.choice(range(3, 10))
        letter_ids = random.sample(
            list(Letter.objects.values_list('id', flat=True)), num_letter_ids)

        url = f'/api/letters?ms_ids={"|".join(str(_) for _ in ms_ids)}' +\
              f'&letter_ids={"|".join(str(_) for _ in letter_ids)}' +\
              f'&count={count}'

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # should be only one top-level key: "mss"
        self.assertTrue(len(response.data) == 1)
        self.assertTrue('mss' in response.data)

        # the number of mss should be equal to the number passed in the url
        self.assertEqual(len(response.data['mss']), num_ms_ids)

        # the ms keys should match the ms_ids passed in
        self.assertEqual(list(response.data['mss'].keys()), ms_ids)

        for ms, letters in response.data['mss'].items():
            # the number of letters should match the number passed
            self.assertEqual(len(letters), num_letter_ids)

            # the letter keys should match the letter_ids passed
            self.assertEqual(list(letters.keys()), letter_ids)

            # for each response, there should me no more than `count`
            #  examples returned
            self.assertTrue(
                all(len(examples) <= count for examples in letters.values()))
