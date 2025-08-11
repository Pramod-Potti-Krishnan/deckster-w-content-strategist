# Layout Architect Testing Guide

## ✅ Setup Status
All components are properly configured and ready for testing!

## Prerequisites
1. **Database Migration**: Run the following SQL in your Supabase SQL Editor:
   ```sql
   -- File: migrations/create_themes_table.sql
   CREATE TABLE IF NOT EXISTS themes (
       id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
       session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
       theme_spec JSONB NOT NULL,
       created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()),
       updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()),
       UNIQUE(session_id)
   );
   
   CREATE INDEX idx_themes_session_id ON themes(session_id);
   ```

2. **Environment Variables**: Your `.env` file should have:
   - `GOOGLE_API_KEY` - Required for theme generation
   - `SUPABASE_URL` - Required for database
   - `SUPABASE_ANON_KEY` - Required for database
   - Optional Layout Architect settings (defaults will be used if not set)

## Testing Options

### Option A: Unit Tests (No external dependencies)
Tests the core functionality of Layout Architect components.

```bash
# Activate virtual environment
source venv/bin/activate

# Run unit tests
pytest test/test_layout_architect.py -v

# Expected: 9 tests should pass
```

**What it tests:**
- White space calculation and validation
- Grid alignment validation  
- Integer positioning
- Layout engine functionality

### Option B: Integration Test (Requires Google API key)
Tests Layout Architect in isolation with mock data.

```bash
# Activate virtual environment
source venv/bin/activate

# Run integration test
python test/test_layout_architect_integration.py
```

**Expected output:**
- Theme generation with colors and typography
- Layout creation for 4 test slides
- White space ratios between 30-50%
- Alignment scores > 90%
- Mock WebSocket messages showing the flow

### Option C: Full Application Test (Requires all credentials)
Tests the complete workflow from user input to layout generation.

**Terminal 1 - Start the application:**
```bash
source venv/bin/activate
python main.py
```

**Terminal 2 - Run the test client:**
```bash
source venv/bin/activate
python test/test_layout_with_main.py
```

**Expected flow:**
1. Connect to WebSocket
2. Send initial presentation request
3. Answer clarifying questions
4. Accept the plan
5. Accept the strawman (this triggers Layout Architect)
6. Receive theme_update message
7. Receive progressive slide_update messages

## Verification Script
To check if everything is set up correctly:

```bash
source venv/bin/activate
python verify_layout_architect_setup.py
```

## What Layout Architect Does

When a strawman is accepted, Layout Architect:

1. **Generates a Theme**:
   - Professional color palette
   - Typography hierarchy (h1, h2, h3, body, caption)
   - Standard layouts for different slide types

2. **Creates Layouts for Each Slide**:
   - Analyzes content and determines best arrangement (vertical/horizontal/grid)
   - Positions containers with integer coordinates on 160×90 grid
   - Ensures 30-50% white space ratio
   - Validates grid alignment (rows/columns)
   - Maintains consistent dimensions for similar elements

3. **Sends Progressive Updates**:
   - theme_update message with complete theme
   - slide_update messages for each slide with layout details
   - status_update messages showing progress

## Troubleshooting

**Import Errors**: Make sure you're in the virtual environment
```bash
source venv/bin/activate
```

**API Key Issues**: Check your .env file
```bash
grep GOOGLE_API_KEY .env
```

**Database Issues**: Ensure the themes table migration has been run in Supabase

**WebSocket Connection Issues**: Make sure main.py is running on port 8000

## Layout Quality Metrics

Each layout is validated for:
- **White Space**: 30-50% of slide area
- **Margins**: Minimum 8 grid units on all edges
- **Gutters**: 4 grid units between containers
- **Alignment**: Containers align to rows/columns
- **Integer Positions**: All coordinates are whole numbers
- **No Overlaps**: Containers don't overlap

## Next Steps

After testing, you can:
1. Adjust layout parameters in `.env`
2. Modify design principles in the layout engine
3. Add new layout arrangements
4. Enhance theme generation with more sophisticated palettes