# Project 3 Report

## Dataset

We recorded number zero through ten 10 times each, labeled with indexes 0 through 9. Steven recorded 0~4 and Luyao recorded 5~9. This is later referred to as the "hard" dataset because we intentionally recorded each instance differently. Steven later recorded 10 more instances for each number, and labeled them indexes that are 10 larger than the previous set. In this second dataset, the instances are very similar to each other.

## Problem 1

We used dynamic time warping (DTW) to match the 39-dimensional boosted normalized Mel frequency cepstrum coefficients (MFCCs) between the templates and the test samples. The implementation is in `./speech/project3/dtw.py`.

### DTW With Single Templates

We started with a basic DTW implementation. We set the node cost to be the Euclidean distance between the input sample and the template, normalized by the length of the template to mitigate the effect of differences template lengths on the cumulative costs.
We started with the "hard" dataset, using the number recordings with index 0 as the single templates, and attempted to test them against recordings 1, 3, 5, 7, and 9. However, since we intentionally recorded each instance differently, the recognition was too difficult and the accuracies were low, at only about 0.33. We later used the second dataset with index 10 through 19 to test the DTW model.

In this process, we experimented with the selection of DTW finish costs used for comparison. We first took the minimum finish costs of each template for comparison to decide which template is the best match:

| Number   | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0  | 1.0 | 0.6 | 1.0   | 1.0  | 0.8  | 1.0 | 1.0   | 1.0   | 1.0  | 1.0 | 0.95    |

We then compared by taking the last finish costs:

| Number   | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0  | 1.0 | 0.6 | 1.0   | 1.0  | 0.6  | 0.6 | 0.8   | 1.0   | 1.0  | 1.0 | 0.87    |

And, we compared by taking the first finish costs:

| Number   | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 0.0  | 0.0 | 0.0 | 0.0   | 0.8  | 1.0  | 0.6 | 0.0   | 0.0   | 0.2  | 0.0 | 0.24    |

On average, taking the minimum finish costs gave the best accuracy, therefore we continued with this method for the time-synchronous DTW. However, the sample size is too small to draw a conclusion.

For time-asynchronous DTW, we feed each input frame into the comparator for each template.

### Pruning for DTW

To implement pruning for DTW, we record a round minimum cost after each round of comparison. We set the round threshold as the sum of the round minimum cost and the pruning threshold, and discard the entries in the last column of the trellis larger than the round threshold by setting them to infinity. When iterating to the next round, we skip calculating the node costs to reduce the computation time.

The best pruning threshold seems to be 13, according to Figure 1.

![Classification accuracy corresponding to pruning thresholds.](./dtw_accuracy_vs_threshold.png)

### DTW With Five Templates

When adding more templates (12, 14, 16, 18), the accuracy increased and quickly reached 1, as shown in Figure 2.

![Classification accuracy corresponding to the number of templates used.](./dtw_n_template_vs_accuracy.png)

Therefore, we reverted to using the initial "hard" recordings with indexes 0 through 9. As shown in Figure 3, the accuracy was lower, and increased as we added Steven's recordings 2 and 4 as templates. This is because Steven's recordings vary significantly, and the added templates contributed to the model.

![Classification accuracy corresponding to the number of templates used (hard mode).](./dtw_n_template_vs_accuracy_hard.png)

The above results are obtained using the best pruning threshold we determined earlier. If we remove the threshold, we get very similar results, as shown in Figure 4.

![Classification accuracy corresponding to the number of templates used (hard mode, no pruning).](./dtw_n_template_vs_accuracy_hard_no_pruning.png)

## Problem 2

### Hidden Markov Model Training

To train the Hidden Markov Model (HMM) for the numbers, we follow the following steps:

1. Initialize all parameters uniformly:
   1. Initialize state means and covariances.
   2. Initialize transition probabilities.
2. Segment all training sequences.
3. Reestimate the parameters from segmented training sequences:
   1. Update state means and covariances based on the segmented sequences.
   2. Update transition probabilities based on the segmented sequences.
4. If the segmenting is not the same as last round, go back to step 2 and repeat the process.

### Prediction

After training the HMM model for each of the numbers (0 to 10), we can make predictions using the following steps:

1. Feed the test sample into each of the HMM models.
2. Calculate the log probability for each HMM model.
3. Select the number associated with the highest log probability as the predicted number.

### Viterbi decoding

We utilize the dynamic programming Viterbi decoding algorithm to find the best observed sequence of the HMM.
The transition probabilities are derived from the sequences segmented into states using the following formula:
$$ P_{ij} = \frac{\sum_k N_{k, i, j}}{\sum_k N_{k, i}} $$
where:

- $N_{k, i}$ is the number of vectors in the ith segment (state) of the kth training sequence
- $N_{k, i, j}$ is the number of vectors in the ith segment (state) of the kth training sequence that were followed by vectors from the jth segment (state)

The emission probabilities are determined using the Gaussian distribution for each state. We calculate the probability density function (PDF) of the input feature vector using the state mean and covariance.

To simplify the computation of the Multivariate Gaussian distribution, we assume a diagonal covariance matrix. This means that the covariance matrix only contains non-zero values along the diagonal and zero values elsewhere. The probability density function (PDF) can be computed using the following formula:

$$ f(x) = \frac{1}{\sqrt{(2\pi)^D \prod\limits_d \sigma_d^2}} \exp \Bigl(-0.5\sum_d \frac{(x_d - \mu_d)^2}{\sigma_d^2}\Bigr) $$

To further reduce computations, we can optimize the calculation of emission probabilities by evaluating them only when the transition probability and Viterbi trellis of the last time step are valid. This optimization helps to save computation time.

We keep track of the best score (log probability) for each state at each time, and then backtrack to find the optimal trace by following the states with the highest scores at each time.

### HMM Result

Result for "easy" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | 0.98 |

Result for "hard" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 0.6 | 0.8 | 0.8 | 0.6 | 0.6 | 0.6 | 0.6 | 1.0 | 1.0 | 0.78 |

## Problem 3

In addition to the routine followed in problem 2, we introduce the following modification:

1. Initialize all parameters uniformly and train HMMs with a single Gaussian:
   1. Initialize state means and covariances with a single Gaussian.
   2. Initialize transition probabilities.
2. Segment all training sequences.
3. Reestimate the parameters from segmented training sequences:
   1. Update state means and covariances based on the segmented sequences.
   2. Update transition probabilities based on the segmented sequences.
4. *Split* the Gaussians in the state output distributions to obtain a larger Gaussian mixture at each state.
5. Use the K-means algorithm to find clusters of Gaussians for each state (Not using EM for GMM for simplicity as suggested in assignment specification).
6. If the convergence criterion is not met, go back to step 2 and repeat the process.

### Splitting Gaussians

To split the Gaussians, we use the following formula:

$$
\begin{align*}
    y_n^+ &= y_n ( 1 + \epsilon  ) \\
    y_n^- &= y_n ( 1 - \epsilon  )
\end{align*}
$$

where $y_n$ represents a cluster mean and $\epsilon$ is set to 0.1.
At each iteration, we increase the number of Gaussians by a power of 2, resulting in 1, 2, 4, 8, and so on Gaussians.

### Emission probabilities with Gaussian mixture

Instead of having a single Gaussian distribution for each state, we represent the emission probabilities as a mixture of multiple Gaussian distributions. Each state contains a Gaussian mixture model, and the emission probability is calculated by selecting the Gaussian component with the highest probability within that segmented state.

This approach allows for capturing the complexities and variations in the observed data by modeling them with multiple Gaussian distributions within each state.

### HMM Result With Two Gaussians

Result for "easy" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | 0.98 |

Result for "hard" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 0.4 | 0.8 | 1.0 | 0.8 | 0.8 | 0.8 | 0.4 | 1.0 | 1.0 | 0.82 |

### HMM Result With Four Gaussians

Result for "easy" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.8 | 1.0 | 1.0 | 1.0 | 1.0 | 0.98 |

Result for "hard" dataset:
| Number | zero | one | two | three | four | five | six | seven | eight | nine | ten | Average |
| -------- | ---- | --- | --- | ----- | ---- | ---- | --- | ----- | ----- | ---- | --- | ------- |
| Accuracy | 1.0 | 1.0 | 0.4 | 1.0 | 0.6 | 0.4 | 0.6 | 0.8 | 0.6 | 1.0 | 1.0 | 0.76 |

As we can see from the results, we observe that for the "easy" dataset, HMMs with 1, 2, and 4 Gaussians perform equally well with an accuracy of 0.98. On the other hand, for the "hard" dataset, the HMM with 2 Gaussians outperforms the others. This difference in performance could be attributed to the fact that the HMM with four Gaussians may be overfitting the training data. Since we only have five templates for each digit, a higher number of Gaussians might lead to overfitting, where the model becomes too specialized and fails to generalize well to unseen data. In future projects, we will include more diverse training data so that the model can generalize more effectively to unseen instances.

### HMM Caching

Since calculating the HMM parameters is computationally expensive, we cache the parameters for each number with the given template file paths and configuration. We achieve this caching function using library `cache_to_disk`. The cached HMM are loaded instantly for our HMM demo.
