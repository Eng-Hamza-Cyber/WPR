import asyncio
import aiohttp
import argparse
import sys
import socket
import os
from datetime import datetime

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", required=True)
    parser.add_argument("-c", "--concurrency", type=int, default=20)
    parser.add_argument("-s", "--start", type=int, default=2000)
    return parser.parse_args()

async def fetch(session, url, sem, is_dir=False):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    async with sem:
        try:
            async with session.get(url, headers=headers, timeout=15, allow_redirects=False) as res:
                status = res.status
                if status == 200:
                    text = await res.text()
                    if is_dir and ("Index of" in text or "Parent Directory" in text):
                        print(f"\n\a[!] DIRECTORY LISTING FOUND: {url}")
                        with open("results.txt", "a") as f:
                            f.write(f"[DIR] {url}\n")
                    elif not is_dir:
                        print(f"\r[*] [200 OK] -> {url}                                ")
                        with open("results.txt", "a") as f:
                            f.write(url + "\n")
                        
                        if any(ext in url.lower() for ext in ['.csv', '.sql', '.log', '.env']):
                            try:
                                preview = text[:80].replace('\n', ' ')
                                print(f"    [PREVIEW] {preview}...")
                            except:
                                pass
                return status
        except:
            return None

async def main():
    args = get_args()
    target = args.target.rstrip('/')
    
    if not os.path.exists("db.txt"):
        print("[!] FATAL ERROR: db.txt not found.")
        sys.exit(1)

    with open("db.txt", "r") as f:
        words = [line.strip() for line in f if line.strip()]
    
    if not words:
        print("[!] FATAL ERROR: db.txt is empty.")
        sys.exit(1)

    sem = asyncio.Semaphore(args.concurrency)
    resolver = aiohttp.ThreadedResolver()
    connector = aiohttp.TCPConnector(
        resolver=resolver,
        family=socket.AF_INET,
        ssl=False,
        use_dns_cache=True,
        limit_per_host=args.concurrency
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        current_year = datetime.now().year
        
        print(f"[*] Target: {target} | Start: {args.start} | Concurrency: {args.concurrency}")
        
        root_url = f"{target}/wp-content/uploads/"
        root_tasks = [fetch(session, root_url, sem, is_dir=True)]
        root_tasks.extend([fetch(session, f"{root_url}{w.lstrip('/')}", sem) for w in words])
        await asyncio.gather(*root_tasks)

        for y in range(args.start, current_year + 1):
            print(f"\n[>] Entering Year: {y}")
            for m in [f"{i:02d}" for i in range(1, 13)]:
                sys.stdout.write(f"\r    [-] Scanning Month: {m}")
                sys.stdout.flush()
                
                base = f"{target}/wp-content/uploads/{y}/{m}/"
                month_tasks = [fetch(session, base, sem, is_dir=True)]
                month_tasks.extend([fetch(session, f"{base}{w.lstrip('/')}", sem) for w in words])
                
                await asyncio.gather(*month_tasks)
        
    print("\n" + "-" * 50)
    print("[*] Scan Completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
