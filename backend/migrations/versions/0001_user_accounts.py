"""Add user accounts and ownership to the existing verification table."""
from alembic import op
import sqlalchemy as sa

revision = "0001_user_accounts"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "users" not in inspector.get_table_names():
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False, unique=True),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )

    inspector = sa.inspect(bind)
    if "verifications" not in inspector.get_table_names():
        op.create_table(
            "verifications",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("source_type", sa.String(length=10), nullable=False),
            sa.Column("source_preview", sa.String(length=160), nullable=False),
            sa.Column("is_fake", sa.Boolean(), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("error", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
    inspector = sa.inspect(bind)
    if "user_id" not in {column["name"] for column in inspector.get_columns("verifications")}:
        with op.batch_alter_table("verifications") as batch:
            batch.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
            batch.create_foreign_key("fk_verifications_user_id_users", "users", ["user_id"], ["id"], ondelete="SET NULL")
    indexes = {index["name"] for index in sa.inspect(bind).get_indexes("verifications")}
    if "ix_verifications_user_created" not in indexes:
        op.create_index("ix_verifications_user_created", "verifications", ["user_id", "created_at"])

def downgrade():
    op.drop_index("ix_verifications_user_created", table_name="verifications")
    with op.batch_alter_table("verifications") as batch:
        batch.drop_constraint("fk_verifications_user_id_users", type_="foreignkey")
        batch.drop_column("user_id")
    op.drop_table("users")
