"""Обертка связующая библиотеку akinator с базой данных в облаке"""

from akinator import Akinator
import ydbmanager as ydbm

class AkinatorHelper(Akinator):
    """Класс-обертка"""
    # pylint: disable=too-many-instance-attributes

    def start(self, user_id, message_id, language=None, child_mode=False):
        """Initialization of the start of the game.
         After initialization object state sends to database"""

        ydbm.ydb_manager.execute(ydbm.CmdCreateAkiUserTable(user_id))
        res = super().start_game(language, child_mode)

        ydbm.ydb_manager.execute(ydbm.CmdUpsertFullDataToTable(user_id, message_id, self))
        return res

    def give_answer(self, user_id, message_id, ans):
        """Object state gets from database.
        Request to Akinator API. Object state sends to database"""

        res = ydbm.ydb_manager.execute(ydbm.CmdSelectDataFromTable(user_id, message_id))

        self.child_mode      = res.child_mode
        #self.first_guess     = res.first_guess
        self.frontaddr       = res.frontaddr
        #self.guesses         = res.guesses
        self.progression     = res.progression
        self.question        = res.question
        self.question_filter = res.question_filter
        self.server          = res.server
        self.session         = res.session
        self.signature       = res.signature
        self.step            = res.step
        #self.timestamp       = res.timestamp
        self.uid             = res.uid
        self.uri             = res.uri

        res = super().answer(ans)

        ydbm.ydb_manager.execute(
            ydbm.CmdUpsertShortDataToTable(
                user_id,
                message_id,
                self.question,
                self.progression,
                self.step
            )
        )
        return res

#    def back(self):
#        """Data for dialog with akinator gets from database"""
#        return super().back()

#    def win(self):
#        """Data for dialog with akinator gets from database"""
#        return super().win()

    def __str__(self) -> str:
        return f"""
                ============================
                child_mode:         {self.child_mode}       [{type(self.child_mode)}]
                first_guess:        {self.first_guess}      [{type(self.first_guess)}]
                frontaddr:          {self.frontaddr}        [{type(self.frontaddr)}]
                guesses:            {self.guesses}          [{type(self.guesses)}]
                progression:        {self.progression}      [{type(self.progression)}]
                question:           {self.question}         [{type(self.question)}]
                question_filter:    {self.question_filter}  [{type(self.question_filter)}]
                server:             {self.server}           [{type(self.server)}]
                session:            {self.session}          [{type(self.session)}]
                signature:          {self.signature}        [{type(self.signature)}]
                step:               {self.step}             [{type(self.step)}]
                ts:                 {self.timestamp}        [{type(self.timestamp)}]
                uid:                {self.uid}              [{type(self.uid)}]
                uri:                {self.uri}              [{type(self.uri)}]
                ============================
            """


if __name__ == "__main__":
    aki = AkinatorHelper()
    aki.start(789, 321)
    aki.give_answer(789, 321, "y")
