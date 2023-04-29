import argparse
import configparser
import datetime
import requests
import json

timers = {
    "1": "6a9a5188-980c-4845-9841-650b5006c7f0",
    "2": "726de5ee-686a-4ce4-8a90-6df2012e9aea"
}

def patchTimer(config, value, id):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.patch(f'{api_url}/timers/{id}', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print(r.status_code)
        print(r.text)


def getTimestamp():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


if __name__ == "__main__":
    configReader = configparser.ConfigParser()
    configReader.read('config.ini')

    config = configReader['TIMER']
    if not config:
        print('Please give config')
        quit()

    parser = argparse.ArgumentParser(description="Script for vauhtijuoksu timer")
    parser.add_argument("option", help="start/stop/reset/continue", type=str)

    args = parser.parse_args()

    if args.option == 'start1':
        patchTimer(config, {
                'start_time': getTimestamp(),
                'end_time': None
            }, timers['1'])

    elif args.option == 'start2':
        patchTimer(config, {
                'start_time': getTimestamp(),
                'end_time': None
            }, timers['2'])

    elif args.option == 'startboth':
        patchTimer(config, {
                'start_time': getTimestamp(),
                'end_time': None
            }, timers['1'])
        patchTimer(config, {
                'start_time': getTimestamp(),
                'end_time': None
            }, timers['2'])

    elif args.option == 'continue1':
        patchTimer(config, {
                'end_time': None
            }, timers['1'])

    elif args.option == 'continue2':
        patchTimer(config, {
                'end_time': None
            }, timers['2'])
    elif args.option == 'stop1':
        patchTimer(config, {
            'end_time': getTimestamp()
            }, timers['1'])
    elif args.option == 'stop2':
        patchTimer(config, {
            'end_time': getTimestamp()
            }, timers['2'])
    elif args.option == 'reset1':
        patchTimer(config, {
                'start_time': None,
                'end_time': None
            }, timers['1'])
    elif args.option == 'reset2':
        patchTimer(config, {
                'start_time': None,
                'end_time': None
            }, timers['2'])
    elif args.option == 'resetboth':
        patchTimer(config, {
                'start_time': None,
                'end_time': None
            }, timers['1'])
        patchTimer(config, {
                'start_time': None,
                'end_time': None
            }, timers['2'])
    else:
        print('invalid option')
