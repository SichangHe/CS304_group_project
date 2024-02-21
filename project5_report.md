# Project 4 Report

## Continuous Speech Recognition

In this project, we build a continuous speech recognition system using Hidden Markov Models (HMMs). The key component of our approach involved constructing a graph of HMM states by connecting the models trained in project 3.

To establish connections between the individual digits, we introduced a non-emitting state. This state was inserted between the last state of the previous digit and the first state of the next digit. This non-emitting state allows recognition of continuous speech.

In terms of the state representation, each position in the speech sequence had 10 possible digits to consider. With each digit consisting of 5 states, a total of 50 states were associated with each position. Consequently, for a 10-digit number, our graph comprised 10 * 50 + 11 = 511 states.

Similar to project 3, we traversed the feature sequence and updated the losses along the way. However, in this project, we needed to account for the presence of the non-emitting state.

### Problem 1

In this problem we need to recognize either 3 or 7 digit number. To address this requirement, we add an exit loss after the non-emitting state after the third position. Additionally, we introduced a silence HMM state following the third state.

### Problem 2

The second problem did not impose any specific constraints, allowing us to utilize the connected HMM state graph directly for recognition.
