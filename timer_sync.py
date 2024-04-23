import argparse
import json
from datetime import datetime, timezone
import requests
import time
import os

time_api_url = "https://api.dev.vauhtijuoksu.fi/stream-metadata"


def get_current_offset():
    pc_time = datetime.now(timezone.utc)
    start = time.time()
    r = requests.get(f'{time_api_url}')
    duration = time.time() - start
    if r.status_code == 200:
        timestr = json.loads(r.content)["server_time"]
        timestr = timestr[:timestr.find(".")+4] + timestr[len(timestr)-6:]
        # "2022-04-07T08:53:42.06717+02:00"
        # '2024-04-23T18:22:25.18142809+03:00'
        servertime = datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%f%z")
        diff = (pc_time - servertime).total_seconds() + duration/2
        return diff
    else:
        print(f'Failed to get timers from {time_api_url}: {r.status_code} ({r.text})')
        return 0


def check_sync(do_print):
    offsets = []
    for i in range(5):
        offsets.append(get_current_offset())
    offsets.sort()
    offset = offsets[2]  # median
    if do_print:
        print(f'{datetime.now()} Current offset: {offset :.2f}')
    with open("offset.txt", "w") as f:
        f.write(f'{offset :.2f}')


def main():
    parser = argparse.ArgumentParser(description="Script for vauhtijuoksu timer")
    parser.add_argument("-l", "--loop", help="How many times to loop (Default: 0 = forever)", type=int, default=1, const=0, nargs='?')
    parser.add_argument("-i", "--interval", help="How many minutes to sleep after each sync", type=int, default=10, nargs='?')
    parser.add_argument("-p", "--print", help="Prints offset", action="store_true")
    args = parser.parse_args()

    i = 0
    mypid = str(os.getpid())
    with open("sync_process_pid.txt", "w") as f:
        f.write(mypid)
    while True:
        check_sync(args.print)
        i += 1
        if i == args.loop:
            return
        for i in range(args.interval):
            time.sleep(60)
            with open("sync_process_pid.txt", "r") as f:
                p = f.read()
            if p != mypid:  # Newer process already running! Time to go!
                quit()



if __name__ == "__main__":
    main()
