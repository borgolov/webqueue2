from datetime import datetime
from dataclasses import dataclass
from sqlalchemy import sql, Column, CHAR, String, Integer, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from flask_bcrypt import generate_password_hash, check_password_hash
from app import db

SCHEMA = 'public'

client_services = db.Table(
    'client_services',
    db.Column('clients', Integer, ForeignKey(SCHEMA + '.clients.id'), comment='Идентификатор клинета'),
    db.Column('services', Integer, ForeignKey(SCHEMA + '.services.id'), comment='Идентификатор услуги'),
    db.Column('priority', Integer, ForeignKey(SCHEMA + '.priority.id'), comment='Идентификатор приоритета')
)

servicezone_services = db.Table(
    'servicezone_services',
    db.Column('service_zone', Integer, ForeignKey(SCHEMA + '.service_zone.id'),
              comment='Идентификатор зона обслуживания'),
    db.Column('services', Integer, ForeignKey(SCHEMA + '.services.id'), comment='Идентификатор услуги'),
)

informationtable_services = db.Table(
    'informationtable_services',
    db.Column('information_table', Integer, ForeignKey(SCHEMA + '.information_table.id'),
              comment='Идентификатор информационного табло'),
    db.Column('services', Integer, ForeignKey(SCHEMA + '.services.id'), comment='Идентификатор услуги'),
)


class Organization(db.Model):
    __tablename__ = 'organization'
    __table_args__ = {
        'comment': 'Организации',
        'schema': SCHEMA,
    }

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String(250), nullable=False)
    shot_name = Column('shot_name', String(50), nullable=False)
    contacts = Column('contacts', String(50), nullable=False)

    def __repr__(self):
        return self.order


class Services(db.Model):
    __tablename__ = 'services'
    __table_args__ = {
        'comment': 'Улсуги',
        'schema': SCHEMA,
    }

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(350), nullable=True)
    prefix = Column(CHAR(1), nullable=False)
    start_num = Column(Integer, nullable=False)
    timetable = Column(Integer, db.ForeignKey(SCHEMA + '.time_table.id'), index=True, nullable=False)
    limit = Column(Integer, nullable=False, default=0, comment='Лимит талонов в день')
    view_display = Column(Boolean, nullable=False, default=True, comment='Статус отображения на табло')
    status = Column(Boolean, nullable=False, default=True, comment='Статус')
    template_sound_alert = Column(Integer, db.ForeignKey(SCHEMA + '.template_sound_alert.id'), index=True,
                                  nullable=False, comment='шаблон звукового сопровождения')
    comment = Column(String(200))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Priority(db.Model):
    __tablename__ = 'priority'
    __table_args__ = {
        'comment': 'Приоритеты',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)


class TimeTable(db.Model):
    __tablename__ = 'time_table'
    __table_args__ = {
        'comment': 'Расписание',
        'schema': SCHEMA,
    }

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False)


class TimeOut(db.Model):
    __tablename__ = 'time_out'
    __table_args__ = {
        'comment': 'Перерыв',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')
    start_time = Column(Time, nullable=False)
    stop_time = Column(Time, nullable=False)


class TimeWeek(db.Model):
    __tablename__ = 'time_week'
    __table_args__ = {
        'comment': 'Время работы',
        'schema': SCHEMA,
    }

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    time_table = Column(Integer, db.ForeignKey(SCHEMA + '.time_table.id'), nullable=False)
    day_week = Column(Integer, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    stop_time = Column(Time, nullable=False)
    time_out = Column(Integer, db.ForeignKey(SCHEMA + '.time_out.id'))
    timetables = relationship('Timetable', backref=backref('time_week'))


class ServiceZone(db.Model):
    __tablename__ = 'service_zone'
    __table_args__ = {
        'comment': 'Зоны обслуживания',
        'schema': SCHEMA,
    }

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')


class TypeClient(db.Model):
    __tablename__ = 'type_client'
    __table_args__ = {
        'comment': 'тип клинета',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')


class Clients(db.Model):
    __tablename__ = 'clients'
    __table_args__ = {
        'comment': 'Клинеты',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')
    mac_address = Column(String(17), nullable=False, comment='Мак адрес', unique=True,)
    service_zone = Column(Integer, db.ForeignKey(SCHEMA + '.service_zone.id'), nullable=False,
                          comment='Зона обслуживаня')
    type_client = Column(Integer, db.ForeignKey(SCHEMA + '.type_client.id'), nullable=False,
                         comment='тип клиента')


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {
        'comment': 'Пользователи',
        'schema': SCHEMA,
    }

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(120), unique=True, comment='Имя пользователя')
    password = Column(String(120), nullable=False, comment='Пароль')
    status = Column(Boolean, default=False, comment='Статус')
    date_creation = Column(DateTime, server_default=sql.func.now(), comment='Дата создания')

    def set_password(self, p):
        self.password = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password.encode('utf-8'), p)


class TemplateSoundAlert(db.Model):
    __tablename__ = 'template_sound_alert'
    __table_args__ = {
        'comment': 'шаблон звукового сопровождения',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')


class TypeNews(db.Model):
    __tablename__ = 'type_news'
    __table_args__ = {
        'comment': 'тип новостей',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')


class News(db.Model):
    __tablename__ = 'news_event'
    __table_args__ = {
        'comment': 'новости, реклама',
        'schema': SCHEMA,
    }
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    type_news = Column(Integer, db.ForeignKey(SCHEMA + '.type_news.id'), nullable=False,
                       comment='Тип новости(видео, картинка, бегущая строка)')
    head = Column('head', String(100), nullable=False)
    service_zone = Column(Integer, db.ForeignKey(SCHEMA + '.service_zone.id'), nullable=False,
                          comment='Зона обслуживаня')
    text = Column('text', String(250), nullable=False)

    def __repr__(self):
        return self.order


class InformationTable(db.Model):
    __tablename__ = 'information_table'
    __table_args__ = {
        'comment': 'Информационное табло',
        'schema': SCHEMA,
    }
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(200), nullable=False, comment='наименование')
    service_zone = Column(Integer, db.ForeignKey(SCHEMA + '.service_zone.id'), nullable=False,
                          comment='Зона обслуживаня')
    view_list = Column(Boolean, nullable=False, default=False, comment='список ожидающих')
    news_event = Column(Integer, db.ForeignKey(SCHEMA + '.type_news.id'), nullable=False,
                        comment='Тип новости(видео, картинка, бегущая строка)')
    count_windows = Column(Integer, nullable=False, default=1, comment='количество отображаемых окон')
    mac_address = Column(String(48), nullable=False, comment='Мак адрес', unique=True,)
