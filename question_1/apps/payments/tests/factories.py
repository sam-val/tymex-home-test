import factory
from faker import Faker

from apps.payments.models import IdempotencyKey

fake = Faker()


class IdempotencyKeyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = IdempotencyKey

    pass

