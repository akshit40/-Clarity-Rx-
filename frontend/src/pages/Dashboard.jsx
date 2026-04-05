import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  listPrescriptions,
  uploadPrescription,
  getSession,
  getChatHistory,
  sendMessage,
  checkOTC,
  getGuardianAnalysis,
} from '../api/client';
import FileUpload from '../components/FileUpload';
import ChatMessage from '../components/ChatMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import DosageTimeline from '../components/DosageTimeline';
import { jsPDF } from 'jspdf';
import { QRCodeSVG } from 'qrcode.react';
import './Dashboard.css';

const NeuralScanner = () => (
  <div className="neural-scanner">
    <div className="scan-line" />
  </div>
);

const SafetyPulse = ({ color = 'var(--color-accent)' }) => (
  <div className="heartbeat-container">
    <svg width="100%" height="40" viewBox="0 0 400 40">
      <path
        className="heartbeat-line"
        style={{ stroke: color }}
        d="M0 20 L40 20 L50 10 L65 35 L75 20 L120 20 L130 5 L145 38 L160 20 L200 20 L210 12 L225 32 L235 20 L280 20 L290 8 L305 34 L320 20 L400 20"
      />
    </svg>
  </div>
);

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // State
  const [prescriptions, setPrescriptions] = useState([]);
  const [activePrescription, setActivePrescription] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionDetails, setSessionDetails] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [otcResult, setOtcResult] = useState(null);
  const [otcLoading, setOtcLoading] = useState(false);
  const [showOtc, setShowOtc] = useState(false);
  const [guardianResult, setGuardianResult] = useState(null);
  const [guardianLoading, setGuardianLoading] = useState(false);
  const [showGuardian, setShowGuardian] = useState(false);
  const [showQR, setShowQR] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [extractedData, setExtractedData] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Load prescriptions
  useEffect(() => {
    if (user) loadPrescriptions();
  }, [user]);

  // Scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadPrescriptions = async () => {
    try {
      const data = await listPrescriptions(user);
      setPrescriptions(data.prescriptions || []);
    } catch (err) {
      console.error('Failed to load prescriptions:', err);
    }
  };

  const selectPrescription = async (p) => {
    setActivePrescription(p);
    setMessages([]);
    setOtcResult(null);
    setShowOtc(false);
    setGuardianResult(null);
    setShowGuardian(false);
    setIsLoadingHistory(true);

    try {
      const sessionData = await getSession(p.id, user);
      setSessionId(sessionData.session_id);
      setSessionDetails(sessionData.details || '');
      setExtractedData(sessionData.extracted_data || null);

      const historyData = await getChatHistory(sessionData.session_id);
      setMessages(historyData.messages || []);
    } catch (err) {
      console.error('Failed to load session:', err);
    } finally {
      setIsLoadingHistory(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleUpload = async (file) => {
    setIsUploading(true);
    try {
      const data = await uploadPrescription(file, user);
      await loadPrescriptions();

      // Auto-select the new prescription
      const newP = {
        id: data.prescription_id,
        title: data.title || `Prescription ${file.name}`,
      };
      await selectPrescription(newP);
    } catch (err) {
      console.error('Upload failed:', err);
      alert(err.message || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activePrescription || !sessionId || isSending) return;

    const question = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setIsSending(true);

    try {
      const data = await sendMessage(question, activePrescription.id, sessionId);
      setMessages((prev) => [...prev, { role: 'ai', content: data.answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'ai', content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  const handleOTCCheck = async () => {
    console.log("OTC Check Clicked. Active P:", activePrescription, "Session ID:", sessionId);
    if (!sessionId) {
      alert("Session not ready. Please wait.");
      return;
    }
    
    // Toggle showOtc
    if (showOtc) {
      setShowOtc(false);
      return;
    }

    setShowOtc(true);
    if (otcResult) return; // Don't re-fetch if we already have it

    setOtcLoading(true);
    try {
      const data = await checkOTC(sessionId, activePrescription.id, sessionDetails || "Check latest prescription content");
      setOtcResult(data.result);
    } catch (err) {
      console.error('OTC check failed:', err);
      setOtcResult({ error: err.message });
    } finally {
      setOtcLoading(false);
    }
  };

  const handleGuardianCheck = async () => {
    if (!sessionId) {
      alert("Session not ready.");
      return;
    }
    if (showGuardian) {
      setShowGuardian(false);
      return;
    }

    setShowGuardian(true);
    if (guardianResult) return;

    setGuardianLoading(true);
    try {
      const data = await getGuardianAnalysis(sessionId, sessionDetails || "No content details");
      setGuardianResult(data.result);
    } catch (err) {
      console.error('Guardian check failed:', err);
      setGuardianResult({ error: err.message });
    } finally {
      setGuardianLoading(false);
    }
  };

  const handleExportPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(22);
    doc.text("Clarity Rx: Medical Report", 20, 20);
    
    doc.setFontSize(14);
    doc.text(`Title: ${activePrescription?.title || 'Unknown'}`, 20, 35);
    
    doc.setFontSize(12);
    const splitDetails = doc.splitTextToSize(sessionDetails || 'No details available', 170);
    doc.text(splitDetails, 20, 50);

    if (guardianResult && !guardianResult.error) {
      let yPos = 50 + (splitDetails.length * 6) + 10;
      doc.setFontSize(14);
      doc.text("Guardian Safety Analysis:", 20, yPos);
      doc.setFontSize(12);
      doc.setTextColor(200, 0, 0); // Red for DDI
      doc.text(`DDI Alert: ${guardianResult.ddi_alert || 'None'}`, 20, yPos + 10);
      doc.setTextColor(0, 0, 0);
    }

    doc.save(`ClarityRx_Report_${activePrescription?.id || 'doc'}.pdf`);
  };

  const handleSetReminder = () => {
    if (!("Notification" in window)) {
      alert("This browser does not support desktop notification");
      return;
    }
    Notification.requestPermission().then(function (permission) {
      if (permission === "granted") {
        new Notification("Clarity Rx: Reminder Set!", {
          body: "We will remind you when it's time to take your medication.",
          icon: "💊"
        });
      }
    });
  };

  const handleSpeak = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    if (!messages.length) return;
    
    // Find last AI message
    const lastAiMsg = [...messages].reverse().find(m => m.role === 'ai');
    if (!lastAiMsg) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(lastAiMsg.content);
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title font-display">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            Prescriptions
          </h2>
          <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
          </button>
        </div>

        {/* Upload */}
        <div className="sidebar-upload">
          <FileUpload onUpload={handleUpload} isUploading={isUploading} />
          {isUploading && <NeuralScanner />}
        </div>

        {/* Chat List */}
        <div className="sidebar-list">
          {prescriptions.length === 0 ? (
            <div className="sidebar-empty">
              <span className="empty-icon">📋</span>
              <p className="font-mono">No prescriptions yet</p>
            </div>
          ) : (
            prescriptions.map((p, idx) => (
              <button
                key={p.id}
                className={`chat-item ${activePrescription?.id === p.id ? 'active' : ''}`}
                onClick={() => selectPrescription(p)}
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                <div className="chat-item-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                </div>
                <span className="chat-item-title">{p.title}</span>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Mobile sidebar toggle */}
      {!sidebarOpen && (
        <button className="sidebar-fab" onClick={() => setSidebarOpen(true)}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
      )}

      {/* Main Content */}
      <main className="main-content">
        {!activePrescription ? (
          /* Welcome State */
          <div className="welcome-state">
            <div className="welcome-content animate-in">
              <div className="welcome-icon animate-float">💊</div>
              <h1 className="welcome-title font-display">
                Welcome to <span className="text-gradient">Clarity Rx</span>
              </h1>
              <p className="welcome-text">
                Upload a prescription or select a chat from the sidebar to begin.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '2rem', alignItems: 'center' }}>
                <label
                  htmlFor="welcome-upload"
                  style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1.5rem', background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '0.9375rem', color: 'var(--color-text-primary)', width: '220px', justifyContent: 'center' }}
                >
                  📸 Upload &amp; Extract
                </label>
                <input id="welcome-upload" type="file" accept="image/*,.pdf" hidden onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    setSidebarOpen(true);
                    // trigger same upload via sidebar
                    const sidebarInput = document.querySelector('.file-upload-zone input[type="file"]');
                    if (sidebarInput) {
                      const dt = new DataTransfer();
                      dt.items.add(file);
                      sidebarInput.files = dt.files;
                      sidebarInput.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    e.target.value = null;
                  }
                }} />
                <button
                  style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1.5rem', background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '0.9375rem', color: 'var(--color-text-primary)', width: '220px', justifyContent: 'center' }}
                  onClick={() => {
                    setSidebarOpen(true);
                    setTimeout(() => {
                      const firstChat = document.querySelector('.chat-item');
                      if (firstChat) firstChat.click();
                      else alert('Please upload a prescription first.');
                    }, 150);
                  }}
                >
                  💬 Ask Question
                </button>
                <button
                  style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.75rem 1.5rem', background: 'var(--color-bg-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', fontSize: '0.9375rem', color: 'var(--color-text-primary)', width: '220px', justifyContent: 'center' }}
                  onClick={() => navigate('/otc')}
                >
                  ✅ OTC Check
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* Chat View */
          <div className="chat-view">
            {/* Chat Header */}
            <div className="chat-header">
              <div className="chat-header-info">
                <h2 className="chat-header-title font-display">{activePrescription.title}</h2>
                <span className="chat-header-session font-mono">
                  Session: {sessionId?.slice(0, 8)}...
                </span>
              </div>
              <div className="chat-header-actions">
                <button 
                  className={`voice-btn ${isSpeaking ? 'speaking' : ''}`}
                  onClick={() => {
                    console.log("Voice Button Clicked. Current isSpeaking:", isSpeaking);
                    handleSpeak();
                  }}
                  title="Listen to Advice"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                  {isSpeaking ? 'Speaking...' : 'Listen'}
                </button>
                <button
                  className={`otc-check-btn ${showOtc ? 'active' : ''}`}
                  onClick={handleOTCCheck}
                  disabled={otcLoading}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  {otcLoading ? 'Checking...' : 'OTC'}
                </button>
                <div style={{ display: 'flex', gap: '8px', borderLeft: '1px solid var(--color-border)', paddingLeft: '8px', marginLeft: '4px' }}>
                  <button className="voice-btn" onClick={handleExportPDF} title="Export PDF" style={{color: '#ff4b4b', borderColor: 'transparent', background: 'rgba(255, 75, 75, 0.1)'}}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                  </button>
                  <button className="voice-btn" onClick={handleSetReminder} title="Set Dose Reminders" style={{color: '#ffb300', borderColor: 'transparent', background: 'rgba(255, 179, 0, 0.1)'}}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"></path></svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Chat Body (Scrollable Area) */}
            <div className="chat-body">
              {/* Medicine Details */}
              {sessionDetails && (
                <div className="dashboard-insights animate-in">
                  <DosageTimeline extractedData={extractedData} />
                  
                  <details className="medicine-details glass-panel">
                    <summary className="details-summary">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
                      <span className="font-display">Medicine Details & Safety</span>
                    </summary>
                    <div className="details-content font-mono" style={{ padding: '0 1rem 1rem' }}>
                      <pre>{sessionDetails}</pre>
                      
                      <div style={{ marginTop: '1rem', borderTop: '1px solid var(--color-border)', paddingTop: '1rem' }}>
                        <button className="otc-check-btn active" onClick={handleGuardianCheck} disabled={guardianLoading} style={{ background: '#7e57c2', color: 'white', borderColor: '#7e57c2', width: '100%', justifyContent: 'center' }}>
                          {guardianLoading ? '🛡️ Analyzing Risks & Savings...' : '🛡️ Run Full Guardian Analysis'}
                        </button>
                      </div>
                    </div>
                  </details>
                </div>
              )}

              {/* Guardian Bento Grid Results */}
              {showGuardian && (
                <div className="bento-grid animate-in">
                  {guardianLoading ? (
                    <div className="glass-panel" style={{ gridColumn: '1 / -1', padding: '3rem' }}>
                      <LoadingSpinner text="Shielding patient from risks: Consulting Knowledge Base..." />
                    </div>
                  ) : guardianResult?.error ? (
                    <div className="form-alert alert-error">{guardianResult.error}</div>
                  ) : guardianResult ? (
                    <>
                      {/* DDI Alert Tile */}
                      <div className={`bento-tile glass-panel ${guardianResult.ddi_alert !== 'None' ? 'tile-alert' : ''}`}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <span className="tile-label">Safety Protocol: DDI</span>
                          <span className="tile-icon">{guardianResult.ddi_alert !== 'None' ? '🚨' : '✅'}</span>
                        </div>
                        <p className="tile-value">{guardianResult.ddi_alert}</p>
                        <SafetyPulse color={guardianResult.ddi_alert !== 'None' ? 'var(--color-danger)' : 'var(--color-success)'} />
                      </div>

                      {/* Generic Savings Tile */}
                      {guardianResult.generics?.length > 0 && (
                        <div className="bento-tile glass-panel tile-saving">
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <span className="tile-label">Guardian Optimization</span>
                            <span className="tile-icon">💎</span>
                          </div>
                          <p className="tile-value">Found {guardianResult.generics.length} Generic Alternatives</p>
                          <div style={{ fontSize: '0.75rem', opacity: 0.7, marginTop: '0.5rem' }}>
                            {guardianResult.generics.slice(0, 2).map((g, i) => (
                              <div key={i}>• {g.brand} &rarr; {g.generic}</div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Food & Lifestyle Group */}
                      <div className="bento-tile glass-panel" style={{ background: 'rgba(64, 196, 255, 0.03)' }}>
                        <span className="tile-label">Clinical Nuance: Diet</span>
                        <p className="tile-value" style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                          • {guardianResult.food_warnings?.[0] || "No critical food warnings detected."}
                        </p>
                      </div>

                      <div className="bento-tile glass-panel">
                        <span className="tile-label">Recovery Plan</span>
                        <p className="tile-value" style={{ fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
                           • {guardianResult.lifestyle_tips?.[0] || "Maintain standard rest and hydration."}
                        </p>
                      </div>
                    </>
                  ) : null}
                </div>
              )}

              {/* Pharmacist QR Panel */}
              <div style={{ margin: '0 2rem 1rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button 
                  onClick={() => setShowQR(!showQR)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--color-text-muted)', fontSize: '0.75rem', cursor: 'pointer', textDecoration: 'underline' }}>
                  {showQR ? 'Hide Pharmacist Share QR' : '📱 Share with Pharmacist via QR'}
                </button>
              </div>
              
              {showQR && (
                 <div className="animate-in" style={{ margin: '0 2rem 1rem', background: 'white', padding: '1.5rem', borderRadius: '12px', display: 'inline-block', textAlign: 'center' }}>
                   <QRCodeSVG value={sessionDetails || "No data"} size={128} />
                   <p style={{ margin: '0.5rem 0 0 0', color: '#000', fontSize: '0.75rem', fontWeight: 600 }}>Scan for clean text</p>
                 </div>
              )}

              {/* OTC Results */}
              {showOtc && (
                <div className="otc-results animate-in">
                  {otcLoading ? (
                    <LoadingSpinner text="Analyzing OTC status..." />
                  ) : otcResult?.error ? (
                    <div className="form-alert alert-error">{otcResult.error}</div>
                  ) : otcResult ? (
                    <div className="otc-grid">
                      {otcResult.otc_medicines?.length > 0 && (
                        <div className="otc-column otc-safe">
                          <h4 className="otc-col-title">
                            <span className="badge-dot dot-green" />
                            Safe to Buy
                          </h4>
                          {otcResult.otc_medicines.map((m, i) => (
                            <div key={i} className="otc-item">
                              <strong>{m.name}</strong>
                              <span>{m.reason}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      {otcResult.consult_medicines?.length > 0 && (
                        <div className="otc-column otc-consult">
                          <h4 className="otc-col-title">
                            <span className="badge-dot dot-amber" />
                            Consult Doctor
                          </h4>
                          {otcResult.consult_medicines.map((m, i) => (
                            <div key={i} className="otc-item">
                              <strong>{m.name}</strong>
                              <span>{m.reason}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>
              )}

              {/* Messages */}
              <div className="chat-messages">
                {isLoadingHistory ? (
                  <LoadingSpinner text="Loading history..." />
                ) : messages.length === 0 ? (
                  <div className="chat-empty">
                    <p className="font-mono">Ask anything about this prescription</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <ChatMessage
                      key={idx}
                      role={msg.role}
                      content={msg.content}
                      index={idx}
                    />
                  ))
                )}

                {/* Typing indicator */}
                {isSending && (
                  <div className="typing-indicator">
                    <div className="typing-dot" style={{ animationDelay: '0s' }} />
                    <div className="typing-dot" style={{ animationDelay: '0.15s' }} />
                    <div className="typing-dot" style={{ animationDelay: '0.3s' }} />
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
            </div>

            {/* Input */}
            <form className="chat-input-form" onSubmit={handleSend}>
              <div className="chat-input-wrap">
                <input
                  ref={inputRef}
                  id="chat-input"
                  type="text"
                  placeholder="Ask about prescriptions..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={isSending}
                  autoComplete="off"
                />
                <button
                  id="chat-send"
                  type="submit"
                  className="send-btn"
                  disabled={!input.trim() || isSending}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                  </svg>
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
