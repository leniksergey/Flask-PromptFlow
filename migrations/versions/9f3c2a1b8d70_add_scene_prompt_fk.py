"""add scene prompt foreign key

Revision ID: 9f3c2a1b8d70
Revises: 702e81965949
Create Date: 2026-10-29 21:10:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9f3c2a1b8d70"
down_revision = "702e81965949"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("scenes", schema=None) as batch_op:
        batch_op.add_column(sa.Column("prompt_id", sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f("ix_scenes_prompt_id"), ["prompt_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_scenes_prompt_id_prompts",
            "prompts",
            ["prompt_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("scenes", schema=None) as batch_op:
        batch_op.drop_constraint("fk_scenes_prompt_id_prompts", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_scenes_prompt_id"))
        batch_op.drop_column("prompt_id")
