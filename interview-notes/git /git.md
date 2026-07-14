What does git init do?
Good answer:
"git init initializes a Git repository by creating a hidden .git directory. This directory stores all version control information such as commits, branches, and repository configuration."

Files
   │(git add .)
   ▼
Staging Area
   │( git commit)
   ▼
Commit(git commit -m "Initial project setup”)
(Git push)

Command	Purpose
git init	Initializes a Git repository by creating the hidden .git folder.
git branch -m main	Renames the current branch from master to main.
git add .	Stages all changes in the current directory.
git commit -m "message"	Creates a snapshot of the staged changes.
git push	Uploads commits to the remote GitHub repository.

1.git init converts a normal folder into a Git repository by creating a hidden .git directory where Git stores all version control information.
2..git folder stores Commit history,Branches,Tags,Repository configuration
3.git add . --It adds them to the staging area.
            git add . stages all new and modified files so they are ready to be committed.

Working Directory

↓

git add .

↓

Staging Area

↓

git commit

↓

Git History

4.Difference between git add and git commit?
-------------------------------

Git Flow

Imagine you're writing a book.

README.md

You edit it.

Where is it now?

Working Directory

Then:

git add .

Moves it here:

Staging Area

Then:

git commit -m "Added README"

Moves it here:

Git Repository (.git)

Still on your laptop.

Finally:

git push

Moves it here:

GitHub

### Real Architecute
Working Directory
       │
       ▼
git add .
       │
       ▼
Staging Area
       │
git commit
       │
       ▼
Local Repository (.git)
       │
git push
       │
       ▼
GitHub Remote Repository

5.What is the difference between git add, git commit, and git push?

Interview Answer
git add stages changes by moving them from the working directory to the staging area.
git commit creates a permanent snapshot of the staged changes in the local Git repository.
git push uploads those local commits to the remote repository, such as GitHub.

6.fastapi
Builds REST APIs.

7.uvicorn
Runs the FastAPI server.
Think of it like Tomcat for Spring Boot.

8.openai
Python SDK for calling LLMs.

9.python-dotenv
Reads API keys from a .env file.

10.Where am I? → pwd
11.What files are here? → ls

12.Why do we use a virtual environment?

"A virtual environment creates an isolated Python environment for a project. It allows each project to maintain its own dependencies and package versions without conflicting with other Python projects on the same machine."

13.Why did you choose FastAPI for your backend?

"I chose FastAPI because it provides high performance, automatic OpenAPI/Swagger documentation, asynchronous request handling, type validation using Pydantic, and it integrates well with AI frameworks like LangChain and OpenAI."

14.: Why do we create main.py?

"main.py serves as the entry point of the FastAPI application. It creates the FastAPI instance, defines API routes, and is the file that Uvicorn loads to start the web server."

15.What is Uvicorn?

Uvicorn is a lightweight ASGI web server used to run FastAPI applications. It listens for incoming HTTP requests, forwards them to the FastAPI application, and returns the generated responses to the client.

Browser
      │
      ▼
Uvicorn (Web Server)
      │
      ▼
FastAPI (Framework)
      │
      ▼
Business Logic (Your Code)
      │
      ▼
OpenAI / ChromaDB / Database

16.Why can't main.py alone serve HTTP requests?
main.py defines the FastAPI application and API routes, but it cannot listen for HTTP requests by itself. A web server like Uvicorn is needed to run the application and handle incoming requests.

17.Why do we need Uvicorn?
Uvicorn is an ASGI web server that runs FastAPI applications, listens for HTTP requests, forwards them to FastAPI, and sends the response back to the client.

18.In the Java world, what is the equivalent of Uvicorn? tomcat

19.What does --reload do?
restart the server whenever python code changes

20.What does main:app mean?
main is file name and app is variable,Then Uvicorn starts that application.

21.when you type http://127.0.0.1:8000/
Browser
    │
    ▼
HTTP GET Request
    │
    ▼
Uvicorn (Web Server)
    │
    ▼
FastAPI
    │
    ▼
@app.get("/")
    │
    ▼
home()
    │
    ▼
Return Python Dictionary
    │
    ▼
FastAPI converts it to JSON
    │
    ▼
Uvicorn sends HTTP Response
    │
    ▼
Browser displays JSON

22.Explain the request lifecycle in FastAPI.

"When a client sends an HTTP request, the Uvicorn ASGI server receives it and forwards it to the FastAPI application. FastAPI performs route matching to identify the correct endpoint. It then invokes the corresponding Python function containing the business logic. The function returns a Python object, such as a dictionary, which FastAPI automatically serializes into JSON. Finally, Uvicorn wraps it in an HTTP response and sends it back to the client."