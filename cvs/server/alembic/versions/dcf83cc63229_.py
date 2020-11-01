"""empty message

Revision ID: dcf83cc63229
Revises: ebf88e22d694
Create Date: 2020-11-02 00:24:04.725397

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String

# revision identifiers, used by Alembic.
revision = 'dcf83cc63229'
down_revision = 'ebf88e22d694'
branch_labels = None
depends_on = None

application_table = table(
    'application',
    column('id', String),
    column('description', String),
    column('jwt_secret', String)
)


def upgrade():
    op.bulk_insert(application_table, [
        {'id': 'f657759719b47d7eebbe24893f2ddef30f1cc0a5c3bacad313a4ca07c272bb19',
         'description': 'VideoRoom sample app',
         'jwt_secret': '-'
         },
    ])


def downgrade():
    pass
