from connect import get_driver, login, launch_game
from helpers import start_bot


def main():
    driver = get_driver()
    login(driver)
    launch_game(driver)
    start_bot(driver)


if __name__ == "__main__":
    main()
