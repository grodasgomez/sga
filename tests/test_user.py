from django.test import TestCase
from django import setup
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sga.settings")
setup()


class TestUser(TestCase):
    def test_prueba1(self):
        self.assertEqual(5 + 3, 8)

    def test_prueba2(self):
        self.assertEqual(5 - 3, 2)

