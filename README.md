## Noora Health Backend

Simple FastAPI backend for exploring the **Rick and Morty** universe:
- **Generate dialogue** between Rick Sanchez and any character using OpenAI.
- **Evaluate** how in-character the dialogue feels using an LLM-based rubric.
- **Semantic search** over characters using natural language (episodes, locations, status, species).
- **Store and manage notes** about characters in a local SQLite database.

All endpoints are exposed under the `/api` prefix.

---

## Features

- **Dialogue generation**
  - `POST /api/dialogue/generate`
  - Uses OpenAI (`gpt-4o-mini`) to write a short script (2–3 exchanges) between Rick Sanchez and a specified character.
  - Returns both the **dialogue** and an **evaluation rubric** (score + reason) judging how in-character the conversation feels.

- **Semantic character search**
  - `POST /api/search`
  - Takes a natural language query (e.g. “alive aliens from S01E04 on Earth”).
  - Uses a mix of:
    - **Rule-based parsing** for status/species/episode (e.g. `S01E04`).
    - **Hugging Face NER** (`dslim/bert-base-NER`) to extract locations.
    - **Rick and Morty API** to fetch matching characters.
  - Returns structured results with id, name, status, species, location, and image.

- **Character notes**
  - `POST /api/note/save` – create a note for a character.
  - `GET /api/note?character_id=...` – list notes for a character, ordered by creation time.
  - `POST /api/note/delete` – delete a note by its id.
  - Notes are stored in a local **SQLite** database with automatic schema creation and indexing.

- **Health check**
  - `GET /api/ping` – simple JSON response to check if the backend is running.

---

## Tech stack

- **Backend**: FastAPI (`main.py`, routers under `routers/`)
- **Database**: SQLite (via `config/db.py`, file path from `DATABASE_ENDPOINT`)
- **LLMs**:
  - OpenAI (`gpt-4o-mini`) for dialogue generation and evaluation (`utils.py`, `routers/dialogue.py`)
  - Hugging Face Transformers (`dslim/bert-base-NER`) for NER in query parsing (`llm/parser.py`)
- **HTTP clients**: `requests` for Rick and Morty API calls (`routers/search.py`, `utils.py`)
- **Containerization**: Docker (`Dockerfile`, `docker_run.sh`)

---

## Prerequisites

- **Python**: 3.10+ (repo includes a `venv` using Python 3.11)
- **pip**: bundled with Python
- **OpenAI API key**: for dialogue generation and evaluation
- **Internet access**:
  - To call the **OpenAI API**
  - To call the **Rick and Morty API**
  - To download the **Hugging Face model** the first time you run the app
- **SQLite**: usually preinstalled on macOS (`sqlite3` CLI is optional but helpful)
- **Docker** (optional): for containerized runs

---

## 1. Clone and create a virtual environment

- **Clone the repo**:

```bash
git clone <your-repo-url> noora_health_backend
cd noora_health_backend
```

- **Create and activate a virtualenv** (recommended, even though the repo ships with one):

```bash
python3 -m venv venv
source venv/bin/activate  # macOS / Linux
# On Windows (PowerShell):
# venv\Scripts\Activate.ps1
```

- **Install dependencies**:

```bash
pip install -r requirements.txt
```

---

## 2. Configure environment variables

The app uses `python-dotenv` to load environment variables from a local `.env` file.

- **Create a `.env` file** in the project root:

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_ENDPOINT=./db/notes.db
EOF
```

- **Required variables**:
  - **`OPENAI_API_KEY`**: your OpenAI API key.
  - **`DATABASE_ENDPOINT`**: path (absolute or relative) to the SQLite database file.
    - Example: `./db/notes.db` (the app will ensure the `db/` directory exists and create the file if needed).

These variables are read on startup by `main.py` and `config/db.py`.

---

## 3. SQLite database setup

You **do not** need to run any manual SQL for basic usage.

On startup, `init_db()` in `config/db.py` will:
- **Create the SQLite file** at `DATABASE_ENDPOINT` (if it does not exist).
- **Create the `notes` table** (if it does not exist).
- **Create an index** to speed up queries by `character_id` and `created_at`.

- **Schema (for reference)**  
  The `notes` table has the following columns:

  - `_id` (`TEXT`, UUID string, primary key)
  - `character_id` (`TEXT`, not null)
  - `note` (`TEXT`, not null)
  - `created_at` (`TEXT`, ISO-8601 datetime string, not null)

- **Search index**  
  To make queries efficient, the app also ensures the following index exists:

  ```sql
  CREATE INDEX IF NOT EXISTS idx_notes_character_created
  ON notes (character_id, created_at);
  ```

- **Optional: manual DB inspection using the SQLite CLI**

```bash
sqlite3 ./db/notes.db
```

You can quit the SQLite shell with:

```sql
.quit
```

---

## 4. Running the app locally (uvicorn)

From the project root (with your virtualenv activated and `.env` configured):

```bash
uvicorn main:app --reload
```

By default, the app will be available at:

- **Base URL**: `http://localhost:8000`
- **Interactive docs (Swagger UI)**: `http://localhost:8000/docs`

Keep this terminal running while you develop or test.

---

## 5. Running the app with Docker

There is a convenience script `docker_run.sh` plus a `Dockerfile` that builds a production-style image.

- **Build and run using the script**:

```bash
chmod +x docker_run.sh
./docker_run.sh
```

What the script does:
- **Builds** a Docker image (default tag: `noor-health-backend:latest`).
- **Stops/removes** any existing container with the same name.
- **Runs** the container, mapping:
  - Host port **8000** → Container port **8000**
- If a `.env` file exists, it is passed into the container (`OPENAI_API_KEY`, `DATABASE_ENDPOINT`, etc.).

After it starts, access the app at:
- `http://localhost:8000`
- Docs at `http://localhost:8000/docs`

> Inside the container, the default `DATABASE_ENDPOINT` is set to `/app/db/notes.db` by the `Dockerfile`.  
> You can override this via `.env` if needed.

---

## 6. API endpoints and example requests

### 6.1 Health check

- **GET `/api/ping`**

```bash
curl "http://localhost:8000/api/ping"
```

---

### 6.2 Generate dialogue

- **Endpoint**: `POST /api/dialogue/generate`
- **Body**:

```json
{
  "character": {
    "id": 1,
    "name": "Morty Smith",
    "species": "Human",
    "status": "Alive"
  }
}
```

- **Example cURL**:

```bash
curl -X POST "http://localhost:8000/api/dialogue/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "character": {
      "id": 1,
      "name": "Morty Smith",
      "species": "Human",
      "status": "Alive"
    }
  }'
```

The response includes:
- **`dialogue`**: generated script between Rick and the character.
- **`metrics.rubric`**: JSON with `score` (1–5) and `reason` describing how in-character the conversation is.

---

### 6.3 Semantic search

- **Endpoint**: `POST /api/search`
- **Body**:

```json
{
  "query": "find alive aliens from S01E04 on Earth"
}
```

- **Example cURL**:

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "find alive aliens from S01E04 on Earth"
  }'
```

The response includes:
- **`interpretation`**: parsed intent (`status`, `species`, `episode_code`, `location_name`).
- **`count`**: number of matching characters.
- **`results`**: list of characters with `id`, `name`, `status`, `species`, `location`, `image`.

---

### 6.4 Notes API

All note routes are under the `/api/note` prefix.

- **Create/save a note**
  - **Endpoint**: `POST /api/note/save`
  - **Body**:

    ```json
    {
      "character_id": "1",
      "note": "This is a test note for Rick."
    }
    ```

  - **Example cURL**:

    ```bash
    curl -X POST "http://localhost:8000/api/note/save" \
      -H "Content-Type: application/json" \
      -d '{
        "character_id": "1",
        "note": "This is a test note for Rick."
      }'
    ```

- **Fetch notes for a character**
  - **Endpoint**: `GET /api/note?character_id=...`
  - **Example cURL**:

    ```bash
    curl "http://localhost:8000/api/note?character_id=1"
    ```

  - Returns a list of notes:
    - Each item has `_id`, `character_id`, `note`, `created_at` (as an ISO timestamp).

- **Delete a note**
  - **Endpoint**: `POST /api/note/delete`
  - **Body**:

    ```json
    {
      "note_id": "uuid-of-note"
    }
    ```

  - **Example cURL**:

    ```bash
    curl -X POST "http://localhost:8000/api/note/delete" \
      -H "Content-Type: application/json" \
      -d '{
        "note_id": "uuid-of-note"
      }'
    ```

---

## 7. Troubleshooting and tips

- **Model downloads**:
  - The first call that touches the NER pipeline (`dslim/bert-base-NER`) will download model weights.  
  - This may take a bit and requires an internet connection.

- **Database path errors**:
  - If `DATABASE_ENDPOINT` is not set, the app will raise an error on startup.
  - Make sure your `.env` file is present and either:
    - You are running via `uvicorn main:app --reload` in the project root, or
    - Your process environment includes `DATABASE_ENDPOINT`.

- **OpenAI errors**:
  - Ensure `OPENAI_API_KEY` is valid.
  - Check network connectivity and OpenAI quota/limits if requests fail.

- **Inspecting the API**:
  - The fastest way to explore endpoints is via Swagger UI at `http://localhost:8000/docs`.
