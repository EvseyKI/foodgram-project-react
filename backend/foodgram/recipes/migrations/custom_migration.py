import os

from django.db import migrations
from rest_framework.utils import json

from recipes.models import Ingredient


def method_to_create_ingredients(first_param, second_param):
    with open(os.path.join(os.path.dirname(__file__),
                           '..', 'ingredients.json'),
              'r') as file:
        data = json.load(file)
        for item in data:
            Ingredient.objects.create(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0002_initial'),
    ]
    operations = [
        migrations.RunPython(method_to_create_ingredients),
    ]
