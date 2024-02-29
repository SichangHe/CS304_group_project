# Project 6 Report

## Training With Continuous Speech

It takes around 17min to train the continuous speech model with 20 isolated
templates, all the continuous templates, and 4 Gaussians.

## Telephone Number Recognition Results

We reuse the 25 `.wav` files of telephone numbers from project 5.

Comparing to the results from project 5,
with single HMM trained with 20 templates for each digit with 4 Gaussians:

Sentence accuracy: 36.00%—9 telephone numbers were recognized correctly.
Average word accuracy: 65.00%—86.0 digits were recognized correctly.

![Telephone number recognition trained with 20templates and 4
Gaussians.](./assets/project5/telephone_number_recognition_20templates_4gaussians.png)

The new results are much improved:

Sentence accuracy: 68.00%—17 telephone numbers were recognized correctly.
Average word accuracy: 85.71%—113.0 digits were recognized correctly.

## Unrestricted Digit String Recognition Results

Comparing to the results from project 5,
using the observed best transition loss 385.08,
the sentence accuracy is 50.00%, and the average word error rate: 10.69%,
as shown in the figure below.

![Unrestricted digit string
recognition.](./assets/project5/digit_string_recognition.png)

## Conclusion
