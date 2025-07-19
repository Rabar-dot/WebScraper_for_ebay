import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

class Scraper:
    def __init__(self):
        self.agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/110.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 Version/14.0 Mobile/15A372 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 13_1 like Mac OS X) AppleWebKit/605.1.15 Version/13.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 Chrome/89.0.4389.90 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/112.0.5615.49 Safari/537.36 Edg/112.0.1722.48",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 9; SM-A205U) AppleWebKit/537.36 Chrome/88.0.4324.93 Mobile Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 Chrome/54.0.2840.99 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 Version/13.1.2 Safari/605.1.15"
        ]
        self.session = requests.Session()

    def scrape(self, query, pages=1):
        results = []
        for page in range(1, pages + 1):
            delay = random.uniform(1.5, 3.5)
            if random.random() < 0.2:
                delay += random.uniform(2, 5)
            time.sleep(delay)
            url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_pgn={page}"
            headers = {"User-Agent": random.choice(self.agents)}
            r = self.session.get(url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select(".s-item")
            for item in items:
                title_tag = item.select_one(".s-item__title")
                price_tag = item.select_one(".s-item__price")
                shipping_tag = item.select_one(".s-item__shipping, .s-item__freeXDays")
                condition_tag = item.select_one(".SECONDARY_INFO")
                link_tag = item.select_one("a.s-item__link")
                if not title_tag or "Shop on eBay" in title_tag.text:
                    continue
                title = title_tag.text.strip()
                price = price_tag.text.strip() if price_tag else "N/A"
                shipping = shipping_tag.text.strip() if shipping_tag else "N/A"
                condition = condition_tag.text.strip() if condition_tag else "N/A"
                link = link_tag["href"] if link_tag else "N/A"
                results.append({
                    "Title": title,
                    "Price": price,
                    "Shipping": shipping,
                    "Condition": condition,
                    "URL": link
                })
        return results

class Table:
    def __init__(self, tree):
        self.tree = tree

    def update(self, data):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in data:
            self.tree.insert("", "end", values=(item["Title"], item["Price"], item["Shipping"], item["Condition"]))

class App:
    def __init__(self, root):
        self.scraper = Scraper()
        self.root = root
        self.root.title("The project")
        self.root.geometry("850x500")

        top = ttk.Frame(root, padding=10)
        top.pack(fill=tk.X)
        ttk.Label(top, text="Search:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(top, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Search", command=self.search).pack(side=tk.LEFT, padx=5)
        self.status = ttk.Label(root, text="")
        self.status.pack()

        columns = ("Title", "Price", "Shipping", "Condition")
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200 if col == "Title" else 100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table = Table(self.tree)

    def search(self):
        query = self.entry.get().strip()
        if not query:
            messagebox.showwarning("Use your brain", "It's empty man, type something there.")
            return
        self.status.config(text="Wait...")
        self.root.update()
        try:
            data = self.scraper.scrape(query, pages=3)
            if not data:
                self.status.config(text="Nothing found, we've probably been detected so change the browser agents.")
                return
            self.table.update(data)
            df = pd.DataFrame(data)
            filename = f"ebay_{query.replace(' ', '_')}.csv"
            df.to_csv(filename, index=False)
            self.status.config(text=f"Saved {len(df)} items to {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text="error??.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
