import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import itertools


def hex_to_rgba(hex_val, opacity):
    """
    :param rgb_val: list of hex values
    :param opacity: opacity value from 0 to 1
    :return: a list rgba values
    """
    color_ls = [list((int(hex_val[i:i+2], 16)) for i in (0, 2, 4))]

    for i in color_ls:
        i.append(opacity)

    merged = list(itertools.chain(*color_ls))

    return merged


def make_sankey(df, src, targ, val, **kwargs):
    """
    :param df: a dataframe
    :param src: source column name
    :param targ: target column name
    :param val: value column name
    :param kwargs: values for pad, thickness, line_color, line_width, opacity
    :return: a sankey diagram!
    """

    df = df.rename(columns={src: "source", targ: "target", val: "value"})

    nodes = np.unique(df[["source", "target"]], axis=None)
    nodes = pd.Series(index=nodes, data=range(len(nodes)))

    pad = kwargs.get('pad', 50)
    thickness = kwargs.get('thickness', 30)
    line_color = kwargs.get('line_color', 'black')
    line_width = kwargs.get('line_width', 1)
    opacity = kwargs.get('opacity', 0.5)

    # create hex-codes for every node
    link_color_ls = [px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i in nodes.loc[df["source"]]]
    # convert hex-codes to rgba values (does this to add opacity b/c hex-codes can't modify opacity) values
    rgba_ls = [hex_to_rgba(color.lstrip('#'), opacity) for color in link_color_ls]

    link = {"source": nodes.loc[df["source"]],
            "target": nodes.loc[df["target"]],
            "value": df["value"],
            "color": [f'rgba({rgba_vals[0]}, {rgba_vals[1]}, {rgba_vals[2]}, {rgba_vals[3]})' for rgba_vals in rgba_ls]}

    node = {"label": nodes.index,
            "color": [px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i in nodes],
            'pad': pad, 'thickness': thickness,
            'line': {'color': line_color, 'width': line_width}
            }

    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)

    return fig

