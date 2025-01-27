import os
import streamlit as st
import requests
import base64
from typing import Optional
import json
import anthropic
import base64

key = os.environ.get('ANTHROPIC_KEY')
st.write(f"API KEY: {key}")
client = anthropic.Anthropic(
    api_key=os.environ.get('ANTHROPIC_KEY'),
)

def count_tokens(params):
    response = client.messages.count_tokens(
		**params
	)
    return json.loads(response.json())['input_tokens']

def make_api_call(params, max_tokens=8192) -> Optional[str]:
    """
    Make API call with the uploaded file and return the response.
    Modify this function to match your API's requirements.
    """
    try:
        response = client.messages.create(
			max_tokens=max_tokens,
            **params
		)

        return response.content[0].text
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error making API call: {str(e)}")
        return None

def get_download_link(text: str, filename: str) -> str:
    """
    Generate a download link for the text content
    """
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}">Download Response</a>'

def main():
	st.title("RAF AI Transcription")

	# Add description
	st.write("""
	Upload a file to process through the API and download the results.
	""")

	# File uploader
	uploaded_file = st.file_uploader("Choose a file", type=["jpg"])  # Modify file types as needed

	if uploaded_file is not None:
        # Read file content
		file_content = uploaded_file.read()
		file = {
			"type": "image",
			"source": {
				"type": "base64",
				"media_type": "image/jpeg",
				"data": base64.standard_b64encode(file_content).decode("utf-8"),
			},
		}
		params = {
			"model": "claude-3-5-sonnet-20241022",
			"system": """You are a document transcription expert, you are able to follow detailed guidelines and rules about transcription.""",
			"messages": [
				{
					"role": "user",
					"content": [
						file,
						{
							"type": "text",
							"text": """Transcribe this ENTIRE document. You must follow these guidelines exactly:
							
							TRANSCRIPTION GUIDELINES:
							General Formatting:
							- Use default MS Word font (like Calibri) in size 11
							- Left-align all text
							- Leave one space after periods
							- Use line breaks between paragraphs
							- Don't try to reproduce original layout, margins, or indents
							- Maintain original spelling, capitalization, and punctuation, even if incorrect

							Special Markups:
							- Use [sic] after incorrect spellings (not grammar)
							- Use [deleted] and [/deleted] for crossed-out but readable text
							- Use [indecipherable word/s] for unreadable text
							- Use [underlined] and [/underlined] for underlined text
							- Use [inserted] and [/inserted] for added text
							- Use [page break] to indicate new pages
							- Use [signature] for unreadable signatures
							- Use [censored] for deliberately censored content
							- Use [missing word/s] for damaged/missing text
							- Use [blank] or [blank page] for empty spaces
							- Use [calculations], [list of payments] etc. for casual notes

							Document Elements:
							- Transcribe dates exactly as written
							- Ignore differences between pen/pencil/ink colors
							- Include accent marks in non-English words
							- Write fractions with forward slash (e.g., 1/3)
							- Use capitals for Roman numerals without formatting
							- Only transcribe printed elements if needed for context
							- Briefly describe diagrams/charts/pictures in brackets
							- Note crests/logos but don't describe them in detail
							- Transcribe photo captions and accompanying text

							Reviewing Process:
							- Check carefully against original
							- Watch for modernization of old writing styles
							- Verify correct spelling markup usage
							- Check punctuation and paragraph breaks
							- Review section by section
							- Read aloud to catch errors
							- Final proofreading by coordinator before archiving

							The overall emphasis is on accurate transcription while maintaining searchability and readability, with consistent markup conventions to preserve important document features.

							Output ONLY the transcription, no explanation is required."""
						}
					],
				}
			]
		}
		
		cost_per_million_tokens = 3
		# Show file details
		st.write("File details:")
		st.write(f"Filename: {uploaded_file.name}")
		st.write(f"Input cost: ${round(count_tokens(params) / 1000000 * cost_per_million_tokens, 4)}")
		
		# Process button
		if st.button("Process File"):
			with st.spinner("Processing file..."):
				
				
				# Make API call
				response_text = make_api_call(params)
				
				if response_text:
					# Show preview of the response
					st.write("### Response Preview:")
					st.text_area("Response", response_text,
								height=200)
					
					# Create download link
					download_filename = f"processed_{uploaded_file.name.rsplit('.', 1)[0]}.txt"
					st.markdown(get_download_link(response_text, download_filename), unsafe_allow_html=True)
					
					# Add success message
					st.success("Processing complete! Click the link above to download the results.")

if __name__ == "__main__":
    main()