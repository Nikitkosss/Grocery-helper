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
        with open(
            os.path.join(FILE_DIR, 'ingredients.csv'), 'r', encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, units = row
                try:
                    Ingredient.objects.create(
                        name=name,
                        units=units
                    )
                except IntegrityError:
                    self.stdout.write(
                        f'Ингредиент {name} уже существует в базе данных'
                    )
        self.stdout.write(self.style.SUCCESS('Ингридиенты загружены!'))
