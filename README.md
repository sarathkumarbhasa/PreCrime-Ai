# PRECRIME AI

Predictive Criminal Intelligence System.

## Backend Setup
1. Navigate to the `backend` directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload --port 8000`

## Frontend Setup
1. Navigate to the root directory (or `frontend` if separated).
2. Install dependencies: `npm install`
3. Run the dev server: `npm run dev`

Make sure to set your `OPENROUTER_API_KEY` to enable the AI Persona Generation features:
1. Create a `.env` file in the root backend directory.
2. Add the following line: `OPENROUTER_API_KEY="your_api_key_here"`
