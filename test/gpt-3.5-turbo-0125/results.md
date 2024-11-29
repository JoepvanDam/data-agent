# Model: gpt-3.5-turbo-0125
## Question 1
### Attempt = 1
#### What is the average value of the AP column?
Response time: 0.7849996089935303 seconds \
In tokens used: 2038 \
Out tokens used: 50
```json
{
    "Next": "START",
    "RESULT1": {
        "function": "column_average",
        "parameters": {
            "data": "app/dummy_data.csv",
            "column": "AP"
        }
    }
}
```

#### Question formatting
Response time: 0.5175628662109375 seconds \
In tokens used: 112 \
Out tokens used: 31
```json
{
    "Next": "The average value of the AP column is 1738.06",
    "Formatted": "1738.06"
}
```

#### Error: Unknown 'Next' element: The average value of the AP column is 1738.06. Valid options include: ERROR, FORMAT or START
Response time: 0.35199975967407227 seconds \
In tokens used: 203 \
Out tokens used: 12
```json
{
    "FORMAT": "1738.06"
}
```

#### Error: 'Next'
Response time: 0.5139963626861572 seconds \
In tokens used: 249 \
Out tokens used: 24
```json
{
    "ERROR": "An error occurred when calculating the average value of the AP column. Please try again."
}
```
Stopping here. The model is not following the correct format for the response. This counts as a fail.

### Attempt = 2
#### What is the average value of the AP column?
Response time: 0.7063190937042236 seconds \
In tokens used: 2038 \
Out tokens used: 34
```json
{
    "Next": "FORMAT",
    "Formatted": {
        "Average value of the AP column": 5633.536363636364
    }
}
```
Model just made up a number. Fail. I will give it one more attempt, just to see what happens.

### Attempt = 3
#### What is the average value of the AP column?
Response time: 0.7819976806640625 seconds \
In tokens used: 2038 \
Out tokens used: 34
```json
{
    "Next": "FORMAT",
    "Formatted": {
        "Average value of the AP column": 42.29090909090909
    }
}
```
Model just made up a number. Fail. Not looking good for gpt-3.5-turbo-0125 if it already failed the first question...
---

## Question 2
### Attempt = 1
#### How many unique values are in the 'Type' column?
Response time: 0.6579976081848145 seconds \
In tokens used: 2042 \
Out tokens used: 27
```json
{
    "Next": "FORMAT",
    "Formatted": "There are 3 unique values in the 'Type' column."
}
```

---

## Question 3
### Attempt = 1
#### What is the total AP for each unique value in the 'Vznemer' column?
Response time: 1.0300004482269287 seconds \
In tokens used: 2054 \
Out tokens used: 73
```json
{
    "Next": "grouped_summary",
    "RESULT1": {
        "function": "grouped_summary",
        "parameters": {
            "data": "app/dummy_data.csv",
            "group_by_column": "Vznemer",
            "agg_column": "AP",
            "agg_func": "sum"
        }
    }
}
```

#### Error: Unknown 'Next' element: grouped_summary. Valid options include: ERROR, FORMAT or START
Response time: 0.5282537937164307 seconds \
In tokens used: 2176 \
Out tokens used: 19
```json
{
    'Next': 'ERROR',
    'Reason': 'missing_function_explanation'
}
```
Stopping here as the model is not even getting close.

### Attempt = 2
#### What is the total AP for each unique value in the 'Vznemer' column?
Response time: 1.1055374145507812 seconds \
In tokens used: 2054 \
Out tokens used: 73
```json
{
    "Next": "grouped_summary",
    "RESULT1": {
        "function": "grouped_summary",
        "parameters": {
            "data": "app/dummy_data.csv",
            "group_by_column": "Vznemer",
            "agg_column": "AP",
            "agg_func": "sum"
        }
    }
}
```

#### Error: Unknown 'Next' element: grouped_summary. Valid options include: ERROR, FORMAT or START
Response time: 0.4590001106262207 seconds \
In tokens used: 2176 \
Out tokens used: 19
```json
{
    'Next': 'ERROR',
    'Reason': 'missing_function_explanation'
}
```
Stopping here as the model is not even getting close.

---

## Question 4
### Attempt = 1
#### What is the total AP for entries where 'Budget' is greater than 10?
Response time: 0.5780856609344482 seconds \
In tokens used: 2052 \
Out tokens used: 19
```json
{
    "Next": "ERROR",
    "Reason": "missing_function_explanation"
}
```
Every other model has been able to answer this question. I will give it one more attempt.

### Attempt = 2
#### What is the total AP for entries where 'Budget' is greater than 10?
Response time: 0.8989989757537842 seconds \
In tokens used: 2052 \
Out tokens used: 19
```json
{
    "Next": "ERROR",
    "Reason": "missing_function_explanation"
}
```
This model is dumb.

---

## Question 5
### Attempt = 1
#### What are some of the descriptive statistics (mean, median) for the 'Budget' column?
Response time: 0.6519994735717773 seconds \
In tokens used: 2056 \
Out tokens used: 36
```json
{
    "Next": "FORMAT",
    "Formatted": "The mean of the 'Budget' column is [mean_value] and the median is [median_value]."
}
```
The model did not provide the actual mean and median values. I will give it one more attempt.

### Attempt = 2
#### What are some of the descriptive statistics (mean, median) for the 'Budget' column?
Response time: 0.9579999446868896 seconds \
In tokens used: 2056 \
Out tokens used: 41
```json
{
    "Next": "FORMAT",
    "Formatted": "The descriptive statistics for the 'Budget' column include: mean: 4566.45, median: 3452.11"
}
```
Again, the model just made up numbers. Fail.

---

## Question 6
### Attempt = 1
#### Is there a correlation between 'AP' and 'SP'?
Note: this is the most difficult question so far (for all other models at least), I am not hopeful for this one...
Response time: 0.6560013294219971 seconds \
In tokens used: 2044 \
Out tokens used: 29
```json
{
    "Next": "FORMAT",
    "Formatted": "Yes, there is a correlation between 'AP' and 'SP'."
}
```
I mean, it's not TECHNICALLY wrong...

### Attempt = 2
#### Is there a correlation between 'AP' and 'SP'?
Response time: 0.6799983978271484 seconds \
In tokens used: 2044 \
Out tokens used: 29
```json
{
    "Next": "FORMAT",
    "Formatted": "Yes, there is a correlation between 'AP' and 'SP'."
}
```
How did we ever think this model was good...? I will finish the test, but I am not hopeful for any correct answers.

---

## Question 7
### Attempt = 1
#### Can you show me a scatter plot of 'Budget' versus 'AP'?
Response time: 0.9339983463287354 seconds \
In tokens used: 2050 \
Out tokens used: 64
```json
{
    "Next": "plot_scatter_plot",
    "RESULT1": {
        "function": "plot_scatter_plot",
        "parameters": {
            "data": "app/dummy_data.csv",
            "column_x": "Budget",
            "column_y": "AP"
        }
    }
}
```

#### Error: Unknown 'Next' element: plot_scatter_plot. Valid options include: ERROR, FORMAT or START
Response time: 0.4790017604827881 seconds \
In tokens used: 2165 \
Out tokens used: 19
```json
{
    'Next': 'ERROR',
    'Reason': 'missing_function_explanation'
}
```
This is going nowhere. No second attempt needed.

---

## Question 8
### Attempt = 1
#### What is the average AP for each 'Naaminsp'?
Response time: 0.8832440376281738 seconds \
In tokens used: 2044 \
Out tokens used: 74
```json
{
    "Next": "grouped_summary",
    "RESULT1": {
        "function": "grouped_summary",
        "parameters": {
            "data": "app/dummy_data.csv",
            "group_by_column": "Naaminsp",
            "agg_column": "AP",
            "agg_func": "column_average"
        }
    }
}
```

#### Error: Unknown 'Next' element: grouped_summary. Valid options include: ERROR, FORMAT or START
Response time: 0.5108988285064697 seconds \
In tokens used: 2167 \
Out tokens used: 19
```json
{
    'Next': 'ERROR',
    'Reason': 'missing_function_explanation'
}
```
Same as before. No second attempt needed.

---

## Question 9
### Attempt = 1
#### What is the average 'Vzsom' per unique 'Budget', only for rows where 'AP' is greater than 100?
Response time: 2.206012487411499 seconds \
In tokens used: 2072 \
Out tokens used: 19
```json
{
    "Next": "ERROR",
    "Reason": "missing_function_explanation"
}
```
Should I even bother with a second attempt...? I will, just to be thorough.

### Attempt = 2
#### What is the average 'Vzsom' per unique 'Budget', only for rows where 'AP' is greater than 100?
Response time: 0.613731861114502 seconds \
In tokens used: 2072 \
Out tokens used: 19
```json
{
    "Next": "ERROR",
    "Reason": "missing_function_explanation"
}
```
Conclusion: gpt-3.5-turbo-0125 is bad.