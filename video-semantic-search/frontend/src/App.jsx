import { useRef, useState } from "react";
import { uploadVideo, uploadVideoUrl, searchVideo } from "./services/api";

function App() {
  const videoRef = useRef(null);
  const youtubeWindowRef = useRef(null);

  // Video state
  const [videoId, setVideoId] = useState(null);
  const [videoFile, setVideoFile] = useState(null);
  const [videoURL, setVideoURL] = useState("");
  const [videoSource, setVideoSource] = useState(""); // "upload" or "url"
  const [youtubeUrl, setYoutubeUrl] = useState("");

  // Search state
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle file upload
  const handleUpload = async () => {
    if (!videoFile) {
      setError("Please select a video file");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      const res = await uploadVideo(videoFile);
      console.log("Upload response:", res);
      
      setVideoId(res.video_id);
      setVideoSource("upload");
      setError("");
      alert("✅ Video uploaded and indexed successfully!");
      
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Upload failed: ${err.message}`);
      alert(`❌ Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle URL upload (YouTube)
  const handleUrlUpload = async () => {
    if (!youtubeUrl || !youtubeUrl.trim()) {
      setError("Please enter a YouTube URL");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      console.log("Uploading URL:", youtubeUrl);
      const res = await uploadVideoUrl(youtubeUrl);
      console.log("URL upload response:", res);
      
      setVideoId(res.video_id);
      setVideoSource("url");
      setVideoURL("");
      setError("");
      
      // Open YouTube in small window
      openYoutubeWindow(youtubeUrl);
      
      alert("✅ YouTube video processed successfully!");
      
    } catch (err) {
      console.error("URL upload error:", err);
      setError(`URL processing failed: ${err.message}`);
      alert(`❌ URL processing failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Open YouTube in small window
  const openYoutubeWindow = (url) => {
    const width = 640;
    const height = 480;
    const left = window.screen.width - width - 20;
    const top = 100;
    
    if (youtubeWindowRef.current && !youtubeWindowRef.current.closed) {
      youtubeWindowRef.current.close();
    }
    
    youtubeWindowRef.current = window.open(
      url,
      "YouTubePlayer",
      `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
    );
  };

  // Handle search
  const handleSearch = async () => {
    if (!query || !query.trim()) {
      setError("Please enter a search query");
      return;
    }

    setLoading(true);
    setError("");
    
    try {
      // Search within current video if one is loaded
      const data = await searchVideo(query, videoId);
      console.log("Search results:", data);
      
      setResults(data.results || []);
      
      if (data.results.length === 0) {
        setError("No results found");
      }
      
    } catch (err) {
      console.error("Search error:", err);
      setError(`Search failed: ${err.message}`);
      alert(`❌ Search failed: ${err.message}`);
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
    }
    // CASE 2: URL video (YouTube) → open with timestamp
    else if (result.source === "url" && result.deep_link) {
      openYoutubeWindow(result.deep_link);
    }
  };

  // Download PDF notes
  const downloadNotes = () => {
    if (!videoId) {
      alert("Please upload a video first");
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
            🎥 Video Semantic Search Engine
          </h1>
          <p className="text-gray-400">
            Upload videos or YouTube links, then search inside them using AI
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-200">⚠️ {error}</p>
          </div>
        )}

        {/* Upload Section */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-6 backdrop-blur-sm border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">📤 Upload Video</h2>
          
          {/* File Upload */}
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">
              Upload Video File
            </label>
            <div className="flex gap-2">
              <input
                type="file"
                accept="video/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    setVideoFile(file);
                    setVideoURL(URL.createObjectURL(file));
                    setVideoSource("upload");
                  }
                }}
                className="flex-1 bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
              />
              <button
                onClick={handleUpload}
                disabled={!videoFile || loading}
                className="bg-blue-600 px-6 py-2 rounded hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Processing..." : "Upload & Index"}
              </button>
            </div>
          </div>

          {/* URL Upload */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">
              Or Enter YouTube URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="https://www.youtube.com/watch?v=..."
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                className="flex-1 bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={handleUrlUpload}
                disabled={!youtubeUrl || loading}
                className="bg-purple-600 px-6 py-2 rounded hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "Processing..." : "Analyze URL"}
              </button>
            </div>
          </div>
        </div>

        {/* Video Player (for uploaded videos) */}
        {videoURL && videoSource === "upload" && (
          <div className="bg-gray-800/50 rounded-lg p-6 mb-6 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">🎬 Video Player</h2>
            <video
              ref={videoRef}
              src={videoURL}
              controls
              className="w-full max-w-3xl mx-auto rounded-lg shadow-2xl"
            />
            <div className="mt-4 text-center">
              <button
                onClick={downloadNotes}
                className="bg-green-600 px-6 py-2 rounded hover:bg-green-700 transition-colors"
              >
                📄 Download Notes (PDF)
              </button>
            </div>
          </div>
        )}

        {/* YouTube indicator */}
        {videoSource === "url" && (
          <div className="bg-gray-800/50 rounded-lg p-6 mb-6 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-semibold mb-2">📺 YouTube Video</h2>
            <p className="text-gray-400">
              YouTube video is being processed. Search results will open in a small window.
            </p>
          </div>
        )}

        {/* Search Section */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-6 backdrop-blur-sm border border-gray-700">
          <h2 className="text-xl font-semibold mb-4">🔍 Search Inside Video</h2>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="e.g., What is machine learning?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              className="flex-1 bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 focus:outline-none focus:border-green-500"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="bg-green-600 px-6 py-2 rounded hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
          {videoId && (
            <p className="text-sm text-gray-400 mt-2">
              Searching in current video
            </p>
          )}
        </div>

        {/* Results Section */}
        {results.length > 0 && (
          <div className="bg-gray-800/50 rounded-lg p-6 backdrop-blur-sm border border-gray-700">
            <h2 className="text-xl font-semibold mb-4">
              📋 Results ({results.length})
            </h2>
            <div className="space-y-3">
              {results.map((result, idx) => (
                <div
                  key={idx}
                  className="bg-gray-700/50 p-4 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors border border-gray-600 hover:border-blue-500"
                  onClick={() => jumpTo(result)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-blue-400 font-mono text-sm">
                      ⏱ {formatTimestamp(result.timestamp)}
                    </span>
                    <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                      {result.source === "url" ? "YouTube" : "Uploaded"}
                    </span>
                  </div>
                  <p className="text-gray-200">
                    {result.text || "Visual match"}
                  </p>
                  <div className="mt-2 text-xs text-gray-500">
                    Similarity: {(100 - result.score).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-400">Processing...</p>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-gray-500 text-sm mt-12 pb-6">
          <p>Powered by Whisper, CLIP, and SentenceTransformers</p>
        </div>
      </div>
    </div>
  );
}

export default App;
