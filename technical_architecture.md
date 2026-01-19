# Technical Design Document: Rick & Morty AI Explorer

## 1. Executive Summary
This project is a full-stack AI-augmented application designed to explore, reason over, and extend the Rick & Morty universe.

It features a hybrid data-fetching strategy, a generative AI layer with self-evaluation capabilities, and entity extaction based seamatic search using Named Entity Recognition (NER).

## 2. System Architecture

The application follows a decoupled client-server architecture:

- **Frontend (Client):** A React application (Vite) that handles UI, direct GraphQL data fetching for browsing, and audio synthesis.
- **Backend (Server):** A FastAPI service acting as the reasoning engine. It handles complex logic (search parsing), sensitive operations (OpenAI calls), and data persistence.
- **Data Persistence:** A lightweight SQLite database for storing user-generated notes.
- **External Services:**
    - **Rick & Morty API:** Consumed via GraphQL (Frontend) and REST (Backend).
    - **OpenAI API:** Used for dialogue generation and heuristic evaluation.
    - **Hugging Face:** Hosting the BERT-NER model for query parsing.

---

## 3. Key Technical Decisions & Trade-offs

### 3.1 Data Retrieval: The Hybrid Strategy
Chose a **hybrid approach** to data retrieval, leveraging the strengths of both GraphQL and REST where appropriate.

| Component | Protocol | Reasoning |
| :--- | :--- | :--- |
| **Frontend (Location Browser)** | **GraphQL** | **Efficiency.** The UI requires a list of locations *nested* with their residents' images and statuses. Using REST would require 1 call for locations + *N* calls for residents (the *N+1* problem). GraphQL fetches the exact view-model in a single request. |
| **Backend (Search Engine)** | **REST** | **Simplicity & Control.** The search logic requires iterating over paginated endpoints and filtering raw data. REST endpoints were easier to integrate into the Python filtering logic without the overhead of constructing complex dynamic GraphQL strings. |

### 3.2 Backend Framework: FastAPI vs. Flask/Django
**Choice:** FastAPI.
* **Async Native:** The application makes heavy use of I/O-bound operations (calling OpenAI, calling Rick & Morty API). FastAPI’s native `async/await` support handles concurrent requests significantly better than Flask.
* **Pydantic Validation:** Ensures that data flowing in and out of the AI endpoints (e.g., search queries, notes) is strictly typed and validated automatically.

### 3.3 Persistence: SQLite
**Choice:** SQLite (embedded).
* **Trade-off:** While not suitable for high-concurrency write-heavy production environments, SQLite was the optimal choice for this assignment. It requires zero configuration (no Docker service needed for the DB), supports complex SQL queries (joins, indexing), and is easily portable.
* **Optimization:** Created a composite index on `(character_id, created_at)` to ensure O(log N) retrieval time for character notes.

---

## 4. Feature Deep Dives

### 4.1 Generative AI & "The Rubric" (Evaluation)
Instead of simply generating text, the system implements a **Generate-Evaluate-Return** loop.

1.  **Generation:** The system prompts `gpt-4o-mini` with character metadata (Status, Species, Origin) to generate a script between Rick & selected character.
2.  **Evaluation:** A second, distinct prompt acts as a "Critic." It analyzes the generated text against the known character traits.
3.  **Result:** The API returns both the dialogue *and* a structured JSON rubric:
    ```json
    {
      "score": 4,
      "reason": "The dialogue captures Rick's cynicism but misses his stutter."
    }
    ```
This ensures the frontend can display a "Confidence Score" alongside the AI output, adding a layer of trust.

### 4.2 Semantic Search via NER
For the search requirement, I avoided a naive keyword match in favor of **Intent Parsing**.

* **Problem:** A query like *"Dead aliens from Anatomy Park"* contains three distinct filters: Status (`Dead`), Species (`Alien`), and Location (`Anatomy Park`).
* **Solution:**
    1.  **Regex/Rule-based:** Extracts standardized terms like `S01E04` (Episode) or `Alive/Dead` (Status).
    2.  **BERT-NER (Hugging Face):** The query is passed through `dslim/bert-base-NER` to identify Location entities that might not match exact keywords.
    3.  **Aggregation:** These filters are combined to construct a precise query against the Rick & Morty API.

---

## 5. Deployment & Infrastructure
The application is fully containerized using Docker to ensure consistency across environments.


## 6. Future Improvements
If given more time, I would address the following:
1.  **Vector Database:** Replace the NER-based search with a true vector database (e.g., ChromaDB) to allow for "fuzzy" semantic matching (e.g., "scary place" -> "Anatomy Park").
2.  **Caching:** Implement Redis caching for the Rick & Morty API calls to reduce latency and avoid rate limits.
3.  **Testing:** Add `pytest` unit tests for the parsing logic and `React Testing Library` tests for the UI components.