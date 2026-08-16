"""Shared style settings for all figures in this paper, so they render consistently
regardless of which figure script is run. Import COLORS and call apply_style()
at the top of each figure script."""

import matplotlib.pyplot as plt

NAVY = "#1a2b4c"
ORANGE = "#DD8452"
GREEN = "#55A868"
BLUE = "#4C72B0"
GREY = "#888888"

SEO_COLORS = {
    "Agriculture": "#2c7a3f", "Environment": "#5aa06c", "Health": "#4C72B0",
    "IPT": "#c44e52", "Earth": "#8172b2", "Energy": "#ccb974",
    "Society": "#64b5cd", "Space": "#937860", "TTI": "#da8bc3",
    "Defence": "#6d6d6d", "GAK": "#dedede",
}
SEO_ORDER = ["Agriculture", "Defence", "Earth", "Energy", "Environment",
             "Health", "IPT", "Society", "Space", "TTI", "GAK"]
FORD_ORDER = ["Natural sciences", "Engineering & technology", "Medical & health",
              "Agricultural sciences", "Social sciences", "Humanities"]


def apply_style():
    plt.rcParams.update({
        "font.size": 10.5,
        "axes.titlesize": 12.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": NAVY,
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.edgecolor": "#444444",
        "axes.labelcolor": "#333333",
    })


import textwrap


def add_caption(fig, text, width=150):
    """Small italic source/methodology caption in the bottom-left corner.
    Manually wraps at `width` characters using textwrap rather than
    matplotlib's wrap=True, which is unreliable in combination with
    bbox_inches="tight" -- a long unwrapped caption can silently expand
    the saved PNG's bounding box far past the actual plot."""
    wrapped = "\n".join(textwrap.wrap(text, width=width))
    fig.text(0.01, 0.005, wrapped, fontsize=6.8, color=GREY, style="italic",
              ha="left", va="bottom")
