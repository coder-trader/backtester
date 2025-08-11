# Collect Candles Flow Diagram

This diagram shows the complete flow of the `collect_candles` method from the `CandleDataCollector` class.

```mermaid
flowchart TD
    A[Start collect_candles] --> B[Load Markets]
    B --> C{Symbol exists?}
    
    C -->|No| D[Raise ValueError<br/>Symbol not available]
    C -->|Yes| E[Check Timeframe]
    
    E --> F{Timeframe valid?}
    F -->|No| G[Raise ValueError<br/>Timeframe not supported]
    F -->|Yes| H[Parse Start/End Times]
    
    H --> I[Initialize Variables<br/>all_candles = []<br/>current_since = since]
    
    I --> J[Print Collection Info]
    J --> K[Start Main Loop<br/>while True]
    
    K --> L[Fetch OHLCV Data<br/>exchange.fetch_ohlcv]
    L --> M{Got candles?}
    
    M -->|No| N[Break Loop<br/>No more data]
    M -->|Yes| O[Filter by End Time<br/>if until specified]
    
    O --> P[Add to all_candles<br/>extend candles]
    P --> Q[Print Progress<br/>Fetched X candles]
    
    Q --> R{Reached end time?}
    R -->|Yes| S[Break Loop<br/>End time reached]
    R -->|No| T{Got full limit?}
    
    T -->|No| U[Break Loop<br/>No more data available]
    T -->|Yes| V[Update current_since<br/>last_timestamp + 1]
    
    V --> W[Rate Limiting<br/>sleep rateLimit]
    W --> K
    
    N --> X{Any candles collected?}
    S --> X
    U --> X
    
    X -->|No| Y[Return Empty DataFrame<br/>print No candle data retrieved]
    X -->|Yes| Z[Create DataFrame<br/>columns: timestamp, OHLCV]
    
    Z --> AA[Convert Timestamps<br/>ms to datetime UTC]
    AA --> BB[Remove Duplicates<br/>Sort by timestamp]
    BB --> CC[Print Success Info<br/>Count and date range]
    CC --> DD[Return DataFrame]
    
    Y --> EE[End]
    DD --> EE
    D --> EE
    G --> EE
    
    %% Exception handling
    L -.->|Exception| FF[Print Error and Raise]
    FF --> EE
    
    %% Styling
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef loop fill:#e0f2f1,stroke:#00695c,stroke-width:2px
    
    class A,EE startEnd
    class B,H,I,J,L,O,P,Q,V,W,Z,AA,BB,CC process
    class C,F,M,R,T,X decision
    class D,G,FF,Y error
    class DD data
    class K,N,S,U loop
```

## Key Decision Points

1. **Symbol Validation**: Checks if the requested symbol exists on the exchange
2. **Timeframe Validation**: Verifies the timeframe is supported by the exchange
3. **Data Availability**: Continues fetching until no more data or end time reached
4. **Rate Limiting**: Respects exchange rate limits between requests

## Loop Termination Conditions

The main fetching loop terminates when:
- ❌ No candles returned (no more data)
- ⏰ End time reached (if specified)
- 📉 Fewer candles than limit returned (last batch)

## Error Handling

- **Symbol Error**: Raises ValueError with available symbols
- **Timeframe Error**: Raises ValueError with supported timeframes  
- **Network/API Error**: Prints error and re-raises exception

## Data Processing Steps

1. **Raw Data**: OHLCV arrays from exchange
2. **DataFrame**: Convert to pandas with proper columns
3. **Timestamps**: Convert milliseconds to UTC datetime
4. **Cleanup**: Remove duplicates and sort chronologically
5. **Validation**: Ensure data integrity and completeness