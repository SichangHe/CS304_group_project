# Project 6 Report

## Alternative Approaches

Before we adopted the approach documented in the lecture slides,
we brainstormed some alternative approaches:

1. Each HMM state stores a set of groups of associated features,
    which are updated each round.
1. Change the means, variances, and transition losses of each state each round.
1. Aggregate the means, variances, and transition losses of training output
 from all sequences.

The two latter approaches may not converge, so we did not attempt them.
We experimented with the first approach,
but it was very complicated to implement.

## Training With Continuous Speech

1. Initialize the Hidden Markov Model (HMM) with isolated word features.

2. Proceed to segment the continuous speech feature vectors by connecting the HMM
states directly, without adding non-emitting states.
This segmentation process divides the continuous speech feature vectors into
separate parts, each corresponding to a specific digit.

3. Use the separated digit feature vectors,
along with the original isolated word features used in step 1,
to train new isolated word HMMs.

4. If convergence is not achieved (i.e.,
the alignment of continuous speech feature vectors for each digit does not
remain unchanged), return to step 2.

It takes around 17min to train the continuous speech model with 20 isolated
templates, all the continuous templates, and 4 Gaussians.
The training takes 10 iterations to converge,
as shown in the log of the difference of feature segmenting in each round:

```sh
Diff: 222, Total: 300
Diff: 75, Total: 300
Diff: 66, Total: 300
Diff: 25, Total: 300
Diff: 16, Total: 300
Diff: 26, Total: 300
Diff: 22, Total: 300
Diff: 23, Total: 300
Diff: 0, Total: 300
```

Please note that the first round does not have a previous alignment to show the difference, hence the log includes 9 lines for the 10 iterations.

## Telephone Number Recognition Results

We reuse the 25 `.wav` files of telephone numbers from project 5.

Comparing to the results from project 5,
with single HMM trained with 20 templates for each digit with 4 Gaussians:

Sentence accuracy: 36.00%—9 telephone numbers were recognized correctly.
Average word accuracy: 65.00%—86.0 digits were recognized correctly.

![Telephone Number Recognition Trained With 20 Isolated Templates And 4
Gaussians.](./assets/project5/telephone_number_recognition_20templates_4gaussians.png)

The new results are much improved:

Sentence accuracy: 68.00%—17 telephone numbers were recognized correctly.
Average word accuracy: 85.71%—113.0 digits were recognized correctly.

![Telephone Number Recognition Trained With 20 Isolated Templates,
30 Continuous Templates,
And 4
Gaussians.](telephone_number_recognition_improved.png)

## Unrestricted Digit String Recognition Results

### Empirical Optimal Transition Loss

Similar to project 5, we explored different transition losses and determined the one that produced the best outcomes.

In project 5, the figure below illustrates the results obtained using the best transition loss of 385.08. The sentence accuracy was 50.00%, and the average word error rate was 10.69%.

![Transition losses vs digit
accuracy.](./assets/project5/transition_losses_vs_digit_accuracy.png)

The new results, displayed in the diagram below, show significant improvement:

Sentence accuracy: 70.00%—7 digit string were recognized correctly.
Avg word error rate: 7.24%.

Best transition loss: 462.09812268378744.
Sentence accuracy: 80.00%.
Average word error rate: 3.27%.

![Transition Losses And Digit Accuracy With Continuous
Templates.](./transition_losses_vs_digit_accuracy_improved.png)

Subsequently, we compared the recognition results between project 5 and this project both using the best transition loss.

The recognition result from project 5 is presented below.

![Unrestricted Digit String
Recognition Trained With 20 Isolated Templates And 4 Gaussians.](./assets/project5/digit_string_recognition.png)

The recognition result from this project, as depicted below, demonstrates a substantial improvement.

![Unrestricted Digit String
Recognition Trained With 20 Isolated Templates, 30 Continuous Templates,
And 4 Gaussians.](digit_string_recognition_improved.png)

## Conclusion

In conclusion,
the results of this project demonstrate that training with continuous speech can
significantly improve the accuracy of telephone number recognition and
unrestricted digit string recognition.
