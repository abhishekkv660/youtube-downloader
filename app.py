from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import tempfile
from pathlib import Path

app = Flask(__name__)
# IMPORTANT: Change this to a random secret key
app.secret_key = 'a-very-random-and-secret-string'

# --- ADD THIS ---
# A common User-Agent to make requests look like they're from a browser
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
# ---------------

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        download_type = request.form['type']
        
        if not url:
            flash('Please enter a YouTube URL', 'error')
            return redirect(url_for('index'))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                if download_type == 'audio':
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'http_headers': COMMON_HEADERS # --- ADD THIS LINE ---
                    }
                else:
                    ydl_opts = {
                        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                        'http_headers': COMMON_HEADERS # --- ADD THIS LINE ---
                    }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                files = list(Path(temp_dir).glob('*'))
                if files:
                    downloaded_file = files[0]
                    return send_file(
                        downloaded_file, 
                        as_attachment=True,
                        download_name=downloaded_file.name
                    )
                else:
                    flash('Download failed. The video might be private or region-locked.', 'error')
                    
            except yt_dlp.utils.DownloadError as e:
                flash('Download Error: This video may not be available. Age-restricted videos often fail.', 'error')
            except Exception as e:
                flash(f'An unexpected error occurred.', 'error')
        
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)