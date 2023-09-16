import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from recipes.models import Ingredient

FILE_DIR = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    help = 'Загрузка из csv'

    def handle(self, *args, **kwargs):
        ingredients = []
        with open(
            os.path.join(FILE_DIR, 'ingredients.csv'), 'r', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, units = row
                ingredients.append(
                    Ingredient(name=name, units=units)
                )
        try:
            Ingredient.objects.bulk_create(ingredients)
        except IntegrityError:
            for ingredient in ingredients:
                try:
                    ingredient.save()
                except IntegrityError:
                    self.stdout.write(
                        f'Ингредиент {ingredient.name} уже существует'
                    )
        self.stdout.write(self.style.SUCCESS('Ингридиенты загружены!'))
