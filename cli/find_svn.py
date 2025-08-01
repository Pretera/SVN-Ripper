import argparse
import time
import requests
from urllib.parse import urlencode
from googlesearch import search as google_search

# ---------------------------------------------
# Google Dorks for exposed .svn
DORKS = [
    'intitle:"Index of /.svn"',
    'inurl:".svn/entries"',
    'inurl:".svn/wc.db"',
    'inurl:".svn"',
    'site:example.com inurl:".svn"',  # customize this if needed
    'intitle:"Index of" ".svn/entries"'
]
# ---------------------------------------------

def search_google(dorks, delay, max_results):
    results = set()
    for dork in dorks:
        print(f"[Google] Searching: {dork}")
        try:
            for url in google_search(dork, num_results=max_results):
                print(f"  [+] {url}")
                results.add(url)
                time.sleep(delay)  # throttle requests
        except Exception as e:
            print(f"  [!] Google error: {e}")
    return results


def search_serpapi(dorks, serpapi_key, max_results):
    results = set()
    for dork in dorks:
        print(f"[SerpAPI] Searching: {dork}")
        params = {
            "engine": "google",
            "q": dork,
            "api_key": serpapi_key,
            "num": max_results
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            for result in data.get("organic_results", []):
                link = result.get("link")
                if link:
                    print(f"  [+] {link}")
                    results.add(link)
        except Exception as e:
            print(f"  [!] SerpAPI error: {e}")
    return results


def search_bing(dorks, bing_key, max_results):
    results = set()
    headers = {"Ocp-Apim-Subscription-Key": bing_key}
    endpoint = "https://api.bing.microsoft.com/v7.0/search"
    for dork in dorks:
        print(f"[Bing] Searching: {dork}")
        params = {"q": dork, "count": max_results}
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            data = response.json()
            for web_page in data.get("webPages", {}).get("value", []):
                link = web_page.get("url")
                if link:
                    print(f"  [+] {link}")
                    results.add(link)
        except Exception as e:
            print(f"  [!] Bing error: {e}")
    return results


def save_results(results, filename="exposed.txt"):
    with open(filename, "w") as f:
        for url in sorted(results):
            f.write(url + "\n")
    print(f"\n[*] Saved {len(results)} results to {filename}")


def main():
    parser = argparse.ArgumentParser(description="Search for exposed .svn directories.")
    parser.add_argument("--engine", choices=["google", "serpapi", "bing"], required=True, help="Search engine to use")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between Google queries (seconds)")
    parser.add_argument("--max", type=int, default=10, help="Max results per dork")
    parser.add_argument("--serpapi-key", help="SerpAPI key")
    parser.add_argument("--bing-key", help="Bing API key")
    args = parser.parse_args()

    if args.engine == "google":
        results = search_google(DORKS, args.delay, args.max)
    elif args.engine == "serpapi":
        if not args.serpapi_key:
            print("[-] Missing SerpAPI key. Use --serpapi-key")
            return
        results = search_serpapi(DORKS, args.serpapi_key, args.max)
    elif args.engine == "bing":
        if not args.bing_key:
            print("[-] Missing Bing key. Use --bing-key")
            return
        results = search_bing(DORKS, args.bing_key, args.max)
    else:
        print("[-] Unknown engine.")
        return

    save_results(results)

if __name__ == "__main__":
    main()
