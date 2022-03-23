from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import sql, Column, CHAR, String, Integer, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_security import RoleMixin
from app import db


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


ServiceLocation = db.Table('service_location',
    db.Column('service', db.Integer, db.ForeignKey('service.id'), primary_key=True),
    db.Column('location', db.Integer, db.ForeignKey('location.id'), primary_key=True)
)


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
    is_offset_time = Column(Boolean, default=False)
    offset_time = Column(Time, default=datetime.now().time().replace(hour=20, minute=00, second=00))
    services = relationship('Service', secondary=ServiceLocation, lazy='subquery', backref=db.backref('services', lazy=True))
    location_company = relationship('Company')

    def __str__(self):
        return self.name


class Service(db.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    prefix = Column(String, nullable=True)
    is_offset_time = Column(Boolean, default=False)
    offset_time = Column(Time, default=datetime.now().time().replace(hour=20, minute=00, second=00))

    def __str__(self):
        return self.name


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

