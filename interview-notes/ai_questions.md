| Component                    | Responsibility                                                                         |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| **Browser**                  | Sends the HTTP request and displays the response.                                      |
| **HTTP**                     | Communication protocol between client and server.                                      |
| **Uvicorn**                  | Runs the FastAPI application, listens for requests, and sends responses.               |
| **FastAPI**                  | Matches routes, validates requests, executes business logic, and serializes responses. |
| **Python Function (`home`)** | Contains the application's business logic.                                             |
| **JSON**                     | Standard data format used for communication between backend and frontend.              |


2.Why use the OpenAI SDK?

"The SDK abstracts HTTP communication, authentication, request serialization, and response parsing, allowing developers to interact with OpenAI models using simple Python methods."

3.Browser
      │
      ▼
Your Backend
      │
 HTTPS Request
      ▼
OpenAI Backend
      │
      ▼
GPT-4.1-mini
      │
      ▼
Response
      │
      ▼
Your Backend
      │
      ▼
Browser

3.OpenAI gives us an SDK. which SDK handles:

Authentication,HTTPS,JSON formatting,Error handling,Response parsing

4.Why does python3 -m uvicorn work even when uvicorn doesn't?

uvicorn is a Python package. Running python3 -m uvicorn executes the package using the active Python interpreter, ensuring the correct virtual environment is used. Running uvicorn directly depends on the shell finding the executable in the system PATH.

5.Q: Why do we store API keys in .env instead of writing them in code?

"API keys are sensitive credentials. Storing them in environment variables prevents accidental exposure in source code repositories and allows different configurations for development, testing, and production."