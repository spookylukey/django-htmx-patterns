import random
from datetime import date

from boltons.iterutils import flatten
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.enums import TextChoices
from faker import Faker


class MonsterType(TextChoices):
    HUMANOID = "humanoid", "Humanoid"
    BLOB = "blob", "Blob"
    LEGGY = "leggy", "Leggy"


TITLE_PREFIXES = flatten([[t + " ", t + "."] for t in ("Mr", "Mrs", "Rev", "Dr")])


def validate_no_title(name):
    if bad_title := next((title for title in TITLE_PREFIXES if name.lower().startswith(title.lower())), None):
        raise ValidationError(f"Please don't call a monster \"{bad_title.strip()}\", they don't like that.")


def validate_not_future(date_value):
    if date_value > date.today():
        raise ValidationError("Date of birth cannot be in the future")


class Monster(models.Model):
    name = models.CharField(max_length=100, validators=[validate_no_title])
    is_happy = models.BooleanField(default=True)
    date_of_birth = models.DateField(default=date.today, validators=[validate_not_future])
    type = models.CharField(
        max_length=50,
        choices=MonsterType.choices,
        help_text="Don't complain about the lack of choices",
    )

    def toggle_happiness(self):
        self.is_happy = not self.is_happy
        self.save()

    def kick(self):
        self.is_happy = False
        self.save()

    def hug(self):
        self.is_happy = True
        self.save()

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if (date.today() - self.date_of_birth).days > 365 * 10 and self.is_happy:
            raise ValidationError("Monsters more than 10 years old are grumpy, everyone knows that!")


def make_monsters(count):
    faker = Faker()
    created = []
    for i in range(count):
        created.append(Monster.objects.create(name=faker.first_name(), is_happy=bool(random.randint(0, 1))))
    return created
