def format_transcript(segments):
    lines = []
    for seg in segments:
        ts = int(seg["start"])
        minutes = ts // 60
        seconds = ts % 60
        lines.append(f"[{minutes:02}:{seconds:02}] {seg['text']}")
    return lines
