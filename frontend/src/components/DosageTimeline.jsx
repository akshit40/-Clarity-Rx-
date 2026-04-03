import React from 'react';

const DosageTimeline = ({ extractedData }) => {
  if (!extractedData || !extractedData.medicines) return null;

  const medicines = extractedData.medicines;
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Map 24h to X position (0 to 100%)
  const getX = (hour) => (hour / 24) * 100;

  // Helper to parse timing into hour slots
  const getMedicineSlots = (timing) => {
    const slots = [];
    if (timing.morning && timing.morning !== '0') slots.push(8);   // 8 AM
    if (timing.afternoon && timing.afternoon !== '0') slots.push(14); // 2 PM
    if (timing.night && timing.night !== '0') slots.push(21);     // 9 PM
    return slots;
  };

  return (
    <div className="dosage-timeline-container" style={{
      background: 'rgba(10, 25, 20, 0.6)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(0, 255, 170, 0.2)',
      borderRadius: '16px',
      padding: '24px',
      marginTop: '24px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ margin: 0, color: '#00ffaa', fontSize: '1.2rem', letterSpacing: '1px', textTransform: 'uppercase' }}>
          🕒 24-Hour Dosage Protocol
        </h3>
        <span style={{ fontSize: '0.8rem', opacity: 0.6, color: '#fff' }}>Surgical-Med 3.0 Visualization</span>
      </div>

      <div style={{ position: 'relative', height: '220px', width: '100%', overflow: 'visible' }}>
        {/* Time Labels */}
        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '10px' }}>
          {[0, 6, 12, 18, 24].map(h => (
            <span key={h} style={{ fontSize: '0.7rem', color: '#00ffaa', opacity: 0.8 }}>
              {h === 12 ? '12:00 PM' : h === 0 || h === 24 ? '12:00 AM' : `${h > 12 ? h - 12 : h}:00 ${h >= 12 ? 'PM' : 'AM'}`}
            </span>
          ))}
        </div>

        {/* Timeline Grid */}
        <div style={{ 
          position: 'absolute', 
          top: '30px', 
          left: 0, 
          right: 0, 
          height: '2px', 
          background: 'linear-gradient(90deg, transparent, rgba(0, 255, 170, 0.5), transparent)',
          boxShadow: '0 0 10px rgba(0, 255, 170, 0.3)'
        }} />

        {/* Medicine Tracks */}
        <div style={{ marginTop: '40px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {medicines.map((med, idx) => {
            const slots = getMedicineSlots(med.timing || {});
            return (
              <div key={idx} style={{ position: 'relative', height: '30px', display: 'flex', alignItems: 'center' }}>
                <div style={{ width: '100px', fontSize: '0.85rem', color: '#fff', fontWeight: '500', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: '10px' }}>
                  {med.name}
                </div>
                <div style={{ flex: 1, position: 'relative', height: '100%', borderLeft: '1px solid rgba(0, 255, 170, 0.1)' }}>
                  {slots.map((hour, sIdx) => (
                    <div 
                      key={sIdx}
                      className="dose-marker"
                      style={{
                        position: 'absolute',
                        left: `${getX(hour)}%`,
                        top: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: '12px',
                        height: '12px',
                        background: '#00ffaa',
                        borderRadius: '50%',
                        boxShadow: '0 0 15px #00ffaa',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                      }}
                      title={`${med.name} at ${hour}:00`}
                    >
                      <div style={{
                        position: 'absolute',
                        top: '-20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        fontSize: '0.65rem',
                        color: '#00ffaa',
                        fontWeight: 'bold'
                      }}>
                        {med.quantity || '1'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      <div style={{ marginTop: '20px', paddingTop: '15px', borderTop: '1px solid rgba(0, 255, 170, 0.1)', fontSize: '0.85rem', color: 'rgba(255, 255, 255, 0.7)' }}>
        ℹ️ <strong>Pro Tip:</strong> Hover over the glowing markers to see specific dosage quantities.
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .dose-marker:hover {
          width: 16px !important;
          height: 16px !important;
          box-shadow: 0 0 25px #00ffaa !important;
        }
      `}} />
    </div>
  );
};

export default DosageTimeline;
