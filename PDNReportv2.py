#!/usr/env/bin python3

#Run:
#python3 PDNReportv2.py 2021-22.xlsx 29 143 75,94,113,128



# from curses.textpad import rectangle
from itertools import count
import pandas as pd
import numpy as np
import sys

FILENAME="2021-22.xlsx"
FIELD_COLUMNS=["Select your College and Department from the lists below.","Level 2"]
#defining a function for pairing
def qurt(pair:tuple):
    a,b=pair
    if a>=3 and b<=3 and not a==b==3:
        return True
    return False

#run starts here
    # run starts here
if __name__ == "__main__":
    df = pd.read_excel(sys.argv[1], sheet_name="Raw Data", header=0)
    question_col_start = int(sys.argv[2])
    question_col_end = int(sys.argv[3])
    question_col_skip = np.array(sys.argv[4].split(","), dtype=int)
    question_col = np.arange(question_col_start, question_col_end)
    question_col = np.setdiff1d(question_col, question_col_skip)

    # df_needed = pd.concat([df[FIELD_COLUMNS],df.iloc[:,question_col]], axis=1)
    df_fields = df[FIELD_COLUMNS]

    """for col in df_fields.columns:
        df_fields[col] = df_fields[col].astype(str).apply(str.strip).replace("&","and",regex=True).str.lower()
    """
    df_questions_long_header = df.iloc[1:,question_col]

    df_questions = pd.DataFrame(columns=np.arange(len(df_questions_long_header.columns)/2, dtype=int))
    for num in range(int(len(df_questions.columns))):
        #to select importance and competency and put them in a same cell
        df_questions.iloc[:,num] = df_questions_long_header.iloc[:,2*num:2*num+2].dropna().agg(tuple, axis=1)
    # Combine fields and questions data
    df_all=pd.concat([df_fields,df_questions], axis=1, join="inner")
    total_answers=len(df_all)

    depcount=df_all.groupby(FIELD_COLUMNS[1]).count().iloc[:,:1]
    collegecount=df_all.groupby(FIELD_COLUMNS[0]).count().iloc[:,:1]

    #list of dataframes. One per question pair
    questions = []
    #shortcut for forloop
    #for col in range(len(df_questions.columns))
    for col in df_all.columns[len(df_fields.columns):]:
        df_q = df_all.groupby(FIELD_COLUMNS+[col],as_index=False).count().iloc[:,:len(FIELD_COLUMNS)+2]
        accept = df_q.iloc[:,-2].apply(qurt)
        #created a dataframe for each question then it will save them into one list of dataframes
        questions += [df_q[accept]]


    #sum of acceptable answers to first question
    #np.sum(questions[0].iloc[:,-1])

    """x += 1
    x = x + 1"""
    #list of categories
    question_names=[]
    for i in range(len(df_questions_long_header.columns)//2):
        question_names+=[list(df_questions_long_header.columns)[2*i].replace(" Importance[Unimportant,Very Important]","")]
    percentages = []

    for i in range(len(questions)):
        percentages += [f"{np.sum(questions[i].iloc[:,-1])/total_answers*100:.2f}%"]
    #    percentages += [str(np.sum(questions[i].iloc[:,-1])/total*100) + "%"]
    percentagesDF=pd.DataFrame(percentages, index=question_names,columns=["percentage"])
    percentagesDF.to_csv("overall_percentage_fixTotal.csv")

    #create a blank dataframe to filled by percentages for each college-questions

    collegedf=pd.DataFrame(None,index=np.unique(list(df_all["Select your College and Department from the lists below."])),
        columns=question_names)
    cpercentages=[]
    for i in range(len(questions)):
        #collegecount is number of summed variables based on each college
        acceptcollegecount=questions[i].groupby(FIELD_COLUMNS[0]).sum("1")
        acceptcollegecount=acceptcollegecount.rename(columns={1:"A", 0:"A"})
        totalcollegecount = df_all.groupby(FIELD_COLUMNS[0]).count()
        collegejoincount = acceptcollegecount.join(totalcollegecount, how='right')
        collegejoincount["A"] = collegejoincount["A"].fillna(0)
        cpercentages += [collegejoincount.iloc[:,0]/collegejoincount.loc[:,i]]
        collegedf.update(cpercentages[i].rename(question_names[i]))
    #    percentages += [str(np.sum(questions[i].iloc[:,-1])/total*100) + "%"]
    collegedf.to_csv("percentagesforCollege.csv")
   #create a blank dataframe to filled percentage for eache department-questions
    departmentdf=pd.DataFrame(None,index=np.unique(list(df_all["Level 2"])),columns=question_names)
   #departmentpercentages=[]
    for i in range(len(questions)):
       acceptdepartmentcount=questions[i].groupby(FIELD_COLUMNS[1]).sum("1")
       acceptdepartmentcount=acceptdepartmentcount.rename(columns={1:"A", 0:"A"})
       totaldepartmentcount=df_all.groupby(FIELD_COLUMNS[1]).count()
       departmentjoincount = acceptdepartmentcount.join(totaldepartmentcount,how='right')
       departmentjoincount["A"] = departmentjoincount["A"].fillna(0)
       departmentpercentages = departmentjoincount.iloc[:,0]/departmentjoincount.loc[:,i]
       departmentdf.update(departmentpercentages.rename(question_names[i]))

    departmentdf.to_csv("percentagesforDepartments.csv")

    #list of needed adjustment
    #number of people from departments
    #number of people from each college
    #categorise the result
    #report for overall college for first 3 cirteria
    #create the visualization
    aa=0


