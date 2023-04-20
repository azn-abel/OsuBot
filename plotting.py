import api
import numpy as np
import matplotlib.pyplot as plt


def scatter_scores(scores: list):
    plt.clf()
    # Data
    x_values = [i for i in range(0, len(scores))]
    y_values = [score['pp'] for score in scores]

    # Create plot
    plt.scatter(x_values, y_values)

    # Add labels
    plt.title("PP for Top 100 Plays")
    plt.xlabel("Play Ranking out of 100")
    plt.ylabel("Performance Points (PP)")

    # Show plot
    plt.savefig("plots/temp.png")

    # Clear once done
    plt.clf()


def histogram_scores(scores: list):
    plt.clf()
    plt.rcParams.update({'font.size': 16})
    scores_pp = [score['pp'] for score in scores]

    print(min(scores_pp), max(scores_pp))

    # Set the bin edges manually to be intervals of 10
    bin_edges = np.arange(min(scores_pp) // 10 * 10, max(scores_pp) // 10 * 10 + 11, 10)

    # Create a histogram with 20 bins
    plt.hist(scores_pp, bins=bin_edges, color="#ff79b8", edgecolor='white')

    # Add labels and title
    plt.xlabel('PP Value')
    plt.ylabel('Frequency')

    fig = plt.gcf()
    fig.set_size_inches(10, 5)

    # Adjust margins
    plt.subplots_adjust(top=0.9, bottom=0.15)

    # Save the plot
    plt.savefig("./plots/temp.png")

    # Clear once done
    plt.clf()


if __name__ == "__main__":
    scores = api.get_scores("btmc", "osu", "best", 100)
    histogram_scores(scores)
    pass
