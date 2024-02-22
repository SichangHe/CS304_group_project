# Project 5 Report

## From Single Word to Continuous Speech Recognition

In this project,
we build a continuous speech recognition system using Hidden Markov Models
(HMMs).
The key component of our approach involved constructing a graph of HMM states by
connecting the models trained in project 3.

Mimicking the trie nodes in lexical trees in project 4,
we take each state in the HMMs corresponding to each digit as a node in the
graph and connect them to form a graph of HMM states.
The graph is then used to recognize continuous speech,
similar to how the trie was used to spellcheck and segment the stings.

To establish connections between the individual digits,
we introduce a non-emitting state.
This state is inserted between the last state of the previous digit and the
first state of the next digit with a transition loss.
This non-emitting state allows recognition of continuous speech.

In terms of the state representation,
each position in the speech sequence had 10 possible digits to consider.
With each digit consisting of 5 states,
a total of 50 states were associated with each position. Consequently,
for a 10-digit number, our graph comprised 10 * 50 + 11 = 511 states.

Similar to project 3,
we traversed the feature sequence and updated the losses along the way. However,
in this project,
we needed to account for the presence of the non-emitting state.

During each round of the travsersal,
we use a beam width to consider only losses smaller than minimum loss at this
round plus beam width.
This significantly reduce computation complexity while not influencing the
results much.

## Problem 1

In this problem,
our objective was to recognize telephone numbers consisting of either 3 or 7
digits. To address this requirement, we made the following modifications:

1.
We add an exit loss after the non-emitting state following the third position.
This allowed us to identify the end of a 3-digit number and initiate the
recognition process.

2. Additionally, we introduced a silence HMM state following the third state.
This state helped improve the recognition accuracy by capturing pauses or breaks
between digits.

### Result

We record wav files of telephone numbers,
the sequence can either be 4 or 7 digits long.
Here is a sample of the telephone numbers we used:

```python
TELEPHONE_NUMBERS = [
    "8765",
    "2356",
    "4198",
    "7432",
    "5321",
    "6214",
    "8743021",
    ...
]
```

We measured the accuracy of our system using two metrics:
sentence accuracy and average word accuracy.
Sentence accuracy represented the percentage of correctly recognized whole
sequences,
while average word accuracy measured the percentage of individual digits
correctly recognized using the 1 - Levenshtein distance divided by the length of
the target word.

We conducted experiments using different configurations of HMMs trained with
varying templates and Gaussians. Here are the results:

1. Single HMM trained with 10 templates for each digit with 2 Gaussians:

    Sentence accuracy: 16.00%—4 telephone numbers were recognized correctly.
    Average word accuracy: 56.29%—74.0 digits were recognized correctly.

    ![Telephone number recognition trained with 10templates and 2
    Gaussians.](./assets/project5/telephone_number_recognition_10templates_2gaussians.png)

2. Single HMM trained with 10 templates for each digit with 4 Gaussians:

    Sentence accuracy: 16.00%—4 telephone numbers were recognized correctly.
    Average word accuracy: 57.00%—78.0 digits were recognized correctly.

    ![Telephone number recognition trained with 10templates and 4
    Gaussians.](./assets/project5/telephone_number_recognition_10templates_4gaussians.png)

3. Single HMM trained with 20 templates for each digit with 4 Gaussians:

    Sentence accuracy: 36.00%—9 telephone numbers were recognized correctly.
    Average word accuracy: 65.00%—86.0 digits were recognized correctly.

    ![Telephone number recognition trained with 20templates and 4
    Gaussians.](./assets/project5/telephone_number_recognition_20templates_4gaussians.png)

We find that increasing the number of Gaussians slightly increase the accuracy
and using more training data significantly increase the accuracy.

## Problem 2

The second problem did not impose any specific constraints,
allowing us to utilize the connected HMM state graph directly for recognition.

### Result

In this experiment,
we use single digit HMMs trained with 20 templates and 4 Gaussians. We explored
various transition losses and identified the transition loss that yielded the
best results.

![Transition losses vs digit
accuracy.](./assets/project5/transition_losses_vs_digit_accuracy.png)

Best transition loss: 385.0817700584015 Sentence accuracy: 50.00%.
Average word error rate: 10.69%.

![Unrestricted digit string
recognition.](./assets/project5/digit_string_recognition.png)
