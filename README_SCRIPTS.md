# Database Debug and Fix Scripts

This directory contains three Python scripts to help debug and fix issues with missing zines in the database.

## Scripts

### 1. `check_database_status.py`
**Purpose**: Get an overview of the database environment and current state

**Usage**:
```bash
python check_database_status.py
```

**What it does**:
- Shows whether you're running on Vercel or locally
- Checks if Firebase/Firestore is configured
- Shows the database URL being used
- Lists all zines for the 'dev' user in both Firestore and SQLAlchemy
- Provides recommendations for next steps

### 2. `debug_zine.py`
**Purpose**: Check if a specific zine exists in the database

**Usage**:
```bash
python debug_zine.py
```

**What it does**:
- Checks both Firestore and SQLAlchemy databases
- Looks specifically for the zine at `/dev/second`
- Shows detailed information if the zine is found
- Reports which database system contains the zine

### 3. `fix_zine.py`
**Purpose**: Create the missing zine at `/dev/second`

**Usage**:
```bash
python fix_zine.py
```

**What it does**:
- Creates the 'dev' user if it doesn't exist
- Creates a zine with slug 'second' for the 'dev' user
- Adds a sample page with text and a blue circle
- Tries Firestore first, falls back to SQLAlchemy if needed
- Sets the zine status to 'published' so it's accessible

## Typical Workflow

1. **Check the current state**:
   ```bash
   python check_database_status.py
   ```

2. **Debug the specific issue**:
   ```bash
   python debug_zine.py
   ```

3. **Fix the missing zine** (if needed):
   ```bash
   python fix_zine.py
   ```

4. **Verify the fix**:
   ```bash
   python debug_zine.py
   ```

## When to Use These Scripts

### On Vercel (Production)
- The in-memory SQLAlchemy database resets on every deployment
- If Firestore is not configured, zines will be lost on each deploy
- Use these scripts to recreate missing demo data after deployments

### Local Development
- Use when the local database gets corrupted or cleared
- Helpful for setting up demo data for testing
- Can be run multiple times safely (checks for existing data first)

## Database Priority

The application uses this priority for data storage:
1. **Firestore** (if configured and available)
2. **SQLAlchemy** (fallback, in-memory on Vercel)

The scripts follow the same priority and will automatically use the appropriate database system.

## Sample Zine Content

The created zine includes:
- **Title**: "Second Zine"
- **Slug**: "second" (accessible at `/dev/second`)
- **Status**: "published"
- **Content**: Welcome text and a blue circle shape
- **Creator**: User 'dev'

## Error Handling

All scripts include comprehensive error handling and will:
- Show clear success/failure messages
- Provide specific error details when something goes wrong
- Continue with fallback options when possible
- Give actionable recommendations