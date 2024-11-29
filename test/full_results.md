# Findings
* During the test, I found that it is probably smart to use less tokens for the formatting question. The whole system input and initial question are not necessary to format the answer. This does seem to slow down the process, I assume because none of the input can be cached. It saves about 2k input tokens for formatting, BUT caching is removed. 
About half of the prompt (only the system prompt) can be cached normally, which is half price.

Let's take o1-preview - the most expensive model - as an example. 1k input tokens cost 0.015, so 1k cached tokens cost 0.0075.

Calculations done in cost_testing.py:
Adding all previous things to the prompt (so making use of caching): 0.671075$
Removing system prompt when formatting (so no caching): 0.6673250000000001$

This saves very little money, but sometimes there's errors that need to be handled, so it would go like this:
1 error with caching: 0.7834875$
1 error without caching: 0.79215$
2 errors with caching: 3.91$
2 errors without caching: 5.315$

Conclusion: just 1 error makes it more expensive to not use caching, so it depends on the error rate. More testing is necessary. Adding more runs to the test... Automating by finding the break-even point... Results:
```md
Calculating break-even point for 1000000 runs...
Break-even point found at error rate: 30.211400%
Cost with caching: 705036.3900250237
Cost without caching: 705036.3800500263
Difference: 0.01 (MORE expensive with caching)
```

Conclusion: if there are more than 30.21% errors, it's better to use caching. If there are less, it's better to not use caching. This will depend on the used model, as some models are more error-prone than others.

* The function: column_correlation was not correctly added to the prompt, which makes question 6 more difficult, BUT not impossible. o1-mini showed that it can be done by dropping all other columns and using correlation matrix.

# Questions
1. What is the average value of the AP column?
2. How many unique values are in the 'Type' column?
3. What is the total AP for each unique value in the 'Vznemer' column?
4. What is the total AP for entries where 'Budget' is greater than 10?
5. What are some of the descriptive statistics (mean, median) for the 'Budget' column?
6. Is there a correlation between 'AP' and 'SP'?
7. Can you show me a scatter plot of 'Budget' versus 'AP'?
8. What is the average AP for each 'Naaminsp'?
9. What is the average 'Vzsom' per unique 'Budget', only for rows where 'AP' is greater than 100?