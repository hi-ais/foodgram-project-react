import os
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient
from foodgram.settings import BASE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        shift_path = os.path.join(BASE_DIR, 'data')
        filename = os.path.join(shift_path,
                                'ingredients.json')
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ingredient in data:
                Ingredient.objects.create(name=ingredient["name"],
                                          measure_unit=ingredient[
                                          "measurement_unit"])
