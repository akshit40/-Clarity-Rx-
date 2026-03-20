import { useState, useEffect, useCallback } from 'react';
import { getOTCList, searchOTC } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import './OTCListPage.css';

export default function OTCListPage() {
  const [medicines, setMedicines] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    loadList();
  }, []);

  const loadList = async () => {
    try {
      const data = await getOTCList();
      setMedicines(data.medicines || []);
    } catch (err) {
      console.error('Failed to load OTC list:', err);
    } finally {
      setLoading(false);
    }
  };

  // Debounced search
  const handleSearch = useCallback(async (q) => {
    if (!q.trim()) {
      setSearchResults(null);
      return;
    }
    setSearching(true);
    try {
      const data = await searchOTC(q);
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => handleSearch(query), 400);
    return () => clearTimeout(timer);
  }, [query, handleSearch]);

  // Group by type
  const groupedMedicines = medicines.reduce((acc, med) => {
    const type = med.type || 'General';
    if (!acc[type]) acc[type] = [];
    acc[type].push(med);
    return acc;
  }, {});

  const typeColors = {
    'Pain Relief Tablets': '#FF6B6B',
    'Antacid & Digestive Tablets': '#4ECDC4',
    'Cold, Cough & Allergy Tablets': '#45B7D1',
    'Laxatives & Constipation Relief': '#96CEB4',
    'Vitamins & Supplements': '#FECA57',
    'Multivitamin Tablets': '#FF9FF3',
    'Calcium Supplements': '#54A0FF',
    'Zinc Tablets': '#5F27CD',
    'Antifungal Tablets': '#FF6348',
    'Eye Care Tablets/Drops (Oral)': '#00D2D3',
    'Ear Care Tablets': '#2ED8A3',
    'Acne Treatment Tablets': '#F368E0',
    'Anti-Diarrheal Tablets': '#FF9F43',
    'Electrolyte Tablets': '#0ABDE3',
    'Motion Sickness Tablets': '#EE5A24',
    'Sleep Aid Tablets': '#6C5CE7',
    'Anthelmintic Tablets': '#A3CB38',
    'Hemorrhoid Tablets': '#FDA7DF',
  };

  return (
    <div className="otc-page">
      <div className="otc-page-inner">
        {/* Header */}
        <div className="otc-page-header animate-in">
          <div className="otc-header-text">
            <h1 className="font-display">
              <span className="text-gradient">OTC Medicines</span>
            </h1>
            <p className="otc-header-desc">
              Allowed over-the-counter medicines. Always consult a doctor if unsure.
            </p>
          </div>

          {/* Search */}
          <div className="otc-search-wrap">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input
              id="otc-search"
              type="text"
              placeholder="Search medicines, brands, or uses..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoComplete="off"
            />
            {query && (
              <button className="search-clear" onClick={() => setQuery('')}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <LoadingSpinner text="Loading medicines..." />
        ) : searchResults !== null ? (
          /* Search Results */
          <div className="search-results animate-in">
            <div className="results-header">
              <span className="font-mono results-count">
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
              </span>
              {searching && <div className="mini-spinner" />}
            </div>

            {searchResults.length === 0 ? (
              <div className="no-results">
                <span className="no-results-icon">🔍</span>
                <p>No medicines match "{query}"</p>
              </div>
            ) : (
              <div className="results-grid">
                {searchResults.map((r, idx) => (
                  <div
                    key={idx}
                    className="result-card glass-panel animate-in"
                    style={{ animationDelay: `${idx * 0.05}s` }}
                  >
                    <div className="result-header">
                      <span className="result-name">{r['Medicine Name']}</span>
                      <span
                        className="result-type-badge"
                        style={{ background: `${typeColors[r.Type] || '#666'}20`, color: typeColors[r.Type] || '#666', borderColor: `${typeColors[r.Type] || '#666'}30` }}
                      >
                        {r.Type}
                      </span>
                    </div>
                    <div className="result-score">
                      <div className="score-bar">
                        <div
                          className="score-fill"
                          style={{ width: `${(r.Score || 0) * 100}%` }}
                        />
                      </div>
                      <span className="score-value font-mono">{((r.Score || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Full List grouped by type */
          <div className="otc-categories">
            {Object.entries(groupedMedicines).map(([type, meds], catIdx) => (
              <div
                key={type}
                className="category-section animate-in"
                style={{ animationDelay: `${catIdx * 0.08}s` }}
              >
                <div className="category-header">
                  <span
                    className="category-dot"
                    style={{ background: typeColors[type] || '#666' }}
                  />
                  <h2 className="category-title font-display">{type}</h2>
                  <span className="category-count font-mono">{meds.length}</span>
                </div>
                <div className="category-grid">
                  {meds.map((med, medIdx) => (
                    <div key={medIdx} className="medicine-card glass-panel glass-panel-hover">
                      <span
                        className="med-indicator"
                        style={{ background: typeColors[type] || '#666' }}
                      />
                      <span className="med-name">{med.medicine_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
