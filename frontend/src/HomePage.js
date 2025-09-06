// src/HomePage.js
import { useEffect } from "react";
import "./App.css";
import SearchCompanies from "./SearchCompanies";

export default function HomePage() {
  useEffect(() => {
    // This effect handles the active link highlighting on scroll
    const links = document.querySelectorAll(".nav-link");
    const sections = [...links]
      .map((a) => document.querySelector(a.getAttribute("href")))
      .filter(Boolean);

    const setActive = () => {
      const y = window.scrollY + 120;
      let active = links[0]; // Default to the first link
      sections.forEach((s, i) => {
        if (s.offsetTop <= y) {
          active = links[i];
        }
      });
      links.forEach((l) => l.classList.toggle("active", l === active));
    };

    setActive();
    window.addEventListener("scroll", setActive);

    // This effect handles the header shadow on scroll
    const header = document.querySelector(".site-header");
    const onScrollShadow = () => {
      if (header) {
        header.style.boxShadow =
          window.scrollY > 6 ? "0 6px 14px rgba(0,0,0,.12)" : "none";
      }
    };
    window.addEventListener("scroll", onScrollShadow);

    // This effect handles smooth scrolling for CTA buttons
    document.querySelectorAll("[data-scroll]").forEach((b) =>
      b.addEventListener("click", () => {
        const t = document.querySelector(b.dataset.scroll);
        if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
      })
    );

    return () => {
      window.removeEventListener("scroll", setActive);
      window.removeEventListener("scroll", onScrollShadow);
    };
  }, []);

  return (
    <>
      <header className="site-header" id="top">
        <div className="header-inner">
          <a className="brand" href="#top" aria-label="Impact Insights Home">
            <span className="brand-badge"><span className="badge-inner">II</span></span>
            <span className="brand-name">IMPACT INSIGHTS</span>
          </a>
          <nav className="nav">
            <a className="nav-link" href="#home">HOME</a>
            <a className="nav-link" href="#search-companies">DASHBOARD</a>
            <a className="nav-link" href="#about">ABOUT</a>
            <a className="nav-link" href="#contact">CONTACT</a>
          </nav>
        </div>
        <div className="header-banner"></div>
      </header>

      <main>
        {/* Hero Section */}
        <section id="home" className="section hero">
          <div className="hero-inner">
            <div className="hero-mark"></div>
            <h1 className="hero-title">
              <span className="t1">Tracking the Impact of Global</span>
              <span className="t2">Movements</span>
              <span className="t3">Through Data</span>
            </h1>
            <p className="hero-sub">
              Visualizing publicly available financial data to explore how events and consumer choices shape companies and markets.
            </p>
            <button className="cta" data-scroll="#search-companies">
              GET STARTED <span className="cta-arrow" aria-hidden="true">→</span>
            </button>
          </div>
        </section>

        {/* Guided by Principles Section */}
        <section id="principles" className="section principles">
          <div className="section-head">
            <h1 className="section-title">GUIDED BY PRINCIPLES</h1>
            <p className="section-sub">Transparency and awareness through data-driven insights</p>
          </div>
          <div className="quotes-grid">
            <article className="quote-card">
              <span className="quote-icon">״</span>
              <p className="quote-text">
                OUR LIVES BEGIN TO END THE <br />
                DAY WE BECOME SILENT ABOUT THE THINGS THAT MATTER
              </p>
            </article>
            <article className="quote-card">
              <span className="quote-icon">״</span>
              <p className="quote-text">
                EVERY PURCHASE IS A VOTE FOR THE WORLD YOU WANT TO SEE.
              </p>
            </article>
            <article className="quote-card">
              <span className="quote-icon">״</span>
              <p className="quote-text">
                SMALL CHOICES CAN LEAD TO BIG CHANGE.
              </p>
            </article>
          </div>
        </section>

        {/* Search Companies Section */}
        <SearchCompanies />

        {/* About Section */}
        <section id="about" className="section features">
          <div className="features-grid">
            <article className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 2l7 3v6c0 5-3.5 9-7 11-3.5-2-7-6-7-11V5l7-3z" fill="#2b6cff"/>
                  <path d="M12 6v10" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                  <path d="M8.5 10.5h7" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              </div>
              <h3 className="feature-title">VERIFIED DATA SOURCES</h3>
              <p className="feature-text">
                All data sourced from publicly available financial reports and verified through multiple channels.
              </p>
            </article>
            
            <article className="feature-card">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" aria-hidden="true">
                  <rect x="3" y="3" width="18" height="18" rx="3" fill="#ffd339"/>
                  <path
                    d="M6 16l3-3 2 2 4-5 3 4"
                    fill="none"
                    stroke="#111"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <h3 className="feature-title">REAL-TIME ANALYSIS</h3>
              <p className="feature-text">
                Dynamic visualizations that update with the latest quarterly reports and market trends.
              </p>
            </article>
          </div>
        </section>
      </main>

      <footer id="contact" className="site-footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="brand-badge"><span className="badge-inner">II</span></span>
            <span className="brand-name">IMPACT INSIGHTS</span>
          </div>
          <p className="foot-note">© 2025 IMPACT INSIGHTS. ALL DATA SOURCED FROM PUBLIC FINANCIAL REPORTS. FOR EDUCATIONAL AND RESEARCH PURPOSES ONLY.</p>
          <div className="footer-badges">
            {/* FIX: Replaced <a> with <button> for accessibility */}
            <button type="button" className="sq-badge blue" aria-label="LinkedIn">
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#2b6cff"/><rect x="6" y="10" width="2.5" height="8" fill="#fff"/><rect x="6" y="6" width="2.5" height="2.5" fill="#fff"/><rect x="10" y="10" width="2.5" height="8" fill="#fff"/><rect x="13.5" y="13" width="2.5" height="5" fill="#fff"/></svg>
            </button>
            <button type="button" className="sq-badge red" aria-label="GitLab">
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><rect width="24" height="24" rx="6" fill="#ff3d00"/><path d="M6 14l6 6 6-6-2-6-4 3-4-3-2 6z" fill="#fff"/></svg>
            </button>
          </div>
          <ul className="legal">
            {/* FIX: Replaced <a> with <button> for accessibility */}
            <li><button type="button">PRIVACY POLICY</button></li><li><span className="dot">•</span></li>
            <li><button type="button">TERMS OF SERVICE</button></li><li><span className="dot">•</span></li>
            <li><button type="button">METHODOLOGY</button></li>
          </ul>
        </div>
      </footer>
    </>
  );
}
