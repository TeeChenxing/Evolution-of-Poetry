import requests
import pandas as pd
from bs4 import BeautifulSoup, element
import re
import string 
from collections import Counter

# Import self made functions
import webscrape_tools

# Initiate output df
poem_line_df = pd.DataFrame(columns=["title", "author", "date", "category", "line"])
poem_word_df = pd.DataFrame(columns=["title", "author", "date", "category", "word", "count"])

# Get Beautiful soup object
home_soup_html = get_poetry_html()

# Get first 16 elements with "a" tag, these are categories
sorted_element_list = home_soup_html.find_all("a")[0:16]

# Initiate url list
category_url_list = []

# Initiate category name list
category_name_list = []

# Loop through each element
for element in sorted_element_list:
    # Get href
    category_url_list.append(element.get("href"))

    # Get category name
    cat_name = element.get_text()

    # Clean name
    cat_name = clean_word(cat_name)
    cat_name = cat_name.replace("\r\n                      ", " ")

    # Deal with edge case, category name html error
    if "Children" in cat_name:
        cat_name = "Poems on Children"

    # Append category name
    category_name_list.append(cat_name)

# Loop through each category cat_ind
for cat_ind in range(len(category_url_list)):
    # Set category cat_ind
    category_url = "https://poetry-archive.com" + category_url_list[cat_ind]

    # Get html for cat_ind
    category_html = get_url(category_url)

    # Create BeautifulSoup object
    category_soup_html = BeautifulSoup(category_html, "html.parser")

    # Get elements with a
    category_element_list = category_soup_html.find_all("a")[0:16]

    # Get elements with a
    date_element_list = category_soup_html.find_all("font")

    # Initiate poem url list
    poem_url_list = []

    # Initiate poem date list
    poem_date_list = []

    # Loop through each element
    for url_elem in category_element_list[4:-7]:
        # Edge case, random amazon href
        if "amazon" in url_elem.get("href")[2:]:
            continue
        else:
            # Get href, skip first two characters ".."
            poem_url_list.append(url_elem.get("href")[2:])

    # Loop through each element
    for date_elem in date_element_list:
        # Get text
        date_elem_text = date_elem.get_text()

        # Check if has double parenthesis
        if "(" in date_elem_text and ")" in date_elem_text:
            # Get date
            elem_date = date_elem_text[date_elem_text.find("(")+1:date_elem_text.find(")")]

            # Remove " " in date
            elem_date = elem_date.replace(" ", "")

            # Append date to lit
            poem_date_list.append(elem_date)

    # Loop through each poem url
    for po_ind in range(len(poem_url_list)):
        # Set final poem url
        poem_url = "https://poetry-archive.com" + poem_url_list[po_ind]

        # Get html for poem url
        poem_html = get_url(poem_url)

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

        # Deal with edge case, author name html error
        if "Laurence Hope" in poem_author:
            poem_author = "Laurence Hope"

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
        clean_poem_text = clean_word(clean_poem_text)

        # Make all lowercase
        clean_poem_text = clean_poem_text.lower()

        # Get each word(len >= 3) and it's occurence as dict
        poem_word_dict = get_word_dict(clean_poem_text)

        # Stop word list
        stop_word_list = ['stop', 'the', 'to', 'and', 'a', 'in', 'it', 'is', 'i', 'that', 'had', 'on', 'for', 'were', 'was', 'they', 
                            'but', 'ast', 'its', 'i could', 'not', 'from', 'with', 'are', "16181667", 'his', 'her', "she", "hers", "all"]

        # Loop and remove keywords
        for key, value in list(poem_word_dict.items()):
            # Check if key or value matches list
            if key in stop_word_list or value in stop_word_list:
                del poem_word_dict[key]

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

        # Check if date is range
        if "-" in poem_date_list[po_ind]:
            # Keep lower 
            poem_date = poem_date_list[po_ind].split("-")[0]

            # Remove punctuation
            poem_date = poem_date.translate(str.maketrans('', '', string.punctuation))

            # Remove all non numeric characters
            poem_date = re.sub('[^0-9]', "", poem_date)

        elif not str.isdigit(poem_date_list[po_ind]):
            # No date associated
            poem_date = 0
        
        # Set date column
        word_df["date"] = poem_date
        line_df["date"] = poem_date

        # Set category column
        word_df["category"] = category_name_list[cat_ind]
        line_df["category"] = category_name_list[cat_ind]

        # Concat df
        poem_word_df = pd.concat([poem_word_df, word_df], ignore_index=True)
        poem_line_df = pd.concat([poem_line_df, line_df], ignore_index=True)

# Read individual poems
poem_individual_df = pd.read_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/poem_word_cut.csv")

# Combine df, read from individual poems
poem_word_df = pd.concat([poem_word_df, poem_individual_df]).reset_index(drop=True)

# Only keep count and word columns
only_word_count_df = poem_word_df[["count", "word"]]

# Trim df and drop na
date_count_df = poem_word_df[["author", "date", "count", "word"]]
date_count_df = date_count_df.dropna(subset=['date'])

# Remove edge case
edge = date_count_df["date"].unique()[31]

# Keep rows not edge
date_count_df = date_count_df[date_count_df["date"] != edge]

# Convert 
date_count_df["date"] = date_count_df["date"].astype(int)
date_count_df["century"] = date_count_df['date'].apply(lambda x: (x // 100 * 100) + 100)
date_count_df = date_count_df.groupby(["century", "word"]).agg({"count": "sum"})
date_count_df = date_count_df.reset_index().sort_values(by=["count"], ascending=False)

# Group by word
only_word_count_df = only_word_count_df.groupby(only_word_count_df["word"]).aggregate({"count": "sum"}).sort_values(by=["count"], ascending=True)

# Remove last column
poem_word_df = poem_word_df.iloc[: , :-1]

# Save to csv
date_count_df.to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/century_count_final.csv")
poem_word_df.sort_values(by=["count"], ascending=False).to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/poem_word_final.csv")
poem_line_df.to_csv("/Users/davidshaknovich/Desktop/Northeastern/ds3500/ds3500_fa22/hw/final/poem_line_final.csv")
