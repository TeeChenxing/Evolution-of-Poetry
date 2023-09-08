import requests
import pandas as pd
from bs4 import BeautifulSoup, element
import re
import string 
from collections import Counter


def get_url(url):
        """
        Returns the html in text from the url provided.

        Args:
            url (str): url of webapge

        Returns:
            html_text (str): string contaning html text for url
        """

        # Get html str from url
        html_text = requests.get(url).text

        return html_text


def get_poetry_html():
        """
        Get html for given poem

        Returns:
            home_soup_html (BeautifulSoup): html for given page
        """
        
        # Get html containg home page poems
        poem_home_html = get_url("https://poetry-archive.com/")
        
        # Create BeautifulSoup object
        home_soup_html = BeautifulSoup(poem_home_html, "html.parser")

        return home_soup_html


def get_word_dict(text):
    """
    Get a dict of unique words and their occurence in text

    Args:
        text (string): associated text

    Returns:
        word_dict (dict): dictionary with keys for a poem 
    """
    # Split each text into words
    word_list = text.split(" ")

    # Loop through list, make sure no extra whitespace
    for word_ind in range(len(word_list)):
        # Check if word contains white space
        if len(word_list[word_ind]) >= 20 :
            temp = word_list[word_ind].split(" ")

    # Count occurence of each word to dict
    word_dict = Counter(word_list)

    # Split if two words registerd as one, keep first and 
    # Only keep words that have 3 or more letters
    word_dict = dict((word, occurence) for word, occurence in word_dict.items() if len(word) >= 3)

    return word_dict


def clean_word(word):
    """
    Clean hypertext from word

    Args:
        word (str): word to be cleaned
    
    Returns:
        clean_word (str): word that was cleaned
    """
    # Remove hypertext characters
    word = word.replace("\r" , "")
    word = word.replace("\t" , "")
    word = word.replace("\n" , "")

    return word