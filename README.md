# Disclaimer
The algorithm employed doesn't match the example given.
I've used an algorithm that amotizes the loan amount and
adds compound interest.

The system of interest accumulation wasn't specified in the brief,
so I've chosen this method.

# Running
First ensure that you have a python3 virtualenvironment configured

then run:
pip install -r requirements.txt

This will install pandas, numpy, pytest and their dependencies.
You don't need to run the tests using pytest, but it's a simple way of doing it.

To run the tests, whilst in the tests directory run:
py.test ./unit.py

In order to use the script, run it in the specified format:

calculate.py <lender_pool_csv> <loan_amount>
