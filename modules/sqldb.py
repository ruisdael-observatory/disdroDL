
from sqlalchemy import FLOAT, Table, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine

# telegram_fields = config_dict['telegram_fields'].keys()
def create_db(dbpath, telegram_fields):
    '''
    create disdrodl.db
    with Table: disdrodl 
    where telegram fields become columns 
    extra columns: id, timestamp, parsivel_id are included 
    '''

    Base = declarative_base()
    disdrodl_table = Table(
        "disdrodl",
        Base.metadata,
        *(Column(f'f_{column_name}', String, primary_key=False)
        for column_name in telegram_fields)
    )
    disdrodl_table.append_column(Column('id', Integer,primary_key=True, autoincrement=True) )
    disdrodl_table.append_column(Column('timestamp', FLOAT ) )
    disdrodl_table.append_column(Column('datetime', String ) )
    disdrodl_table.append_column(Column('parsivel_id', String))
    print(disdrodl_table._columns)

    engine = create_engine(f'sqlite:///{dbpath}', echo=False)
    Base.metadata.create_all(engine)

