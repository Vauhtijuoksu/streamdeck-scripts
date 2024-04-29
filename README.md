# streamdeck-scripts

timer.py
========

Remever to make sure `config.ini` is up to date

```
Arguments:
  -h, --help            show this help message and exit
  -g, --get             Get list of existing timers and write them to timers.json
  -n NEW [NEW ...], --new NEW [NEW ...]
                        Creates new timer(s) with name(s) <x> [<y> <z>...]
  -s START [START ...], --start START [START ...]
                        Starts timer(s) <x> [<y> <z>...]
  -p PAUSE [PAUSE ...], --pause PAUSE [PAUSE ...]
                        Pauses timer(s) <x> [<y> <z>...]
  -c CONT [CONT ...], --continue CONT [CONT ...]
                        Continues timer(s) <x> [<y> <z>...] like it was never paused.
  -r RESET [RESET ...], --reset RESET [RESET ...]
                        Reset timer(s) <x> [<y> <z>...] to 0
  -f FORCE FORCE, --force FORCE FORCE
                        Force timer <x> to value HH:MM:SS
  -d DELETE [DELETE ...], --delete DELETE [DELETE ...]
                        Delete timer(s) <x> [<y> <z>...]
  --sync                Start sync script after running
```

use `--sync` on main timer start so the time sync script activates.
for example:

`python3 timer.py -s 1 --sync`
