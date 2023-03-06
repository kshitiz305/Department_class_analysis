
# Needs Assesment Survey


This is a Python script that processes data from an Excel file containing responses to a needs assessment survey from QuestionPro. It calculates the percentages of positive responses for each question, broken down by college and department. It also generates an overall_percentage.csv and percentagesforDepartments.csv.

#### Prerequisites:

- Python 3

- Pandas

- NumPy



#### Usage:

You can run the script by executing the following command in the terminal:

python3 /path/to/brandonORewriteV2.py /path/to/inputfile.xlsx 29 143 75,94,113,128

/path/to/brandonORewriteV2.py is the path to the script file

/path/to/inputfile.xlsx is the path to the input Excel file

29 and 143 are the column range for the questions of interest

75,94,113,128 are the column numbers to skip (if any)

#### Output

overall_percentage.csv: A file containing the percentages of positive responses for each question across all colleges and departments



percentagesforColleges.csv: A file containing the percentages of positive responses for each question broken down by college

