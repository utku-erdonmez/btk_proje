import my_gemini_model 
import process_video
from flask import Flask, render_template, request
import markdown

app = Flask(__name__)

# --
@app.route('/')
def home():
    return render_template('index.html')
#--
@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    video_url = request.form.get('url')  # Get the video URL entered by the user from the form submission
    text =  process_video.process_video(video_url)  # Process the video to extract text using the process_video module
    markdown_output =  my_gemini_model.process_text(text)  # Process the extracted text with the Gemini model to convert it to markdown format
    html_content = markdown.markdown(markdown_output)  # Convert the markdown output to HTML for rendering

    # Modify the video URL for embedding in an iframe
    video_url = video_url.replace("watch?v=", "embed/")  
    return render_template("output.html", test=html_content, url=video_url)

# --
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  
