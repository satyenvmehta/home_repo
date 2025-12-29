class Currency:
    def __init__(self, amount, currency_code):
        self.amount = amount
        self.currency_code = currency_code

    def __str__(self):
        return f"{self.amount} {self.currency_code}"

    def __add__(self, other):
        if self.currency_code != other.currency_code:
            raise ValueError("Cannot add different currencies")
        new_amount = self.amount + other.amount
        return Currency(new_amount, self.currency_code)

    def __sub__(self, other):
        if self.currency_code != other.currency_code:
            raise ValueError("Cannot subtract different currencies")
        new_amount = self.amount - other.amount
        return Currency(new_amount, self.currency_code)

    def __mul__(self, multiplier):
        new_amount = self.amount * multiplier
        return Currency(new_amount, self.currency_code)

    def __divmod__(self, divisor):
        new_amount, remainder = divmod(self.amount, divisor)
        return Currency(new_amount, self.currency_code), Currency(remainder, self.currency_code)

    def convert(self, exchange_rate, target_currency):
        if self.currency_code == target_currency.currency_code:
            raise ValueError("Cannot convert to the same currency")

        if self.currency_code != exchange_rate.source_currency_code or target_currency.currency_code != exchange_rate.target_currency_code:
            raise ValueError("Invalid exchange rate")

        new_amount = self.amount * exchange_rate.rate
        return Currency(new_amount, target_currency.currency_code)


class ExchangeRate:
    def __init__(self, source_currency_code, target_currency_code, rate):
        self.source_currency_code = source_currency_code
        self.target_currency_code = target_currency_code
        self.rate = rate

    def __str__(self):
        return f"1 {self.source_currency_code} = {self.rate} {self.target_currency_code}"


class Money:
    def __init__(self, amount, currency_code):
        self.amount = amount
        self.currency_code = currency_code

    def __str__(self):
        return f"{self.amount} {self.currency_code}"

    def __add__(self, other):
        if self.currency_code != other.currency_code:
            raise ValueError("Cannot add different currencies")
        new_amount = self.amount + other.amount
        return Money(new_amount, self.currency_code)

    def __sub__(self, other):
        if self.currency_code != other.currency_code:
            raise ValueError("Cannot subtract different currencies")
        new_amount = self.amount - other.amount
        return Money(new_amount, self.currency_code)

    def __mul__(self, multiplier):
        new_amount = self.amount * multiplier
        return Money(new_amount, self.currency_code)

    def __truediv__(self, divisor):
        new_amount = self.amount / divisor
        return Money(new_amount, self.currency_code)

    def convert(self, exchange_rate, target_currency):
        if self.currency_code == target_currency.currency_code:
            raise ValueError("Cannot convert to the same currency")

        if self.currency_code != exchange_rate.source_currency_code or target_currency.currency_code != exchange_rate.target_currency_code:
            raise ValueError("Invalid exchange rate")

        new_amount = self.amount * exchange_rate.rate
        return Money(new_amount, target_currency.currency_code)

    def format(self):
        return f"{self.currency_code} {self.amount:.2f}"


class ExchangeRate:
    def __init__(self, source_currency_code, target_currency_code, rate):
        self.source_currency_code = source_currency_code
        self.target_currency_code = target_currency_code
        self.rate = rate

    def __str__(self):
        return f"1 {self.source_currency_code} = {self.rate} {self.target_currency_code}"


# Example usage:
if __name__ == "__main__":
    # Create money objects
    usd = Money(100, "USD")
    eur = Money(80, "EUR")

    # Create an exchange rate
    usd_to_eur = ExchangeRate("USD", "EUR", 0.8)

    # Convert USD to EUR
    eur_equivalent = usd.convert(usd_to_eur, eur)
    print(eur_equivalent.format())  # Should print "EUR 80.00"

    # Perform arithmetic operations
    total_money = usd + eur_equivalent
    print(total_money.format())  # Should print "USD 180.00"


# Example usage:
# if __name__ == "__main__":
    # Create currencies
    usd = Currency(100, "USD")
    eur = Currency(80, "EUR")

    # Create an exchange rate
    usd_to_eur = ExchangeRate("USD", "EUR", 0.8)

    # Convert USD to EUR
    eur_equivalent = usd.convert(usd_to_eur, eur)
    print(eur_equivalent)  # Should print "80.0 EUR"
