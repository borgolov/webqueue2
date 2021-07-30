"""empty message

Revision ID: 92ad1b4f0ce8
Revises: eb787621d51a
Create Date: 2021-07-30 15:19:26.409577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92ad1b4f0ce8'
down_revision = 'eb787621d51a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('client_services_priority_fkey', 'client_services', type_='foreignkey')
    op.drop_constraint('client_services_clients_fkey', 'client_services', type_='foreignkey')
    op.drop_constraint('client_services_services_fkey', 'client_services', type_='foreignkey')
    op.create_foreign_key(None, 'client_services', 'clients', ['clients'], ['id'], referent_schema='public')
    op.create_foreign_key(None, 'client_services', 'services', ['services'], ['id'], referent_schema='public')
    op.create_foreign_key(None, 'client_services', 'priority', ['priority'], ['id'], referent_schema='public')
    op.drop_constraint('clients_service_zone_fkey', 'clients', type_='foreignkey')
    op.create_foreign_key(None, 'clients', 'service_zone', ['service_zone'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('information_table_service_zone_fkey', 'information_table', type_='foreignkey')
    op.drop_constraint('information_table_news_event_fkey', 'information_table', type_='foreignkey')
    op.create_foreign_key(None, 'information_table', 'service_zone', ['service_zone'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'information_table', 'type_news', ['news_event'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('informationtable_services_information_table_fkey', 'informationtable_services', type_='foreignkey')
    op.drop_constraint('informationtable_services_services_fkey', 'informationtable_services', type_='foreignkey')
    op.create_foreign_key(None, 'informationtable_services', 'services', ['services'], ['id'], referent_schema='public')
    op.create_foreign_key(None, 'informationtable_services', 'information_table', ['information_table'], ['id'], referent_schema='public')
    op.drop_constraint('news_event_service_zone_fkey', 'news_event', type_='foreignkey')
    op.drop_constraint('news_event_type_news_fkey', 'news_event', type_='foreignkey')
    op.create_foreign_key(None, 'news_event', 'service_zone', ['service_zone'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'news_event', 'type_news', ['type_news'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('services_template_sound_alert_fkey', 'services', type_='foreignkey')
    op.drop_constraint('services_timetable_fkey', 'services', type_='foreignkey')
    op.create_foreign_key(None, 'services', 'time_table', ['timetable'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'services', 'template_sound_alert', ['template_sound_alert'], ['id'], source_schema='public', referent_schema='public')
    op.drop_constraint('servicezone_services_services_fkey', 'servicezone_services', type_='foreignkey')
    op.drop_constraint('servicezone_services_service_zone_fkey', 'servicezone_services', type_='foreignkey')
    op.create_foreign_key(None, 'servicezone_services', 'service_zone', ['service_zone'], ['id'], referent_schema='public')
    op.create_foreign_key(None, 'servicezone_services', 'services', ['services'], ['id'], referent_schema='public')
    op.drop_constraint('time_week_time_out_fkey', 'time_week', type_='foreignkey')
    op.drop_constraint('time_week_time_table_fkey', 'time_week', type_='foreignkey')
    op.create_foreign_key(None, 'time_week', 'time_table', ['time_table'], ['id'], source_schema='public', referent_schema='public')
    op.create_foreign_key(None, 'time_week', 'time_out', ['time_out'], ['id'], source_schema='public', referent_schema='public')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'time_week', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'time_week', schema='public', type_='foreignkey')
    op.create_foreign_key('time_week_time_table_fkey', 'time_week', 'time_table', ['time_table'], ['id'])
    op.create_foreign_key('time_week_time_out_fkey', 'time_week', 'time_out', ['time_out'], ['id'])
    op.drop_constraint(None, 'servicezone_services', type_='foreignkey')
    op.drop_constraint(None, 'servicezone_services', type_='foreignkey')
    op.create_foreign_key('servicezone_services_service_zone_fkey', 'servicezone_services', 'service_zone', ['service_zone'], ['id'])
    op.create_foreign_key('servicezone_services_services_fkey', 'servicezone_services', 'services', ['services'], ['id'])
    op.drop_constraint(None, 'services', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'services', schema='public', type_='foreignkey')
    op.create_foreign_key('services_timetable_fkey', 'services', 'time_table', ['timetable'], ['id'])
    op.create_foreign_key('services_template_sound_alert_fkey', 'services', 'template_sound_alert', ['template_sound_alert'], ['id'])
    op.drop_constraint(None, 'news_event', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'news_event', schema='public', type_='foreignkey')
    op.create_foreign_key('news_event_type_news_fkey', 'news_event', 'type_news', ['type_news'], ['id'])
    op.create_foreign_key('news_event_service_zone_fkey', 'news_event', 'service_zone', ['service_zone'], ['id'])
    op.drop_constraint(None, 'informationtable_services', type_='foreignkey')
    op.drop_constraint(None, 'informationtable_services', type_='foreignkey')
    op.create_foreign_key('informationtable_services_services_fkey', 'informationtable_services', 'services', ['services'], ['id'])
    op.create_foreign_key('informationtable_services_information_table_fkey', 'informationtable_services', 'information_table', ['information_table'], ['id'])
    op.drop_constraint(None, 'information_table', schema='public', type_='foreignkey')
    op.drop_constraint(None, 'information_table', schema='public', type_='foreignkey')
    op.create_foreign_key('information_table_news_event_fkey', 'information_table', 'type_news', ['news_event'], ['id'])
    op.create_foreign_key('information_table_service_zone_fkey', 'information_table', 'service_zone', ['service_zone'], ['id'])
    op.drop_constraint(None, 'clients', schema='public', type_='foreignkey')
    op.create_foreign_key('clients_service_zone_fkey', 'clients', 'service_zone', ['service_zone'], ['id'])
    op.drop_constraint(None, 'client_services', type_='foreignkey')
    op.drop_constraint(None, 'client_services', type_='foreignkey')
    op.drop_constraint(None, 'client_services', type_='foreignkey')
    op.create_foreign_key('client_services_services_fkey', 'client_services', 'services', ['services'], ['id'])
    op.create_foreign_key('client_services_clients_fkey', 'client_services', 'clients', ['clients'], ['id'])
    op.create_foreign_key('client_services_priority_fkey', 'client_services', 'priority', ['priority'], ['id'])
    # ### end Alembic commands ###
