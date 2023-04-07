#by github.com/Kuucheen
import re, os, time, threading, random, ctypes

try:
    import httpx, yaml
    from pystyle import Colors, Colorate, Center
except ImportError:
    os.system('python -m pip install httpx httpx[http2] pyyaml pystyle')
    import httpx, yaml
    from pystyle import Colors, Colorate, Center

proxies = set([])
goodsites = set([])
sitelist = []
timeout = ""
proxycount = 0
threadcount = 0
clearingcnt = ""
clearingproxy = ""
randomUseragent = ""
white = Colors.light_gray
color = Colors.StaticMIX((Colors.purple, Colors.blue))    


def main():
    global threadcount, clearingcnt, clearingproxy, randomUseragent, timeout, sitelist, start

    printLogo()
    print()
    config, clearingcnt, clearingproxy, randomUseragent, threads, timeout = getSettings()

    terminal()
    
    start = time.time()

    #dispatcher
    with open(config) as sites:

        sitelist = sites.readlines()
        threading.Thread(target=terminalthread).start()

        while len(sitelist) > 0:
            if threadcount < threads:
                threading.Thread(target=scrape, args=[sitelist[0]]).start()
                threadcount += 1
                sitelist.pop(0)

        while threadcount > 0:
            terminal(f"| Waiting for threads to finish | active threads {threadcount} | Proxies {proxycount} | Time {time.time()-start:.2f}s")

        terminal()
        

    lenproxies = len(proxies)
    print(f"\n{white}[{color}^{white}] Removed {color}{proxycount-lenproxies} {white}Duplicates\n")
    print(f"{white}[{color}^{white}] Remaining Proxies: {color}{lenproxies}{white}\n")
    print(f"{white}[{color}^{white}] Writing {color}Proxies\n")

    with open("proxies.txt", "w") as output:

        for i in proxies:
            output.write(i.replace("\n", "") + "\n")
    
    if clearingcnt == True or clearingproxy == True:

        print(f"{white}[{color}^{white}] Removing {color}bad Websites\n")
        
        with open(config, "w") as inp:

            for site in goodsites:
                inp.write(site + "\n")

    terminal()

    print(f"{white}[{color}^{white}] Finished in {color}{time.time()-start:.2f}s{white}!\n")
    print("You can now close the tab")

    input("")


def scrape(site: str):
    global proxies, threadcount, proxycount
    uas=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; MDDCJS)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"]
    site = site.replace("\n", "")
    try:
        with httpx.Client(http2=True,headers = {'accept-language': 'en','user-agent': random.choice(uas) if randomUseragent == True else uas[0]},follow_redirects=True) as client:
            r = client.get(site, timeout=timeout).text
    except:
        print(f"{white}[{Colors.red}!{white}] Failed connecting to {color}{site}")
        if clearingcnt != True:
            goodsites.add(site)
    else:
        goodsites.add(site)
        r = r.replace("&colon", ":")
        locProxies = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\:\d{1,5}\b", r)
        length = len(locProxies)
        print(f"{white}[{Colors.green}+{white}] Scraped {color}{length}{white} from {color}{site}")
        proxycount += length
        proxies = proxies | set(locProxies)
        if clearingproxy == True and length == 0:
            goodsites.remove(site)
    finally:
        threadcount -= 1

def getSettings() -> list:
    with open("settings.yaml") as setting:
        settings = yaml.safe_load(setting.read())

    premades = settings["premades"]
    clearingcnt = settings["removeWebsites"]
    clearingproxy = settings["removeProxyless"]
    randomUseragent = settings["randomUseragent"]
    threads = settings["threads"]
    timeout = settings["timeout"]

    yes = ["yes", "y", "ye"]
    no = ["no", "n", "nah"]

    if premades == "?":
        premades = input(f"{white}[{color}^{white}] {color}Use premades [y/n] {white}>> {color}")
        if premades in yes:
            os.system("cls")
            printLogo()
            print(Colorate.Diagonal(Colors.DynamicMIX((Colors.dark_gray, Colors.StaticMIX((Colors.purple, Colors.blue)))), Center.XCenter("\n[1] HTTP/S\t[2] SOCKS4\t[3] SOCKS5")))

            premades = input(f"\n{white}[{color}^{white}] {white}>> {color}")

        elif premades not in no:
            print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
            time.sleep(3)
            main()
            exit()

    elif premades != "1" and premades != "2" and premades != "3" and premades != "n":
        print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at premades")
        input()
        exit()

    config = {"1": "premades/http.txt", "2": "premades/socks4.txt", "3": "premades/socks5.txt", "n": "sites.txt", "no": "sites.txt"}

    try:
        config = config[premades]
    except KeyError:
        print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
        time.sleep(3)
        main()
        exit()


    printLogo()

    if clearingcnt == "?":

        clearingcnt = input(f"\n{white}[{color}^{white}] {color}Remove not connectable site [y/n] {white}>> {color}")

        if clearingcnt not in yes and clearingcnt not in no:
            print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
            time.sleep(3)
            main()
            exit()
    elif clearingcnt not in yes and clearingcnt not in no:
        print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at removewebsites")
        input()
        exit()
    
    if clearingcnt in yes:
        clearingcnt = True

    printLogo()

    if clearingproxy == "?":

        clearingproxy = input(f"\n{white}[{color}^{white}] {color}Remove sites with no proxies [y/n] {white}>> {color}")

        if clearingproxy not in yes and clearingproxy not in no:
            print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
            time.sleep(3)
            main()
            exit()
    
    elif clearingproxy not in yes and clearingproxy not in no:
            print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at removeproxyless")
            input()
            exit()

    if clearingproxy in yes:
        clearingproxy = True
    
    printLogo()
    
    if randomUseragent == "?":

        randomUseragent = input(f"\n{white}[{color}^{white}] {color}Random Useragent? [y/n] {white}>> {color}")

        if randomUseragent not in yes and randomUseragent not in no:
            print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
            time.sleep(3)
            main()
            exit()
    
    elif randomUseragent not in yes and randomUseragent not in no:
            print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at removeproxyless")
            input()
            exit()

    if randomUseragent in yes:
        randomUseragent = True

    
    printLogo()

    if timeout == "?":
        timeout = input(f"\n{white}[{color}^{white}] {color}Timeout [seconds] {white}>> {color}")

    elif timeout.isdigit() == False:
        print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at threads")
        input()
        exit()

    try:
        timeout = int(timeout)
    except ValueError:
        print(f"{white}[{color}!{white}] {color}Timeout needs a number")
        time.sleep(3)
        main()
        exit()
    
    if timeout < 1:
        print(f"{white}[{color}!{white}] {color}Timeout must be higher than 0")
        time.sleep(3)
        main()
        exit()
    
    printLogo()

    if threads == "?":
        threads = input(f"\n{white}[{color}^{white}] {color}Threads {white}>> {color}")

    elif threads.isdigit() == False:
        print(f"{white}[{Colors.red}!{white}] {Colors.red}Error{white} in settings.json at threads")
        input()
        exit()

    try:
        threads = int(threads)
    except ValueError:
        print(f"{white}[{color}!{white}] {color}Thread needs a number")
        time.sleep(3)
        main()
        exit()
        
    if threads < 1:
        print(f"{white}[{color}!{white}] {color}Thread needs a number greater than 0")
        time.sleep(3)
        main()
        exit()

    printLogo()

    return config, clearingcnt, clearingproxy, randomUseragent, threads, timeout

def terminal(string:str = ""):
    ctypes.windll.kernel32.SetConsoleTitleW("KC Scraper | github.com/Kuucheen " + string)

def terminalthread():
    while len(sitelist) > 0:
        terminal(f"| Remaining sites {len(sitelist)} | active threads {threadcount} | Proxies {proxycount} | Time {time.time()-start:.2f}s")

def printLogo():
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
    os.system("cls")
    print(Colorate.Diagonal(Colors.DynamicMIX((Colors.dark_gray, Colors.StaticMIX((Colors.purple, Colors.blue)))), Center.XCenter(logo)))


if __name__ == "__main__":
    main()