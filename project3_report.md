# Project 3 Report

In DTW, the node cost is set as the Euclidean distance between the input sample and the template, normalized by the length of the template to mitigate the effect of differences template lengths on the cumulative costs.

We started with the number recordings with index 0, and attempted to test them against recordings 1, 3, 5, 7, and 9. However, since we intentionally recorded each instance differently, the recognition was too difficult and the accuracies were low, at only about 0.33. We re-recorded 10 similar instances for each number, gave them indexes that are 10 larger than the previous set, and used them to test the DTW model.

Single DTW, taking the minimum finish costs of each template for comparison to decide which template is the best match:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|1.0|1.0|0.6|1.0|1.0|0.8|1.0|1.0|1.0|1.0|1.0|0.95

By taking the last finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|1.0|1.0|0.6|1.0|1.0|0.6|0.6|0.8|1.0|1.0|1.0|0.87

By taking the first finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|1.0|1.0|0.6|1.0|1.0|0.6|0.6|0.8|1.0|1.0|1.0|0.87

On average, taking the minimum finish costs gave the best accuracy, therefore we continued with this method for the time-synchronous DTW. However, the sample size is too small to draw a conclusion.

Best pruning threshold seems to be 13:

![Classification accuracy corresponding to pruning thresholds.](./dtw_accuracy_vs_threshold.pdf)
