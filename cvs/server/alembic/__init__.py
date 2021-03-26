from alembic import op, context

def create_database_if_not_exists():
    import logging
    from sqlalchemy.engine.url import make_url
    from sqlalchemy import create_engine
    url = make_url(context.config.get_main_option("sqlalchemy.url"))
    database = url.database
    url.database = 'postgres'
    engine = create_engine(str(url))
    engine.update_execution_options(isolation_level="AUTOCOMMIT")
    try:
        engine.execute(f'CREATE DATABASE {database} WITH OWNER postgres')
    except Exception as exc:
        logging.warning(exc)
    engine.dispose()