import argparse
import configparser
import datetime
import requests
import json


def patchStreamMetadata(config, value):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.patch(f'{api_url}/stream-metadata/', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print(r.status_code)
        print(r.content)


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

    if args.option == 'start':
        patchStreamMetadata(config, {
            'timers':[
                {
                    'start_time': getTimestamp(),
                    'end_time': None
                }
            ]
            })

    elif args.option == 'continue':
        patchStreamMetadata(config, {
            'timers':[
                {
                    'end_time': None
                }
            ]
            })

    elif args.option == 'stop':
        patchStreamMetadata(config, {
            'timers':[
                {
                    'end_time': getTimestamp(),

                }
            ]
            })
    elif args.option == 'reset':
        patchStreamMetadata(config, {
            'timers':[
                {
                    'start_time': None,
                    'end_time': None
                }
            ]
            })
    else:
        print('invalid option')
