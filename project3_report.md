# Project 3 Report

Single DTW, taking the minimum finish costs of each template for comparison to decide which template is the best match:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten
-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.2|0.2|1.0|0.2|0.2|0.4|0.2|0.2

By taking the last finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten
-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.4|0.0|0.8|1.0|0.0|0.0|0.0|0.2

By taking the first finish costs:

Number|zero|one|two|three|four|five|six|seven|eight|nine|ten
-|-|-|-|-|-|-|-|-|-|-|-
Accuracy|0.4|0.4|0.2|0.4|0.0|0.8|1.0|0.0|0.0|0.0|0.2

On average, taking the minimum finish costs gave the best accuracy, therefore we continued with this method for the time-synchronous DTW. However, the sample size is too small to draw a conclusion.
