# Project 6 Report

## Training With Continuous Speech

## Telephone Number Recognition Results

We reuse the 25 `.wav` files of telephone numbers from project 5.

Comparing to the results from project 5,
with single HMM trained with 20 templates for each digit with 4 Gaussians:

Sentence accuracy: 36.00%—9 telephone numbers were recognized correctly.
Average word accuracy: 65.00%—86.0 digits were recognized correctly.

![Telephone number recognition trained with 20templates and 4
Gaussians.](./assets/project5/telephone_number_recognition_20templates_4gaussians.png)

## Unrestricted Digit String Recognition Results

Comparing to the results from project 5,
using the observed best transition loss 385.08,
the sentence accuracy is 50.00%, and the average word error rate: 10.69%,
as shown in the figure below.

![Unrestricted digit string
recognition.](./assets/project5/digit_string_recognition.png)

## Conclusion
