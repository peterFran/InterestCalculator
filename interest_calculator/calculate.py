#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import argparse
import pandas

class Formatter():
    def __init__(self, interest, amount, monthly_payments, total_repayable):
        self.interest = interest
        self.amount = amount
        self.monthly_repayments = monthly_payments
        self.total_repayable = total_repayable

    def get_message(self):
        return "Requested amount: £{}\nRate: {:.1f}%\nMonthly repayment: £{:.2f}\nTotal repayment: £{:.2f}".format(
            self.amount,
            self.interest,
            self.monthly_repayments,
            self.total_repayable
        )

class Calculator():
    def __init__(self, dataframe, duration=36, max=15000):
        self.dataframe = dataframe.sort_values("Rate")
        self.duration = duration
        self.dataframe["cumulative_sum"] = self.dataframe.Available.cumsum()
        self.dataframe["rate_by_required"] = self.dataframe["Available"] * self.dataframe["Rate"]

        self.dataframe["last_cumulative"] = self.dataframe["cumulative_sum"].shift(1)
        self.dataframe["last_cumulative"] = self.dataframe["last_cumulative"].fillna(0)
        self.total = self.dataframe["Available"].sum()
        self.max = max

    def get_rate(self, amount):
        '''
        Get the rate of interest that the current pool can provide for the given amount
        :param amount: quantity of loan requested
        :return: calculated interest rate.
        '''
        self.check_validity(amount)

        if amount > self.total:
            return None

        self.dataframe["needed"] = np.where(self.dataframe["cumulative_sum"] < amount, self.dataframe["Available"],                                    amount - self.dataframe["last_cumulative"])
        self.dataframe["needed"] = np.where(self.dataframe["needed"] <= 0, 0, self.dataframe["needed"])

        # Yes this makes more work for pandas, but pandas complains about it if I do the op on the copy
        self.dataframe["interest_by_amount"] = self.dataframe["Rate"] * self.dataframe["needed"]
        mask = self.dataframe['needed'].isin([0])
        temp_dataframe = self.dataframe[~mask]
        return (temp_dataframe["interest_by_amount"].sum() / temp_dataframe["needed"].sum()) * 100

    def get_monthly_payment(self, amount, rate):
        self.check_validity(amount)
        interest = rate / 100
        monthly_interest = interest / 12
        amortization_coef = 1 / (1 - np.power(1+monthly_interest, -self.duration))
        payment = monthly_interest * amortization_coef * amount
        return payment

    def get_report(self, amount):
        rate = self.get_rate(amount)
        monthly_repayments = self.get_monthly_payment(amount, rate)
        total_repayment = monthly_repayments * self.duration
        return {"rate":rate, "monthly_repayments":monthly_repayments, "total_repayment": total_repayment}

    def check_validity(self, amount):
        '''
        Raises error if input not valid, returns None if it is
        :param amount: quantity of loan requested
        :return: None
        '''
        try:
            if amount <= 0:
                raise ValueError("Requested amount must be a positive integer")

            if amount > self.max:
                raise ValueError("Requested amount is greater than permitted maximum")

            if amount % 100 != 0:
                raise ValueError("Requested amount must be a multiple of 100")

        except TypeError as e:
            raise ValueError("Requested amount must be a positive integer")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create summary of loan breakdown')
    parser.add_argument('file', type=str,
                        help='a csv document containing a table of lenders, amounts and rates')
    parser.add_argument('amount', type=int,
                        help='loan amount required')

    args = parser.parse_args()


    try:
        df = pandas.read_csv(args.file)
        try:
            calc = Calculator(df)
            report = calc.get_report(args.amount)
            f = Formatter(report["rate"], args.amount, report["monthly_repayments"], report["total_repayment"])
            print(f.get_message())
        except ValueError as e:
            print(e.args[0])
    except Exception as e:
        print("CSV file corrupted")


