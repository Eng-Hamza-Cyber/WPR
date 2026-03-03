import asyncio
import aiohttp
import random
import argparse
import sys
from datetime import datetime

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-c", "--concurrency", type=int, default=25)
    return parser.parse_args()

def get_wordlist():
    try:
        with open("db.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        sys.exit(1)

async def scan(session, sem, url, is_dir=False):
    async with sem:
        headers = {"User-Agent": random.choice(UA_LIST)}
        try:
            async with session.get(url, headers=headers, ssl=False, allow_redirects=True, timeout=15) as res:
                if res.status == 429:
                    await asyncio.sleep(5)
                    return await scan(session, sem, url, is_dir)

                if res.status == 200:
                    content = await res.read()
                    text = content.decode('utf-8', errors='ignore').lower()
                    
                    bad_keywords = ["page not found", "404 not found", "nothing found", "oops!", "error 404"]
                    if any(word in text for word in bad_keywords):
                        return

                    if is_dir:
                        if "index of" in text:
                            print(f"[!] DIR: {url}")
                            with open("results.txt", "a") as f: f.write(f"[DIR] {url}\n")
                    else:
                        ctype = res.headers.get("Content-Type", "").lower()
                        if "text/html" in ctype and not (url.endswith('.html') or url.endswith('.htm')):
                            return
                        
                        print(f"[+] FOUND: {url}")
                        with open("results.txt", "a") as f: f.write(url + "\n")
        except:
            pass

async def main():
    args = get_args()
    words = get_wordlist()
    target = args.target.rstrip('/')
    curr_year = datetime.now().year
    
    conn = aiohttp.TCPConnector(limit=args.concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        sem = asyncio.Semaphore(args.concurrency)
        tasks = []
        
        base_path = f"{target}/wp-content/uploads/"
        for word in words:
            tasks.append(scan(session, sem, base_path + word))

        for y in range(2000, curr_year + 1):
            for m in range(1, 13):
                path = f"{target}/wp-content/uploads/{y}/{m:02d}/"
                tasks.append(scan(session, sem, path, is_dir=True))
                for word in words:
                    tasks.append(scan(session, sem, path + word))

        print(f"[*] Total tasks: {len(tasks)} | Concurrency: {args.concurrency}")
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
