import re, os, time, threading, random, ctypes

try:
    import httpx, yaml
    from pystyle import Colors, Colorate, Center
except ImportError as e:
    print("Looks like you forgot to install the requirements!")
    print("use \"python -m pip install -r requirements.txt\" to install")
    print("Error: " + str(e))


class KCScraper:
    def __init__(self):

        self.proxies = set()
        self.goodSites = set()
        self.siteList = []
        self.timeout = ""
        self.proxyCount = 0
        self.clearingCNT = ""
        self.clearingProxy = ""
        self.proxyDelimiter = ""
        self.randomUseragent = ""
        self.dictReplacements = {"&colon": ":", "</td><td>": ":"}

        self.start = 0

        self.white = Colors.light_gray
        self.color = Colors.StaticMIX([Colors.purple, Colors.blue])
        self.clear = "cls" if os.name == "nt" else "clear"

        self.prefix_warning = f"{self.white}[{self.color}!{self.white}] {self.color}"
        self.prefix_plus = f"{self.white}[{Colors.green}+{self.white}] {self.color}"
        self.prefix_error = f"{self.white}[{Colors.red}!{self.white}] {self.color}"
        self.prefix_info = f"{self.white}[{self.color}^{self.white}] {self.color}"

        self.uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
        ]

    def main(self):
        self.printLogo()
        print()
        self.terminal()

        config, self.clearingCNT, self.clearingProxy, self.randomUseragent, threads, self.timeout = self.getSettings()

        self.start = time.time()

        # dispatcher
        with open(config) as sites:
            self.siteList = sites.readlines()
            if os.name == "nt":
                threading.Thread(target=self.terminalthread).start()

            while len(self.siteList) > 0:
                if self.activethreads() <= threads:
                    threading.Thread(target=self.scrape, args=[self.siteList[0]]).start()
                    self.siteList.pop(0)

            while self.activethreads() > 0:
                self.terminal(
                    f"| Waiting for threads to finish | active threads {self.activethreads()} | Proxies {self.proxyCount} | Time {time.time() - self.start:.2f}s")

            self.terminal()

        print()

        lenproxies = len(self.proxies)
        print(f"{self.prefix_info} Removed {self.color}{self.proxyCount - lenproxies} {self.white}Duplicates\n")
        print(f"{self.prefix_info} Remaining Proxies: {self.color}{lenproxies}{self.white}\n")
        print(f"{self.prefix_info} Writing {self.color}Proxies\n")

        with open("proxies.txt", "w") as output:
            for i in self.proxies:
                output.write(i.replace("\n", "") + "\n")

        if self.clearingCNT or self.clearingProxy:
            print(f"{self.prefix_info} Removing {self.color}bad Websites\n")
            with open(config, "w") as inp:
                for site in self.goodSites:
                    inp.write(site + "\n")

        self.terminal()

        print(f"{self.prefix_info} Finished in {self.color}{time.time() - self.start:.2f}s{self.white}!\n")
        print("You can now close the tab")
        input("")

    def scrape(self, site: str):

        site = site.replace("\n", "")
        try:
            with httpx.Client(
                    http2=True,
                    headers={
                        "accept-language": "en",
                        "user-agent": random.choice(self.uas) if self.randomUseragent else self.uas[0],
                    },
                    follow_redirects=True,
            ) as client:
                r = client.get(site, timeout=self.timeout).text
        except:
            print(f"{self.prefix_warning} Failed connecting to {self.color}{site}")
            if not self.clearingCNT:
                self.goodSites.add(site)
        else:
            self.goodSites.add(site)

            r = re.sub(r"<[^/][^>]*>", self.proxyDelimiter, r)
            r = re.sub(r"</[^>]*>", "", r)
            r = r.replace("\n", self.proxyDelimiter)
            r = r.replace(" ", self.proxyDelimiter)

            while r.count(self.proxyDelimiter*2) > 0:
                r = r.replace(self.proxyDelimiter*2, self.proxyDelimiter)

            locProxies = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}" +
                                    self.proxyDelimiter +
                                    r"\d{1,5}\b", KCScraper.replaceAll(self, r))
            length = len(locProxies)
            print(f"{self.prefix_plus} Scraped {self.color}{length}{self.white} from {self.color}{site}")
            self.proxyCount += length
            self.proxies = self.proxies | set(locProxies)
            if self.clearingProxy and length == 0:
                self.goodSites.remove(site)

    def replaceAll(self, string: str) -> str:
        for key, value in self.dictReplacements.items():
            string = string.replace(key, value)

        return string

    def getSettings(self) -> tuple:
        with open("settings.yaml") as setting:
            settings = yaml.safe_load(setting.read())

        presets = settings["presets"]
        self.clearingCNT = settings["removeWebsites"]
        self.clearingProxy = settings["removeProxyless"]
        self.randomUseragent = settings["randomUseragent"]
        threads = settings["threads"]
        self.timeout = settings["timeout"]
        self.proxyDelimiter = settings["proxyDelimiter"]

        yes = ["yes", "y", "ye"]
        no = ["no", "n", "nah"]

        if presets == "?":
            presets = input(f"{self.prefix_info} Use presets [y/n] {self.white}>> {self.color}")
            if presets in yes:
                os.system("cls")
                self.printLogo()
                print(Colorate.Diagonal(
                    Colors.DynamicMIX([Colors.dark_gray, Colors.StaticMIX([Colors.purple, Colors.blue])]),
                    Center.XCenter("\n[1] HTTP/S\t[2] SOCKS4\t[3] SOCKS5")))

                presets = input(f"\n{self.prefix_info} {self.white}>> {self.color}")

            elif presets not in no:
                print(f"{self.prefix_warning} No option was chosen returning to home..")
                time.sleep(3)
                self.main()
                exit()

        elif presets not in {"1", "2", "3", "n"}:
            print(f"{self.prefix_error} Error in settings.json at presets")
            input()
            exit()

        config = {"1": "presets/http.txt", "2": "presets/socks4.txt", "3": "presets/socks5.txt", "n": "sites.txt",
                  "no": "sites.txt"}

        try:
            config = config[presets]
        except KeyError:
            print(f"{self.prefix_warning} No option was chosen returning to home..")
            time.sleep(3)
            self.main()
            exit()

        self.printLogo()

        if self.clearingCNT == "?":
            self.clearingCNT = input(
                f"{self.prefix_info} Remove not connectable site [y/n] {self.white}>> {self.color}"
            )

            if self.clearingCNT not in yes and self.clearingCNT not in no:
                print(f"{self.prefix_warning} No option was chosen returning to home..")
                time.sleep(3)
                self.main()
                exit()
        elif self.clearingCNT not in yes and self.clearingCNT not in no:
            print(f"{self.prefix_error} Error in settings.json at removewebsites")
            input()
            exit()

        self.clearingCNT = self.clearingCNT in yes

        self.printLogo()

        if self.clearingProxy == "?":
            self.clearingProxy = input(
                f"{self.prefix_info} Remove sites with no proxies [y/n] {self.white}>> {self.color}"
            )

            if self.clearingProxy not in yes and self.clearingProxy not in no:
                print(f"{self.prefix_warning} No option was chosen returning to home..")
                time.sleep(3)
                self.main()
                exit()

        elif self.clearingProxy not in yes and self.clearingProxy not in no:
            print(f"{self.prefix_error} Error in settings.json at removeProxyless")
            input()
            exit()

        self.clearingProxy = self.clearingProxy in yes

        self.printLogo()

        if self.randomUseragent == "?":
            self.randomUseragent = input(
                f"{self.prefix_info} Random Useragent? [y/n] {self.white}>> {self.color}"
            )

            if self.randomUseragent not in yes and self.randomUseragent not in no:
                print(f"{self.prefix_warning} No option was chosen returning to home..")
                time.sleep(3)
                self.main()
                exit()

        elif self.randomUseragent not in yes and self.randomUseragent not in no:
            print(f"{self.prefix_error} Error in settings.json at removeproxyless")
            input()
            exit()

        self.randomUseragent = self.randomUseragent in yes

        self.printLogo()

        if self.timeout == "?":
            self.timeout = input(
                f"{self.prefix_info} Timeout [seconds] {self.white}>> {self.color}"
            )

        elif not self.timeout.isdigit():
            print(f"{self.prefix_error} Error in settings.json at threads")
            input()
            exit()

        try:
            self.timeout = int(self.timeout)
        except ValueError:
            print(f"{self.prefix_warning} Timeout needs a number")
            time.sleep(3)
            self.main()
            exit()

        if self.timeout < 1:
            print(f"{self.prefix_warning} Timeout must be higher than 0")
            time.sleep(3)
            self.main()
            exit()

        self.printLogo()

        if threads == "?":
            threads = input(f"{self.prefix_info} Threads {self.white}>> {self.color}")

        elif not threads.isdigit():
            print(f"{self.prefix_error} Error in settings.json at threads")
            input()
            exit()

        try:
            threads = int(threads)
        except ValueError:
            print(f"{self.prefix_warning} Thread needs a number")
            time.sleep(3)
            self.main()
            exit()

        if threads < 1:
            print(f"{self.prefix_warning} Thread needs a number greater than 0")
            time.sleep(3)
            self.main()
            exit()

        self.printLogo()

        if self.proxyDelimiter == "?":
            self.proxyDelimiter = input(
                f"{self.prefix_info} Proxy Delimiter {self.white}>> {self.color}"
            )

        self.printLogo()

        #^^ i need a better solution for that

        return config, self.clearingCNT, self.clearingProxy, self.randomUseragent, threads, self.timeout

    def terminal(self, string: str = ""):
        if os.name == "nt":
            ctypes.windll.kernel32.SetConsoleTitleW("KC Scraper | github.com/Kuucheen " + string)

    def terminalthread(self):
        while len(self.siteList) > 0:
            self.terminal(
                f"| Remaining sites {len(self.siteList)} | active threads {self.activethreads()} | Proxies {self.proxyCount} | Time {time.time() - self.start:.2f}s"
            )

    def activethreads(self):
        return threading.active_count() - 1

    def printLogo(self):
        logo = """
     _     _ _______     ______                                     
    (_)   | (_______)   / _____)                                    
     _____| |_         ( (____   ____  ____ _____ ____  _____  ____ 
    |  _   _) |         \____ \ / ___)/ ___|____ |  _ \| ___ |/ ___)
    | |  \ \| |_____    _____) | (___| |   / ___ | |_| | ____| |    
    |_|   \_)\______)  (______/ \____)_|   \_____|  __/|_____)_|    
                                                 |_|                
                        by github.com/Kuucheen

    """
        os.system(self.clear)
        print(Colorate.Diagonal(Colors.DynamicMIX([Colors.dark_gray, Colors.StaticMIX([Colors.purple, Colors.blue])]),
                                Center.XCenter(logo)))


if __name__ == "__main__":
    KCScraper().main()