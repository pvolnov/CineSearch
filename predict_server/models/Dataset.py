from models import *

class Dataset(Model):
    id = IdentityField()
    user_value = JSONField()
    film_value = JSONField()
    result = IntegerField(default=0)
    data = DateField()

    class Meta:
        database = db
        db_table='Dataset'