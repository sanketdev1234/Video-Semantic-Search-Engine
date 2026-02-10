const API_BASE = "http://127.0.0.1:8000";

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || `Upload failed with status ${res.status}`);
  }
  return res.json();
}

export async function uploadVideoUrl(url) {
  const res = await fetch(`${API_BASE}/upload-url`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || `URL upload failed with status ${res.status}`);
  }
  return res.json();
}

export async function searchVideo(query, videoId = null) {
  let url = `${API_BASE}/search?query=${encodeURIComponent(query)}`;
  if (videoId) {
    url += `&video_id=${videoId}`;
  }

  const res = await fetch(url);

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Search failed");
  }
  return res.json();
}

export async function getVideoInfo(videoId) {
  const res = await fetch(`${API_BASE}/video/${videoId}`);
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Failed to fetch video info");
  }
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/stats`);
  
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}
