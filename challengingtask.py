# start of the programme

"""Importing all the modules that will be used."""
import os
import random
import sys
import click
import mysql.connector
import speech_recognition as sr
from gtts import gTTS
from mysql.connector import Error

"""
Setting up the SQL database, creating a table, and adding an admin account for demo.
"""

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",  # Enter your details.
        password="redraj200"  # Enter your password.
    )
except Error as err:
    print("Error:", err)

mycursor = mydb.cursor()


def execute_query(*args):
    try:
        mycursor.execute(*args)
        mydb.commit()
    except Error as err:
        print(err)


query = 'CREATE DATABASE bank_account'
try:
    mycursor.execute(query)
    mydb.commit()
except Error as err:
    pass

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",  # Enter your details
        password="redraj200",  # Enter your password
        database="bank_account"
    )
except Error as err:
    print("Error:", err)

mycursor = mydb.cursor()
create_table = """CREATE TABLE accounts (
    user_id INT PRIMARY KEY,
    name VARCHAR(45) NOT NULL,
    acc_no VARCHAR(45) UNIQUE,
    password VARCHAR(45) NOT NULL,
    aad_no INT UNIQUE,
    pan_no VARCHAR(45) UNIQUE,
    balance BIGINT(255))"""

execute_query(create_table)

admin_data = 'INSERT INTO accounts VALUES (0,"admin",0,"admin123",0,0,1000000)'
execute_query(admin_data)

"""
End of setting up the SQL database.
Setting up the functions for TTS and STT features next.
"""

r = sr.Recognizer()


def audio_input():
    with sr.Microphone() as source:
        try:
            audio = r.listen(source)
            global speech
            speech = r.recognize_google(audio).replace(" ", "")
            print("The input we received:", speech)
        except sr.RequestError as er:
            print("Could not request results;", er)
            input("Press enter to try again: ")
            audio_input()
        except sr.UnknownValueError:
            print("Couldn't hear you properly.")
            input("Press enter to try again: ")
            audio_input()


def speak(text, name):
    my_obj = gTTS(text=text, lang="en", slow=False)
    my_obj.save(name + ".mp3")
    os.system(name + ".mp3")


"""
Setting up other general functions.
"""


def check_pass_val(password):
    pas_val = True
    special_characters = ["$", "#", "@"]
    if not any(i.isupper() for i in password):
        print("You need to have at least one upper case letter in your password.")
        pas_val = False
    if not any(i.islower() for i in password):
        print("You need to have at least one lower case letter in your password.")
        pas_val = False
    if not any(i.isdigit() for i in password):
        print("You need to have at least one digit in your password.")
        pas_val = False
    if not any(i in special_characters for i in password):
        print("You need to have at least one special character(@,#,$) in your password.")
        pas_val = False
    if len(password) < 6:
        print("Your password needs to be at least six characters.")
        pas_val = False
    if len(password) > 20:
        print("Your password can't be more than twenty characters in length.")
    if not pas_val:
        password = input("Try again: ")
        check_pass_val(password)
    if pas_val:
        print("Valid password.")
        global valid_pas
        valid_pas = password


def get_bal(user_id):
    get_bal = "SELECT * FROM accounts WHERE user_id = %s"
    get_bal_val = (user_id,)
    mycursor.execute(get_bal, get_bal_val)
    user = mycursor.fetchall()
    for data in user:
        avail_balance = data[6]
    return avail_balance


"""
Start of the actual programme.
"""

speak("Welcome to the bank. Do you have an existing bank account?", "welcome")
print("Welcome to the bank. Do you have an existing bank account?")
answer = click.prompt("Type 0 for no or 1 for yes", type=bool)
if answer == 0:
    speak("Do you wish to create one?", "create_acc")
    answer = click.prompt("Type 0 for no or 1 for yes", type=bool)
    if answer == 0:
        speak("Understandable. Have a nice day.", "bye")
        print("Understandable. Have a nice day.")
        sys.exit()
    if answer == 1:
        # Getting the name.
        speak("Please enter your full name.", "name")
        name = input("Please enter your full name: ")

        # Creating a password.
        speak("Please create a password for your account. Make sure it is between six to twenty letters"
              ", has at least one lower-case character, at least one upper-case character, at least one digit"
              ", and at least one special character", "pass_ins")
        password = input("Please create a password for your account. "
                         "\nMake sure it is between six to twenty letters, "
                         "\nhas at least one lower-case character, "
                         "\nat least one upper-case character, "
                         "\nat least one digit, "
                         "\nand at least one special character (@,$, or #)"
                         "\nType here: ")
        check_pass_val(password)
        # Double-checking the password.
        pass_con = input("Please enter the password again to confirm it: ")
        match = False
        while not match:
            if valid_pas == pass_con:
                match = True
                print("Password confirmed.")
            if not valid_pas == pass_con:
                pass_con = input("The passwords did not match, please type it again: ")

        # Getting Aadhaar number information.
        speak("Please press enter and say your Aadhaar number.", "aad_no")
        input("Please press enter and say your Aadhaar number.")
        audio_input()
        print("Your Aadhaar number is:", speech)
        speak("Is this correct?", "aad_con")
        print("Is this correct?")
        aad_con = click.prompt("Type 0 for no or 1 for yes", type=bool)
        if aad_con == 1:
            aad_no = speech
        if aad_con == 0:
            aad_no = input("Please type your Aadhaar number: ")

        # Getting the PAN information.
        speak("Please press enter and say your PAN number.", "aad_no")
        input("Please press enter and say your PAN number.")
        audio_input()
        speech = speech.upper()
        print("Your PAN number is:", speech)
        speak("Is this correct?", "pan_con")
        print("Is this correct?")
        aad_con = click.prompt("Type 0 for no or 1 for yes", type=bool)
        if aad_con == 1:
            pan_no = speech
        if aad_con == 0:
            pan_no = input("Please type your PAN number: ")

        mycursor.execute("SELECT * FROM accounts")
        user = mycursor.fetchall()
        for data in user:
            user_id = data[0]

        # Adding the account.
        add_acc = "INSERT INTO accounts (user_id, name, acc_no, password, aad_no, pan_no, balance) VALUES (%s,%s,%s," \
                  "%s,%s,%s,2000) "
        add_acc_val = (
            user_id + 1, name, "ABCD" + str(random.randrange(10000000000000, 100000000000000)), valid_pas, aad_no,
            pan_no
        )
        execute_query(add_acc, add_acc_val)

        # Giving back the created information to the user.
        acc_info = "SELECT * FROM accounts WHERE user_id = %s"
        acc_info_val = (user_id + 1,)
        execute_query(acc_info, acc_info_val)
        user = mycursor.fetchall()
        for data in user:
            print("Your account has been created. The details are as follows:"
                  "\nYour ID:", data[0],
                  "\nYour name:", data[1],
                  "\nYour account number:", data[2],
                  "\nYour password:", "*" * len(data[3]),
                  "\nYour Aadhaar number:", data[4],
                  "\nYour PAN number:", data[5],
                  "\nWe will check your provided details and confirm your account."
                  )

if answer == 1:
    pass

"""
The login process
"""

login = False
while not login:
    speak("Please enter your ID to login.", "login")
    login_id = click.prompt("Please enter your ID to login", type=int)
    login_password = input("If you have entered the wrong ID, press 0; else please enter your password: ")
    if login_password == "0":
        continue
    else:
        isCorrect = False
        chances = 3
        while chances > 0 and not isCorrect:
            check_pas = "SELECT * FROM accounts WHERE user_id = %s"
            check_pas_val = (login_id,)
            mycursor.execute(check_pas, check_pas_val)
            user = mycursor.fetchall()
            for data in user:
                if login_password == data[3]:
                    print("Password matched.")
                    isCorrect = True
                    login = True
                else:
                    chances -= 1
                    print("Wrong password. You have {} chance(s) left.".format(chances))
            if chances == 0:
                sys.exit()
            if not isCorrect:
                login_password = input("Please enter your password: ")

# Starting the bank process.
process = True
speak("What do you want to do?"
      "Type 1 to inquire balance."
      "Type 2 to withdraw money."
      "Type 3 to deposit money."
      "Type 4 to transfer money."
      "Type 5 to modify your bank account."
      "Type 6 to call an employee from our bank."
      "Type 0 to exit the programme.", "list")
while process:
    choice = click.prompt("""
*************************
* 1 | Inquire balance.  *
*************************
* 2 | Withdraw money.   *
*************************
* 3 | Deposit money.    *
*************************
* 4 | Transfer money.   *
*************************
* 5 | Modify account.   *
*************************
* 6 | Call an employee. *
*************************
* 0 | Exit the process. *
*************************
Type here""", type=click.IntRange(0, 6))

    if choice == 1:
        avail_balance = get_bal(login_id)
        speak("Your balance is rupees {}".format(avail_balance), "bal")
        print("Your balance is Rs", avail_balance)

    if choice == 2:
        speak("Enter the amount you want to withdraw or type 0 to go back. "
              "You can withdraw 50,000 at maximum in one go.", "withdraw")
        with_mon = click.prompt("""Enter the amount you want to withdraw or type 0 to go back. 
You can withdraw 50,000 at maximum in one go""", type=click.IntRange(0, 50000))
        if with_mon == 0:
            continue
        else:
            avail_balance = get_bal(login_id)
            if avail_balance < with_mon:
                print("Not enough balance.")
            if avail_balance >= with_mon:
                del_money = "UPDATE accounts SET balance = %s WHERE user_id = %s"
                del_money_val = (avail_balance - with_mon, login_id)
                execute_query(del_money, del_money_val)
                print("Transaction successful.")
                avail_balance = get_bal(login_id)
                speak("You have rupees {} remaining in your account.".format(avail_balance), "withrem")
                print("You have Rs {} remaining in your account.".format(avail_balance))

    if choice == 3:
        speak("Enter the amount you want to deposit or press 0 to go back. "
              "You can deposit 10,00,000 at maximum in one go", "deposit")
        dep_mon = click.prompt("""Enter the amount you want to deposit or press 0 to go back.
You can deposit 10,00,000 at maximum in one go""", type=click.IntRange(0, 1000000))
        if dep_mon == 0:
            continue
        else:
            avail_balance = get_bal(login_id)
            add_mon = "UPDATE accounts SET balance = %s WHERE user_id = %s"
            add_mon_val = (avail_balance + dep_mon, login_id)
            execute_query(add_mon, add_mon_val)
            speak("Transaction successful", "dep")
            print("Transaction successful. We will send an employee to collect the money soon.")
            avail_balance = get_bal(login_id)
            speak("You have Rs {} remaining in your account.".format(avail_balance), "deprem")
            print("You have Rs {} remaining in your account.".format(avail_balance))

    if choice == 4:
        speak("Enter the ID of the receiving account", "rec_id")
        rec_id = click.prompt("Enter the ID of the receiving account", type=int)
        trans = "SELECT * FROM accounts WHERE user_id = %s"
        trans_val = (rec_id,)
        mycursor.execute(trans, trans_val)
        user = mycursor.fetchall()
        for data in user:
            speak(
                "The details of the account you to transfer money to are: Account holder name: {} Account number: {}".format(
                    data[1], data[2]), "details")
            print("The details of the account you to transfer money to are:",
                  "\nAccount holder name:", data[1],
                  "\nAccount number:", data[2])
        print("Is this correct?")
        trans_con = click.prompt("Type 0 for no or 1 for yes", type=bool)
        if trans_con == 0:
            continue
        if trans_con == 1:
            speak("Enter the amount you want to transfer or type 0 to go back. "
                  "You can transfer 50,000 at maximum in one go", "trans_mon")
            trans_mon = click.prompt("""Enter the amount you want to transfer or type 0 to go back. 
You can transfer 50,000 at maximum in one go""", type=click.IntRange(0, 50000))
            if trans_mon == 0:
                continue
            else:
                speak("Are you sure you want to transfer Rs {} to {}'s account?".format(trans_mon, data[1]),
                      "trans_con")
                print("Are you sure you want to transfer Rs", trans_mon, "to", data[1], "\'s account?")
                trans_con = click.prompt("Type 0 for no or 1 for yes", type=bool)
                if trans_con == 0:
                    continue
                if trans_con == 1:
                    trans_bal = get_bal(login_id)
                    if trans_bal >= trans_mon:
                        rec_bal = get_bal(rec_id)
                        add_mon = "UPDATE accounts SET balance = %s WHERE user_id = %s"
                        add_mon_val = (rec_bal + trans_mon, rec_id)
                        execute_query(add_mon, add_mon_val)

                        del_money = "UPDATE accounts SET balance = %s WHERE user_id = %s"
                        del_money_val = (trans_bal - trans_mon, login_id)
                        execute_query(del_money, del_money_val)
                        avail_balance = get_bal(login_id)
                        speak("Transaction successful. Your balance is Rs {}".format(avail_balance), "con")
                        print("Transaction successful. Your balance is Rs", avail_balance)
                    else:
                        print("Not enough balance.")

    if choice == 5:
        speak("Type 0 to change your name or type 1 to change your password.", "mod")
        change = click.prompt("""
***********************
* 0 | Change name     *
***********************
* 1 | Change password *
***********************
Type here""", type=bool)
        if change == 0:
            speak("Please enter your new name", "new_name")
            new_name = input("Please enter your new name:")
            change_name = "UPDATE accounts SET name = %s WHERE user_id = %s"
            change_name_val = (new_name, login_id)
            execute_query(change_name, change_name_val)

        if change == 1:
            speak("Please create a new password.", "new_pas")
            new_pas = input("Please create a new password. "
                            "\nMake sure it is between six to twenty letters, "
                            "\nhas at least one lower-case character, "
                            "\nat least one upper-case character, "
                            "\nat least one digit, "
                            "\nand at least one special character (@,$, or #)"
                            "\nType here: ")
            check_pass_val(new_pas)
            new_pas_con = input("Please enter the password again to confirm it: ")
            match = False
            while not match:
                if valid_pas == new_pas_con:
                    match = True
                    print("Password confirmed.")
                    change_pas = "UPDATE accounts SET password = %s WHERE user_id = %s"
                    change_pas_val = (valid_pas, login_id)
                    execute_query(change_pas, change_pas_val)
                if not valid_pas == new_pas_con:
                    new_pas_con = input("The passwords did not match, please type it again: ")

    if choice == 6:
        speak("You will be contacted by an employee soon.", "call")
        print("You will be contacted by an employee soon.")
        sys.exit()

    if choice == 0:
        print("Thank you for using our service.")
        process = False
