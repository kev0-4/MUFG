#!/bin/bash

#---------- UNTESTED WITH UPDATES-----------
# FinGuard Servers Initialization Script
# Initializes and runs Financial Server (port 8001), NLP Server (port 8000), and AI Analytics Server (port 8002)
# Usage: ./start_finguard_servers.sh [start|stop]

# Configuration
FINANCIAL_DIR="financial-server"
NLP_DIR="server_4_nlp"
ANALYTICS_DIR="server_5_analytics"
FINANCIAL_VENV="$FINANCIAL_DIR/finance_venv"
NLP_VENV="$NLP_DIR/nlp_venv"
ANALYTICS_VENV="$ANALYTICS_DIR/analytics_venv"
FINANCIAL_PORT=8001
NLP_PORT=8000
ANALYTICS_PORT=8002
FINANCIAL_SERVER_URL="http://localhost:8001"
NLP_SERVER_URL="http://localhost:8000"
REDIS_PASSWORD="your_redis_password"  # Replace with actual Redis password
LOG_DIR="logs"
FINANCIAL_PID_FILE="$LOG_DIR/financial_server.pid"
NLP_PID_FILE="$LOG_DIR/nlp_server.pid"
ANALYTICS_PID_FILE="$LOG_DIR/analytics_server.pid"

# Check for Python 3.11
check_python() {
    if ! command -v python3.11 &> /dev/null; then
        echo "Error: Python 3.11 is required but not installed."
        exit 1
    fi
}

# Create logs directory
setup_logs() {
    mkdir -p "$LOG_DIR"
    touch "$LOG_DIR/financial_server.log"
    touch "$LOG_DIR/nlp_server.log"
    touch "$LOG_DIR/analytics_server.log"
}

# Set up Financial Server
setup_financial_server() {
    echo "Setting up Financial Server in $FINANCIAL_DIR..."
    if [ ! -d "$FINANCIAL_DIR" ]; then
        echo "Error: Directory $FINANCIAL_DIR not found."
        exit 1
    fi

    # Create virtual environment
    if [ ! -d "$FINANCIAL_VENV" ]; then
        python3.11 -m venv "$FINANCIAL_VENV"
    fi

    # Activate virtual environment and install dependencies
    source "$FINANCIAL_VENV/bin/activate"
    if [ -f "$FINANCIAL_DIR/requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r "$FINANCIAL_DIR/requirements.txt"
    else
        echo "Error: requirements.txt not found in $FINANCIAL_DIR."
        deactivate
        exit 1
    fi

    # Create .env file
    cat > "$FINANCIAL_DIR/.env" << EOF
HOST=0.0.0.0
PORT=$FINANCIAL_PORT
DEBUG=true
LOG_LEVEL=INFO
YAHOO_FINANCE_ENABLED=true
YAHOO_FINANCE_RATE_LIMIT=2000
MOCK_DATA_ENABLED=false
NLP_SERVICE_URL=$NLP_SERVER_URL
EOF

    deactivate
    echo "Financial Server setup complete."
}

# Set up NLP Server
setup_nlp_server() {
    echo "Setting up NLP Server in $NLP_DIR..."
    if [ ! -d "$NLP_DIR" ]; then
        echo "Error: Directory $NLP_DIR not found."
        exit 1
    fi

    # Create virtual environment
    if [ ! -d "$NLP_VENV" ]; then
        python3.11 -m venv "$NLP_VENV"
    fi

    # Activate virtual environment and install dependencies
    source "$NLP_VENV/bin/activate"
    if [ -f "$NLP_DIR/requirements/dev.txt" ]; then
        pip install --upgrade pip
        pip install -r "$NLP_DIR/requirements/dev.txt"
    else
        echo "Error: requirements/dev.txt not found in $NLP_DIR."
        deactivate
        exit 1
    fi

    # Create .env file
    cat > "$NLP_DIR/.env" << EOF
HOST=0.0.0.0
PORT=$NLP_PORT
DEBUG=true
LOG_LEVEL=INFO
EOF

    deactivate
    echo "NLP Server setup complete."
}

# Set up AI Analytics Server
setup_analytics_server() {
    echo "Setting up AI Analytics Server in $ANALYTICS_DIR..."
    if [ ! -d "$ANALYTICS_DIR" ]; then
        echo "Error: Directory $ANALYTICS_DIR not found."
        exit 1
    fi

    # Create virtual environment
    if [ ! -d "$ANALYTICS_VENV" ]; then
        python3.11 -m venv "$ANALYTICS_VENV"
    fi

    # Activate virtual environment and install dependencies
    source "$ANALYTICS_VENV/bin/activate"
    if [ -f "$ANALYTICS_DIR/requirements/dev.txt" ]; then
        pip install --upgrade pip
        pip install -r "$ANALYTICS_DIR/requirements/dev.txt"
    else
        echo "Error: requirements/dev.txt not found in $ANALYTICS_DIR."
        deactivate
        exit 1
    fi

    # Create .env file
    cat > "$ANALYTICS_DIR/.env" << EOF
HOST=0.0.0.0
PORT=$ANALYTICS_PORT
DEBUG=true
LOG_LEVEL=INFO
FINANCIAL_SERVER_URL=$FINANCIAL_SERVER_URL
REDIS_PASSWORD=$REDIS_PASSWORD
NLP_SERVER_URL=$NLP_SERVER_URL
EOF

    deactivate
    echo "AI Analytics Server setup complete."
}

# Start Financial Server
start_financial_server() {
    echo "Starting Financial Server on port $FINANCIAL_PORT..."
    source "$FINANCIAL_VENV/bin/activate"
    cd "$FINANCIAL_DIR" || exit 1
    nohup uvicorn run_dev:app --reload --host 0.0.0.0 --port "$FINANCIAL_PORT" > "../$LOG_DIR/financial_server.log" 2>&1 &
    FINANCIAL_PID=$!
    echo $FINANCIAL_PID > "../$FINANCIAL_PID_FILE"
    cd - > /dev/null
    deactivate
    echo "Financial Server started (PID: $FINANCIAL_PID)."
}

# Start NLP Server
start_nlp_server() {
    echo "Starting NLP Server on port $NLP_PORT..."
    source "$NLP_VENV/bin/activate"
    cd "$NLP_DIR" || exit 1
    nohup uvicorn main:app --reload --host 0.0.0.0 --port "$NLP_PORT" > "../$LOG_DIR/nlp_server.log" 2>&1 &
    NLP_PID=$!
    echo $NLP_PID > "../$NLP_PID_FILE"
    cd - > /dev/null
    deactivate
    echo "NLP Server started (PID: $NLP_PID)."
}

# Start AI Analytics Server
start_analytics_server() {
    echo "Starting AI Analytics Server on port $ANALYTICS_PORT..."
    source "$ANALYTICS_VENV/bin/activate"
    cd "$ANALYTICS_DIR" || exit 1
    nohup uvicorn main:app --reload --host 0.0.0.0 --port "$ANALYTICS_PORT" > "../$LOG_DIR/analytics_server.log" 2>&1 &
    ANALYTICS_PID=$!
    echo $ANALYTICS_PID > "../$ANALYTICS_PID_FILE"
    cd - > /dev/null
    deactivate
    echo "AI Analytics Server started (PID: $ANALYTICS_PID)."
}

# Stop all servers
stop_servers() {
    echo "Stopping all servers..."
    for pid_file in "$FINANCIAL_PID_FILE" "$NLP_PID_FILE" "$ANALYTICS_PID_FILE"; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            if ps -p "$PID" > /dev/null; then
                kill -TERM "$PID"
                echo "Stopped process with PID $PID."
            fi
            rm -f "$pid_file"
        fi
    done
    echo "All servers stopped."
}

# Main execution
case "$1" in
    start)
        check_python
        setup_logs
        setup_financial_server
        setup_nlp_server
        setup_analytics_server
        start_financial_server
        sleep 2  # Wait for Financial Server to start
        start_nlp_server
        sleep 2  # Wait for NLP Server to start
        start_analytics_server
        echo "All servers started. Logs are in $LOG_DIR."
        echo "Swagger UIs:"
        echo "  Financial Server: http://localhost:$FINANCIAL_PORT/docs"
        echo "  NLP Server: http://localhost:$NLP_PORT/docs"
        echo "  AI Analytics Server: http://localhost:$ANALYTICS_PORT/docs"
        echo "Run './start_finguard_servers.sh stop' to stop the servers."
        ;;
    stop)
        stop_servers
        ;;
    *)
        echo "Usage: $0 [start|stop]"
        exit 1
        ;;
esac