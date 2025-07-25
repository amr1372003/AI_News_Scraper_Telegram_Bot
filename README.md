# 📰 AI News Scraper & Telegram Bot

A complete Python-based system that **scrapes AI news**, **summarizes content using NLP**, and **delivers personalized updates via Telegram** based on user-defined keywords.

## 🔧 Features

* ✅ Scrapes fresh articles from:

  * [VentureBeat - AI](https://venturebeat.com/category/ai/)
  * [The Decoder - AI Research](https://the-decoder.com/artificial-intelligence-news/ai-research/)
  * [The Decoder - AI & Society](https://the-decoder.com/artificial-intelligence-news/ai-and-society/)
  * [The Decoder - AI Practice](https://the-decoder.com/artificial-intelligence-news/ai-practice/)
* 🤖 Summarizes content using [BART-large-CNN](https://huggingface.co/facebook/bart-large-cnn)
* 🔍 Filters articles based on **user-defined keywords**
* 📩 Sends **relevant news summaries** directly via **Telegram**
* 🕐 Automatically checks for updates every hour

---

## 🚀 How It Works

1. **Web Scraping**: Uses `requests` + `BeautifulSoup` to extract titles, links, authors, and publication dates.
2. **Summarization**: Long articles are shortened using Hugging Face's Transformers.
3. **Keyword Matching**: Checks if news matches a user's saved keywords (must match 2+).
4. **Telegram Bot**: Sends relevant articles to the user in clean format.

---

## 📂 Project Structure

```bash
├── news_scraper.py        # Web scraping, summarization, and CSV saving
├── telegram_bot.py        # Telegram bot logic, keyword management, and user interaction
├── news_data.csv          # Stores latest scraped news
├── users_keywords.json    # Stores user-specific keywords
├── requirements.txt       # All required libraries
└── README.md              # You are here
```

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/ai-news-telegram-bot.git
cd ai-news-telegram-bot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🛠 Requirements

* Python 3.8+
* `transformers`
* `torch`
* `beautifulsoup4`
* `pandas`
* `python-telegram-bot`

Create a `requirements.txt` file:

```txt
requests
beautifulsoup4
pandas
transformers
torch
python-telegram-bot==20.0
```

---

## 💬 Telegram Bot Commands

| Command              | Description                          |
| -------------------- | ------------------------------------ |
| `/start`             | Shows help and usage instructions    |
| `/mykeywords`        | View your current keywords           |
| `/removekeywords`    | Delete specific or all keywords      |
| `keyword1, keyword2` | Set new keywords (just type message) |
| `/news`              | Get relevant news based on keywords  |

---

## 📌 Keyword Matching Logic

* A news article is **relevant** if it matches **at least 2 keywords** from your list (either in title or summary).
* Keywords are **case-insensitive**.

---

## 🧠 Model Used

* [facebook/bart-large-cnn](https://huggingface.co/facebook/bart-large-cnn) for summarization.
* Loaded using Hugging Face's `pipeline()` API.

---

## 🛡️ Legal Note

* This tool scrapes public data from websites for educational and personal use.
* Always respect each website’s [robots.txt](https://venturebeat.com/robots.txt) and TOS before deploying at scale.

---

## 🧑‍💻 Author

* **Name:** Amr Hassan
* **GitHub:** [amr1372003](https://github.com/amr1372003)

---
