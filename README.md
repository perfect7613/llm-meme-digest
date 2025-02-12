# LLM Research Meme Digest

## Overview
This project is an automated pipeline that fetches recent research papers related to Large Language Models (LLMs) from ArXiv, transforms them into meme-style summaries using AI, and sends a daily email digest with the summarized content. The goal is to make cutting-edge AI research more engaging and accessible.

## Features
- Fetches recent research papers from ArXiv based on predefined search terms.
- Generates meme-style summaries using the Groq AI API.
- Formats and sends an HTML email containing the summaries via Brevo (SendinBlue).
- Ensures required environment variables are set before execution.

## Technologies Used
- **Python** for scripting and automation.
- **ArXiv API** to fetch research papers.
- **Groq API** for AI-generated meme-style summaries.
- **Brevo (SendinBlue) API** for sending email digests.
- **Pydantic** for structured data validation.
- **Dotenv** to manage environment variables.

## Installation
1. **Clone the repository:**
   ```sh
   git clone <repo_url>
   cd <repo_folder>
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the root directory with the following content:
     ```env
     BREVO_API_KEY=your_brevo_api_key
     BREVO_SENDER_EMAIL=your_sender_email
     BREVO_SENDER_NAME=your_sender_name
     BREVO_RECIPIENT_EMAIL=recipient_email
     BREVO_RECIPIENT_NAME=recipient_name
     GROQ_API_KEY=your_groq_api_key
     ```

## Usage
Run the script using:
```sh
python main.py
```
This will:
1. Validate required environment variables.
2. Search ArXiv for relevant papers.
3. Generate meme-style summaries using the Groq API.
4. Format and send an email with the summaries.

## Groq API Integration
The project utilizes the Groq API to generate meme-style summaries of research papers. Here's how the integration works:

1. **Initialization:**
   - The Groq API client is initialized using the `GROQ_API_KEY` from the environment variables.
   - Example:
     ```python
     from groq import Groq
     import os

     client = Groq(api_key=os.getenv("GROQ_API_KEY"))
     ```

2. **Generating Meme Summaries:**
   - For each research paper, a prompt is created combining the paper's title and abstract.
   - The prompt is sent to the Groq API's chat completion endpoint to generate a meme-style summary.
   - Example:
     ```python
     prompt = f"Transform this research paper into a meme explanation:\n\nTitle: {paper.title}\nAbstract: {paper.abstract}\n\nProvide a meme-style summary."
     response = client.chat.completions.create(
         model="llama-3.3-70b-versatile",
         messages=[{"role": "user", "content": prompt}]
     )
     meme_summary = response.choices[0].message.content
     ```

3. **Supported Models:**
   - The project uses the `llama-3.3-70b-versatile` model from Groq for generating summaries.
   - For a list of available models, refer to the [Groq Models Documentation](https://console.groq.com/docs/models).


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your proposal.

## License
This project is open-source and available under the [MIT License](LICENSE).

For more detailed information on the Groq API, please refer to the [Groq API Documentation](https://console.groq.com/docs/api-reference). 