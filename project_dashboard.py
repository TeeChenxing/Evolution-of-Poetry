import pandas as pd
import project_sankey as proj_sk
import sentiment as flower
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import re

word_df = pd.read_csv("poem_word_final.csv")

# possible emotions from pyplutchik's library
emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

def read_poems():
    """
    :return: convert a csv to a dataframe and change values in the century column
             Ex. 1900 --> 19th Century
    """
    century_df = pd.read_csv("century_count_final.csv")

    for century in century_df['century']:
        century_df['century'] = century_df['century'].replace(century, f'{str(century)[:-2]}th Century')

    # substitute certain values such as \r with ' '
    word_df['author'] = word_df['author'].apply(lambda x: re.sub('\s+', ' ', x))

    return century_df, word_df


def trim_count_df(df, col='century', n=5):
    """
    :param df: a poem dataframe
    :param col: a column name
    :param n: top n words for each specified column value
    :return: in the default, will return top 5 words for every century
    """
    return df.groupby(col).head(n).reset_index()


def trim_word(df, author, word_count=5):
    """
    :param df: a dataframe
    :param author: author name
    :param word_count: top n most common words for that author
    :return: a dataframe showing the top n most common words for specified author
    """
    # Keep required columns
    trim_word_df = df[["author", "word", "count"]]

    # Keep required columns, sort by count
    trim_word_df = trim_word_df[trim_word_df["author"] == author].sort_values(by=["count"], ascending=False).reset_index(drop=True)

    # Keep top n
    trim_word_df = trim_word_df.iloc[:word_count]

    return trim_word_df


century_df, word_df = read_poems()

app = Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Dashboard for the Evolution of Poetry",
                    style={"font-weight": "bold", "textAlign": "center"}),
            html.H4("Aanay Anandpara, Srishti Kundu, David Shaknovich, Teera Tesharojanasup",
                    style={"textAlign": "center"}),
            html.P("ㅤ")
        ])
    ], justify="center"),

    dbc.Row([
        dbc.Col([
            html.H4("Top n Common Words for Each Century",
                    style={"textAlign": "center"}),
            dcc.Graph(id="sankey1")
        ], width = 6),
        dbc.Col([
            html.H4("Top n Common Words for Specified Author",
                    style={"textAlign": "center"}),
            dcc.Graph(id="sankey2")
        ], width = 6)
    ]),

    dbc.Row([
        dbc.Col([
            html.P("Select the number of top most common words for each century:",
                   style={"font-family": "cursive"}),
            dcc.Slider(id="most_common", min=1, max=10, step=1, value=3)
        ]),
        dbc.Col([
            html.P("Select Author:", style={"font-family": "cursive"}),
            dcc.Dropdown(id="author_name", options=word_df['author'].unique(), value='Thomas Dunn English (1819-1902)'),
            html.P("ㅤ"),
            html.P("Select the number of top most common words for the author:",
                   style={"font-family": "cursive"}),
            dcc.Slider(id="author_wc", min=1, max=10, step=1, value=5),
            html.P("ㅤ")
        ])
    ]),
    dbc.Row([
        html.H4("Sentiment Analysis: Flower Diagram",
                    style={"textAlign": "center"})]),

    dbc.Row([
        dbc.Col(html.Div(html.Img(id='flower1')), width=6),
        dbc.Col(html.Div(html.Img(id='flower2')), width=3)
    ]),

    dbc.Row([
        dbc.Col([
            html.P("Select 1st Genre:",
                   style={"font-family": "cursive"}),
            dcc.Dropdown(id="category1", options=word_df['category'].unique(), value='Historical Poems')
        ]),
        dbc.Col([
            html.P("Select 2nd Genre:",
                   style={"font-family": "cursive"}),
            dcc.Dropdown(id="category2", options=word_df['category'].unique(), value='Historical Poems'),
            html.P("ㅤ")
        ])
        ]),
    dbc.Row([
        dbc.Col([
            html.H4("Emotion over Time",
                    style={"textAlign": "center"}),
            html.P("We recommend zooming into 1700-1900s for greater detail!",
                    style={"textAlign": "center"}),
            dcc.Graph(id="line1"),
            html.P("Note: Age of Revolution= Wave of revolutions for indepedence in EU",
                   style={"font-family": "cursive"})
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.P("Select Emotion:",
                   style={"font-family": "cursive"}),
            dcc.Dropdown(id="emotion", options=emotions, value='joy')
        ])
    ]),

], fluid=True)

@app.callback(
    Output("sankey1", "figure"),
    Output("sankey2", "figure"),
    Output("flower1", "src"),
    Output("flower2", "src"),
    Output("line1", "figure"),
    Input("most_common", "value"),
    Input("author_name", "value"),
    Input("author_wc", "value"),
    Input("category1", "value"),
    Input("category2", "value"),
    Input("emotion", "value"),
    )

def update_graphs(most_common, author_name, author_wc, category1, category2, emotion):
    # sankey diagram 1
    local1 = trim_count_df(century_df, 'century', most_common)
    fig1 = proj_sk.make_sankey(local1, 'century', 'word', 'count', pad=50, thickness=40, line_width=1, opacity=0.6)

    # sankey diagram 2
    local2 = trim_word(word_df, author_name, author_wc)
    fig2 = proj_sk.make_sankey(local2, 'word', 'author', 'count', pad=50, thickness=40, line_width=1, opacity=0.6)

    # flower diagrams
    fig3 = flower.make_flower(word_df, category1)
    fig4 = flower.make_flower(word_df, category2)

    # line graph
    fig5 = flower.make_line(word_df, emotion)

    return fig1, fig2, fig3, fig4, fig5

app.run_server(debug=False)
