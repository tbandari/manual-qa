import React, { useState } from "react";
import axios from "axios";
import "./App.css"; 

function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse("");
    setIsSubmitted(true);

    try {
      const res = await axios.post("http://localhost:5000/query", { query });
      setResponse(res.data.answer);
      setQuery("");
    } catch (error) {
      console.error("Error fetching response:", error);
      setResponse("Error: Unable to fetch the response. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>{"How may I help you?"}</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit} className="query-form">
          <div className="input-container" >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your question here..."
              required
              className="query-input"
            />
            <button type="submit" className="submit-button" disabled={loading || query.trim() === ""}>
              {loading ? <span className="loading-dots"></span> : "⬆"}
            </button>
          </div>
        </form>
        <div className="response-container">
          {response && (
            <div className="response-box">
              <p>{response}</p>
            </div>
          )}
        </div>
      </main>
      <footer className="app-footer">
        <p>Powered by OpenAI and LangChain</p>
      </footer>
    </div>
  );
}

export default App;