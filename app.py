from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import tempfile
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        download_type = request.form['type']
        
        if not url:
            flash('Please enter a YouTube URL', 'error')
            return redirect(url_for('index'))
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            if download_type == 'audio':
                # Download as MP3
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                }
            else:
                # Download video (max 1080p)
                ydl_opts = {
                    'format': 'best[height<=1080]',
                    'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                }
            
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