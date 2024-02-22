# Project 5 Report

## From Single-Word to Multi-Word Speech Recognition

In this project,
we build a continuous speech recognition system using Hidden Markov Models
(HMMs).
The key component of our approach involved constructing a graph of HMM states by
connecting the models trained in project 3.

Mimicking the trie nodes in lexical trees in project 4,
we take each state in the HMMs corresponding to each digit as a node in the
graph and connect them to form a graph of HMM states.
The graph is composed of layers of digit HMMs,
with each layer having 10 digits to consider,
and each digit having 5 states (that is 50 states per layer).
The graph is then used to recognize continuous speech,
similar to how the trie was used to spellcheck and segment the stings.

To match MFCC features against the HMM states in a similar fashion as we matched
strings against the trie nodes in project 4,
we modified the HMM states from project 3 to include the transition loss
(defined as the negative log transition probabilities)
from previous states to the current state,
as opposed to the previous implementation where we record the transition
probabilities from the current state to the new states.
This change makes it more each to chain HMM states corresponding to different
digits together.
It also allows fewer lookup operations when walking the HMM graph.

To establish connections between two individual digits,
we introduce a non-emitting state.
This state is inserted between the last state of the previous digit and the
first state of the next digit.
Non-emitting states are identical to the emitting states,
except that they do not contain the label for a corresponding digit,
nor parameters for the Gaussian mixtures,
so they do not emit any observation losses.
By starting with a non-emitting state,
using non-emitting states to connect multiple layers of digit HMMs,
and ending with another non-emitting state,
we allow recognizing speech with multiple digits.

To handle non-emitting states,
we distinguish non-emitting states and process all of them before we match each
MFCC feature vector against the emitting states.
The resulting loss nodes (please refer to project 4 for the design of loss
nodes) are compared to the previous losses and used to replace them if smaller,
that is,
these states are "teleported" before matching the next MFCC feature vector.
After the last MFCC feature vector is processed,
this "teleportation" process is repeated so that the HMM graph reaches the final
non-emitting state.

Similar to project 3,
we traversed the feature sequence and updated the losses along the way.
We also handle the non-emitting states similarly to how we handled the emitting
states in each round,
and reset the round-minimum loss after considering all non-emitting states.
In our testing, we found a beam width of 4000 to be good enough.

## Problem 1

In this problem,
our recognize telephone numbers consisting of either 4 or 7 digits.
Because the input search space is well-defined,
we first build an acyclic graph connecting seven layers of digit HMMs,
with the first layer only having digits 2 ~ 9.
The ability to have multiple layers of digit HMMs is achieved by cloning the HMM
states in a way that preserves the transition losses among them.
To connect each layer, we specify eight non-emitting states in between,
and record an exit loss for the last state of HMM states corresponding to each
digit for the transition loss from the non-emitting states to the next digit
layers. In total, our HMM graph has $(7 + 6 × 10) × 5 + 8 = 343$ HMM states.

A separate cost-free transition from the first non-emitting state to the
non-emitting state before the forth digit layer is added to enable recognizing
4-digit numbers.

Additionally, we introduce a silence HMM state and allow transition between it
and the fourth non-emitting state.
This state helps allow a pause between the first three digits and the last four.

### Result

We recorded 25 `.wav` files of telephone numbers,
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
the target word, with a lower bound of 0.

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
We also note that the model has a tendency to recognize 4-digit numbers as
7-digit numbers due to a lack of transition loss between digits,
and it particularly struggles with the digit 7 and 9,
presumably because of training data with less variation.

## Problem 2

In this problem, the digit strings do not have any specific constraints,
so we simply connect one non-emitting state to one digit layer,
allowing transitions from the HMM states at the end of the digit layer to the
non-emitting state,
from the non-emitting state to HMM states at the beginning of the digit layer.

The "insertion penalty" is implemented by adding an extra transition loss at the
transition loss from the last digit HMM states to the non-emitting state.
This mechanism discourages digit insertion during recognition.

### Empirical Optimal Transition Loss

In this experiment,
we use single digit HMMs trained with 20 templates and 4 Gaussians. We explored
various transition losses and identified the transition loss that yielded the
best results.

![Transition losses vs digit
accuracy.](./assets/project5/transition_losses_vs_digit_accuracy.png)

The observed best transition loss is 385.08,
where the sentence accuracy is 50.00%, and the average word error rate: 10.69%,
as shown in the figure below.

![Unrestricted digit string
recognition.](./assets/project5/digit_string_recognition.png)

Like before, the model struggles with the digit 7 and 9,
as well as long digit strings.
