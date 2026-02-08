const API_BASE = "http://127.0.0.1:8000";

export async function uploadVideo(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function searchVideo(query) {
  const res = await fetch(
    `${API_BASE}/search?query=${encodeURIComponent(query)}`
  );

  if (!res.ok) throw new Error("Search failed");
  return res.json();
}
