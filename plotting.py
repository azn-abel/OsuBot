import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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

    if len(scores_pp) <= 0:
        raise Exception("User has no plays for the specified mode.")

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
    plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)

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
    all_countries = [ranking['user']['country_code'] for ranking in rankings]

    countries = list(set(all_countries))
    countries.sort()

    # Algorithm to get indices of top three countries
    counts = [all_countries.count(country) for country in countries]
    sorted_counts = sorted(counts, reverse=True)
    highest_indices = []
    num_countries_to_list = 10 if len(countries) > 10 else len(countries)
    for i in range(num_countries_to_list):
        start = 0
        index = counts.index(sorted_counts[i], start)
        while index in highest_indices:
            start = index + 1
            index = counts.index(sorted_counts[i], start)
        highest_indices.append(index)

    top_countries_dict = {}
    for index in highest_indices:
        top_countries_dict[countries[index]] = counts[index]

    plt.xlabel('Country')
    plt.ylabel('Count')

    fig = plt.gcf()
    len_values = len(countries)

    fig.set_size_inches(8.5 if len_values < 23 else len_values * 0.4, 6)
    plt.subplots_adjust(left=0.07, right=0.98, top=0.9, bottom=0.15)

    plt.bar(countries, counts, color="#ff79b8", edgecolor='white')

    # Create an in-memory binary stream
    buffer = io.BytesIO()

    # Set the y-axis to show a maximum of 5 integer ticks
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))

    # Save the figure to the binary stream as bytes, clear plt
    plt.savefig(buffer, format='png')
    plt.clf()

    # Return image bytes in png form, close buffer
    image_bytes = buffer.getvalue()
    buffer.close()
    return image_bytes, top_countries_dict
