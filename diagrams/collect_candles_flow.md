# Collect Candles Flow Diagram

This diagram shows the complete flow of the `collect_candles` method from the `CandleDataCollector` class.

```mermaid
flowchart TD
    A[Start collect_candles] --> B[Load Markets]
    B --> C{Symbol exists?}
    
    C -->|No| D[Raise ValueError: Symbol not available]
    C -->|Yes| E[Check Timeframe]
    
    E --> F{Timeframe valid?}
    F -->|No| G[Raise ValueError: Timeframe not supported]
    F -->|Yes| H[Parse Start/End Times]
    
    H --> I[Initialize Variables]
    
    I --> J[Print Collection Info]
    J --> K[Start Main Loop]
    
    K --> L[Fetch OHLCV Data]
    L --> M{Got candles?}
    
    M -->|No| N[Break Loop: No more data]
    M -->|Yes| O[Filter by End Time]
    
    O --> P[Add to all_candles]
    P --> Q[Print Progress]
    
    Q --> R{Reached end time?}
    R -->|Yes| S[Break Loop: End time reached]
    R -->|No| T{Got full limit?}
    
    T -->|No| U[Break Loop: No more data available]
    T -->|Yes| V[Update current_since]
    
    V --> W[Rate Limiting Sleep]
    W --> K
    
    N --> X{Any candles collected?}
    S --> X
    U --> X
    
    X -->|No| Y[Return Empty DataFrame]
    X -->|Yes| Z[Create DataFrame]
    
    Z --> AA[Convert Timestamps]
    AA --> BB[Remove Duplicates and Sort]
    BB --> CC[Print Success Info]
    CC --> DD[Return DataFrame]
    
    Y --> EE[End]
    DD --> EE
    D --> EE
    G --> EE
    
    %% Exception handling
    L -.->|Exception| FF[Print Error and Raise]
    FF --> EE
    
    %% Styling with better contrast and readability
    classDef startEnd fill:#1e3a8a,stroke:#1e40af,stroke-width:3px,color:#ffffff
    classDef process fill:#059669,stroke:#047857,stroke-width:2px,color:#ffffff
    classDef decision fill:#d97706,stroke:#b45309,stroke-width:2px,color:#ffffff
    classDef error fill:#dc2626,stroke:#b91c1c,stroke-width:3px,color:#ffffff
    classDef data fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#ffffff
    classDef loop fill:#0891b2,stroke:#0e7490,stroke-width:2px,color:#ffffff
    
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