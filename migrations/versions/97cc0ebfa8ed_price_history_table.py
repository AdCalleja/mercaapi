"""Price history table

Revision ID: 97cc0ebfa8ed
Revises: 4aa707f4e2de
Create Date: 2024-10-04 10:39:39.345081

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "97cc0ebfa8ed"
down_revision: Union[str, None] = "4aa707f4e2de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pricehistory",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pricehistory")
    # ### end Alembic commands ###
