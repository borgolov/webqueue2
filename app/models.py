from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import sql, Column, CHAR, String, Integer, Time, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_security import RoleMixin
from app import db


weekdays = Enum('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', name='weekdays')


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

services_operators = db.Table(
    'services_operators',
    db.Column('service_id', db.Integer(), db.ForeignKey('service.id')),
    db.Column('operator_id', db.Integer(), db.ForeignKey('operator.id'))
)


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(100), nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('user', lazy='dynamic'))

    @property
    def is_authenticated(self):
        return True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    @property
    def is_active(self):
        # override UserMixin property which always returns true
        # return the value of the active column instead
        return self.active

    def __str__(self):
        return self.username


#ServiceLocation = db.Table('service_location',
#    db.Column('service', db.Integer, db.ForeignKey('service.id'), primary_key=True),
#    db.Column('location', db.Integer, db.ForeignKey('location.id'), primary_key=True),
#    db.Column('priority', db.Integer, nullable=True, default=0)
#)


class ServiceLocation(db.Model):
    __tablename__ = 'service_location'

    service = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    location = db.Column(db.Integer, db.ForeignKey('location.id'), primary_key=True)
    #priority = db.Column(db.Integer, nullable=True, default=0)

    service_rel = db.relationship('Service', backref=db.backref('service_locations', lazy='dynamic'))
    location_rel = db.relationship('Location', backref=db.backref('service_locations', lazy='dynamic'))

    def __str__(self):
        return self.service_rel.name


class Company(db.Model):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __str__(self):
        return self.name


class Location(db.Model):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    company = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=True)
    #is_offset_time = Column(Boolean, default=False)
    #offset_time_up = Column(Time, default=datetime.now().time().replace(hour=20, minute=00, second=00))
    #offset_time_down = Column(Time, default=datetime.now().time().replace(hour=7, minute=30, second=00))
    #services = relationship('Service', secondary=ServiceLocation, lazy='subquery', backref=db.backref('services', lazy='dynamic'))
    location_company = relationship('Company')
    #service_locations = relationship('ServiceLocation', back_populates='location')

    def __str__(self):
        return self.name
    
    @property
    def services(self):
        return [service_location.service for service_location in self.service_locations]


class Service(db.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    prefix = Column(String, nullable=True)
    #is_offset_time = Column(Boolean, default=False)
    #offset_time_up = Column(Time, default=datetime.now().time().replace(hour=20, minute=00, second=00))
    #offset_time_down = Column(Time, default=datetime.now().time().replace(hour=7, minute=30, second=00))

    def __str__(self):
        return self.name
    

class ServiceLocationOffset(db.Model):
    __tablename__ = 'service_location_offset'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    priority = db.Column(db.Integer, nullable=True, default=0)
    day_of_week = db.Column(weekdays, nullable=False)
    offset_time_up = db.Column(db.Time, nullable=False)
    offset_time_down = db.Column(db.Time, nullable=False)

    service = db.relationship('Service', backref=db.backref('location_offsets', lazy='dynamic'))
    location = db.relationship('Location', backref=db.backref('service_offsets', lazy='dynamic'))

    def __str__(self):
        return f"ServiceLocationOffset for {self.service.name} at {self.location.name} on {self.day_of_week}"


class Operator(db.Model):
    __tablename__ = 'operator'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    duber = Column(String)
    user = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    location = Column(Integer, ForeignKey('location.id', ondelete='CASCADE'), nullable=False)
    user_operator = relationship('User')
    location_operator = relationship('Location')
    services = db.relationship('Service', secondary=services_operators, backref=db.backref('operator', lazy='dynamic'))

    def __str__(self):
        return self.name

    def has_service(self, *args):
        return set(args).issubset({service.id for service in self.services})

