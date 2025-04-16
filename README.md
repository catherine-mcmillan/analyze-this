# Analyze This - CSV Data Analysis Assistant

Analyze This is a web application that simplifies data analysis for users working with CSV files. The app allows you to upload CSV files, annotate columns with contextual information, craft analysis prompts with guided suggestions, and generate comprehensive analytical reports using Anthropic's Claude AI models.

![Dashboard Screenshot](docs/images/dashboard.png)

## Features

- **CSV Parsing and Annotation**: Upload CSV files and provide context for each column
- **AI-Powered Analysis**: Generate detailed analysis reports using Claude AI models
- **Prompt Engineering**: Get help crafting effective analysis prompts
- **Visualization Recommendations**: Receive suggestions for the most effective ways to visualize your data
- **Report Editing**: Edit and customize AI-generated reports
- **Export Options**: Download reports in Markdown, PDF, or extract data tables as CSV files
- **User Management**: Create an account to save and manage your analyses

## Installation

### Prerequisites

- Python 3.9+
- Conda (recommended for environment management)
- Anthropic API key for Claude models

### Setting up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/analyze-this.git
   cd analyze-this
   ```

2. Create and activate a conda environment:
   ```bash
   conda create -n analyze_this python=3.9
   conda activate analyze_this
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   CLAUDE_MODEL=claude-3-opus-20240229
   ```

5. Set up the database:
   ```bash
   flask db upgrade
   ```

6. Run the development server:
   ```bash
   flask run
   ```

7. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

### Uploading Data

1. Sign in to your account
2. Click "New Analysis" in the navigation bar
3. Provide an analysis title and upload your CSV file

### Column Annotation

1. Review the sample data displayed
2. Provide descriptions for each column to help the AI understand your data
3. Add optional source information and notes

### Creating Analysis Prompt

1. Write your analysis goal or question
2. Use the suggested templates as a starting point if needed
3. Click "Generate Enhanced Prompt" to create an AI-ready prompt

### Reviewing and Generating Report

1. Review and edit the enhanced prompt if needed
2. Click "Generate Analysis Report" to have Claude analyze your data
3. The AI will create a comprehensive analysis based on your data and prompt

### Editing and Exporting

1. Use the report editor to make any necessary changes
2. Export your report in your preferred format
3. Access your saved analyses anytime from the "History" page

## Development

### Project Structure

```
analyze_this/
├── app/                  # Application package
│   ├── routes/           # Route definitions
│   ├── static/           # Static assets
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
├── migrations/           # Database migrations
├── tests/                # Test suite
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point
```

### Running Tests

```bash
pytest
```

### Adding New Features

1. Create a new branch for your feature
2. Implement your changes
3. Write tests for new functionality
4. Submit a pull request

## Deployment

The application is configured for deployment on Fly.io:

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Log in to Fly.io
flyctl auth login

# Deploy the application
flyctl deploy
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Flask web framework
- Powered by Anthropic's Claude AI models
- Bootstrap for responsive frontend design