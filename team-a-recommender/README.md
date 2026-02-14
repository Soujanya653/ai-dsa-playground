AI-DSA Problem Recommender

AI-DSA Problem Recommender is a lightweight system that suggests similar LeetCode-style coding problems based on a user’s input problem title or description. The system also highlights common algorithmic patterns to help users prepare more effectively for coding interviews.

The project demonstrates how classic data structures and algorithms can be combined with simple, CPU-friendly AI techniques to build a real-world recommendation system.

Project Overview

The goal of this project is to show how recommendation systems can be built using basic machine learning concepts and efficient algorithms.

When a user enters a coding problem description, the system:

Recommends similar coding problems

Identifies shared algorithmic patterns

Displays the results in a clean and user-friendly interface

No heavy model training or GPU usage is required.

Features

Text-based problem recommendation using TF-IDF

Similarity computation using cosine similarity

Rule-based pattern detection such as sliding window, hash map, binary search, BFS, DFS, and dynamic programming

RESTful backend built with FastAPI

Interactive frontend built with Streamlit

Curated dataset of LeetCode-style problems

Modular and testable codebase

Tech Stack

Python 3

FastAPI for backend APIs

Streamlit for frontend UI

scikit-learn for TF-IDF vectorization

JSON for dataset storage

pytest for unit testing

How It Works

Problem titles and descriptions are preprocessed and converted into numerical vectors using TF-IDF.
The user’s query is transformed into the same vector space.
Cosine similarity is used to find the most relevant problems.
Algorithmic patterns are inferred using keyword-based rules.
The backend returns recommendations through an API.
The frontend displays the recommendations in a structured and readable format.

Running the Project

Start the backend server using FastAPI.
Make sure the backend is running before starting the frontend.
Start the frontend using Streamlit and access the application through the browser.

Example Usage

Input:
Longest substring without repeating characters

Output:

A list of similar coding problems

Difficulty level for each problem

Common algorithmic patterns shared with the input query

Learning Outcomes

Applying data structures and algorithms in real-world systems

Understanding text similarity and recommendation pipelines

Designing clean REST APIs

Building interactive user interfaces with Streamlit

Using Git effectively in a collaborative development environment

Future Improvements

Difficulty-based filtering of problems

User feedback-based recommendation refinement

Expansion of the problem dataset

Deployment to a cloud platform