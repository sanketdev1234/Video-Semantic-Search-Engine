import { useRef, useState } from "react";
import { uploadVideo, searchVideo } from "./services/api";

function App() {
  const videoRef = useRef(null);

  const [videoFile, setVideoFile] = useState(null);
  const [videoURL, setVideoURL] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!videoFile) return;

    setLoading(true);
    try {
      await uploadVideo(videoFile);
      alert("Video uploaded and indexed!");
    } catch (err) {
      alert("Upload failed");
    }
    setLoading(false);
  };

  const handleSearch = async () => {
    if (!query) return;

    setLoading(true);
    try {
      const data = await searchVideo(query);
      setResults(data.results);
    } catch (err) {
      alert("Search failed");
    }
    setLoading(false);
  };

  const jumpTo = (timestamp) => {
    if (!videoRef.current) return;
    videoRef.current.currentTime = timestamp;
    videoRef.current.play();
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-6">
        🎥 Video Semantic Search Engine
      </h1>

      {/* Upload */}
      <div className="mb-4">
        <input
          type="file"
          accept="video/*"
          onChange={(e) => {
            setVideoFile(e.target.files[0]);
            setVideoURL(URL.createObjectURL(e.target.files[0]));
          }}
          className="mb-2"
        />
        <br />
        <button
          onClick={handleUpload}
          className="bg-blue-600 px-4 py-2 rounded"
        >
          Upload & Index
        </button>
      </div>

      {/* Video Player */}
      {videoURL && (
        <video
          ref={videoRef}
          src={videoURL}
          controls
          className="w-full max-w-3xl mb-6"
        />
      )}

      {/* Search */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search inside the video (e.g. stock market)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="text-black px-3 py-2 w-64 rounded mr-2"
        />
        <button
          onClick={handleSearch}
          className="bg-green-600 px-4 py-2 rounded"
        >
          Search
        </button>
      </div>

      {/* Results */}
      <div>
        {results.map((r, idx) => (
          <div
            key={idx}
            className="bg-gray-800 p-3 rounded mb-2 cursor-pointer hover:bg-gray-700"
            onClick={() => jumpTo(r.timestamp)}
          >
            <p className="text-sm text-gray-300">
              ⏱ {r.timestamp.toFixed(2)} sec
            </p>
            <p>{r.text || "Visual match"}</p>
          </div>
        ))}
      </div>

      {loading && <p className="mt-4">Processing...</p>}
    </div>
  );
}

export default App;
