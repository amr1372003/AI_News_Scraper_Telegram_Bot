import requests
from bs4 import BeautifulSoup
import torch
from transformers import pipeline
import csv
import os
import time
import pandas as pd


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}


url = 'https://venturebeat.com/category/ai/'
url2 = 'https://the-decoder.com/artificial-intelligence-news/ai-research/'
url3 = 'https://the-decoder.com/artificial-intelligence-news/ai-and-society/'
url4 = 'https://the-decoder.com/artificial-intelligence-news/ai-practice/'

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_text(text, max_length=300, min_length=30):
    text = text[:3000]  
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']


def get_text_content(link):
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    content = soup.find('div', class_='article-content').get_text(strip=True)
    if content is None:
        return 'No content found'
    else:
        return content
    

def get_text2_content(link):
    try:
        page = requests.get(link, headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')

        content_div = soup.find('div', class_='summary__text')
        if not content_div:
            content_div = soup.find('div', class_='entry-content')

        if content_div:
            return content_div.get_text(strip=True)
        else:
            print(f"⚠️ No content found for: {link}")
            return f"No content found for: {link}"

    except Exception as e:
        print(f"❌ Error fetching {link}: {type(e).__name__}: {e}")
        return f"Error fetching content from {link}"



def get_first_title(page):
    soup = BeautifulSoup(page.content, 'lxml')
    title_tag = soup.find('a', class_='ArticleListing__title-link')
    return title_tag.text.strip() if title_tag else None

def get_first_title2(page):
    soup = BeautifulSoup(page.content, 'lxml')
    title_tag = soup.find('a', class_='link-overlay')
    return title_tag.text.strip() if title_tag else None

def the_decoder(page):
    scr2 = page.content
    soup2 = BeautifulSoup(scr2, 'lxml')
    titles2_content = soup2.find_all('a', class_='link-overlay')
    titles2 = [a.get('aria-label', '').strip() for a in titles2_content]
    links2 = [a['href'] for a in titles2_content]

    dates2_content = soup2.select('div.card__content__date time.entry-date.published')
    dates2 = [time.text.strip() for time in dates2_content]

    authors2 = ['the-decoder'] * len(titles2)

    return titles2, links2, authors2, dates2

def get_content(page, page2, page3, page4): # title ==, date ==, link ==, author ==, content summarized ==
    scr = page.content
    soup = BeautifulSoup(scr, 'lxml')
    details = []

    titles_content = soup.find_all('a', class_ = 'ArticleListing__title-link')
    titles = [a.text.strip() for a in titles_content]
    links = [a['href'] for a in titles_content]

    authors_content = soup.find_all('a', class_ = 'ArticleListing__author')
    authors = [a.text.strip() for a in authors_content]

    dates_content = soup.find_all('time', class_ = 'ArticleListing__time')
    dates = [time.text.strip() for time in dates_content]

    titles2, links2, authors2, dates2 = the_decoder(page2)
    titles3, links3, authors3, dates3 = the_decoder(page3)
    titles4, links4, authors4, dates4 = the_decoder(page4)


    all_titles = titles2 + titles3 + titles4 + titles
    all_links = links2 + links3 + links4 + links
    all_authors = authors2 + authors3 + authors4 + authors
    all_dates = dates2 + dates3 + dates4 + dates

    text2_summaries = []
    for i in range(len(titles2)):
        text2_summaries.append(get_text2_content(links2[i]))

    text3_summaries = []
    for i in range(len(titles3)):
        text3_summaries.append(get_text2_content(links3[i]))

    text4_summaries = []
    for i in range(len(titles4)):
        text4_summaries.append(get_text2_content(links4[i]))

    details = []

    n_decoder = len(titles2) + len(titles3) + len(titles4)

    decoder_summaries = []
    for link in links2 + links3 + links4:
        decoder_summaries.append(get_text2_content(link))

    for i in range(len(all_titles)):
        is_venturebeat = i >= n_decoder

        summary = ""
        try:
            if is_venturebeat:
                corrected_index = i - n_decoder
                text = get_text_content(links[corrected_index])
                summary = summarize_text(text)
            else:
                summary = decoder_summaries[i]
        except Exception as e:
            print(f"❌ Error processing {all_titles[i]} → {e}")
            summary = "Error fetching content"

        details.append({
            'title': all_titles[i],
            'date': all_dates[i] if i < len(all_dates) else 'Unknown',
            'link': all_links[i],
            'author': all_authors[i] if i < len(all_authors) else 'Unknown',
            'content_summary': summary
        })

        print(f"{'✅' if is_venturebeat else '⏩'} Processed: {all_titles[i]}")


    return details


def save_to_csv(data, filename='news_data.csv'):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def load_last_title(filename='news_data.csv'):
    if not os.path.exists(filename):
        return None
    df = pd.read_csv(filename)
    return df.iloc[0]['title'] if not df.empty else None

def has_title_changed(current_title, filename='news_data.csv'):
    last_title = load_last_title(filename)
    return current_title != last_title


previous_title = None

while True:
    try:
        page = requests.get(url, headers=headers)
        page2 = requests.get(url2, headers=headers)
        page3 = requests.get(url3, headers=headers)
        page4 = requests.get(url4, headers=headers)

        current_title = get_first_title(page)
        current_title2 = get_first_title2(page2)
        current_title3 = get_first_title2(page3)
        current_title4 = get_first_title2(page4)

        if (current_title and current_title != previous_title) or (current_title2 and current_title2 != previous_title) or (current_title3 and current_title3 != previous_title) or (current_title4 and current_title4 != previous_title):
            previous_title = current_title
            info = get_content(page, page2, page3, page4)
            save_to_csv(info)
            print(f"✅ Updated at {time.ctime()} - New headline: {current_title}")
        else:
            print(f"🕒 No update at {time.ctime()} - Last headline: {previous_title}")

    except Exception as e:
        print(f"❌ Error: {e.__class__.__name__}: {e}")
    
    time.sleep(3600)
