""" Helper for work with Yandex Database"""

import os
import datetime
import time
import ydb
from akinator import Akinator

YDB_ENDPOINT = os.getenv('YDB_ENDPOINT')
YDB_DATABASE = os.getenv('YDB_DATABASE')

driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)

class Command:
    """ Interface for commands """
    #pylint: disable=too-few-public-methods

    def _callee(self, session : ydb.Session):
        raise NotImplementedError()

    def execute(self):
        """ Method for realizing Command Pattern"""

        try:
            return pool.retry_operation_sync(self._callee)
        except Exception as ex:
            print("COMMAND EXECUTE ERROR")
            print(ex)
            return None

class CmdCreateAkiUserTable(Command):
    """ Command for ctreating new table in database """
    #pylint: disable=too-few-public-methods

    def __init__(self, table_name, path : str = YDB_DATABASE) -> None:
        self.name = str(table_name)
        self.full_path = os.path.join(path, "akinator", self.name)
        super().__init__()

    def _callee(self, session : ydb.Session):
        session.create_table(
            path = self.full_path,
            table_description = ydb.TableDescription()
                .with_column(ydb.Column('user_id',         ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('session',         ydb.OptionalType(ydb.DataType.Uint32)))
                .with_column(ydb.Column('signature',       ydb.OptionalType(ydb.DataType.Uint32)))
                .with_column(ydb.Column('question',        ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('progression',     ydb.OptionalType(ydb.DataType.Float)))
                .with_column(ydb.Column('step',            ydb.OptionalType(ydb.DataType.Uint32)))
                .with_column(ydb.Column('time',            ydb.OptionalType(ydb.DataType.Datetime)))
                .with_column(ydb.Column('uri',             ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('server',          ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('uid',             ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('frontaddr',       ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('child_mode',      ydb.OptionalType(ydb.DataType.Bool)))
                .with_column(ydb.Column('question_filter', ydb.OptionalType(ydb.DataType.Utf8)))
                .with_column(ydb.Column('ts',              ydb.OptionalType(ydb.DataType.Float)))
                .with_column(ydb.Column('message_id',      ydb.OptionalType(ydb.DataType.Utf8)))
                .with_primary_key('message_id')
                .with_ttl(ydb.TtlSettings().with_date_type_column('time', 900))
        )

class CmdUpsertFullDataToTable(Command):
    """ Command for filling full table """
    #pylint: disable=too-few-public-methods

    def __init__(self, user_id, message_id, aki : Akinator) -> None:
        self.user_id = user_id
        self.message_id = message_id
        self.aki = aki
        super().__init__()

    def _callee(self, session : ydb.Session):
        time_for_ttl = datetime.datetime.fromtimestamp(time.time())
        time_for_ttl = time_for_ttl + datetime.timedelta(minutes=15)

        query = f"""
            PRAGMA TablePathPrefix("{os.path.join(os.getenv('YDB_DATABASE'), "akinator")}");
            UPSERT INTO `{str(self.user_id)}` (user_id, session, signature, question, progression, step, time, uri, server, uid, frontaddr, child_mode, question_filter, ts, message_id)
            VALUES
            (
                '{str(self.user_id)}', 
                {self.aki.session}, 
                {self.aki.signature},
                Utf8('{self.aki.question.replace("'", "")}'),
                Float('{str(self.aki.progression)}'),
                {self.aki.step},
                Datetime('{time_for_ttl.strftime('%Y-%m-%dT%H:%M:%SZ')}'),
                Utf8('{str(self.aki.uri)}'), 
                Utf8('{str(self.aki.server)}'), 
                Utf8('{str(self.aki.uid)}'), 
                Utf8('{str(self.aki.frontaddr)}'), 
                Bool('{self.aki.child_mode}'), 
                Utf8('{str(self.aki.question_filter)}'), 
                Float('{str(self.aki.timestamp)}'), 
                Utf8('{str(self.message_id)}')
            );
        """
        session.transaction().execute(query, commit_tx=True)

class CmdUpsertShortDataToTable(Command):
    """ Command for filling only necessary data in database """
    #pylint: disable=too-few-public-methods

    def __init__(self, user_id, message_id, question : str, progression : float, step : int):
        #pylint: disable=too-many-arguments

        self.user_id = user_id
        self.message_id = message_id
        self.question = question
        self.progression = progression
        self.step = step
        super().__init__()

    def _callee(self, session : ydb.Session):
        time_for_ttl = datetime.datetime.fromtimestamp(time.time())
        time_for_ttl = time_for_ttl + datetime.timedelta(minutes=15)

        query = f"""
            PRAGMA TablePathPrefix("{os.path.join(os.getenv('YDB_DATABASE'), "akinator")}");
            UPSERT INTO `{str(self.user_id)}` ( question, progression, step, time, message_id )
            VALUES
            (
                Utf8('{self.question.replace("'", "")}'),
                Float('{str(self.progression)}'),
                {self.step},
                Datetime('{time_for_ttl.strftime('%Y-%m-%dT%H:%M:%SZ')}'),
                Utf8('{str(self.message_id)}')
            );
        """
        session.transaction().execute(query, commit_tx=True)

class CmdSelectDataFromTable(Command):
    """ Get all data from table """
    #pylint: disable=too-few-public-methods

    def __init__(self, user_id, message_id) -> None:
        self.user_id = user_id
        self.message_id = message_id
        super().__init__()

    def _callee(self, session  : ydb.Session):
        res_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            f"""
                PRAGMA TablePathPrefix("{os.path.join(os.getenv('YDB_DATABASE'), "akinator")}");
                SELECT *
                FROM `{self.user_id}`
                WHERE message_id = "{self.message_id}"
                LIMIT 1;
            """,
            commit_tx=True
        )
        return res_sets[0].rows[0]

class YDBManager():
    """ Yandex Database Invoker """
    #pylint: disable=too-few-public-methods

    def execute(self, cmd : Command):
        """ Runs the commands """
        return cmd.execute()

ydb_manager = YDBManager()




if __name__ == "__main__":
    pass
