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

async def scan(client, sem, url):
    async with sem:
        ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/123.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.2277.112",
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]
        headers = {"User-Agent": random.choice(ua_list)}
        try:
            await asyncio.sleep(random.uniform(0.1, 0.5))
            res = await client.head(url, headers=headers, timeout=10.0, follow_redirects=True)
            if res.status_code == 200:
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

    m_numeric = [f"{i:02d}" for i in range(1, 13)]
    m_full = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    m_short = [m[:3] for m in m_full]
    all_variants = m_numeric + m_full + m_short

    print(f"[*] WPR Started | Target: {target} | From: {args.start} | Concurrency: {args.concurrency}")

    sem = asyncio.Semaphore(args.concurrency)
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=args.concurrency)
    
    async with httpx.AsyncClient(http2=True, limits=limits, verify=False) as client:
        tasks = []
        for year in range(args.start, curr_year + 1):
            for variant in all_variants:
                for file in words:
                    url = f"{target}/wp-content/uploads/{year}/{variant}/{file}"
                    tasks.append(scan(client, sem, url))
        
        await asyncio.gather(*tasks)
    print("[*] Finished.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
