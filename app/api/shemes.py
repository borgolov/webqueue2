from marshmallow import fields
from flask import current_app as app
from ..extensions import ma, db
from ..models import *


class ServiceLocationOffsetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ServiceLocationOffset
        load_instance = True
        include_relationships = True
        include_fk = True
        fields = ('priority', 'day_of_week', 'offset_time_up', 'offset_time_down')

    # Используем Enum для day_of_week
    weekday = fields.Method('get_day_of_week')

    def get_day_of_week(self, obj):
        return obj.weekday.name if isinstance(obj.day_of_week, Enum) else obj.weekday


class ServiceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service
        load_instance = True
        include_relationships = True
        fields = ('id', 'name', 'prefix', 'location_offsets')

    location_offsets = fields.Nested(ServiceLocationOffsetSchema, many=True)


class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = True


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Location
        load_instance = True


class OperatorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Operator
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True