import operator, calendar, time
from datetime import date
from decimal import *


class Loan:
    def __init__(self, start_date, rate, principal, compounding):
        """ This function creates a new loan instance and initializes key variables.

        Parameters
        ----------
        start_date : Date Loan starts accruing interest
        rate : Annual Percentage Rate
        principal : Starting Loan Balance
        compounding : Number of Times Per Year Interest is Compounded.
        """
        self.starting_date = start_date
        self.interest_rate = Decimal(rate/100)
        self.starting_balance = principal
        self.compounds_per_year = compounding
        self.annualized_interest_rate = Decimal(self.interest_rate / self.compounds_per_year)
        self.previous__date = start_date
        self.current_balance = Decimal(principal)
        self.outstanding_interest = 0

    def calculate_interest(self, date):
        days = (date - self.previous__date).days
        years = Decimal(days / 365)
        self.previous__date = date
        interest = Decimal((Decimal(self.current_balance) * Decimal(1 + self.annualized_interest_rate)**Decimal(self.compounds_per_year * years)) - Decimal(self.current_balance))
        return interest

    def apply_payment(self, amount):
        payment_balance = 0  # start by assuming the full payment amount will be used

        if self.current_balance > 0:
            self.current_balance = self.current_balance - amount

            if self.current_balance < 0:
                payment_balance = (-1) * self.current_balance
                self.current_balance = 0

        else:
            payment_balance = amount

        return payment_balance


class LoanManager:
    loans = []
    regular_payment = 0
    start_date = date(1970, 1, 1)
    original_total = 0
    total_balance = 0
    total_interest = 0
    total_paid = 0
    weighed_average = 0

    def __init__(self, regular_payment, start_date):
        self.regular_payment = regular_payment
        self.start_date = start_date

    def weighted_average_interest(self):
        total_dollars = 0
        for loan in self.loans:
            total_dollars += loan.current_balance

        weighted_percent = 0
        for loan in self.loans:
            weight = loan.current_balance/total_dollars
            weighted_percent += (weight * (loan.interest_rate * 100))

        self.weighed_average = weighted_percent

    def load_loan(self, loan):
        self.loans.append(loan)
        self.loans.sort(key=operator.attrgetter('interest_rate'), reverse=True)  # sort the loan list in order of interest rate greatest to least
        self.total_balance += loan.current_balance
        self.original_total += loan.current_balance

    def __apply_payment(self, amount, payment_date):

        self.total_paid += amount

        group_interest = 0
        for loan in self.loans:
            group_interest += loan.calculate_interest(payment_date)

        self.total_interest += group_interest
        amount = Decimal(amount) - group_interest
        if amount > 0:
            for loan in self.loans:
                amount = loan.apply_payment(amount)

            #  if there is a remaining balance after all loans have been paid keep money!
            if amount > 0:
                self.total_paid -= amount

            self.total_balance = 0
            for loan in self.loans:
                self.total_balance = self.total_balance + loan.current_balance
        else:
            raise Exception("Payment too low interest outgrows payment")

    def analyze_repayment_scenario(self):
        next_date = add_months(self.start_date, 1)
        while self.total_balance > 0:
            self.__apply_payment(self.regular_payment, next_date)
            if self.total_balance > 0:
                next_date = add_months(next_date, 1)

        print("Total to be paid by " + str(next_date) + " is " + str(round(self.total_paid, 2)))

    def calculate_equivalent_consolidation_rate(self):
        print("Consolidation Scenarios")
        test_rate = self.loans[-1].interest_rate * 100
        increment_by = 0.05
        number_of_passes = 0
        while True:
            nested_manager = LoanManager(self.regular_payment, self.start_date)
            nested_manager.load_loan(Loan(start_date=self.start_date, rate=test_rate, principal= self.original_total, compounding=365))
            nested_manager.analyze_repayment_scenario()
            print("At rate " + str(round(test_rate, 2)))
            test_rate += Decimal(increment_by)
            if nested_manager.total_paid > self.total_paid:
                if number_of_passes < 1:
                    test_rate -= Decimal(0.1)
                    increment_by = 0.01
                    number_of_passes += 1
                else:
                    break


def add_months(source_date, months):
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def run():
    start_date = date(2018, 4, 14)
    payment = 500

    manager = LoanManager(payment, start_date)
    manager.load_loan(Loan(start_date=start_date, rate=4.25, principal=3378.96, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=6.55, principal=2206.69, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=6.55, principal=5634.57, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=6.55, principal=7512.61, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=2705.95, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=1086.73, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=2705.95, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=540.81, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=2705.95, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=3.61, principal=534.49, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=5.96, principal=3923.04, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=5.96, principal=14821.44, compounding=365))
    manager.load_loan(Loan(start_date=start_date, rate=5.59, principal=21056.49, compounding=365))

    manager.weighted_average_interest()

    manager.analyze_repayment_scenario()

    manager.calculate_equivalent_consolidation_rate()

    time.sleep(1)
