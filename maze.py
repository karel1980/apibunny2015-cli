
import requests
import json
import fileinput
import yaml
import sys

class MazeRunner:
    def __init__(self, base, start):
        self.base = base
        self.start = start
        self.history = []
        self.cache = {} # Assuming no state changes
        self._load(start)

    def reset(self):
        self.history = []
        self.current = start
        self.cache = {}

    def status(self):
        return self.current

    def write_pretty_status(self, out):
        yaml.safe_dump(self.current, out, encoding='utf-8', allow_unicode=True)

    def back(self):
        if len(self.history) > 1:
            self.history = self.history[:-1]
            self.current = self.history[-1]

    def follow(self, link):
        if link not in self.current['_links']:
            print "nu-uh"
            return

        self._load(self.current['_links'][link]['href'])

    def _load(self, path):
        text = requests.get(self.base + path).text
        try:
            self.current = json.loads(text)
        except:
            print "Bummer, not valid json?: " + text
            return
        self.history.append(self.current)

def print_usage():

    print "Available commands: "
    print " go <link>      # Follows a link"
    print " back           # Go back (e.g. after collecting an egg, but can be used to backtrack"
    print " history        # Print your trail"
    print " n,e,s,w        # Shortcuts for `go doors:{north,east,south,west}`"
    print " quit           # Quit playing"


def next_round(mazerunner):
    """ Print game status, ask for command and execute it
        Returns False if cli should exit 
    """
    mazerunner.write_pretty_status(sys.stdout)
    if 'start' in mazerunner.status().get("_links", {}):
        print "Example to get you started: 'go start'"
    print " command or 'help' > ", 
    cmd = raw_input()
    print

    if cmd == None:
        return False

    cmd = cmd.strip().split(" ")
    if cmd[0] == "help":
        print_usage()
    elif cmd[0] == "quit":
        return False

    elif cmd[0] == "back":
        mazerunner.back()
    elif cmd[0] == "go":
        # Todo: handle 'go abandon' separately -> open in browser instead
        mazerunner.follow(cmd[1])

    # shortcuts
    elif cmd[0] == "n":
        mazerunner.follow("doors:north")
    elif cmd[0] == "e":
        mazerunner.follow("doors:east")
    elif cmd[0] == "s":
        mazerunner.follow("doors:south")
    elif cmd[0] == "w":
        mazerunner.follow("doors:west")

    else:
        print "Unknown commmand"

    if len(mazerunner.current.get("_links",{})) == 0:
        mazerunner.write_pretty_status(sys.stdout)
        print
        print "There's no way to go but back"

    print
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        mazepath = open(".maze").readline().strip()
    else:
        mazepath = sys.argv[1]
        with open(".maze", 'w') as dotmaze:
            dotmaze.write(sys.argv[1])

    m = MazeRunner("http://apibunny.com", mazepath)

    done = False
    while not done:
        done = not next_round(m)

    print "Byebye"
