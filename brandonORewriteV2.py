#!/usr/bin/env python
# coding: utf-8

#!/bin/bash-- user commands
#python3 /path/to/brandonORewriteV2.py /path/to/inputfile.xlsx 29 143 75,94,113,128

#python3 /Users/brandono/PycharmProjects/pythonProject/brandonORewriteV2.py /Users/brandono/Documents/NeedsAssesment/2022-23.xlsx 29 143 75,94,113,128




#!/usr/bin/env python
# coding: utf-8

# First, import the required libraries
import sys
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter("ignore", category=UserWarning)

# Define a function for checking whether a pair of values meet certain criteria
def is_qurt(pair: tuple) -> bool:
    try:
        a, b = map(int, pair)
    except ValueError:
        return False
    if a >= 3 and b <= 3 and not a == b == 3:
        return True
    return False



if __name__ == "__main__":
    # Parse command line arguments
    # The first argument is the input data file path
    # The second and third arguments specify the column range for the questions of interest
    # The fourth argument specifies the column numbers to skip (if any)
    print(sys.argv)
    df = pd.read_excel(sys.argv[1], sheet_name="Raw Data", header=0)
    question_col_start = int(sys.argv[2])
    question_col_end = int(sys.argv[3])
    question_col_skip = np.array(sys.argv[4].split(","), dtype=int)
    question_col = np.arange(question_col_start, question_col_end)
    question_col = np.setdiff1d(question_col, question_col_skip)


    # Extract fields of interest and questions from the data
    # We need the "Select your College and Department from the lists below." and "Level 2" fields
    df_fields = df[["Select your College and Department from the lists below.", "Level 2"]]
    # We also need the questions of interest
    df_questions_long_header = df.iloc[1:, question_col]
    # Extract individual question values and combine them
    df_questions = pd.DataFrame(columns=np.arange(len(df_questions_long_header.columns)/2, dtype=int))
    for num in range(int(len(df_questions.columns))):
        df_questions.iloc[:,num] = df_questions_long_header.iloc[:,2*num:2*num+2].dropna().agg(tuple, axis=1)
    # Combine fields and questions data
    df_all=pd.concat([df_fields,df_questions], axis=1, join="inner")
    total_answers=len(df_all)


    # Count answers for each department and college
    # Group the data by department and count the number of responses
    depcount = df_all.groupby("Level 2").count().iloc[:,:1]
    # Group the data by college and department and count the number of responses
    collegecount=df_all.groupby("Select your College and Department from the lists below.").count().iloc[:,:1]


    # Create a list of dataframes, one for each question pair
    questions = []
    for col in df_all.columns[len(df_fields.columns):]:
        df_q = df_all.groupby(["Select your College and Department from the lists below.", "Level 2", col], as_index=False).count().iloc[:, :len(df_fields.columns)+2]
        # Apply the "is_qurt" function to check if a pair of values meets certain criteria
        accept = df_q.iloc[:, -2].apply(is_qurt)
        questions += [df_q[accept]]


    # Calculate percentages of positive answers for each question
    question_names = []
    for i in range(len(df_questions_long_header.columns)//2):
        # Extract the name of each question from the long header
        question_names += [list(df_questions_long_header.columns)[2*i].replace(" Importance[Unimportant,Very Important]", "")]
    percentages = []
    for i in range(len(questions)):
        # Calculate the percentage of positive answers for each question
        percentages += [f"{np.sum(questions[i].iloc[:, -1])/total_answers*100:.2f}%"]
    percentages_df = pd.DataFrame(percentages, index=question_names, columns=["percentage"])
    percentages_df.to_csv("overall_percentage.csv")


    # Define a list of field column names to be used in the script
    FIELD_COLUMNS = ["Select your College and Department from the lists below.", "Level 2"]

    # Create a blank dataframe to be filled with percentages for each college-questions
    collegedf = pd.DataFrame(None, index=np.unique(list(df_all[FIELD_COLUMNS[0]])), columns=question_names)


    # create a blank dataframe to filled percentage for each department-questions
    departmentdf = pd.DataFrame(None, index=np.unique(list(df_all["Level 2"])), columns=question_names)

    #Iterate over each question and calculate percentages for each college and department

    for i in range(len(questions)):
        # Group the data by college and count the number of accepted responses for each question
        acceptcollegecount = questions[i].groupby("Select your College and Department from the lists below.").sum("1")
        acceptcollegecount = acceptcollegecount.rename(columns={1: "A", 0: "A"})

        # Calculate the total number of responses for each college and join it to the previous group
        totalcollegecount = df_all.groupby("Select your College and Department from the lists below.").count()
        totalcollegecount = totalcollegecount.add_suffix('_total')
        collegejoincount = acceptcollegecount.join(totalcollegecount, how='right')

        # Fill the NaN values with 0 for the colleges that did not respond to the question
        collegejoincount["A"] = collegejoincount["A"].fillna(0)

        # Calculate the percentage of accepted responses for the question for each college
        collegepercentages = collegejoincount.iloc[:, 0] / collegejoincount.iloc[:, i + 2] * 100
        collegepercentages[collegejoincount.iloc[:, i + 2] == 0] = 0

        # Update the corresponding row of the college dataframe with the calculated percentages
        collegedf.update(collegepercentages.rename(question_names[i]))

        # Group the data by department and perform the same calculation as above for each question
        acceptdepartmentcount = questions[i].groupby("Level 2").sum("1")
        acceptdepartmentcount = acceptdepartmentcount.rename(columns={1: "A", 0: "A"})
        totaldepartmentcount = df_all.groupby("Level 2").count()
        totaldepartmentcount = totaldepartmentcount.add_suffix('_total')
        departmentjoincount = acceptdepartmentcount.join(totaldepartmentcount, how='right')
        departmentjoincount["A"] = departmentjoincount["A"].fillna(0)
        departmentpercentages = departmentjoincount.iloc[:, 0] / departmentjoincount.iloc[:, i + 2] * 100
        departmentpercentages[departmentjoincount.iloc[:, i + 2] == 0] = 0
        departmentdf.update(departmentpercentages.rename(question_names[i]))

    #Write the calculated percentages for each college and department to a csv file
    # define a custom rounding function
    def round_to_nearest_1000(x):
        if pd.isna(x):
            return np.nan
        elif isinstance(x,float) :
            return round(float(x), 3)
        else:
            return str(round(int(x) / 1000) * 1000)


    # apply the custom rounding function to all columns
    departmentdf = departmentdf.apply(lambda x: x.apply(round_to_nearest_1000))
    collegedf = collegedf.apply(lambda x: x.apply(round_to_nearest_1000))

    # departmentdf = departmentdf.round(3)
    # collegedf = collegedf.round(3)

    collegedf.to_csv("percentagesforColleges.csv")
    departmentdf.to_csv("percentagesforDepartments.csv")


    print(collegedf.to_csv)
    print(departmentdf.to_csv)












    

    
    
    
   









