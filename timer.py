import argparse
import configparser
import datetime
import signal

import requests
import json
import os.path
import subprocess


def load_timers():
    if os.path.isfile("timers.json"):
        with open("timers.json", "r") as f:
            timers = json.load(f)
        return timers
    return {}


def save_timers(timers):
    with open("timers.json", "w") as f:
        json.dump(timers, f)


def patch_timer(config, value, tid):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.patch(f'{api_url}/timers/{tid}', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)
    else:
        print(f'Failed to patch timer {tid} at {api_url}: {r.status_code} ({r.text})')


def make_timer(config, name):
    value = {
      "name": name,
      "start_time": None,
      "end_time": None
    }
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.post(f'{api_url}/timers', json=value, auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 201:
        return json.loads(r.content)
    else:
        print(f'Failed to make timer {name} to {api_url}: {r.status_code} ({r.text})')
        quit()


def get_timers(config):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.get(f'{api_url}/stream-metadata', auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 200:
        return json.loads(r.content)["timers"]
    else:
        print(f'Failed to get timers from {api_url}: {r.status_code} ({r.text})')


def delete_timer(config, tid):
    api_url = config['VAUHTIJUOKSU_API_URL']
    r = requests.delete(f'{api_url}/timers/{tid}', auth=(config['BASIC_AUTH_USER'], config['BASIC_AUTH_PW']))
    if r.status_code == 204:
        return
    else:
        print(f'Failed to delete timer {tid} from {api_url}: {r.status_code} ({r.text})')
        quit()


def get_timestamp(offset_str=""):
    time = datetime.datetime.utcnow()
    if os.path.isfile("offset.txt"):
        with open("offset.txt", "r") as f:
            sync_offset = float(f.read())
    else:
        sync_offset = 0
    time -= datetime.timedelta(seconds=sync_offset)
    if offset_str:
        o = datetime.datetime.strptime(offset_str, "%H:%M:%S")
        time -= datetime.timedelta(hours=o.hour, minutes=o.minute, seconds=o.second)
    return time.replace(tzinfo=datetime.timezone.utc).isoformat()


def main():
    configreader = configparser.ConfigParser()
    configreader.read('config.ini')

    config = configreader['TIMER']
    if not config:
        print('Please give config')
        quit()

    parser = argparse.ArgumentParser(description="Script for vauhtijuoksu timer")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", "--get", help="Get list of existing timers and write them to timers.json", action="store_true")
    group.add_argument("-n", "--new", help="Creates new timer(s) with name(s) <x> [<y> <z>...]", type=str, nargs='+')
    group.add_argument("-s", "--start", help="Starts timer(s) <x> [<y> <z>...]", type=str, nargs='+')
    group.add_argument("-p", "--pause", help="Pauses timer(s) <x> [<y> <z>...]", type=str, nargs='+')
    group.add_argument("-c", "--continue", dest="cont", help="Continues timer(s) <x> [<y> <z>...] like it was never paused.", type=str, nargs='+')
    group.add_argument("-r", "--reset", help="Reset timer(s) <x> [<y> <z>...] to 0", type=str, nargs='+')
    group.add_argument("-f", "--force", help="Force timer <x> to value HH:MM:SS", type=str, nargs=2)
    group.add_argument("-d", "--delete", help="Delete timer(s) <x> [<y> <z>...]", type=str, nargs='+')
    parser.add_argument("--sync", help="Start sync script after running", action="store_true")

    args = parser.parse_args()
    found_arg = False
    for a in vars(args).values():
        if a:
            found_arg = True
            break
    if not found_arg:
        print("Suply atleast one argument! info with --help")
        return
    do_actions(config, args)
    if args.sync:
        start_sync_script()


def do_actions(config, args):
    timers = {}

    if args.get:
        ts = get_timers(config)
        for timer in ts:
            timers[timer["name"]] = timer["id"]
        if len(timers.keys()) == 0:
            print("No timers found!")
        else:
            print(timers)
        save_timers(timers)
        return 0
    else:
        timers = load_timers()

    if args.new:
        for name in args.new:
            timer = make_timer(config, name)
            timers[timer["name"]] = timer["id"]
        save_timers(timers)
        return 0
    elif len(timers.keys()) == 0:
        print("No timers found!")
        return 1

    timestamp = get_timestamp()

    if args.start:
        for name in args.start:
            if name not in timers.keys():
                print(f'No such timer: {name}')
            else:
                patch_timer(config, {
                        'start_time': timestamp,
                        'end_time': None
                    }, timers[name])

    elif args.cont:
        for name in args.cont:
            if name not in timers.keys():
                print(f'No such timer: {name}')
            else:
                patch_timer(config, {
                        'end_time': None
                    }, timers[name])

    elif args.pause:
        for name in args.pause:
            if name not in timers.keys():
                print(f'No such timer: {name}')
            else:
                patch_timer(config, {
                        'end_time': timestamp
                    }, timers[name])

    elif args.reset:
        for name in args.reset:
            if name not in timers.keys():
                print(f'No such timer: {name}')
            else:
                patch_timer(config, {
                        'start_time': None,
                        'end_time': None
                    }, timers[name])

    elif args.delete:
        for name in args.delete:
            if name not in timers.keys():
                print(f'No such timer: {name}')
            else:
                delete_timer(config, timers[name])
        print("Timers deleted!")

    elif args.force:
        name = args.force[0]
        value = args.force[1]
        if name not in timers.keys():
            print(f'No such timer: {name}')
            return 1
        patch_timer(config, {
            'start_time': get_timestamp(value),
            'end_time': None
        }, timers[name])


def start_sync_script():
    if os.path.isfile("offset.txt"):
        with open("sync_process_pid.txt", "r") as f:
            p = f.read()
        try:
            os.kill(int(p), signal.SIGKILL)
        except ProcessLookupError:
            pass  # No process, no problem.
    subprocess.Popen(["python3", "timer_sync.py", "-l", str(10*6)], stdin=None, stdout=None, stderr=None)


if __name__ == "__main__":
    main()
