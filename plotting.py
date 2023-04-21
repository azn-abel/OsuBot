import api
import numpy as np
import matplotlib.pyplot as plt
import io


def scatter_scores(scores: list):
    plt.clf()
    # Data
    x_values = [i for i in range(0, len(scores))]
    y_values = [score['pp'] for score in scores]

    # Create plot
    plt.scatter(x_values, y_values)

    # Add labels. No title because the embed will handle it
    plt.xlabel("Play Ranking out of 100")
    plt.ylabel("Performance Points (PP)")

    # create an in-memory binary stream
    buffer = io.BytesIO()

    # Save the figure to the binary stream as bytes and clear plt
    plt.savefig(buffer, format='png')
    plt.clf()

    # Close buffer and return bytes
    image_bytes = buffer.getvalue()
    buffer.close()
    return image_bytes


def histogram_scores(scores: list):
    plt.clf()
    plt.rcParams.update({'font.size': 16})
    scores_pp = [score['pp'] for score in scores]

    # Set the bin edges manually to be intervals of 10
    bin_edges = np.arange(min(scores_pp) // 10 * 10, max(scores_pp) // 10 * 10 + 11, 10)

    # Create a histogram with 20 bins
    plt.hist(scores_pp, bins=bin_edges, color="#ff79b8", edgecolor='white')

    # Add label. No title because the embed will handle it
    plt.xlabel('PP Value')
    plt.ylabel('Frequency')

    # Set size and adjust margins
    fig = plt.gcf()
    fig.set_size_inches(10, 5)
    plt.subplots_adjust(top=0.9, bottom=0.15)

    # Create an in-memory binary stream
    buffer = io.BytesIO()

    # Save the figure to the binary stream as bytes, clear plt
    plt.savefig(buffer, format='png')
    plt.clf()

    # Return image bytes in png form, close buffer
    image_bytes = buffer.getvalue()
    buffer.close()
    return image_bytes


def bar_ranks(rankings: list):
    plt.clf()
    plt.rcParams.update({'font.size': 14})
    penis = [ranking['user']['country_code'] for ranking in rankings]

    x_values = list(set(penis))
    x_values.sort()

    y_values = [penis.count(country) for country in x_values]

    plt.xlabel('X-axis label')
    plt.ylabel('Y-axis label')
    plt.title('Bar chart title')

    fig = plt.gcf()
    fig.set_size_inches(18, 4)
    plt.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.15)

    plt.bar(x_values, y_values)

    plt.show()


if __name__ == "__main__":
    # scores = api.get_scores("btmc", "osu", "best", 100)
    # histogram_scores(scores)
    rankings = api.get_rankings('osu', 3)
    bar_ranks(rankings)
    pass
