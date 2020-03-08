import os
from time import sleep

import pyperclip
from threading import Thread
from termcolor import colored, cprint
import numpy as np
from terminaltables import SingleTable
from multiprocessing import Process


class bcolors:

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


def comma_value(max_buy):
    return format(max_buy, ",")


class Main:
    def __init__(self):
        self.__FINISH = False
        self.margin = 0.10
        self.min_margin = 0.02
        self.fees = 0.10
        self.storage = ""
        self.mode = 0
        self.capital = 5000
        self.volume_multiplier = 5
        self.order_count = 20
        self.margin_skill = 4
        self.sell_price = 0.00
        self.order_price = 0
        self.BUY = 0
        self.SELL = 1
        self.OFF = 2

        self.setup()
        self.run()

    def setup(self):
        self.calculate_order_price()

    def display_header(self):
        if self.mode == self.BUY:
            hr_mode = "Buy"
        elif self.mode == self.SELL:
            hr_mode = "Sell"
        else:
            hr_mode = "Off"

        hr_margin = "{}%".format(self.margin * 100)

        mode = "Mode: {}".format(hr_mode)
        capital = "Capital: {}".format(self.capital)
        volume = "Volume Multi: {}".format(self.volume_multiplier)
        divider = "=======" * 10
        margin = "Min Margin: {}".format(hr_margin)
        print(
            "{}\n{:<2}  {:<2}  {:<2}  {:<2}\n{}\n".format(
                divider, mode, capital, volume, margin, divider
            )
        )

    def clear_term(self):
        os.system("cls" if os.name == "nt" else "clear")

    def user_input(self):
        while True:
            if self.__FINISH:
                break
            users_input = input("Please enter an option\n")

            if users_input == "q":
                print("Quitting")
                self.__FINISH = True
            if users_input == "b":
                self.mode = self.BUY
            if users_input == "s":
                self.mode = self.SELL
            if users_input == "o":
                self.mode = OFF

            if users_input:
                self.clear_term()
                self.display_header()

    def get_clip_data(self):
        return pyperclip.paste()

    def calculate_max_buy(self, value):
        cost = 1.12
        value_with_margin = value / cost
        return round(value_with_margin, 2)

    def calculate_margin_sell(self, value):
        cost = self.calculate_fees(value)
        margin = self.margin + 1
        value_with_margin = cost * margin
        return round(value_with_margin, 2)

    def calculate_min_sell(self, value):
        cost = self.calculate_fees(value)
        min_margin = self.min_margin + 1
        value_with_margin = cost * min_margin
        return round(value_with_margin, 2)

    def calculate_fees(self, value):
        fees = self.fees + 1
        value_with_margin = value * fees
        return round(value_with_margin, 2)

    def parse_value(self, value):
        split_value = value.split()
        price_location = 0
        loc = 0
        for location in split_value:
            if location == "ISK":
                price_location = loc - 1
                break
            loc += 1
        if not price_location:
            return None
        price = float(split_value[price_location].replace(",", ""))
        return round(price, 2)

    def calculate_order_price(self):
        capital = self.capital * 1000000
        margin_capital = (capital * 0.75 ** self.margin_skill) + capital
        order_price = margin_capital / self.order_count
        self.order_price = round(order_price, 2)
        print("Order Price: %s" % self.order_price)

    def calculate_competitive_price(self, value):
        value = float(value)
        if self.mode == self.BUY:
            value = round(value + 0.01, 2)
        else:
            value = round(value - 0.01, 2)
        return value

    def calculate_needed_qty(self, value):
        qty = self.order_price / value
        return round(qty, 0)

    def calculate_min_daily_volume(self, value):
        return value * self.volume_multiplier

    def convert_daily_volume_thousands(self, value):
        new_value = value / 1000
        if new_value < 0.01:
            return "N/A"
        conversion = "{} K".format(round(new_value, 2))
        return conversion

    def convert_daily_volume_millions(self, value):
        new_value = value / 1000000
        if new_value < 0.01:
            return "N/A"
        conversion = "{} M".format(round(new_value, 2))
        return conversion

    def convert_daily_volume_billions(self, value):
        new_value = value / 1000000000
        if new_value < 0.09:
            return "N/A"
        conversion = "{} B".format(round(new_value, 2))
        return conversion

    def buy_mode(self, value, competitive_price=None):
        margin_sell = self.calculate_margin_sell(value)
        min_sell = self.calculate_min_sell(value)
        cost = self.calculate_fees(value)
        if not competitive_price:
            competitive_price = self.calculate_competitive_price(value)
        self.sell_price = competitive_price
        pyperclip.copy(competitive_price)

        needed_qty = self.calculate_needed_qty(value)
        min_daily_volume = self.calculate_min_daily_volume(needed_qty)
        daily_volume_thousands = self.convert_daily_volume_thousands(min_daily_volume)
        daily_volume_millions = self.convert_daily_volume_millions(min_daily_volume)
        daily_volume_billions = self.convert_daily_volume_billions(min_daily_volume)

        sub_divider = "_______" * 10

        table_data = [
            [
                "Target Sell",
                colored(comma_value(margin_sell), "grey", "on_red", attrs=["bold"]),
            ],
            ["Min Sell", comma_value(min_sell)],
            ["Cost", comma_value(cost)],
            ["Competitive Price", comma_value(competitive_price)],
        ]
        for item in table_data:
            print("{:<40}{}\n".format(item[0], item[1]))

        print(
            "{}\n\nQty: {:,.0f}\n\nMin Volume\n{:,.0f}\n{}\n{}\n{}\n".format(
                sub_divider,
                needed_qty,
                min_daily_volume,
                daily_volume_thousands,
                daily_volume_millions,
                daily_volume_billions,
            )
        )

        return [margin_sell, min_sell]

    def get_results(self, data):
        value = self.parse_value(data)
        if not value:
            return

        if self.mode == self.BUY:
            self.buy_mode(value)

        if self.mode == self.SELL:
            competitive_price = self.calculate_competitive_price(value)
            max_buy = self.calculate_max_buy(value)
            self.sell_price = competitive_price

            pyperclip.copy(competitive_price)

            table_data = [
                [
                    "Max Buy",
                    colored(comma_value(max_buy), "grey", "on_red", attrs=["bold"]),
                ],
                ["Competitive Price", comma_value(competitive_price)],
            ]
            for item in table_data:
                print("{:<40}{}\n".format(item[0], item[1]))

    def run(self):
        t1 = Thread(target=self.user_input)
        t1.start()
        self.display_header()

        while True:
            if self.__FINISH:
                t1.join()
                self.clear_term()
                quit()
            result = self.get_clip_data()
            if result == "":
                continue
            if result == self.storage:
                sleep(0.01)
                continue
            if result == str(self.sell_price):
                sleep(0.01)
                continue
            if result == None:
                sleep(0.01)
                continue

            self.storage = result
            self.clear_term()
            self.display_header()
            self.get_results(result)


Main()
