import random

from django.db import models
from faker import Faker


class Monster(models.Model):
    name = models.CharField(max_length=100)
    is_happy = models.BooleanField(default=True)

    def __str__(self):
        return self.name


def make_monsters(count):
    faker = Faker()
    created = []
    for i in range(count):
        created.append(Monster.objects.create(name=faker.first_name(), is_happy=bool(random.randint(0, 1))))
    return created
