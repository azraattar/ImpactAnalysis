// src/App.js
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./HomePage";
import CompanyDetail from "./CompanyDetail";
import "./App.css";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/company/:companyName" element={<CompanyDetail />} />
      </Routes>
    </Router>
  );
}
