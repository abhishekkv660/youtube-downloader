from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import tempfile
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Path to your cookies.txt (uploaded securely in Render)
COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        download_type = request.form.get('type')
        
        if not url:
            flash('Please enter a YouTube URL', 'error')
            return redirect(url_for('index'))
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()

            # Common yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'cookiefile': COOKIE_FILE if os.path.exists(COOKIE_FILE) else None,
                'quiet': False,  # Show logs in Render
            }

            if download_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                ydl_opts.update({
                    'format': 'best[height<=1080]',
                })
            
            # Download the file
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            files = list(Path(temp_dir).glob('*'))
            if files:
                downloaded_file = files[0]
                return send_file(
                    downloaded_file, 
                    as_attachment=True, 
                    download_name=downloaded_file.name
                )
            else:
                flash('Download failed - no file created', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
