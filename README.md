# Job Tracker with AI Integration

A comprehensive job search and application management tool built with Flask, featuring AI-powered CV customization and cover letter generation using Anthropic Claude.

## Features

### 📋 Job Management
- **Kanban Board Interface**: Visual job tracking with drag-and-drop functionality
- **Job Status Pipeline**: Saved → Applied → Interview → Offered
- **Job Details**: Store job URLs, titles, companies, descriptions, locations, and salary ranges
- **Auto-fill Job Details**: Scrape job information from job posting URLs

### 🤖 AI-Powered Features
- **CV Customization**: Automatically tailor your CV to specific job descriptions using Claude AI
- **Cover Letter Generation**: Create personalized cover letters based on your CV and job requirements
- **Company Research**: Generate comprehensive company insights for interview preparation

### 📄 Document Management
- **CV Upload**: Support for PDF, TXT, DOC, and DOCX files
- **Text Extraction**: Automatic text extraction from uploaded documents
- **CV Selection**: Easy dropdown selection from previously uploaded CVs

### 🔍 Job Search
- **Job Scraping**: Integration with JobSpy for Indeed job searches
- **Search Results**: Browse and save jobs directly from search results
- **URL Support**: Manual job URL input with validation

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI**: Anthropic Claude 3 Haiku API
- **Job Scraping**: JobSpy, BeautifulSoup4
- **Document Processing**: PyPDF2, python-docx
- **Frontend**: Bootstrap 5, jQuery UI
- **Deployment**: Python Flask development server

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iwatts3519/jobtracker.git
   cd jobtracker
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser to `http://localhost:5000`

## Configuration

### Required Environment Variables
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key for AI features
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (optional, uses default for development)

### API Key Setup
1. Sign up for an Anthropic account at https://console.anthropic.com/
2. Generate an API key
3. Add it to your `.env` file as `ANTHROPIC_API_KEY=your_key_here`

## Usage

### Adding Jobs
1. Click "Add Job" to manually enter job details
2. Use "Job Search" to find and save jobs from Indeed
3. Paste job URLs for automatic detail extraction

### Managing Applications
- Drag and drop jobs between status columns
- Click on any job to view details and access AI features
- Update job status with the dropdown menu

### AI Features
- **Customize CV**: Select an uploaded CV and let AI tailor it to the job description
- **Generate Cover Letter**: Create personalized cover letters with your name and CV details
- **Research Company**: Get comprehensive company insights for interview preparation

### Document Management
- Upload CVs in the CV Customizer section
- Previously uploaded CVs appear in dropdown menus for easy selection
- Generated documents are automatically saved

## Project Structure

```
jobtracker/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── services/             # Business logic services
│   ├── ai_service.py     # Anthropic Claude integration
│   ├── cv_processor.py   # Document processing
│   └── job_scraper.py    # Job scraping functionality
├── static/               # Static assets
│   ├── css/style.css     # Custom styles
│   ├── js/               # JavaScript files
│   └── uploads/          # Uploaded files directory
└── templates/            # Jinja2 templates
    ├── base.html         # Base template
    ├── index.html        # Dashboard/kanban board
    ├── job_detail.html   # Job details and AI features
    └── ...               # Other templates
```

## Development Phases

- **Phase 1**: Core job tracking with kanban interface ✅
- **Phase 2**: AI integration with Anthropic Claude ✅
- **Phase 3**: Advanced features and enhancements (planned)

## Contributing

1. Create a new branch for each feature/phase
2. Follow the existing code structure and conventions
3. Test AI features with a valid Anthropic API key
4. Submit pull requests to the main branch

## License

This project is for personal use and learning purposes.

## Support

For issues and questions, please check the project documentation or create an issue in the GitHub repository.