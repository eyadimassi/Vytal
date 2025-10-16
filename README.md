# Vytal - AI Medical Chatbot

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)

> A full-stack, containerized medical chatbot that provides trusted health information using a multi-tool AI agent.

Vytal is an intelligent and empathetic AI health educator designed to answer your medical questions. It leverages a sophisticated AI agent that prioritizes information from trusted medical sources and uses a fallback web search for more obscure or recent topics. The entire application is containerized with Docker for a seamless setup and deployment experience.


## ✨ Core Features

-   **Interactive Chat Interface:** A clean, modern, and responsive UI built with React for a smooth user experience.
-   **Trusted Medical Source:** Prioritizes searching the **MedlinePlus** medical encyclopedia to provide reliable, evidence-based health information.
-   **Web Search Fallback:** If a query cannot be answered by MedlinePlus, the agent intelligently performs a web search using **Tavily** to find answers on more recent or specialized topics.
-   **Advanced AI Agent:** Built with LangChain, the ReAct agent can reason about which tool to use (MedlinePlus or Tavily) to best answer a user's query.
-   **Robust Full-Stack Architecture:** A resilient three-tier system composed of a Frontend, an API Gateway, and a dedicated AI Service.
-   **Containerized & Portable:** Fully containerized with Docker and Docker Compose, allowing for a simple, one-command setup on any machine.

## 🛠️ Tech Stack & Architecture

Vytal is built with a modern, microservice-style architecture to ensure scalability and separation of concerns.

-   **Frontend:** `React.js`
-   **Backend (API Gateway):** `Node.js` with `Express`
-   **AI Service:** `Python` with `Flask`, `LangChain`, and `Google Gemini`

### System Architecture

The services are networked together using Docker Compose, allowing for seamless internal communication.
[User on Browser] ↔ [Frontend (Nginx)] ↔ [Backend API (Node.js)] ↔ [AI Service (Python/Flask)]
code
Code
## 🚀 Getting Started

Follow these instructions to get the project running on your local machine for development and testing purposes.

### Prerequisites

Ensure you have the following software installed on your system:

-   [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/) 
-   [Git](https://git-scm.com/) for cloning the repository

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url/Vytal.git
    cd Vytal
    ```

2.  **Configure Environment Variables:**
    The AI service requires API keys for Google Gemini and Tavily Search.
    -   Navigate to the `backend-python` directory.
    -   Create a new file named `.env`.
    -   Add your API keys to this file as shown below:

    ```env
    # Located in /backend-python/.env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY_HERE"
    ```

3.  **Build and Run with Docker Compose:**
    From the root directory of the project (`Vytal`), run the following command. This will build the Docker images for all services and start the application.

    ```bash
    docker-compose up --build
    ```

4.  **Access Vytal:**
    Once the containers are up and running, open your favorite web browser and navigate to:
    [**http://localhost:3000**](http://localhost:3000)

You can now start a conversation with Vytal!


## 📂 Project Structure

The project is organized as a monorepo with a clear separation of concerns for each service. Each primary directory in the root represents a self-contained, containerized service.

```Vytal/
├── .gitignore          
├── docker-compose.yml  
├── README.md           
│
├── frontend/             
│   ├── Dockerfile        
│   └── src/              
│
├── backend-node/         
│   ├── Dockerfile        
│   └── server.js         
│
└── backend-python/       
    ├── .env              
    ├── Dockerfile        
    ├── requirements.txt  
    └── src/              
        ├── chatbot/      
        └── medline_client/ 

## 🔮 Future Improvements

Here are some planned features to enhance Vytal:

-   **Conversation History:** Implement a database (e.g., PostgreSQL or Redis) to save and retrieve chat histories, allowing users to continue previous conversations.
-   **User Authentication:** Add a secure login system to manage user-specific data and conversation history.
-   **Streaming Responses:** Modify the backend to stream the AI's response token-by-token for a more interactive and dynamic "typing" effect in the UI.
-   **Cloud Deployment:** Create configuration files (e.g., Terraform, Helm charts) for deploying the application to a major cloud provider like AWS, Google Cloud, or Azure.
-   **Enhanced Error Handling:** Improve system-wide error handling and logging for easier debugging and maintenance.