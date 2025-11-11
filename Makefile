# Workplace Safety Monitoring Application - Makefile
# For use with GNU Make (available via Git Bash, WSL, or MinGW on Windows)

.PHONY: help install setup init check run run-backend run-frontend stop clean test

# Default target
help:
	@echo "Workplace Safety Monitoring - Available Commands"
	@echo "================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make setup      - Setup environment files"
	@echo "  make init       - Initialize database"
	@echo "  make check      - Verify setup"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run        - Start both backend and frontend"
	@echo "  make run-backend - Start backend only"
	@echo "  make run-frontend - Start frontend only"
	@echo "  make stop       - Stop all running services"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean      - Clean generated files"
	@echo "  make test       - Run tests"
	@echo ""

# Install all dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	pip install -r backend/requirements.txt
	@echo ""
	@echo "Installing frontend dependencies..."
	cd frontend && npm install --legacy-peer-deps
	@echo ""
	@echo "✓ All dependencies installed!"

# Setup environment files
setup:
	@echo "Setting up environment files..."
	@if [ ! -f backend/.env ]; then \
		cp backend/.env.example backend/.env 2>/dev/null || echo "Warning: backend/.env.example not found"; \
		echo "✓ Created backend/.env"; \
	else \
		echo "✓ backend/.env already exists"; \
	fi
	@if [ ! -f frontend/.env ]; then \
		cp frontend/.env.example frontend/.env 2>/dev/null || echo "Warning: frontend/.env.example not found"; \
		echo "✓ Created frontend/.env"; \
	else \
		echo "✓ frontend/.env already exists"; \
	fi
	@echo ""
	@echo "⚠️  Remember to configure:"
	@echo "  - backend/.env: Add SMTP credentials"
	@echo "  - frontend/.env: Add Google Client ID"

# Initialize database
init:
	@echo "Initializing database..."
	python setup_database.py
	@echo "✓ Database initialized!"

# Check setup
check:
	@echo "Checking setup..."
	python check_setup.py

# Run both backend and frontend
run:
	@echo "Starting Workplace Safety Monitoring Application..."
	@echo ""
	@echo "Backend will run on: http://localhost:8000"
	@echo "Frontend will run on: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop"
	@echo ""
	@$(MAKE) -j2 run-backend run-frontend

# Run backend only
run-backend:
	@echo "Starting backend..."
	python start_backend.py

# Run frontend only
run-frontend:
	@echo "Starting frontend..."
	cd frontend && npm run dev

# Stop all services
stop:
	@echo "Stopping services..."
	@-pkill -f "start_backend.py" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
	@echo "✓ Services stopped"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf backend/__pycache__
	rm -rf backend/uploads/*
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -f backend/workplace_safety.db
	@echo "✓ Cleaned!"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v
	@echo "✓ Tests complete!"

# Full setup from scratch
full-setup: install setup init check
	@echo ""
	@echo "================================================="
	@echo "✓ Full setup complete!"
	@echo "================================================="
	@echo ""
	@echo "Next steps:"
	@echo "1. Configure backend/.env with SMTP credentials"
	@echo "2. Configure frontend/.env with Google Client ID"
	@echo "3. Run: make run"

