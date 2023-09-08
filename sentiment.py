import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('SVG')   
from nrclex import NRCLex   
import numpy as np
import plotly.express as px
from pyplutchik import plutchik 
import io
import base64

# reading in the data
df = pd.read_csv("poem_word_final.csv")
print(df)
# keys for sentiment analysis
emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']


def get_emotions_text(text, keys):
    '''
    use NRCLex to obtain the emotion scores for a given text and list of emotions (i.e., keys)
    '''
    # Gets emotions associated to words in the review's text
    emo = NRCLex(text).raw_emotion_scores

    # Counts emotions occurrences (default is 0)
    # The difference is quite small so multiplying by 10 to scale the difference
    emo = {key: int(emo[key] > 0) * 10 if key in emo else 0 for key in keys}

    return emo

def grouped_df(df, element):
    """
    outputs a grouped df based on the input element
    """
    # convert to string
    df[element] = df[element].astype(str)
    df['word'] = df['word'].astype(str)

    # group by element (could be year, genre, etc.)
    genre = df.groupby([element], as_index = False).agg({'word': ' '.join})

    return genre

def get_emo_genre(df,genre):
    """
    get emotion scores based on genre
    """
    # call the grouped_df function to obtain df grouped by genre/category
    df = grouped_df(df, 'category')
    emo_scores = {}

    # Get texts that matches the genre inputted
    rslt_df = df[df['category'] == genre]
    # obtain individual words
    x = [str(x) for x in rslt_df['word']]
    x = x[0].split()

    # Get scores
    scores = [get_emotions_text(t, emotions) for t in x]
    emo_scores[genre] = {key: np.mean([s[key] for s in scores]) for key in emotions}

    return emo_scores
def get_overall_emo(df, emotion):
    """
    provide score for a given emotion, over time.
    For ex, joy over time or disgust over time
    """
    # update keys list to only include the inputted emotion
    keys = [emotion]

    # call grouped_df function to group by date and drop values lower than 1000
    df = grouped_df(df, 'date')
    df.drop(df.tail(4).index,
        inplace = True)

    # convert year to a type that python recognizes
    # note: some visualization packages don't consider earlier years like 1000 as 'date-time,' therefore int was chosen.
    df['date'] = df['date'].astype('float')
    df['date'] = df['date'].astype('int')

    # obtain a list of unique years
    years = df['date'].unique()

    # For each year, obtain the respective score for a given emotion
    emo_scores = {}
    for i in range(len(years)):
        year = df.loc[i]['date']
        text = df.loc[i]['word']
        # Obtain individual words
        # and obtain scores
        words = text.split()
        scores = [get_emotions_text(word, keys) for word in words]
        emo_scores[year] = np.mean([s[emotion] for s in scores])

    return emo_scores

def make_flower(df, genre):
    """
    forms a flower visualization using pyplutchik package (https://github.com/alfonsosemeraro/pyplutchik)
    outputs the visualization as an image source
    """
    # calls grouped_df and get_emo_genre functions to obtain the data for the viz
    output = get_emo_genre(grouped_df(df, 'category'), genre)[genre]

    buf = io.BytesIO() # in-memory files
    fig = plutchik(output, title = genre)  # makes the flower diagram
    plt.savefig(buf, format = "png") # save to the above file object
    plt.close()
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements

    return "data:image/png;base64,{}".format(data)

def make_line(df, emotion):
    """
    outputs a line graph visualizing a given emotion over time
    """
    # calls get_overall_emo to obtain values of a given emotion over the years
    emo_scores = get_overall_emo(df, emotion)
    emo_scores_df = pd.DataFrame(emo_scores.items(), columns=['Year', 'Value']) # convert to a format that px uses

    # plot
    fig = px.line(emo_scores_df, x="Year", y="Value", title= emotion.capitalize() + ' over Time')

    # add annotations manually to include relevant occurences of world events and art periods
    # ----------------- shapes, vertical lines ---------------------
    fig.update_layout(shapes=
                  [dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0=1400, x1=1400,
                        line=dict(color="MediumPurple",
                                  width=2,
                                  dash="dot")
                        ),
                  dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0=1600, x1=1600,
                        line=dict(color="MediumPurple",
                                  width=2,
                                  dash="dot")
                        ),
                  dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0=1750, x1=1750,
                        line=dict(color="MediumPurple",
                                  width=2,
                                  dash="dot")
                       ),
                  dict(type= 'line',
                        yref= 'paper', y0= 0, y1= 1,
                        xref= 'x', x0=1850, x1=1850,
                        line=dict(color="MediumPurple",
                                  width=2,
                                  dash="dot")
                       ),
                  ])

    # ----------------- text, annotations ---------------------
    fig.add_annotation(x=1757, y=emo_scores_df.loc[emo_scores_df['Year'] == 1757, 'Value'].iloc[0],
            text="7 Year War Starts",
            showarrow=True,
            arrowhead=1)

    fig.add_annotation(x=1830, y=emo_scores_df.loc[emo_scores_df['Year'] == 1830, 'Value'].iloc[0],
            text="Age of Revolution",
            showarrow=True,
            arrowhead=1)

    fig.add_annotation(x=1870, y=emo_scores_df.loc[emo_scores_df['Year'] == 1870, 'Value'].iloc[0],
            text="Franco-Prussian War",
            showarrow=True,
            arrowhead=4,
            ay = -150)

    # ----------------- text, art/historical periods ---------------------
    fig.add_annotation(
        x=1300, y=2, text=f'Medieval', yanchor='bottom', showarrow=False
        , align="center")

    fig.add_annotation(
        x=1500, y=2, text=f'Renaissance', yanchor='bottom', showarrow=False
        , align="center")

    fig.add_annotation(
        x=1630, y=2, text=f'Baroque', yanchor='bottom', showarrow=False
        , align="center")

    fig.add_annotation(
        x=1680, y=1.5, text=f'Scientific Revolution', yanchor='bottom', showarrow=False
        , align="center")

    fig.add_annotation(
        x=1790, y=2, text=f'Neo-classism', yanchor='bottom', showarrow=False
        , align="center")

    fig.add_annotation(
        x=1820, y=1.8, text=f'Romanticism', yanchor='bottom', showarrow=False
        , align="center")

    return fig

