#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# ExamGuard AI — Dev Environment Setup Script
# ────────────────────────────────────────────────────────────────
set -e

echo "🛡️  ExamGuard AI — Setting up development environment"
echo "──────────────────────────────────────────────────────"

# 1. Copy env file if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from .env.example — please edit it with your API keys"
else
    echo "ℹ️  .env already exists, skipping"
fi

# 2. Python virtual environments for each agent
for service in backend vision_agent reasoning_agent action_agent; do
    echo ""
    echo "📦 Setting up $service..."
    cd "$service"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    deactivate
    cd ..
done

# 3. Dashboard dependencies
echo ""
echo "📦 Setting up dashboard (Node.js)..."
cd dashboard
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your OPENAI_API_KEY or GROQ_API_KEY"
echo "  2. Run 'docker-compose up --build' for full stack"
echo "  3. Or run services individually — see README.md"
