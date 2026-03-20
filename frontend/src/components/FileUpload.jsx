import { useRef, useState } from 'react';
import './FileUpload.css';

export default function FileUpload({ onUpload, isUploading }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleFile = (file) => {
    if (!file) return;
    const allowed = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      alert('Please upload a PDF or image file (PNG, JPG).');
      return;
    }
    setFileName(file.name);
    onUpload(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  return (
    <div
      className={`file-upload-zone ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
      onClick={() => !isUploading && inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        onChange={(e) => handleFile(e.target.files[0])}
        style={{ display: 'none' }}
      />

      {isUploading ? (
        <div className="upload-progress">
          <div className="upload-spinner" />
          <span className="upload-text">Processing prescription...</span>
        </div>
      ) : (
        <>
          <div className="upload-icon-wrap">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
          </div>
          <div className="upload-label">
            <span className="upload-main">Drop prescription here</span>
            <span className="upload-sub font-mono">PDF, PNG, JPG — Click or drag</span>
          </div>
          {fileName && <span className="upload-filename">{fileName}</span>}
        </>
      )}
    </div>
  );
}
