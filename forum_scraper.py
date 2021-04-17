#!/usr/bin/python3
import aiohttp
import time
from bs4 import BeautifulSoup

class NetworkErrorDuringScraping(Exception):
    'Raised when a network error happen during scraping.'


class ForumMessage():
    def __init__(self, id:int, datetime:str, author_nick:str, text:str):
        self.id = id
        self.datetime = datetime
        self.author_nick = author_nick
        self.text = text

        # Check if the text got deals in it
        text_lower = text.lower()
        self.has_deals = ('#akció' in text_lower) or ('#akcio' in text_lower)


def convert_children_link_tags_to_discord_links(parent):
    r"Converts the tag's children \<a\> tags to discord embed link format."
    for a in parent.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        dc_link = f'[{text}]({href})'
        a.replace_with(dc_link) 


async def request_webpage_src(from_message_id:int) -> str:
    'Requests the webpage from the given message id. Returns a string of the webpage source it gets.'
    topic_url = f'https://prohardver.hu/tema/bestbuy_topik_akcio_ajanlasakor_akcio_hashtag_kote/hsz_{from_message_id}-{from_message_id+199}.html'
    async with aiohttp.ClientSession() as session:
        async with session.get(topic_url) as response:
            if not response.status == 200:
                raise NetworkErrorDuringScraping

            return await response.text()


async def scrape(from_message_id):
    webpage_src = await request_webpage_src(from_message_id=from_message_id)
    bs = BeautifulSoup(webpage_src, 'html.parser')

    page_center = bs.find(name='div', id='center')
    message_id_tags = page_center.select('div.msg-list:not(.thread-content) div.card div.card-header span.msg-head-author > span.msg-num a')
    date_tags = page_center.select('div.msg-list:not(.thread-content) div.card div.card-header time')
    author_nick_tags = page_center.select('div.msg-list:not(.thread-content) div.card div.card-body > div.msg-user p.user-title')
    text_tags = page_center.select('div.msg-list:not(.thread-content) div.card div.card-body > div.media-body > div.msg-content')

    data_scraped = []
    for message_id_tag, date_tag, author_nick_tag, text_tag in zip(message_id_tags, date_tags, author_nick_tags, text_tags):
        id = int(message_id_tag.get_text(strip=True)[1:]) # Slice out the '#' character
        datetime = date_tag.get_text(strip=True)
        author_nick = author_nick_tag.get_text(strip=True)

        convert_children_link_tags_to_discord_links(text_tag)
        text = text_tag.get_text(separator='\n', strip=True)

        data_scraped.append(ForumMessage(id, datetime, author_nick, text))

    return tuple(data_scraped)


async def scrape_recursively(from_message_id):
    data = await scrape(from_message_id=from_message_id)
    if data:
        last_entry_id = data[-1].id
        # If we scraped the maximum data of the request (199 entries)
        if from_message_id+199 == last_entry_id:
            # then request the next messages recursively.
            return tuple(data + await scrape_recursively(last_entry_id+1))
    
    # else just return the data we scraped
    return tuple(data)
    