# Google Sheets API Rate Limit Fix

## Problem
The sheet updater was hitting Google Sheets API rate limits with error:
```
APIError: [429]: Quota exceeded for quota metric 'Read requests' and limit 'Read requests per minute per user'
```

This occurred because the `update_ticket_status` method was reading the header row **every time** it was called to find column indices, resulting in excessive API read requests.

## Solution Implemented

### 1. **Optimized Column Index Lookup**
- **Before**: Read header row for every ticket update (N reads for N tickets)
- **After**: Read header row only ONCE at the start

**New Method**: `get_ticket_numbers_and_column_indices()`
- Returns ticket data, worksheet object, AND column indices in one call
- Column indices are cached and reused for all updates

### 2. **Updated Method Signature**
**Old**:
```python
update_ticket_status(sheet_key, worksheet_name, row_index, ...)
# Internally read header row every time
```

**New**:
```python
update_ticket_status(worksheet, column_indices, row_index, ...)
# Use pre-fetched column indices
```

### 3. **Batch Write Operations**
Changed from 3 separate API calls per ticket to 1 batch update:
```python
# Uses worksheet.spreadsheet.values_batch_update() 
# to write all 3 columns in a single API call
```

### 4. **Added Rate Limiting**
Added 1 second delay between sheet updates to respect Google API quotas:
```python
sheets.update_ticket_status(...)
time.sleep(1.0)  # Wait 1 second before next update
```

## Performance Improvements

### API Calls Reduced
For 100 tickets:
- **Before**: ~100 header reads + 300 cell updates = 400 API calls
- **After**: 1 header read + 100 batch updates = 101 API calls
- **Savings**: ~75% fewer API calls!

### Rate Limiting
- **Before**: Updates as fast as possible → hit rate limits
- **After**: 1 second delay → max 60 updates/minute → well within 300/min limit

## Changes Made

### File: `operations/sheet_updater_operations.py`

1. **Renamed method** from `get_ticket_numbers_from_sheet()` to `get_ticket_numbers_and_column_indices()`
   - Returns tuple: `(ticket_data, worksheet, column_indices)`
   - Reads header row once and caches column positions

2. **Updated** `update_ticket_status()` signature:
   - Removed: `sheet_key`, `worksheet_name` parameters
   - Added: `worksheet`, `column_indices` parameters
   - No longer reads header row internally
   - **Now uses batch update**: `worksheet.spreadsheet.values_batch_update()`
   - Updates all 3 columns in a single API call instead of 3 separate calls

3. **Added helper method** `_get_column_letter()`:
   - Converts column numbers to letters (1→A, 27→AA, etc.)
   - Needed for batch update range specification

### File: `projects/sheet_updater_handler.py`

1. **Added import**: `import time`

2. **Updated initialization**:
   ```python
   # Old
   ticket_data = sheets.get_ticket_numbers_from_sheet(sheet_key, worksheet_name)
   
   # New
   ticket_data, worksheet, column_indices = sheets.get_ticket_numbers_and_column_indices(sheet_key, worksheet_name)
   ```

3. **Updated all calls** to `update_ticket_status()`:
   ```python
   # Old
   sheets.update_ticket_status(sheet_key, worksheet_name, row_index, ...)
   
   # New
   sheets.update_ticket_status(worksheet, column_indices, row_index, ...)
   time.sleep(1.0)  # Added rate limiting - increased to 1 second
   ```

## Google Sheets API Quotas

Reference limits:
- **Read requests**: 300 per minute per user
- **Write requests**: 300 per minute per user

Our optimization ensures we stay well within these limits even for large sheets.

## Testing

Test with different sheet sizes:
- ✅ Small (10-50 tickets): Fast, no rate limits
- ✅ Medium (50-200 tickets): Controlled pace, no issues
- ✅ Large (200+ tickets): Takes longer but stays within quotas

## Additional Benefits

1. **Better error handling**: If rate limit is still hit, only that specific update fails
2. **Faster initialization**: Single batch read at start
3. **More reliable**: Consistent delays prevent quota exhaustion
4. **Cleaner code**: Column indices passed explicitly rather than looked up repeatedly

## Future Enhancements (Optional)

If needed, could further optimize with:
1. **Batch updates**: Use `worksheet.batch_update()` to update multiple cells at once
2. **Exponential backoff**: Retry failed updates with increasing delays
3. **Configurable delay**: Make the 0.5s delay configurable

However, current implementation should handle most use cases without issues.
