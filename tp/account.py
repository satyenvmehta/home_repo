
import common_include as C

@C.dataclass
class TradingAccount(C.BaseObject):
    """
    Represents a trading account with properties like account number, balance, and trading status.
    """
    account_number:C.BaseString
    key :C.BaseString
    balance: C.BaseFloat
    is_trading: C.BaseBool

    def __post_init__(self):
        """
        Validate the account number and balance during object initialization.
        """
        self.validate_account_number()
        return

    def validate_account_number(self):
        """
        Validate the account number format.
        """
        # Implement account number validation logic here
        pass

actList1 = [
    'Joint WROS - TOD (X84970863)',
    'Joint WROS - TOD (Z30257063)',
    'Rollover IRA (224916532)',
    'Self Employed 401K (493089129)',
    'Health Savings Account (237182357)'
]
actList = [
    TradingAccount(account_number='Joint WROS - TOD (X84970863)', key = 'JX',balance=1000, is_trading=True),
    TradingAccount(account_number='Joint WROS - TOD (Z30257063)', key = 'JZ',balance=500, is_trading=True),
    TradingAccount(account_number='Rollover IRA (224916532)', key = 'R2', balance=500, is_trading=True),
    TradingAccount(account_number='Health Savings Account (237182357)', key = 'H2', balance=500, is_trading=True),
    TradingAccount(account_number='Self Employed 401K (493089129)', key = 'S4', balance=500, is_trading=True),
    TradingAccount(account_number='Joint WROS - TOD (2BQ833959)', key = 'J2B', balance=500, is_trading=True),
    TradingAccount(account_number='Traditional IRA (2YD005797)', key = 'TR', balance=500, is_trading=False),
]
@C.dataclass
class AccountManager(C.BaseDict):
    """
    Manages trading accounts and provides methods to create, retrieve, update, and delete accounts.
    """

    def __post_init__(self):
        """
        Initialize the account manager with an empty set of accounts.
        """
        super().__post_init__()

        self.create()

        return

    def create(self):
        """
        Create a new trading account with the given account number and initial balance.
        """
        # new_account = TradingAccount(account_number=account_number, balance=initial_balance, is_trading=True)

        for act in actList:
            self.append(act.account_number, act)
        return

    def get(self, account_number):
        """
        Retrieve the trading account with the given account number.
        """
        val = self.getValue(account_number)
        return val

    def getKey(self,  account_number):
        """
        Retrieve the trading account with the given account number.
        """
        val = self.get(account_number)
        if isinstance(val, TradingAccount):
            return val.key
        return None

    def actListToActIdList(self, actNumList):
        actIdList = None
        for act in actNumList:
            if isinstance(act, C.BaseObject):
                act = act.getBase()
            aid = self.getKey(act)
            if aid:
                if not actIdList:
                    actIdList = aid
                else:
                    actIdList = actIdList + "|" + aid
        return actIdList



if __name__ == '__main__':
    # Example usage
    account_manager = AccountManager()
    # account_manager.append('123')
    # account = account_manager.create('123456', 1000)
    # print(account)
    retrieved_account = account_manager.getKey('Joint WROS - TOD (X84970863)')
    aidl = account_manager.actListToActIdList(actList1)
    print(aidl)