from django.test import TestCase

from scripts.models import Manuscript, Coordinates, Letter, Page


class PriorityFieldTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.letter = Letter.objects.create(letter='test letter')
        cls.alt_letter = Letter.objects.create(letter='alt. letter')

        cls.manuscript = Manuscript.objects.create(shelfmark='test manuscript')
        cls.alt_manuscript = Manuscript.objects.create(shelfmark='alt. ms')

        cls.alt_page = Page.objects.create(
            manuscript=cls.alt_manuscript,
            number='alt. page',
            height=1,
            width=1
        )

    def setUp(self):
        # these tests abuse the page.number field as a way to keep a handle on
        #  different coordinates objects

        for i, page_num in enumerate('abcdefghij'):
            _page = Page.objects.create(
                manuscript=self.manuscript,
                number=page_num,
                height=1,
                width=1
            )

            Coordinates.objects.create(
                page=_page,
                top=1,
                left=1,
                height=1,
                width=1,
                letter=self.letter,
                priority=i+1
            )

        for i, page_num in enumerate('klmn'):
            _page = Page.objects.create(
                manuscript=self.manuscript,
                number=page_num,
                height=1,
                width=1
            )

            Coordinates.objects.create(
                page=_page,
                top=1,
                left=1,
                height=1,
                width=1,
                letter=self.letter,
                priority=None
            )

    def tearDown(self):
        Page.objects.filter(manuscript=self.manuscript).delete()
        Coordinates.objects.filter(page=self.alt_page).delete()

    def get_result(self, manuscript, letter):
        """ Returns a list of coordinates from the relevannt collection
            sorted by priority (nulls last).
        """
        queryset = Coordinates.objects.filter(
            manuscript_id=manuscript.id, letter=letter)
        values = queryset.values_list('page__number', 'priority')
        return list(sorted(values, key=lambda x: (x[1] is None, x[1])))

    def test_setup(self):

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_priority_removal(self):
        # Test priority removal

        coords_a = Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='a'
        )

        coords_a.priority = None
        coords_a.save()

        expected_result = [
            ('b', 1), ('c', 2), ('d', 3), ('e', 4), ('f', 5),
            ('g', 6), ('h', 7), ('i', 8), ('j', 9), ('a', None),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_priority_change(self):

        coords_a = Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='a'
        )

        coords_a.priority = 6
        coords_a.save()

        expected_result = [
            ('b', 1), ('c', 2), ('d', 3), ('e', 4), ('f', 5),
            ('a', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_priority_change_to_out_of_bounds_priority(self):

        coords_a = Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='a'
        )

        coords_a.priority = 11
        coords_a.save()

        expected_result = [
            ('b', 1), ('c', 2), ('d', 3), ('e', 4), ('f', 5),
            ('g', 6), ('h', 7), ('i', 8), ('j', 9), ('a', 10),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_priority_added(self):

        # add a new object with priority=None
        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        coords_o = Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter,
            priority=None
        )

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None),
            ('o', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

        # now update it to priority=6
        coords_o.priority = 6
        coords_o.save()

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('o', 6), ('f', 7), ('g', 8), ('h', 9), ('i', 10), ('j', 11),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_insertion_with_no_priority(self):
        # Test new insertion with no priority

        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter
        )

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None),
            ('o', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_insertion_with_valid_priority(self):

        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter,
            priority=2
        )

        expected_result = [
            ('a', 1), ('o', 2), ('b', 3), ('c', 4), ('d', 5), ('e', 6),
            ('f', 7), ('g', 8), ('h', 9), ('i', 10), ('j', 11),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_insertion_with_invalid_priority(self):

        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter,
            priority=-1
        )

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None),
            ('o', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_insertion_with_out_of_bounds_priority(self):

        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter,
            priority=9999
        )

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('o', 11),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_insertion_with_priority_zero(self):

        page_o = Page.objects.create(
            manuscript=self.manuscript,
            number='o',
            height=1,
            width=1
        )

        Coordinates.objects.create(
            page=page_o,
            top=1,
            left=1,
            height=1,
            width=1,
            letter=self.letter,
            priority=0
        )

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('i', 9), ('j', 10),
            ('k', None), ('l', None), ('m', None), ('n', None),
            ('o', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_object_deletion(self):
        # Test object deletion

        Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='c'
        ).delete()

        expected_result = [
            ('a', 1), ('b', 2), ('d', 3), ('e', 4),
            ('f', 5), ('g', 6), ('h', 7), ('i', 8), ('j', 9),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

    def test_object_moved_to_another_ms(self):
        # Test object moved to another manuscript

        coords_i = Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='i'
        )
        coords_i.page = self.alt_page
        coords_i.save()

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4), ('e', 5),
            ('f', 6), ('g', 7), ('h', 8), ('j', 9),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

        # check that it's gone where it's supposed to
        #  (Note: the space in 'alt. page' will have been expunged by the
        #   `Page.save()` method.)
        expected_alt_result = [('alt.page', 1)]

        self.assertEqual(
            self.get_result(self.alt_manuscript, self.letter),
            expected_alt_result
        )

    def test_object_moved_to_another_letter(self):
        # Test object moved to another manuscript

        coords_e = Coordinates.objects.get(
            manuscript_id=self.manuscript.id,
            letter=self.letter,
            page__number='e'
        )
        coords_e.letter = self.alt_letter
        coords_e.save()

        expected_result = [
            ('a', 1), ('b', 2), ('c', 3), ('d', 4),
            ('f', 5), ('g', 6), ('h', 7), ('i', 8), ('j', 9),
            ('k', None), ('l', None), ('m', None), ('n', None)
        ]

        self.assertEqual(
            self.get_result(self.manuscript, self.letter), expected_result)

        # check that it's gone where it's supposed to
        expected_alt_result = [('e', 1)]

        self.assertEqual(
            self.get_result(self.manuscript, self.alt_letter),
            expected_alt_result
        )
