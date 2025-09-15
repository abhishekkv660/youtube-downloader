from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import yt_dlp
import os
import tempfile
from pathlib import Path

app = Flask(__name__)
# IMPORTANT: Change this to a random secret key
app.secret_key = 'a-very-random-and-secret-string'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        download_type = request.form['type']
        
        if not url:
            flash('Please enter a YouTube URL', 'error')
            return redirect(url_for('index'))
        
        # Use a temporary directory that is automatically cleaned up
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                if download_type == 'audio':
                    # Download as MP3 (audio only)
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
                    # Download video (MP4, max 1080p)
                    ydl_opts = {
                        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    }
                
                # Download the file
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Find the downloaded file
                files = list(Path(temp_dir).glob('*'))
                if files:
                    downloaded_file = files[0]
                    # Send the file and then it will be deleted when the 'with' block exits
                    return send_file(
                        downloaded_file, 
                        as_attachment=True,
                        download_name=downloaded_file.name
                    )
                else:
                    flash('Download failed. The video might be private or region-locked.', 'error')
                    
            except yt_dlp.utils.DownloadError as e:
                # Handle specific download errors gracefully
                flash('Download Error: This video may not be available for download.', 'error')
            except Exception as e:
                flash(f'An unexpected error occurred: {str(e)}', 'error')
        
        # Redirect back to the index if anything goes wrong
        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)