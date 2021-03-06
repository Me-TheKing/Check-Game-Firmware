import re
# import sys
import time
import requests
from bs4 import BeautifulSoup as Bs
from colorama import Fore, init

init(autoreset=True)
ver = 1.01


def result(playable, current_fw, game_day, game_month, game_year):
    if playable == "Yes":
        print(f'{Fore.GREEN}\nInitial game release[dd/mm/yyyy]: {game_day} {game_month} {game_year}')
        print(f'{Fore.GREEN}Playable on {current_fw[0]}\n')
    elif playable == "No":
        print(f'{Fore.RED}\nInitial game release[dd/mm/yyyy]: {game_day} {game_month} {game_year}')
        print(f'{Fore.RED}"Unfortunately the game requires a later firmware than {current_fw[0]}\n')
    else:
        print(f'{Fore.YELLOW}\nInitial game release[dd/mm/yyyy]: {game_day} {game_month} {game_year}')
        print(f'{Fore.YELLOW}"Unplayable on {current_fw[0]} unless the game was built on an older SDK\n')


def loop_ans(question, ans_lst):
    ans = input(question).lower()
    # to convert any num to str
    ans_lst = list(map(str, ans_lst))

    while ans not in ans_lst:
        print("Invalid input...")
        ans = input(question).lower()

    return ans


def main():
    month = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
             "September": 9, "October": 10, "November": 11, "December": 12}

    with open("fw release date.ini", "r") as file:
        firmware = file.readlines()
        for num, firmware_num in enumerate(firmware):
            print(f'{Fore.CYAN}{num + 1}. {firmware_num.split(" ")[0]}')

        # latest_fw = False
        user_input = loop_ans("Choose a firmware[number exp: 1 or 2] or Q to quit:",
                              list(range(1, len(firmware) + 1)) + ['q'])
        if user_input == "q":
            print(f'{Fore.CYAN}Thanks for using CGFw (Check Game Firmware) v{ver} by @OfficialAhmed0. Bye!')
            time.sleep(3)
            raise SystemExit

        user_input = int(user_input) - 1

        # if user_input == 0:  # This is the latest fw
        #     latest_fw = True

        if len(firmware) > user_input >= 0:  # There is a later fw
            try:
                later_fw = firmware[user_input - 1].split(" ")
                # later_fw_ver = later_fw[0]
                later_fw_year = int(later_fw[3])
                later_fw_month = month[later_fw[1]]
                later_fw_day = int(later_fw[2])
            except Exception as e:
                print("Wrong form of the latest firmware info. Error[dev]:", e)

        # From selected firmware
        current_fw = firmware[user_input].split(" ")
        # current_fw_year = int(current_fw[3])
        # current_fw_month = month[current_fw[1]]
        # current_fw_day = int(current_fw[2])

        GameTitle = input("Enter Game title: ")
        search = GameTitle.replace(" ", "+") + "+Playstation+4+store"
        google = "https://www.google.com/search?hl=en&sxsrf=ALeKk008zPfPySZ73hbkXUMf_Az50hGTMA%3A1600888031936&ei=35xrX7G9OKPuxgOlyKvYBw&q=" + search
        read = requests.get(google).text
        soup = Bs(read, "html.parser")

        GameLink = []
        # Get game link for Playstation 4 store
        for link in soup.find_all('a'):
            check = link.get('href')
            if "https://store.playstation.com/" in check:
                link = check[check.find("=") + 1: check.find("&")]
                GameLink.append(link)

        if len(GameLink) == 0:
            print("Cannot find", GameTitle, "in PlayStation store")
            main()
        else:  # Try all links for a valid one
            foundReleaseDate = False
            counter = 0
            Game_year, Game_month, Game_day = 0, 0, 0
            while (foundReleaseDate == False and counter < len(GameLink)):
                read = requests.get(GameLink[counter]).text
                data = read.split(",")
                for info in data:
                    if "releaseDate" in info:
                        starting_point = len('"releaseDate":"')
                        date = re.findall("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]", info[starting_point:])
                        Game_release_date = date[0].split("-")
                        Game_year = int(Game_release_date[0])
                        Game_month = int(Game_release_date[1])
                        Game_day = int(Game_release_date[2])
                        foundReleaseDate = True
                        break
                counter += 1
            if foundReleaseDate == True:
                """
                Check if the game was released before a later fw release date 
                if selected firmware's not the latest
                otherwise all games would be playable
                """
                # if latest_fw == False:  # If this is not the latest official firmware available
                if Game_year == later_fw_year:
                    if Game_month <= later_fw_month:
                        if Game_day <= later_fw_day:
                            result("Yes", current_fw, Game_day, Game_month, Game_year)
                        else:
                            result("Yes", current_fw, Game_day, Game_month, Game_year)
                    else:
                        result("Not sure", current_fw, Game_year, Game_month, Game_day)
                elif Game_year < later_fw_year:
                    result("Yes", current_fw, Game_day, Game_month, Game_year)
                else:
                    result("No", current_fw, Game_year, Game_month, Game_day)

                # else:  # If this is the latest official firmware available
                #     result("Yes", current_fw, Game_day, Game_month, Game_year)
            else:
                print("Cannot find release date for", GameTitle)
        main()


main()
