def initialize_db_tables(engine, BaseDBModel):
    if engine is None:
        raise RuntimeError("DB connection not initialized")

    BaseDBModel.metadata.create_all(bind=engine)
