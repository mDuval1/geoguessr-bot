import time
from selenium.webdriver.common.by import By
from os import system
import json
from typing import Dict
from selenium.webdriver.chrome.webdriver import WebDriver

SLEEP_BETWEEN_COUNTRY_ATTEMPTS = 2


def get_country_code_to_country_name_dict():
    with open("./country_codes.json", "r") as f:
        data = json.load(f)
    return {k.split("country.country-")[1]: v for k, v in data.items()}


CODE_TO_COUNTRY: Dict[str, str] = get_country_code_to_country_name_dict()


def start_bot(driver: WebDriver):
    while True:
        events = read_events(driver)
        nb_streak_events = len(get_streak_events(driver, events))
        if nb_streak_events > 0:
            # say_current_country(driver, get_streak_event(driver, events))
            send_current_country(driver, get_streak_event(driver, events))
        time.sleep(SLEEP_BETWEEN_COUNTRY_ATTEMPTS)


def say_current_country(driver: WebDriver, streak_event):
    current_round = get_last_position(driver, streak_event)
    streak_location_code = current_round["streakLocationCode"]
    country = CODE_TO_COUNTRY[streak_location_code]
    system(f"say {country}")
    print(f"Country is {country}")


BASE_CODE = """
    const map = document.getElementsByClassName('guess-map')[0];
    function FindReact(dom, traverseUp = 0) {
        const key = Object.keys(dom).find((key) => {
            return (
            key.startsWith("__reactFiber$") || // react 17+
            key.startsWith("__reactInternalInstance$")
            ); // react <17
        });
        const domFiber = dom[key];
        if (domFiber == null) return null;

        // react 16+
        const GetCompFiber = (fiber) => {
            //return fiber._debugOwner; // this also works, but is __DEV__ only
            let parentFiber = fiber.return;
            while (typeof parentFiber.type == "string") {
            parentFiber = parentFiber.return;
            }
            return parentFiber;
        };
        let compFiber = GetCompFiber(domFiber);
        for (let i = 0; i < traverseUp; i++) {
            compFiber = GetCompFiber(compFiber);
        }
        return compFiber;
    };
    const mapFiber = FindReact(map);
    """


def get_code_to_execute(streak_location_code: str):
    return (
        BASE_CODE
        + f'mapFiber.memoizedProps.onRegionSelected("{streak_location_code}");'
    )


def submit_guess(driver: WebDriver):
    perform_guess_button = driver.find_element(
        By.XPATH, "//button[@data-qa='perform-guess']"
    )
    perform_guess_button.click()
    time.sleep(1)

    to_next_round = driver.find_element(
        By.XPATH, "//button[@data-qa='close-round-result']"
    )
    to_next_round.click()
    time.sleep(1)


def send_current_country(driver: WebDriver, streak_event):
    current_round = get_last_position(driver, streak_event)
    streak_location_code = current_round["streakLocationCode"]
    driver.execute_script(get_code_to_execute(streak_location_code))
    time.sleep(0.2)
    submit_guess(driver)


def get_last_position(driver: WebDriver, streak_event):
    request_id = streak_event["params"]["requestId"]
    event_response = driver.execute_cdp_cmd(
        "Network.getResponseBody", {"requestId": request_id}
    )
    event_body = json.loads(event_response["body"])
    current_round = event_body["rounds"][-1]
    return current_round


def get_game_id(driver: WebDriver) -> str:
    current_url = driver.current_url
    game_id = current_url.split("/")[-1]
    return game_id


def read_events(driver: WebDriver):
    browser_log = driver.get_log("performance")
    return list(map(process_browser_log_entry, browser_log))


def process_browser_log_entry(entry):
    return json.loads(entry["message"])["message"]


def get_streak_events(driver: WebDriver, events):
    game_id = get_game_id(driver)
    return [
        event
        for event in events
        if "Network.responseReceived" in event.get("method", "")
        and event.get("params", {}).get("response", {}).get("url", "")
        in [
            "https://www.geoguessr.com/api/v3/games/streak",
            f"https://www.geoguessr.com/api/v3/games/{game_id}?client=web",
        ]
    ]


def get_streak_event(driver: WebDriver, events):
    streak_events = get_streak_events(driver, events)
    if len(streak_events) == 0:
        write_events(events)
        raise Exception("No streak events found")
    return streak_events[-1]


def write_events(events):
    with open("events.txt", "w") as f:
        for event in events:
            f.write(f"{event}\n")
