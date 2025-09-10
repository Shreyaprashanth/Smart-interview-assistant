**AI-Powered Interview Practice Chatbot**

**Project Overview**

This project is an AI-powered chatbot designed to help students and job seekers prepare for interviews. It provides real-time
practice by answering commonly asked technical and HR questions. The system simulates a mock interview environment, making it 
easier for users to build confidence and improve their communication skills. The chatbot acts as a self-practice platform for 
those who may not have access to mentors or mock interviewers.

 **1. Objective of the Project**

The main objective is to create a platform that enables users to practice interview questions in an interactive manner.

* Solves the problem of lack of guidance during interview preparation.
* Helps users overcome stage fear and answer questions with more confidence.
* Provides 24/7 access to an interview practice assistant.

**2. Data Source**

* The data is stored in a CSV file containing structured interview questions and answers(OS,CN,DBMS).
* Data size: around 50 rows and 2 columns in each CSV file.
* Features included:
     Question – the interview question text.
     Answer – suggested response or explanation.
     Category – type of question such as CS fundamentals(OS,CN,DBMS).
     Data was collected from publicly available resources and curated manually into a structured dataset.

**3. Methodologies Used**

* Data Preprocessing – cleaned and organized the dataset to remove duplicates and inconsistencies.
* Embedding Generation – converted text questions into vector embeddings for efficient similarity search.
* Vector Database – used a database SQLite to store embeddings and allow fast retrieval.
* Flask Framework – developed a web-based application to provide user interaction with the chatbot.
* User Interface– implemented a responsive and styled UI to make the chatbot interactive and visually engaging.

**4. AI / ML Model Used**

* OpenAI Embeddings Model for converting questions into numerical representations.
* Cosine Similarity for retrieving the most relevant answers to user queries.
* Flask Backend to handle communication between the model, database, and frontend.
* The system can be extended to include fine-tuned GPT models for more personalized and dynamic answers.

 **5. Predictions and Findings**

* The chatbot predicts and provides the most relevant answer to user queries from the dataset.
* It has been found to improve user confidence during interview preparation.
* The project reduces dependency on external coaching resources.
* Future scope includes adding features such as voice-based interaction, adaptive question difficulty, and mock interview scoring.

 
