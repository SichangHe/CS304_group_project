"""Unrestricted number of digits.
Run as `python3 -m speech.project6.unrestricted_digits`."""

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from speech.project5.phone_rand import avg
from speech.project5.unrestricted_digits import DIGIT_STRINGS, TRANSITION_LOSSES, test
from speech.project6.trncontspch import train_digit_sequences

plt.rcParams["font.size"] = 24
plt.rcParams["lines.linewidth"] = 4


def main() -> None:
    ax: Axes
    digit_hmm_dict = train_digit_sequences()
    digit_hmms = [digit_hmm_dict[digit] for digit in range(10)]

    metrics_list: list[tuple[list[str], list[float], list[float], float]] = []
    for transition_loss in TRANSITION_LOSSES:
        metrics = test(digit_hmms, transition_loss)
        metrics_list.append(metrics)

    fig, ax = plt.subplots()
    ax.plot(
        TRANSITION_LOSSES,
        [sentence_accuracy for _, _, _, sentence_accuracy in metrics_list],
        label="% Accurate Sentence",
    )
    ax.plot(
        TRANSITION_LOSSES,
        [avg(word_error_rates) for _, _, word_error_rates, _ in metrics_list],
        label="Average % Accurate Word",
    )
    ax.grid()
    ax.set_xlabel("Transition Loss")
    ax.legend()
    plt.xticks(ha="center", rotation=60)
    plt.show(block=True)
    fig.savefig("transition_losses_vs_digit_accuracy_improved.png", bbox_inches="tight")

    best_transition_loss, (
        recognitions,
        _,
        word_error_rates,
        sentence_accuracy,
    ) = min(
        zip(TRANSITION_LOSSES, metrics_list), key=lambda metrics: avg(metrics[1][2])
    )
    print(
        f"""
Best transition loss: {best_transition_loss}
Sentence accuracy: {sentence_accuracy:.2f}%.
Average word error rate: {avg(word_error_rates):.2f}%."""
    )
    fig, ax = plt.subplots()
    bars = ax.bar(DIGIT_STRINGS, word_error_rates)
    for bar, recognition in zip(bars, recognitions):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            recognition,
            ha="center",
            va="bottom",
            rotation=60,
        )
    ax.grid()
    ax.set_xlabel("Digit String")
    ax.set_ylabel("% Word Error Rate")
    plt.xticks(ha="center", rotation=60)
    plt.show(block=True)
    fig.savefig("digit_string_recognition_improved.png", bbox_inches="tight")


main() if __name__ == "__main__" else None
