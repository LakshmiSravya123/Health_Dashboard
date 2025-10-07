#!/bin/bash
# Simple installation script for Mental Health Dashboard

echo "🏥 Mental Health Dashboard - Installation Script"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install core dependencies first
echo ""
echo "📦 Installing core dependencies..."
pip install numpy pandas

# Install ML/NLP packages
echo ""
echo "🧠 Installing ML and NLP packages..."
pip install scikit-learn transformers torch nltk spacy statsmodels

# Install dashboard packages
echo ""
echo "📊 Installing dashboard packages..."
pip install plotly dash dash-bootstrap-components

# Install utilities
echo ""
echo "🔧 Installing utilities..."
pip install loguru python-dotenv pyyaml tqdm joblib requests pytest pytest-cov

# Download spaCy model
echo ""
echo "📥 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Generate sample data: python scripts/generate_sample_data.py"
echo "2. Run pipeline: python scripts/run_full_pipeline.py"
echo "3. Launch dashboard: python src/dashboard/app.py"
echo "4. Open browser: http://localhost:8050"
