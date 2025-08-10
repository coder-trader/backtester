# Makefile for Data Collection CLI
# Usage: make collect SYMBOL=BTC/USDT TIMEFRAME=1h START=2024-01-01 END=2024-01-07

# Default values
SYMBOL ?= BTC/USDT
EXCHANGE ?= binance
TIMEFRAME ?= 1h
START ?= 
END ?= 
OUTPUT ?= data
LIMIT ?= 1000

# Python command with uv
PYTHON_CMD = uv run python

.PHONY: help collect list-symbols list-timeframes example clean test

# Default target
help:
	@echo "Data Collection CLI Makefile"
	@echo "============================="
	@echo ""
	@echo "Commands:"
	@echo "  make collect         - Collect candle data (use variables below)"
	@echo "  make list-symbols    - List available symbols for exchange"
	@echo "  make list-timeframes - List available timeframes for exchange"
	@echo "  make example         - Run example script"
	@echo "  make clean          - Clean up data directory"
	@echo "  make test           - Test CLI functionality"
	@echo ""
	@echo "Variables:"
	@echo "  SYMBOL=$(SYMBOL)         - Trading pair symbol"
	@echo "  EXCHANGE=$(EXCHANGE)       - Exchange name"
	@echo "  TIMEFRAME=$(TIMEFRAME)        - Candle timeframe"
	@echo "  START=$(START)           - Start time (optional)"
	@echo "  END=$(END)             - End time (optional)"
	@echo "  OUTPUT=$(OUTPUT)          - Output directory"
	@echo "  LIMIT=$(LIMIT)        - Limit per request"
	@echo ""
	@echo "Examples:"
	@echo "  make collect SYMBOL=BTC/USDT TIMEFRAME=1h"
	@echo "  make collect SYMBOL=ETH/USDT TIMEFRAME=5m START=2024-01-01 END=2024-01-07"
	@echo "  make collect SYMBOL=BTC/USD EXCHANGE=coinbase TIMEFRAME=1d"
	@echo "  make list-symbols EXCHANGE=kraken"

# Collect data with parameters
collect:
ifeq ($(START),)
ifeq ($(END),)
	$(PYTHON_CMD) cli.py $(SYMBOL) -x $(EXCHANGE) -t $(TIMEFRAME) -l $(LIMIT) -o $(OUTPUT)
else
	$(PYTHON_CMD) cli.py $(SYMBOL) -x $(EXCHANGE) -t $(TIMEFRAME) -e "$(END)" -l $(LIMIT) -o $(OUTPUT)
endif
else
ifeq ($(END),)
	$(PYTHON_CMD) cli.py $(SYMBOL) -x $(EXCHANGE) -t $(TIMEFRAME) -s "$(START)" -l $(LIMIT) -o $(OUTPUT)
else
	$(PYTHON_CMD) cli.py $(SYMBOL) -x $(EXCHANGE) -t $(TIMEFRAME) -s "$(START)" -e "$(END)" -l $(LIMIT) -o $(OUTPUT)
endif
endif

# Quick collection shortcuts
btc:
	$(MAKE) collect SYMBOL=BTC/USDT TIMEFRAME=1h

eth:
	$(MAKE) collect SYMBOL=ETH/USDT TIMEFRAME=1h

# List available symbols
list-symbols:
	$(PYTHON_CMD) cli.py --list-symbols -x $(EXCHANGE)

# List available timeframes
list-timeframes:
	$(PYTHON_CMD) cli.py --list-timeframes -x $(EXCHANGE)

# Run example script
example:
	$(PYTHON_CMD) example.py

# Test CLI functionality
test:
	@echo "Testing CLI help..."
	$(PYTHON_CMD) cli.py --help
	@echo ""
	@echo "Testing list timeframes..."
	$(PYTHON_CMD) cli.py --list-timeframes -x binance | head -5
	@echo ""
	@echo "CLI test completed!"

# Clean up data directory
clean:
	@echo "Cleaning data directory..."
	rm -rf $(OUTPUT)/*.csv
	@echo "Data directory cleaned!"

# Development helpers
dev-install:
	uv sync

dev-lint:
	uv run ruff check .

dev-format:
	uv run ruff format .

# Common collection patterns
daily:
	$(MAKE) collect TIMEFRAME=1d LIMIT=365

weekly:
	$(MAKE) collect TIMEFRAME=1w LIMIT=52

hourly:
	$(MAKE) collect TIMEFRAME=1h LIMIT=168

# Popular pairs shortcuts
btc-eth:
	$(MAKE) collect SYMBOL=BTC/ETH

usdt-pairs:
	$(MAKE) collect SYMBOL=BTC/USDT
	$(MAKE) collect SYMBOL=ETH/USDT
	$(MAKE) collect SYMBOL=ADA/USDT

# Show recent data files
show-data:
	@echo "Recent data files:"
	@ls -la $(OUTPUT)/*.csv 2>/dev/null | head -10 || echo "No CSV files found in $(OUTPUT)/"

# Quick stats on a data file
stats:
	@echo "Data file statistics:"
	@if [ -f "$(FILE)" ]; then \
		echo "File: $(FILE)"; \
		echo "Lines: $$(wc -l < $(FILE))"; \
		echo "Size: $$(du -h $(FILE) | cut -f1)"; \
		head -2 $(FILE); \
		echo "..."; \
		tail -1 $(FILE); \
	else \
		echo "Usage: make stats FILE=path/to/file.csv"; \
	fi