import tkinter as tk
from tkinter import filedialog
import subprocess
import whisper
import csv
import os
import sys
from urllib.parse import urlparse, parse_qs

# ✅ Ensure proper paths in bundled PyInstaller app
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# YouTube URL extractor
def extract_youtube_id(url):
    parsed = urlparse(url)
    if parsed.hostname in ["www.youtube.com", "youtube.com"]:
        return parse_qs(parsed.query).get("v", [None])[0]
    elif parsed.hostname == "youtu.be":
        return parsed.path[1:]
    return None

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def browse_file():
    filepath = filedialog.askopenfilename()
    if filepath:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filepath)

def start_analysis():
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "🟢 Starting keyword search...\n")
    print("🟢 GUI Triggered")

    url = url_entry.get().strip()
    audio_path = file_entry.get().strip()
    raw_keywords = keyword_entry.get().strip()
    if not url or not audio_path or not raw_keywords:
        output_box.insert(tk.END, "❌ Please fill in all fields.\n")
        return

    youtube_id = extract_youtube_id(url)
    if not youtube_id:
        output_box.insert(tk.END, "❌ Invalid YouTube URL.\n")
        return

    keywords = [kw.strip().lower() for kw in raw_keywords.split(",") if kw.strip()]
    model = whisper.load_model("base")

    try:
        result = model.transcribe(audio_path, word_timestamps=True, verbose=True)
    except Exception as e:
        output_box.insert(tk.END, f"❌ Error: {e}\n")
        return

    matches = []
    matched_keywords = set()

    for segment in result["segments"]:
        segment_text = segment["text"].lower()
        for kw in keywords:
            if kw in segment_text:
                matched_keywords.add(kw)
                start = format_time(segment["start"])
                end = format_time(segment["end"])
                raw_seconds = int(segment["start"])
                link = f"https://www.youtube.com/watch?v={youtube_id}&t={raw_seconds}s"
                snippet = segment["text"].strip()
                matches.append({
                    "keyword": kw,
                    "start": start,
                    "end": end,
                    "link": link,
                    "snippet": snippet
                })

    matches.sort(key=lambda x: x["keyword"])
    unmatched = sorted(set(keywords) - matched_keywords)

    csv_file = "keyword_timestamps.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword", "start", "end", "link", "snippet"])
        writer.writeheader()
        writer.writerows(matches)

    if unmatched:
        with open("keywords_not_found.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["unmatched_keywords"])
            for kw in unmatched:
                writer.writerow([kw])

    try:
        subprocess.run(["open", csv_file])
    except Exception as e:
        print("⚠️ Could not auto-open:", e)

    output_box.insert(tk.END, "\n✅ DONE! Check terminal and CSV output.\n")
    for m in matches:
        output_box.insert(tk.END, f"\n🔑 {m['keyword']} [{m['start']}–{m['end']}]\n🔗 {m['link']}\n📝 {m['snippet']}\n")

    if unmatched:
        output_box.insert(tk.END, "\n❌ Keywords not found:\n")
        for kw in unmatched:
            output_box.insert(tk.END, f"  - {kw}\n")

def run_gui():
    global url_entry, file_entry, keyword_entry, output_box

    root = tk.Tk()
    root.title("M2 - Audio Intelligence")
    root.configure(bg="black")
    root.geometry("960x600")

    font = ("Courier New", 12, "bold")
    label_opts = {"bg": "black", "fg": "white", "font": font}
    entry_opts = {"bg": "black", "fg": "lime", "insertbackground": "white", "font": font, "bd": 1}

    tk.Label(root, text="YouTube URL:", **label_opts).pack(anchor="w")
    url_entry = tk.Entry(root, **entry_opts, width=120)
    url_entry.pack(fill="x")

    tk.Label(root, text="Audio File:", **label_opts).pack(anchor="w")
    file_frame = tk.Frame(root, bg="black")
    file_entry = tk.Entry(file_frame, **entry_opts, width=110)
    file_entry.pack(side="left", fill="x", expand=True)
    tk.Button(file_frame, text="Browse", command=browse_file, bg="white", fg="green").pack(side="right")
    file_frame.pack(fill="x")

    tk.Label(root, text="Keywords (comma-separated):", **label_opts).pack(anchor="w")
    keyword_entry = tk.Entry(root, **entry_opts, width=120)
    keyword_entry.pack(fill="x")

    tk.Button(root, text="PRINT", command=start_analysis, font=("Courier", 14, "bold"), bg="white", fg="black").pack(pady=8)

    output_box = tk.Text(root, bg="black", fg="lime", font=("Courier", 12), height=18, insertbackground="white")
    output_box.pack(fill="both", expand=True, padx=6)

    signature = tk.Label(root, text="(M2000 - M2 1.0)", fg="gray", bg="black", anchor="e", font=("Courier", 10))
    signature.pack(anchor="se", padx=10, pady=4)

    root.mainloop()

if __name__ == "__main__":
    run_gui()
