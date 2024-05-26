import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from collections import deque

# Global set to store visited URLs to avoid duplicate work
visited_urls = set()

def crawl(start_url, max_depth=1):
    urls_to_crawl = deque([(start_url, 0)])
    indexed_urls = []

    while urls_to_crawl:
        url, depth = urls_to_crawl.popleft()
        if url in visited_urls or depth > max_depth:
            continue

        visited_urls.add(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        indexed_urls.append(url)

        if depth < max_depth:
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                if is_valid_url(full_url):
                    urls_to_crawl.append((full_url, depth + 1))

    return indexed_urls

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def search(indexed_urls, query):
    return [url for url in indexed_urls if query in url]

def main():
    parser = argparse.ArgumentParser(description="A simple web crawler and search engine.")
    parser.add_argument('start_url', help='The starting URL to begin crawling from.')
    parser.add_argument('-d', '--depth', type=int, default=1, help='The maximum depth to crawl.')
    parser.add_argument('-q', '--query', required=True, help='The search query.')
    parser.add_argument('-o', '--output', help='Output results to a file.')

    args = parser.parse_args()

    print(f"Crawling {args.start_url} up to depth {args.depth}...")
    indexed_urls = crawl(args.start_url, args.depth)
    print(f"Indexed {len(indexed_urls)} URLs.")

    print(f"Searching for '{args.query}'...")
    results = search(indexed_urls, args.query)
    print(f"Found {len(results)} results:")
    for result in results:
        print(result)

    if args.output:
        with open(args.output, 'w') as f:
            for result in results:
                f.write(result + '\n')
        print(f"Results written to {args.output}")

if __name__ == "__main__":
    main()

