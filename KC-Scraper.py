#by github.com/Kuucheen
import re, os, time, threading, httpx, random, ctypes
from pystyle import Colors, Colorate, Center

proxies = set([])
goodsites = set([])
proxycount = 0
threadcount = 0
clearing = "n"
white = Colors.light_gray
color = Colors.StaticMIX((Colors.purple, Colors.blue))

def main():
    global threadcount, clearing

    terminal()

    os.system("cls")


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

    print(Colorate.Diagonal(Colors.DynamicMIX((Colors.dark_gray, Colors.StaticMIX((Colors.purple, Colors.blue)))), Center.XCenter(logo)))
    print("\n"*3)

    clearing = input(f"{white}[{color}^{white}] {color}Remove not connectable site [y/n] {white}>> {color}")

    if clearing != "y" and clearing != "ye" and clearing != "yes" and clearing != "n" and clearing != "no":
        print(f"{white}[{color}!{white}] {color}No option was choosen returning to home..")
        time.sleep(3)
        main()
        exit()
    elif clearing == "y" or clearing == "ye" or clearing == "yes":
        clearing = True

    threads = input(f"{white}[{color}^{white}] {color}Threads {white}>> {color}")
    print()

    try:
        threads = int(threads)
    except ValueError:
        print(f"{white}[{color}!{white}] Thread needs a number")
        time.sleep(3)
        exit()
    
    start = time.time()

    with open("sites.txt") as sites:

        sitelist = sites.readlines()

        while len(sitelist) > 0:
            if threadcount < threads:
                threading.Thread(target=scrape, args=[sitelist[0]]).start()
                threadcount += 1
                sitelist.pop(0)
                terminal(f"| Remaining sites {len(sitelist)} | active threads {threadcount} | Proxies {proxycount} | Time {time.time()-start:.2f}s")

        while threadcount > 0:
            try:
                terminal(f"| Waiting for threads to finish | active threads {threadcount} | Proxies {proxycount} | Time {time.time()-start:.2f}s")
            except KeyboardInterrupt:
                threadcount -= 1        #dont use it can cause errors

        terminal()
        

        
    print(f"\n{white}[{color}^{white}] Removed {color}Duplicates\n")
    print(f"{white}[{color}^{white}] Writing {color}Proxies\n")

    with open("proxies.txt", "w") as output:

        for i in proxies:
            output.write(i.replace("\n", "") + "\n")
    
    if clearing == True:

        print(f"{white}[{color}^{white}] Removing {color}not reachable Websites\n")

        with open("sites.txt", "w") as inp:

            for site in goodsites:
                inp.write(site + "\n")

    terminal()

    print(f"{white}[{color}^{white}] Finished in {color}{time.time()-start:.2f}s{white}!\n")
    print(f"{white}[{color}^{white}] Scraped {color}{len(proxies)} {white}Proxies\n")
    print("You can now close the tab")

    input("")



def scrape(site: str):
    global proxies, threadcount, proxycount
    #random useragent by (idk dm me if you are the guy) but thank you helped me learn how to use httpx
    uas=['Mozilla/5.0 (X11; CrOS x86_64 14588.123.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.72 Safari/537.36', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.4; rv:101.0) Gecko/20100101 Firefox/101.0', 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36', 'Mozilla/5.0 (Linux; Android 12; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.99 Mobile Safari/537.36']
    site = site.replace("\n", "")
    proxycount = len(proxies)
    try:
        with httpx.Client(http2=True,headers = {'accept-language': 'en','user-agent':random.choice(uas)},follow_redirects=True) as client:
            r = client.get(site, timeout=10).text
    except:
        print(f"{white}[{Colors.red}!{white}] Failed connecting to {color}{site}")
    else:
        print(f"{white}[{Colors.green}+{white}] Scraping {color}{site}")
        if clearing == True:
            goodsites.add(site)
        pattern = r'^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\:[0-9]+$'
        if r.count(":") > 0 and r.count(".") > 2:
            for _ in range(r.count(":")):
                pos = r.find(":")
                if r[pos-1].isdigit() and r[pos+1].isdigit():
                    for port in range(6, 1, -1):
                        if proxycount == len(proxies):
                            for ip in range(13, 6, -1):
                                proxy = f"{r[pos-ip:pos]}{r[pos:pos+port]}"
                                if re.match(pattern, proxy):
                                    proxies.add(proxy)
                                    proxycount += 1
                                    break
                            
                        else:   
                            break
                if proxycount != len(proxies):
                    proxycount = len(proxies)
                r = r.replace(":", "", 1)
        
    threadcount -= 1


def terminal(string:str = ""):
    ctypes.windll.kernel32.SetConsoleTitleW("KC Scraper | github.com/Kuucheen " + string)



main()