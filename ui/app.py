from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('audio_files', filename)

if __name__ == '__main__':
    app.run(debug=True)
