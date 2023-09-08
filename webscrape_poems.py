import requests
import pandas as pd
from bs4 import BeautifulSoup
import string 
from collections import Counter
import webscrape_tools as web

# Initiate output df
poem_line_df = pd.DataFrame(columns=["title", "author", "date", "category", "line"])
poem_word_df = pd.DataFrame(columns=["title", "author", "date", "category", "word", "count"])

# Get url for poem
poem_url_list = ["/a/cruel_compassion.html", "/a/hermocrates_to_euphorion.html", "/a/my_days_my_months_my_years.html", "/m/madame_dalberts_laugh.html", "/m/to_monsieur_de_la_mothe_le_vayer.html", "/o/the_bivouac_of_the_dead.html", "/o/the_enchantment.html", 
                    "/v/seguidilla.html", "/t/persicos_odi.html", "/w/la_bella_donna_della_mia_mente.html", "/w/london_1802.html"
                    , "/w/epilogue_to_the_country_wife.html", "/x/cantiga.html", "/x/the_treasury.html", "/l/to_amarantha_that_she_would.html"]

# Iniate list with a date for each poem
poem_date_list = ["600", "600", "1700", "1600", "1700", "1800", "1600", "1565", "1811", "1876", "1700", "1641", "1221", "1221", "1618"]

# Loop through each poem url
for po_ind in range(len(poem_url_list)):
    # Set final poem url
    poem_url = "https://poetry-archive.com" + poem_url_list[po_ind]

    # Get html for poem url
    poem_html = web.get_url(poem_url)

    # Create BeautifulSoup object
    poem_soup_html = BeautifulSoup(poem_html, "html.parser")
    
    # Get title from 5th element with "p" tag
    poem_title = poem_soup_html.find_all("p")[5].get_text()
    
    # Get elements with "i" tag
    i_element_list = poem_soup_html.find_all("i")

    # Loop through list
    for i_ele in i_element_list:
        # Get text
        i_ele_text = i_ele.get_text()

        # Check if correct element
        if "by: " in i_ele_text:
            # Remove first 4 characters
            poem_author = i_ele_text[4:]
            
            # Clean name
            poem_author = clean_word(poem_author)

    # Get poem text from 1st element with "dt" tag
    poem_text = poem_soup_html.find_all("dt")[0].get_text()
    
    # Remove punctuation
    poem_text = poem_text.translate(str.maketrans('', '', string.punctuation))

    # Split text for line df
    poem_line_list = poem_text.split("\r\n                      ")

    # Remove empty lines
    poem_line_list = [poem_line for poem_line in poem_line_list if not str.isspace(poem_line)]

    # Clean text for word df
    clean_poem_text = poem_text.replace("\r\n                      ", " ")
    clean_poem_text = clean_poem_text.replace("\r" , "")
    clean_poem_text = clean_poem_text.replace("\t" , "")
    clean_poem_text = clean_poem_text.replace("\n" , " ")

    # Make all lowercase
    clean_poem_text = clean_poem_text.lower()

    # Get each word(len >= 3) and it's occurence as dict
    poem_word_dict = web.get_word_dict(clean_poem_text)

    # Stop word list
    stop_word_list = ['stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'i', 'that', 'had', 'on', 'for', 'were', 'was', 'they', 
                        'but', 'ast', 'its', 'i could', 'not', 'from', 'with', 'are', "16181667", 'his', 'her', "she", "hers", "all"]

    # Loop and remove keywords
    for key, value in list(poem_word_dict.items()):
        # Check if key or value matches list
        if key in stop_word_list or value in stop_word_list:
            del poem_word_dict[key]

    yoo = poem_word_dict.keys()

    # Set df for poem
    word_df = pd.DataFrame(poem_word_dict.items(), columns=['word', 'count'])
    line_df = pd.DataFrame()

    # Set line column
    line_df["line"] = poem_line_list

    # Set author column
    word_df["author"] = poem_author
    line_df["author"] = poem_author

    # Set title column
    word_df["title"] = poem_title
    line_df["title"] = poem_title

    # Set date column
    word_df["date"] = poem_date_list[po_ind]
    line_df["date"] = poem_date_list[po_ind]

    # Set category column
    word_df["category"] = "None"
    line_df["category"] = "None"

    # Concat df
    poem_word_df = pd.concat([poem_word_df, word_df], ignore_index=True)
    poem_line_df = pd.concat([poem_line_df, line_df], ignore_index=True)

# Only keep count and word columns
only_word_count_df = poem_word_df[["count", "word"]]

# Trim df and drop na
date_count_df = poem_word_df[["author", "date", "count", "word"]]
date_count_df = date_count_df.dropna(subset=['date'])

# Convert 
date_count_df["date"] = date_count_df["date"].astype(int)
date_count_df["century"] = date_count_df['date'].apply(lambda x: (x // 100 * 100) + 100)
date_count_df = date_count_df.groupby(["century", "word"]).agg({"count": "sum"})
date_count_df = date_count_df.reset_index().sort_values(by=["count"], ascending=False)

# Group by word
only_word_count_df = only_word_count_df.groupby(only_word_count_df["word"]).aggregate({"count": "sum"}).sort_values(by=["count"], ascending=True).reset_index(drop=True)

# Save to csv
date_count_df.to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/century_count_cut.csv")
poem_word_df.sort_values(by=["count"], ascending=False).to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/poem_word_cut.csv")
poem_line_df.to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/poem_line_cut.csv")