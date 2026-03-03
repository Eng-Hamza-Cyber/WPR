import asyncio
import httpx
import random
import argparse
import sys
from datetime import datetime

def get_args():
    parser = argparse.ArgumentParser(description="WPR - WordPress Reaper")
    parser.add_argument("-t", "--target", help="Target URL", required=True)
    parser.add_argument("-s", "--start", type=int, help="Start year", default=2000)
    parser.add_argument("-c", "--concurrency", type=int, help="Concurrency", default=5)
    return parser.parse_args()

def get_wordlist():
    try:
        with open("db.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        sys.exit(1)

async def scan(client, sem, url, is_dir=False):
    async with sem:
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/123.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.2277.112",
            "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.164 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; ARM64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (PlayStation 5 7.61) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
        ]
        
        headers = {"User-Agent": random.choice(ua_list)}
        try:
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            if is_dir:
                res = await client.get(url, headers=headers, timeout=10.0, follow_redirects=True)
                if res.status_code == 200 and "Index of" in res.text:
                    print(f"[!] DIRECTORY LISTING EXPOSED: {url}")
                    with open("results.txt", "a") as f:
                        f.write(f"[DIR] {url}\n")
            else:
                res = await client.head(url, headers=headers, timeout=10.0, follow_redirects=True)
                if res.status_code == 200:
                    ctype = res.headers.get("Content-Type", "").lower()
                    if "text/html" in ctype and not (url.endswith('.html') or url.endswith('.htm')):
                        return
                    
                    print(f"[+] FOUND: {url}")
                    with open("results.txt", "a") as f:
                        f.write(url + "\n")
        except:
            pass

async def main():
    args = get_args()
    words = get_wordlist()
    target = args.target.rstrip('/')
    curr_year = datetime.now().year

    m_variants = [f"{i:02d}" for i in range(1, 13)] + \
                 ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
    print(f"[*] WPR Started | Target: {target}")

    sem = asyncio.Semaphore(args.concurrency)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=args.concurrency)
    
    async with httpx.AsyncClient(http2=True, limits=limits, verify=False) as client:
        tasks = []
        
        main_uploads = f"{target}/wp-content/uploads/"
        tasks.append(scan(client, sem, main_uploads, is_dir=True))
        for file in words:
            tasks.append(scan(client, sem, main_uploads + file))

        for year in range(args.start, curr_year + 1):
            for variant in m_variants:
                base_url = f"{target}/wp-content/uploads/{year}/{variant}/"
                tasks.append(scan(client, sem, base_url, is_dir=True))
                
                for file in words:
                    url = base_url + file
                    tasks.append(scan(client, sem, url))
        
        await asyncio.gather(*tasks)
    print("[*] Finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
