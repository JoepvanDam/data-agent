# Findings
* During the test, I found that it is probably smart to use less tokens for the formatting question. The whole system input and initial question are not necessary to format the answer. This does seem to slow down the process, I assume because none of the input can be cached. It saves about 2k input tokens for formatting, BUT caching is removed. 
About 1k can be cached normally, which is half price.
Say cost is 1$ for 1k normal tokens, then 1k cached tokens is 0.5$
Normally it goes: Question AND Format is ~2k input of which ~1k is cached = 1.50$ * 2 = 3.00$
Now it goes: Question is ~2k input = 2.00$, Format is 200 input = 0.20$ = 2.20$
So we do actually save 0.80$...

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