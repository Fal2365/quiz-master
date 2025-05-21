import os
import sqlite3

conn = sqlite3.connect("quiz_master.db")
cursor = conn.cursor()

query = """
INSERT INTO question (quiz_id, question_statement, option1, option2, option3, option4, correct_option) VALUES
(1, 'Which of the following is a well-defined set?', 'The set of good football players', 'The set of all prime numbers less than 10', 'The set of beautiful flowers', 'The set of fast cars', '2'),
(1, 'If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∩ B?', '{1, 2, 3, 4, 5}', '{3}', '{1, 2}', '{}', '2'),
(1, 'The universal set is denoted by which symbol?', 'U', 'Ø', '{}', '∩', '1'),
(1, 'If a set contains n elements, how many subsets does it have?', 'n²', '2ⁿ', 'n!', 'n + 1', '2'),
(1, 'What is the power set of {a, b}?', '{{}, {a}, {b}, {a, b}}', '{{a, b}}', '{{}, {a, b}}', '{{a}, {b}}', '1'),
(1, 'Which of the following is an empty set?', 'The set of all even prime numbers', 'The set of all natural numbers less than 0', 'The set of vowels in the English alphabet', 'The set of positive integers', '2'),
(1, 'If A = {1, 2, 3} and B = {3, 4, 5}, what is A ∪ B?', '{3}', '{1, 2, 3, 4, 5}', '{1, 2}', '{4, 5}', '2'),
(1, 'What is the complement of a universal set?', 'The empty set', 'The universal set itself', 'The set of all prime numbers', 'The set of all real numbers', '1'),
(1, 'If A = {x | x is a vowel in the English alphabet}, what is A?', '{a, b, c, d, e}', '{a, e, i, o, u}', '{a, i, u}', '{b, c, d, e}', '2'),
(1, 'Which of the following is a finite set?', 'The set of all even numbers', 'The set of all prime numbers', 'The set of all whole numbers less than 100', 'The set of all real numbers', '3');
"""

cursor.execute('''INSERT INTO question (quiz_id, question_statement, option1, option2, option3, option4, correct_option) VALUES
(2, 'What is the correct file extension for Python files?', '.python', '.py', '.pyt', '.pt', '2'),
(2, 'Which keyword is used to define a function in Python?', 'define', 'func', 'def', 'function', '3'),
(2, 'What will print(type(5)) output?', '<class ''int''>', '<class ''str''>', '<class ''float''>', '<class ''bool''>', '1'),
(2, 'Which of the following is used for comments in Python?', '/* comment */', '# comment', '<!-- comment -->', '-- comment', '2'),
(2, 'What is the correct way to declare a variable in Python?', 'var x = 5;', 'x = 5', 'int x = 5;', 'declare x = 5', '2'),
(2, 'How do you take user input in Python?', 'input()', 'scanf()', 'gets()', 'readline()', '1'),
(2, 'What will print(2 ** 3) output?', '6', '8', '9', '16', '2'),
(2, 'Which of the following is an immutable data type in Python?', 'List', 'Dictionary', 'Tuple', 'Set', '3'),
(2, 'What will print("Hello" + "World") output?', 'Hello World', 'HelloWorld', 'Hello+World', 'Error', '2'),
(2, 'How do you start a loop that runs 5 times in Python?', 'for i in range(5):', 'for (i = 0; i < 5; i++)', 'repeat(5)', 'while i < 5:', '1');
''')
    

# Commit and close the connection
conn.commit()
conn.close()

print("Subjects and chapters inserted successfully!")
