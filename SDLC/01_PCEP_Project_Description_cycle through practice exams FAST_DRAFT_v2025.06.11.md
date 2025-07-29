#Goal: Create an offline practice tool that helps me cycle through practice exams quickly.

1) Define - Product Requirements

      #Name: QuickTest
    - provide "burn-down test-taking sessions" that allow users to focus on specific topics or areas of weakness.
    - store all exam data in a local SQLite database for fast access and offline use.
    - allow users to set goals and track their progress towards those goals.
    - allow users to view their performance history and compare it with previous sessions.
    - allow users to create custom exams by selecting specific questions from the available pool, grouped by specific topic and exam modules.

 2) Design - Design Document: List of components

      #Web interface using Flask to display exam questions and answers, let users cycle quickly through an exam and quickly burn-down what they don't know on that exam.

     
      - allow users to upload new exam data in HTML format.
      - allow users to download their exam data in HTML format
      - allow users to view the raw HTML data for each exam in a browser window.
     - using AI to discover, verify, and clearly identify the correct answers.
  
    - provide a leaderboard to compare scores with other users. (MVP 2.0)
    - allow users to export their exam results in a CSV or PDF format.

3) Develop - Layout

  #The web interface should provide the following functionalities:
  - display the questions and answers for the selected exam.
  - allow users to create custom exams by selecting specific questions from the available pool, grouped by specific topic and exam modules.
  - Analyze questions and answers correctly.  Some questions have multiple correct answers, some have only one.  Some questions have no correct answer, and some have multiple correct answers.  The program must be able to identify these cases and handle them correctly.
  - cycle through practice exams quickly, allowing users to skip and save questions they find too difficult or time-consuming.  Let user return to these questions later in the same session.
  - allow users to view their scores and statistics after completing an exam.
  - allow users to navigate through the questions and answers.
  - Provide a report on the user's performance, including the number of questions answered correctly, the time taken to complete the exam, and any areas for improvement.
  - allow users to filter questions by topic or difficulty level.
  - allow users to search for specific questions or topics.
  - allow users to provide feedback on questions and answers.
  - provide a detailed report of user performance, including strengths and      weaknesses.
-


4) Debug - 

5) Document - Code Implementation

     - Extract these JSON objects from each exam data file, write them out to a JSON file named "{filename}.json"
    - The exam Question and Answer is embeded in the HTML file as a JSON object in container: <script>"let data = {<<exam data is here>>}"</script>.

    - Source data is stored in a directory named "Exam_HTML_Raw_Data" and the JSON files will be saved in a directory named "Exam_Raw_Data_JSON".  Provide a Python script to extract the JSON data from all HTML files in the "Exam_HTML_Raw_Data" directory and save them as JSON files in the "Exam_Raw_Data_JSON" directory.

  - Make the program robust and fault-tolerant for handling conversion errors, and  provide informative error messages in any try-except blocks. 

  - Store all exam data in a local SQLite database for fast access and offline use.

  - Add full logging for each function and save the runlog files with a datetime stamp in the filename suffix. 

 - Display all Python code in a syntax-highlighted format, properly indented and    formatted. 
  - Provide an embedded Python interpreter to allow users to select Python code embedded in any question or answer, right-click and send it to the interpreter to run it in real-time and see the result.
  - Allow users to view their exam history, including completed exams and scores.
  allow users to track their progress over time and see how they are improving.
   - allow users to bookmark questions for later review.
    - exam data storage and display (question data is in tagged HTML format for webpage display, and must be preserved - correctly display),


6) Deliver - Github

