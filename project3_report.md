# Project 3 Report

<!--
pandoc --pdf-engine latexmk \
    -V papersize=a4paper -V fontsize=12pt \
    -V geometry:margin=1in -V mainfont=Times \
    -s project3_report.md -o project3_report.pdf
-->

In DTW, the node cost is set as the Euclidean distance between the input sample and the template, normalized by the length of the template to mitigate the effect of differences template lengths on the cumulative costs.

We recorded number zero through ten 10 times each, labeled with indexes 0 through 9. Steven recorded 0~4 and Luyao recorded 5~9. We started with the number recordings with index 0, and attempted to test them against recordings 1, 3, 5, 7, and 9. However, since we intentionally recorded each instance differently, the recognition was too difficult and the accuracies were low, at only about 0.33. Steven re-recorded 10 similar instances for each number, labeled them indexes that are 10 larger than the previous set, and used them to test the DTW model.

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

Best pruning threshold seems to be 13, according to Figure 1.

![Classification accuracy corresponding to pruning thresholds.](./dtw_accuracy_vs_threshold.pdf)

When adding more templates (12, 14, 16, 18), the accuracy increased and quickly reached 1, as shown in Figure 2.

![Classification accuracy corresponding to the number of templates used.](./dtw_n_template_vs_accuracy.pdf)

Therefore, we reverted to using the initial recordings with indexes 0 through 9, which we refer to as hard mode. As shown in Figure 3, the accuracy was lower, and increased as we added Steven's recordings 2 and 4 as templates. This is because Steven's recordings vary significantly, and the added templates contributed to the model.

![Classification accuracy corresponding to the number of templates used (hard mode).](./dtw_n_template_vs_accuracy_hard.pdf)
