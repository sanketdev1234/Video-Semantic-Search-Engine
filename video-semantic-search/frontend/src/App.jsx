import { useRef, useState } from "react";
import { uploadVideo, uploadVideoUrl, searchVideo } from "./services/api";

function App() {
  const videoRef = useRef(null);

  // Video state
  const [videoId, setVideoId] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [videoURL, setVideoURL] = useState("");
  const [videoSource, setVideoSource] = useState(""); // "upload" or "url"
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [youtubeEmbedUrl, setYoutubeEmbedUrl] = useState("");

  // Search state
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Extract YouTube video ID and create embed URL
  const getYoutubeEmbedUrl = (url) => {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    const videoId = match && match[2].length === 11 ? match[2] : null;
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!videoFile) {
      setError("Please select a video file");
      setTimeout(() => setError(""), 3000);
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    
    try {
      const res = await uploadVideo(videoFile);
      console.log("Upload response:", res);
      
      setVideoId(res.video_id);
      setVideoSource("upload");
      setSuccess("✅ Video uploaded and indexed successfully!");
      setTimeout(() => setSuccess(""), 5000);
      
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Upload failed: ${err.message}`);
      setTimeout(() => setError(""), 5000);
    } finally {
      setLoading(false);
    }
  };

  // Handle URL upload (YouTube)
  const handleUrlUpload = async () => {
    if (!youtubeUrl || !youtubeUrl.trim()) {
      setError("Please enter a YouTube URL");
      setTimeout(() => setError(""), 3000);
      return;
    }

    setLoading(true);
    setError("");
    setSuccess("");
    
    try {
      console.log("Uploading URL:", youtubeUrl);
      const res = await uploadVideoUrl(youtubeUrl);
      console.log("URL upload response:", res);
      
      setVideoId(res.video_id);
      setVideoSource("url");
      
      // Set embed URL for iframe
      const embedUrl = getYoutubeEmbedUrl(youtubeUrl);
      if (embedUrl) {
        setYoutubeEmbedUrl(embedUrl);
      }
      
      setSuccess("✅ YouTube video processed successfully!");
      setTimeout(() => setSuccess(""), 5000);
      
    } catch (err) {
      console.error("URL upload error:", err);
      setError(`URL processing failed: ${err.message}`);
      setTimeout(() => setError(""), 5000);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = async () => {
    if (!query || !query.trim()) {
      setError("Please enter a search query");
      setTimeout(() => setError(""), 3000);
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const data = await searchVideo(query, videoId);
      console.log("Search results:", data);
      
      setResults(data.results || []);
      
      if (data.results.length === 0) {
        setError("No results found");
        setTimeout(() => setError(""), 3000);
      }
      
    } catch (err) {
      console.error("Search error:", err);
      setError(`Search failed: ${err.message}`);
      setTimeout(() => setError(""), 5000);
    } finally {
      setLoading(false);
    }
  };

  // Jump to timestamp
  const jumpTo = (result) => {
    console.log("Jumping to:", result);
    
    // CASE 1: Uploaded video → seek locally
    if (result.source === "upload" && videoRef.current) {
      videoRef.current.currentTime = result.timestamp;
      videoRef.current.play();
      
      // Scroll to video
      videoRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    // CASE 2: URL video (YouTube) → update iframe with timestamp
    else if (result.source === "url" && youtubeEmbedUrl) {
      const timestampUrl = `${youtubeEmbedUrl}?start=${Math.floor(result.timestamp)}&autoplay=1`;
      setYoutubeEmbedUrl(timestampUrl);
      
      // Scroll to video
      const videoPlayer = document.getElementById('video-player-section');
      if (videoPlayer) {
        videoPlayer.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  // Download PDF notes
  const downloadNotes = () => {
    if (!videoId) {
      setError("Please upload a video first");
      setTimeout(() => setError(""), 3000);
      return;
    }

    window.open(
      `http://127.0.0.1:8000/processed/${videoId}/notes.pdf`,
      "_blank"
    );
  };

  // Format timestamp for display
  const formatTimestamp = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="container">
          <h1 className="header-title">
            <span className="icon">🎥</span>
            Video Semantic Search Engine
          </h1>
          <p className="header-subtitle">
            Upload videos or YouTube links, then search inside them using AI
          </p>
        </div>
      </header>

      <div className="container main-content">
        <div className="row">
          {/* Left Column - Upload & Search */}
          <div className="col-lg-4 left-panel">
            
            {/* Alerts */}
            {error && (
              <div className="alert alert-danger alert-dismissible fade show" role="alert">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                {error}
                <button type="button" className="btn-close" onClick={() => setError("")}></button>
              </div>
            )}

            {success && (
              <div className="alert alert-success alert-dismissible fade show" role="alert">
                <i className="bi bi-check-circle-fill me-2"></i>
                {success}
                <button type="button" className="btn-close" onClick={() => setSuccess("")}></button>
              </div>
            )}

            {/* Upload Section */}
            <div className="card panel-card mb-4">
              <div className="card-header">
                <h5 className="card-title mb-0">
                  <i className="bi bi-cloud-upload me-2"></i>
                  Upload Video
                </h5>
              </div>
              <div className="card-body">
                {/* File Upload */}
                <div className="mb-4">
                  <label className="form-label">Upload Video File</label>
                  <input
                    type="file"
                    accept="video/*"
                    className="form-control mb-2"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setVideoFile(file);
                        setVideoURL(URL.createObjectURL(file));
                        setVideoSource("upload");
                        setYoutubeEmbedUrl(""); // Clear YouTube embed
                      }
                    }}
                  />
                  <button
                    onClick={handleUpload}
                    disabled={!videoFile || loading}
                    className="btn btn-primary w-100"
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Processing...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-upload me-2"></i>
                        Upload & Index
                      </>
                    )}
                  </button>
                </div>

                <div className="divider">
                  <span>OR</span>
                </div>

                {/* URL Upload */}
                <div>
                  <label className="form-label">Enter YouTube URL</label>
                  <div className="input-group mb-2">
                    <span className="input-group-text">
                      <i className="bi bi-youtube"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="https://www.youtube.com/watch?v=..."
                      value={youtubeUrl}
                      onChange={(e) => setYoutubeUrl(e.target.value)}
                    />
                  </div>
                  <button
                    onClick={handleUrlUpload}
                    disabled={!youtubeUrl || loading}
                    className="btn btn-danger w-100"
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Processing...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-play-circle me-2"></i>
                        Analyze YouTube
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Search Section */}
            <div className="card panel-card mb-4">
              <div className="card-header">
                <h5 className="card-title mb-0">
                  <i className="bi bi-search me-2"></i>
                  Search Inside Video
                </h5>
              </div>
              <div className="card-body">
                <div className="input-group mb-2">
                  <span className="input-group-text">
                    <i className="bi bi-chat-dots"></i>
                  </span>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="What are you looking for?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                  />
                </div>
                <button
                  onClick={handleSearch}
                  disabled={loading || !videoId}
                  className="btn btn-success w-100"
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Searching...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-search me-2"></i>
                      Search Video
                    </>
                  )}
                </button>
                {videoId && (
                  <small className="text-muted d-block mt-2">
                    <i className="bi bi-info-circle me-1"></i>
                    Searching in current video
                  </small>
                )}
                {!videoId && (
                  <small className="text-muted d-block mt-2">
                    <i className="bi bi-exclamation-circle me-1"></i>
                    Please upload a video first
                  </small>
                )}
              </div>
            </div>

            {/* Results Section */}
            {results.length > 0 && (
              <div className="card panel-card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h5 className="card-title mb-0">
                    <i className="bi bi-list-check me-2"></i>
                    Results
                  </h5>
                  <span className="badge bg-primary">{results.length}</span>
                </div>
                <div className="card-body results-container">
                  {results.map((result, idx) => (
                    <div
                      key={idx}
                      className="result-item"
                      onClick={() => jumpTo(result)}
                    >
                      <div className="result-header">
                        <span className="timestamp">
                          <i className="bi bi-clock me-1"></i>
                          {formatTimestamp(result.timestamp)}
                        </span>
                        <span className={`badge ${result.source === "url" ? "bg-danger" : "bg-primary"}`}>
                          {result.source === "url" ? "YouTube" : "Uploaded"}
                        </span>
                      </div>
                      <p className="result-text">
                        {result.text || "Visual match"}
                      </p>
                      <div className="result-similarity">
                        <div className="progress">
                          <div 
                            className="progress-bar bg-success" 
                            style={{width: `${(100 - result.score)}%`}}
                          >
                            {(100 - result.score).toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Video Player */}
          <div className="col-lg-8 right-panel">
            <div id="video-player-section" className="card video-card">
              <div className="card-header">
                <h5 className="card-title mb-0">
                  <i className="bi bi-play-btn me-2"></i>
                  Video Player
                </h5>
              </div>
              <div className="card-body">
                {/* YouTube Video (iframe) */}
                {youtubeEmbedUrl && videoSource === "url" && (
                  <div className="video-wrapper">
                    <iframe
                      src={youtubeEmbedUrl}
                      title="YouTube video player"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="video-iframe"
                    ></iframe>
                  </div>
                )}

                {/* Uploaded Video */}
                {videoURL && videoSource === "upload" && (
                  <div className="video-wrapper">
                    <video
                      ref={videoRef}
                      src={videoURL}
                      controls
                      className="video-player"
                    />
                  </div>
                )}

                {/* Placeholder */}
                {!videoURL && !youtubeEmbedUrl && (
                  <div className="video-placeholder">
                    <i className="bi bi-camera-video placeholder-icon"></i>
                    <p className="placeholder-text">No video loaded</p>
                    <p className="placeholder-subtext">Upload a video or enter a YouTube URL to get started</p>
                  </div>
                )}

                {/* Video Actions */}
                {videoId && (
                  <div className="video-actions mt-3">
                    <button
                      onClick={downloadNotes}
                      className="btn btn-outline-success"
                    >
                      <i className="bi bi-file-earmark-pdf me-2"></i>
                      Download Notes (PDF)
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Stats/Info Card */}
            {videoId && (
              <div className="card info-card mt-4">
                <div className="card-body">
                  <h6 className="card-subtitle mb-3 text-muted">
                    <i className="bi bi-info-circle me-2"></i>
                    Video Information
                  </h6>
                  <div className="row">
                    <div className="col-md-6 mb-2">
                      <strong>Video ID:</strong>
                      <span className="ms-2 font-monospace text-muted">{videoId}</span>
                    </div>
                    <div className="col-md-6 mb-2">
                      <strong>Source:</strong>
                      <span className="ms-2">
                        {videoSource === "url" ? (
                          <span className="badge bg-danger">YouTube</span>
                        ) : (
                          <span className="badge bg-primary">Uploaded</span>
                        )}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p className="footer-text">
            <i className="bi bi-lightning-charge me-2"></i>
            Powered by Whisper, CLIP, and SentenceTransformers
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
