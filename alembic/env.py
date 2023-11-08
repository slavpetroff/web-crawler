from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
from sqlalchemy import engine_from_config

from db.models.screenshot import Base
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option(
    "sqlalchemy.url", settings.sqlalchemy_sync_database_url
)  # Override the URL here

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.sqlalchemy_sync_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode using a synchronous engine."""

    # Here you should create a synchronous engine instead of an async one
    # This assumes SQLALCHEMY_DATABASE_URL is a valid sync DB URI
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.sqlalchemy_sync_database_url

    # Create a synchronous engine using the altered URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Use the synchronous engine to run migrations
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
