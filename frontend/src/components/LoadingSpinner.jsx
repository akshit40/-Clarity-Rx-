import './LoadingSpinner.css';

export default function LoadingSpinner({ text = 'Loading...' }) {
  return (
    <div className="loading-container">
      <div className="loading-orb">
        <div className="orb-ring" />
        <div className="orb-ring ring-2" />
        <div className="orb-core" />
      </div>
      <span className="loading-label font-mono">{text}</span>
    </div>
  );
}
