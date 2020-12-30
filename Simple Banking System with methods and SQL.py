"""Simple Banking System"""
import random
import sys
import sqlite3


class Card:
    """contains info about client's cards"""

    def __init__(self):
        self.balance = 0
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.sql_table()

    def sql_table(self):
        """create table"""
        query = """CREATE TABLE IF NOT EXISTS card ( id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
        number TEXT NOT NULL UNIQUE, pin TEXT NOT NULL, balance INTEGER DEFAULT 0);"""
        self.cur.execute(query)
        self.conn.commit()

    def main_menu(self):
        """program main menu"""
        print('''
1. Create an account
2. Log into account
0. Exit
''')
        menu_item = int(input())
        if menu_item == 1:
            self.create_card()
        elif menu_item == 2:
            self.log_in()
        elif menu_item == 0:
            print('\nBye!')
            sys.exit()

    def create_card(self):
        """create card number with Luhn Algorithm and pin"""
        card_number_without_last_digit = [4, 0, 0, 0, 0, 0]
        while len(card_number_without_last_digit) != 15:
            card_number_without_last_digit.append(random.randint(0, 9))
        card_number_multipy = []
        for n, item in enumerate(card_number_without_last_digit):
            if n in (0, 2, 4, 6, 8, 10, 12, 14, 16):
                item = item * 2
            card_number_multipy.append(item)
        card_number_subtract_9 = []
        for i in card_number_multipy:
            if i > 9:
                i = i - 9
            card_number_subtract_9.append(i)
        while True:
            n = random.randint(0, 9)
            if (sum(card_number_subtract_9) + n) % 10 == 0:
                card_number_without_last_digit.append(n)
                break
        card_number = ''
        for i in card_number_without_last_digit:
            i = str(i)
            card_number = card_number + i

        pin = str(random.randint(0, 9999)).zfill(4)
        query = "INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);"
        self.cur.execute(query, (card_number, pin, self.balance))
        self.conn.commit()
        print('Your card has been created\nYour card number:\n{}\nYour card PIN:\n{}'.format(card_number, pin))
        self.main_menu()

    def log_in(self):
        """Log into account"""
        card_number = input('Enter your card number: ')
        card_pin = input('Enter your PIN: ')
        for i in self.cur.execute('SELECT * FROM card;'):
            if i[1] == card_number and i[2] == card_pin:
                print('\n' + 'You have successfully logged in!')
                self.card_menu(card_number, card_pin)
        else:
            print('Wrong card number or PIN!')
            self.main_menu()

    def card_menu(self, card_number, card_pin):
        """card menu when card number and pin is true"""
        print("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit
""")
        menu_item = int(input())
        if menu_item == 1:
            # print('Balance: {}'.format(self.balance))
            self.cur.execute("SELECT balance FROM card WHERE number = {};".format(card_number))
            balance = self.cur.fetchone()[0]
            print(balance)
            self.card_menu(card_number, card_pin)
        elif menu_item == 2:
            self.add_income(card_number, card_pin)
        elif menu_item == 3:
            self.do_transfer(card_number, card_pin)
        elif menu_item == 4:
            self.close_account(card_number)
        elif menu_item == 5:
            print('You have successfully logged out!')
            self.main_menu()
        elif menu_item == 0:
            print('\nBye!')
            sys.exit()
        else:
            self.main_menu()

    def add_income(self, card_number, card_pin):
        """add income"""
        print('Enter income:')
        income = int(input())
        # self.cur.execute("SELECT balance FROM card WHERE number = {};".format(card_number))
        # query = "UPDATE card SET balance = {} WHERE number = {};".format(balance + income, card_number)
        self.cur.execute("UPDATE card SET balance = balance + {} WHERE number = {};".format(income, card_number))
        self.conn.commit()
        self.card_menu(card_number, card_pin)

    def do_transfer(self, card_number, card_pin):
        """transfer operations"""
        print("\nTransfer\nEnter card number:")
        transfer_card_number = input()
        if card_number == transfer_card_number:
            print("You can't transfer money to the same account!")
            self.card_menu(card_number, card_pin)
        elif len(transfer_card_number) != 16 and transfer_card_number[0] != '4':
            print("Such a card does not exist.")
            self.card_menu(card_number, card_pin)
        else:
            transfer_card_number_without_last_digit = transfer_card_number[:-1]
            transfer_card_number_without_last_digit_int = list(map(int, transfer_card_number_without_last_digit))
            transfer_card_number_multy = []
            for n, item in enumerate(transfer_card_number_without_last_digit_int):
                if n in (0, 2, 4, 6, 8, 10, 12, 14, 16):
                    item = item * 2
                transfer_card_number_multy.append(item)
            transfer_card_number_subtract_9 = []
            for i in transfer_card_number_multy:
                if int(i) > 9:
                    i = int(i) - 9
                transfer_card_number_subtract_9.append(i)
            if (sum(transfer_card_number_subtract_9) + int(transfer_card_number[-1])) % 10 == 0:
                print("Enter how much money you want to transfer:")
                transfer_money = int(input())
                self.cur.execute("SELECT balance FROM card WHERE number = {};".format(card_number))
                balance = self.cur.fetchone()[0]
                if transfer_money > balance:
                    print('Not enough money!')
                    self.card_menu(card_number, card_pin)
                else:
                    # self.cur.execute("SELECT balance FROM card WHERE number = {};".format(card_number))
                    self.cur.execute("UPDATE card SET balance = balance - {} WHERE number = {};".format(transfer_money,
                                                                                                        card_number))
                    # self.cur.execute("SELECT balance FROM card WHERE number = {};".format(transfer_card_number))
                    self.cur.execute(
                        "UPDATE card SET balance = balance + {} WHERE number = {};".format(transfer_money,
                                                                                           transfer_card_number))
                    self.conn.commit()
                    print('Success!')
                    self.card_menu(card_number, card_pin)
            else:
                print("Probably you made a mistake in the card number. Please try again!")
                self.card_menu(card_number, card_pin)

    def close_account(self, card_number):
        """close and delete account"""
        self.cur.execute("DELETE FROM card WHERE number = {};".format(card_number))
        self.conn.commit()
        print("The account has been closed!")
        Card.main_menu(self)


user = Card()
user.main_menu()
