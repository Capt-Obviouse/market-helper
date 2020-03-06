import os
from time import sleep
import clipboard
from threading import Thread
from termcolor import colored, cprint
import numpy as np
from terminaltables import SingleTable


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
        self.sell_price = 0.00
        self.BUY = 0
        self.SELL = 1
        self.OFF = 2


        self.setup()
        self.run()

    def setup(self):
        pass



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
        data = clipboard.paste()
        return data

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

    def calculate_competitive_price(self, value):
        value = float(value)
        if self.mode == self.BUY:
            value = round(value + 0.01, 2)
        else:
            value = round(value - 0.01, 2)
        return value

    def buy_mode(self, value, competitive_price=None):
        margin_sell = self.calculate_margin_sell(value)
        min_sell = self.calculate_min_sell(value)
        cost = self.calculate_fees(value)
        if not competitive_price:
            competitive_price = self.calculate_competitive_price(value)
        self.sell_price = competitive_price
        clipboard.copy(competitive_price)

        table_data = [
            [
                "Target Sell",
                colored(comma_value(margin_sell), "grey", "on_red", attrs=["bold"]),
            ],
            ["Min Sell", comma_value(min_sell)],
            ["Cost", comma_value(cost)],
            ["Competitive Price", comma_value(competitive_price)],
        ]
        try:
            for item in table_data:
                print("{:<40}{}\n".format(item[0], item[1]))
        except Exception as e:
            print(e)            

        return [margin_sell, min_sell]


    def get_results(self, data):
        value = self.parse_value(data)
        if not value:
            return

        if self.mode == self.BUY:
            self.buy_mode(value)

        if self.mode == self.SELL:
            competitive_price = self.calculate_competitive_price(value)
            self.sell_price = competitive_price
            clipboard.copy(competitive_price)
            


    def run(self):
        t1 = Thread(target=self.user_input)
        t1.start()
        count = 0
        minute_in_seconds = 60
        idle_minutes = 5
        total_seconds = idle_minutes * minute_in_seconds

        self.display_header()

        while True:
            if self.__FINISH:
                t1.join()
                self.clear_term()
                quit()
            sleep(0.1)
            result = self.get_clip_data()

            if result == self.storage:
                sleep(0.1)
                continue
            if result == str(self.sell_price):
                sleep(0.1)
                continue

            self.storage = result
            self.clear_term()
            self.display_header()
            self.get_results(result)




Main()
