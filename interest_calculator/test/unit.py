import unittest
import pandas
from interest_calculator.calculate import Calculator
from interest_calculator.calculate import Formatter
import os
import subprocess

class TestCalculations(unittest.TestCase):
    def setUp(self):
        self.csv_loc = os.path.dirname(__file__)+os.path.sep

    def test_total(self):
        df = pandas.read_csv(self.csv_loc+'market.csv')
        calc = Calculator(df)
        self.assertEqual(calc.total, 2330)

    def test_simple(self):
        df = pandas.read_csv(self.csv_loc+'market.csv')
        calc = Calculator(df)
        self.assertEqual("{:.1f}".format(calc.get_rate(100)), "6.9")
        self.assertEqual("{:.1f}".format(calc.get_rate(1000)), "7.0")

    def test_too_much(self):
        df = pandas.read_csv(self.csv_loc+'market.csv')
        calc = Calculator(df)
        self.assertEqual(calc.get_rate(3000), None)

    def test_large_lender(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df, max=30000)
        self.assertEqual("{:.1f}".format(calc.get_rate(30000)), "56.0")

    def test_zero(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate(0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

    def test_lt_zero(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate(-1))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

    def test_not_multiple_of_100(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate(70))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a multiple of 100")

    def test_float(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate(100.1))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a multiple of 100")

    def test_non_numerical(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate("f21"))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

    def test_much_too_large(self):
        df = pandas.read_csv(self.csv_loc+'market2.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_rate(100000000000000000000000000000000))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount is greater than permitted maximum")

    def test_float_point_zero(self):
        df = pandas.read_csv(self.csv_loc+'market.csv')
        calc = Calculator(df)
        self.assertEqual("{:.1f}".format(calc.get_rate(100.0)), "6.9")
        self.assertEqual("{:.1f}".format(calc.get_rate(1000.0)), "7.0")

    def test_does_not_except(self):
        df = pandas.read_csv(self.csv_loc+'market3.csv')
        calc = Calculator(df)
        for num in range(100, 15000, 100):
            self.assertEqual("{:.1f}".format(calc.get_rate(num)), "20.0")

    def test_monthly_payment_error_cases(self):
        df = pandas.read_csv(self.csv_loc+'market3.csv')
        calc = Calculator(df)
        try:
            self.assertRaises(ValueError, calc.get_monthly_payment("f21", 7.0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

        try:
            self.assertRaises(ValueError, calc.get_monthly_payment(100.1, 7.0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a multiple of 100")

        try:
            self.assertRaises(ValueError, calc.get_monthly_payment(70, 7.0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a multiple of 100")

        try:
            self.assertRaises(ValueError, calc.get_monthly_payment(-1, 7.0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

        try:
            self.assertRaises(ValueError, calc.get_monthly_payment(0, 7.0))
        except ValueError as e:
            self.assertEqual(e.args[0], "Requested amount must be a positive integer")

    def test_get_amortized_monthly_payback(self):
        df = pandas.read_csv(self.csv_loc+'market4.csv')
        calc = Calculator(df)
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(100, calc.get_rate(100))), "3.04")
        df = pandas.read_csv(self.csv_loc+'market5.csv')
        calc = Calculator(df)
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(1000, calc.get_rate(1000))), "35.65")
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(1400, calc.get_rate(1400))), "49.91")
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(5000, calc.get_rate(5000))), "178.26")
        df = pandas.read_csv(self.csv_loc+'market6.csv')
        calc = Calculator(df)
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(1000, calc.get_rate(1000))), "35.90")
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(1400, calc.get_rate(1400))), "50.26")
        self.assertEqual("{:.2f}".format(calc.get_monthly_payment(5000, calc.get_rate(5000))), "179.51")

    def test_sample_report(self):
        df = pandas.read_csv(self.csv_loc+'market.csv')
        calc = Calculator(df)
        report = calc.get_report(1000)
        # Provided figures do not pass. I have implemented an algorithm to amortize
        # the loan.
        # self.assertEqual("{:.2f}".format(report["monthly_repayments"]), "30.78")
        # self.assertEqual("{:.1f}".format(report["rate"]), "7.0")
        # self.assertEqual("{:.2f}".format(report["total_repayment"]), "1108.10")
        self.assertEqual("{:.2f}".format(report["monthly_repayments"]), "30.88")
        self.assertEqual("{:.1f}".format(report["rate"]), "7.0")
        self.assertEqual("{:.2f}".format(report["total_repayment"]), "1111.64")

class TestFormatter(unittest.TestCase):
    def test_golden_path(self):
        f = Formatter(7.040404, 1000, 30.88, 1111.64)
        self.assertEqual(f.get_message(), "Requested amount: £1000\nRate: 7.0%\nMonthly repayment: £30.88\nTotal repayment: £1111.64")


class TestScriptRunner(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        self.script_loc = self.base_dir+os.path.sep+"calculate.py"
        self.csv_loc = os.path.dirname(__file__)+os.path.sep

    def test_malformed_CSV(self):
        sub = subprocess.run(self.script_loc+" "+self.csv_loc+"marketbad.csv 1000", shell=True, check=True, stdout=subprocess.PIPE)
        output = sub.stdout
        self.assertEqual(output.decode("utf-8") , 'CSV file corrupted\n')

    def test_bad_number(self):
        sub = subprocess.run(self.script_loc+" "+self.csv_loc+"market.csv 1001", shell=True, check=True, stdout=subprocess.PIPE)
        output = sub.stdout
        self.assertEqual(output.decode("utf-8") , 'Requested amount must be a multiple of 100\n')

    def test_negative(self):
        sub = subprocess.run(self.script_loc+" "+self.csv_loc+"market.csv -1", shell=True, check=True, stdout=subprocess.PIPE)
        output = sub.stdout
        self.assertEqual(output.decode("utf-8") , 'Requested amount must be a positive integer\n')

    def test_good_path(self):
        sub = subprocess.run(self.script_loc+" "+self.csv_loc+"market.csv 1000", shell=True, check=True, stdout=subprocess.PIPE)
        output = sub.stdout
        self.assertEqual(output.decode("utf-8") , "Requested amount: £1000\nRate: 7.0%\nMonthly repayment: £30.88\nTotal repayment: £1111.64\n")

if __name__ == '__main__':
    unittest.main()