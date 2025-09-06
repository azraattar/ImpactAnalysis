// src/SearchCompanies.js
import { useEffect, useRef, useState, useCallback } from "react"; // 1. Import useCallback
import { Link } from "react-router-dom";

// Debounce helper
function useDebouncedCallback(cb, delay) {
  const t = useRef();
  // Clear any existing timer on re-render to prevent memory leaks
  useEffect(() => () => clearTimeout(t.current), []); 
  return (...args) => {
    clearTimeout(t.current);
    t.current = setTimeout(() => cb(...args), delay);
  };
}

export default function SearchCompanies() {
  const [query, setQuery] = useState("");
  const [companies, setCompanies] = useState([]);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [suggestions, setSuggestions] = useState([]);
  const [showSug, setShowSug] = useState(false);

  const API_BASE = process.env.REACT_APP_API_URL || "";

  // 2. Wrap fetchCompanies in useCallback
  const fetchCompanies = useCallback(async (q = "", p = 1) => {
    try {
      const url = new URL(`${API_BASE}/api/companies`);
      url.searchParams.set("query", q);
      url.searchParams.set("page", p);
      url.searchParams.set("per_page", 5);

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

      const data = await res.json();
      setCompanies(data.results || []);
      setPage(data.pagination?.page || 1);
      setPages(data.pagination?.pages || 1);
    } catch (err) {
      console.error("companies fetch failed:", err);
      setCompanies([]);
    }
  }, [API_BASE]); // Dependency is API_BASE

  // 3. Wrap the suggestion fetching logic in useCallback
  const fetchSuggestions = useCallback(async (text) => {
    try {
      const url = new URL(`${API_BASE}/api/suggestions`);
      if (text?.trim()) url.searchParams.set("q", text);

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

      const json = await res.json();
      setSuggestions(Array.isArray(json) ? json : []);
    } catch (err) {
      console.error("suggestions fetch failed:", err);
      setSuggestions([]);
    }
  }, [API_BASE]); // Dependency is API_BASE

  const debouncedSuggest = useDebouncedCallback(fetchSuggestions, 180);
  
  // 4. Add the memoized functions to the dependency array
  useEffect(() => {
    fetchCompanies("", 1);
    fetchSuggestions(""); 
  }, [fetchCompanies, fetchSuggestions]);

  // Input handling
  const onInput = (e) => {
    const val = e.target.value;
    setQuery(val);
    setShowSug(true);
    debouncedSuggest(val);
  };

  // Select suggestion
  const onSelectSuggestion = (name) => {
    setQuery(name);
    setShowSug(false);
    fetchCompanies(name, 1);
  };

  // Search button click
  const onSearchClick = () => {
    setShowSug(false);
    fetchCompanies(query, 1);
  };

  // Pagination
  const nextPage = () => {
    if (page < pages) fetchCompanies(query, page + 1);
  };
  const prevPage = () => {
    if (page > 1) fetchCompanies(query, page - 1);
  };

  return (
    <section id="search-companies" className="section search-section">
        <div className="search-inner">
            <h2 className="search-title">SEARCH COMPANIES</h2>
            <p className="search-subtitle">Find details about companies and their impact</p>
            <div className="search-box" style={{ position: "relative" }}>
                <input
                    type="text"
                    id="companySearchInput"
                    placeholder="Search for a company... eg. PepsiCo, Nestlé"
                    aria-label="Search for a company"
                    value={query}
                    onChange={onInput}
                    onFocus={() => setShowSug(true)}
                    onBlur={() => setTimeout(() => setShowSug(false), 120)}
                />
                <button className="search-btn" onClick={onSearchClick}>Search</button>

                {showSug && suggestions.length > 0 && (
                    <ul
                        className="suggestions"
                        style={{
                            position: 'absolute', top: '100%', left: 0, width: '100%',
                            maxWidth: 350, background: '#fff', border: '3px solid #111',
                            borderTop: 'none', zIndex: 10, listStyle: 'none', margin: 0,
                            padding: 0, maxHeight: 240, overflow: 'auto'
                        }}
                    >
                        {suggestions.map((s) => (
                            <li
                                key={s}
                                onMouseDown={(e) => e.preventDefault()}
                                onClick={() => onSelectSuggestion(s)}
                                style={{ padding: '10px 12px', cursor: 'pointer', borderTop: '1px solid #eee' }}
                            >
                                {s}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="features-grid" style={{ marginTop: 22 }}>
                {companies.length > 0 ? companies.map((c) => (
                    <Link key={c.name} to={`/company/${encodeURIComponent(c.name)}`} className="card-link">
                        <article className="feature-card">
                            <h3 className="feature-title">{c.name}</h3>
                            <p className="feature-text">{c.description}</p>
                            {(c.month || c.year) && (
                                <p className="feature-text date-info">
                                    {c.month} {c.year}
                                </p>
                            )}
                        </article>
                    </Link>
                )) : (
                    <p style={{ textAlign: 'center', marginTop: 20 }}>No companies found</p>
                )}
            </div>

            <div style={{ marginTop: 16, display: 'flex', gap: 12, justifyContent: 'center' }}>
                <button className="search-btn" disabled={page <= 1} onClick={prevPage}>Prev</button>
                <span style={{ alignSelf: 'center' }}>Page {page} of {pages}</span>
                <button className="search-btn" disabled={page >= pages} onClick={nextPage}>Next</button>
            </div>
        </div>
    </section>
  );
}
