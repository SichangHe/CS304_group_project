# Project 3 Report

In DTW, the node cost is set as the Euclidean distance between the input sample and the template, normalized by the length of the template to mitigate the effect of differences template lengths on the cumulative costs.

Single DTW, taking the minimum finish costs of each template for comparison to decide which template is the best match:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.2|0.2|1.0|0.2|0.2|0.4|0.2|0.2|0.33

By taking the last finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.4|0.0|0.8|1.0|0.0|0.0|0.0|0.2|0.31

By taking the first finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten|Average
-|-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.4|0.0|0.8|1.0|0.0|0.0|0.0|0.2|0.31

On average, taking the minimum finish costs gave the best accuracy, therefore we continued with this method for the time-synchronous DTW. However, the sample size is too small to draw a conclusion.
