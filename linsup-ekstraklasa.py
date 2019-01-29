#!/usr/bin/env python

import json
import datetime
import argparse
from termcolor import colored, cprint


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
         "--log",
        help="Print events.",
        dest="log",
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--limit",
        help="Limit log entries",
        dest="limit",
        type=int,
        default=0
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Input event. Provide participants as a list.",
        dest="input",
        type=str,
        nargs="+"
    )
    parser.add_argument(
        "-d",
        "--date",
        help="Date of the event. Today if not provided",
        dest="date",
        default=datetime.datetime.now().strftime("%Y/%m/%d")
    )
    return parser.parse_args()


class Event:
    eid_counter = 0
    def __init__(self, date, games):
        Event.eid_counter += 1
        self.eid = Event.eid_counter
        self.date = date
        self.games = games
        self.mistrz = self._get("mistrz")
        self.pastuch = self._get("pastuch")
        self.name = "#{} {}".format(self.eid, self.date)

    def _get(self, mode):
        teams = []
        for game in self.games:
            team = game["winner"]
            if mode == "pastuch":
                if team == "team_a":
                    team = "team_b"
                else:
                    team = "team_a"
            teams.append(set(game[team]))
        if set.intersection(*teams):
            result = set.intersection(*teams)
            # convert to str
            result = next(iter(result))
        else:
            result = None
        return result


def laod_events(data):
    events = []
    #print("======== LOADING ========")
    for eid, event in data.items():
        #print("loading data for event #{}".format(eid))
        events.append(Event(event["date"], event["games"]))
    #print("========= DONE ==========")
    return events


def log_events(events, limit=0):
    for event in events[-limit:]:
        cprint(event.name, "yellow")
        if event.mistrz is not None: cprint("Mistrz: {}".format(event.mistrz))
        if event.pastuch is not None: cprint("Pastuch: {}".format(event.pastuch))
        for game in event.games:
            if game["winner"] == "team_a":
                color_a = "green"
                color_b = "red"
            else:
                color_a = "red"
                color_b = "green"
            vs = (colored(game["team_a"], color_a), colored("vs."), colored(game["team_b"], color_b))
            flawless_victory = (colored("FLAWLESS VICTORY!", "red", attrs=['reverse', 'blink', 'bold']),)
            if game["zero"]:
                sequence = vs + flawless_victory
            else:
                sequence = vs
            print(" ".join(sequence))


def add_event(date, players, events):
    teams = get_teams(players)
    matches = get_matches(teams)
    games = []
    game_counter = 0
    for match in matches:
        game_counter += 1
        #game = {"team_a":"", "team_b":"", "winner":"", "zero":False}
        game = {}
        game["team_a"] = match[0]
        game["team_b"] = match[1]
        print("======== GAME #{} ========".format(game_counter))
        print("a: {} VS. b: {}".format(game["team_a"], game["team_b"]))
        game["winner"] = input_winner("Who won? (a/b) ")
        game["zero"] = input_zero("Flawless victory? (y/n) ")
        games.append(game)
    events.append(Event(date, games))


def save_events(events):
    data = {}
    for event in events:
        event_params= {}
        event_params["date"] = event.date
        event_params["games"] = event.games
        data[Event.eid_counter] = event_params
    with open('events.json', 'w') as file:
        json.dump(data, file, sort_keys=True, indent=4)


def get_teams(input_list):
    result = []
    for index1 in range(len(input_list)):
            for index2 in range(index1+1,len(input_list)):
                    result.append([input_list[index1],input_list[index2]])
    return result


def get_matches(input_list):
    result = []
    for index1 in range(len(input_list)):
            for index2 in range(index1+1,len(input_list)):
                    team_a = input_list[index1]
                    team_b = input_list[index2]
                    if not bool(set(team_a) & set(team_b)):
                        result.append([input_list[index1],input_list[index2]])
    return result


def input_zero(prompt):
    while True:
        try:
           return {"y":True,"n":False}[input(prompt).lower()]
        except KeyError:
           print("Invalid input please enter y or n!")


def input_winner(prompt):
    while True:
        try:
           return {"a":"team_a" ,"b":"team_b"}[input(prompt).lower()]
        except KeyError:
           print("Invalid input please enter a or b!")


def main():
    args = parse_args()
    with open("events.json") as file:
        data = json.load(file)
    events = laod_events(data)
    if args.input:
        add_event(args.date, args.input, events)
        save_events(events)
    if args.log:
        log_events(events, args.limit)


if __name__ == "__main__":
    main()
