# event_tracker

## Configuration
1. In Windows open "System Properties -> Environment Variables..."
2. Create the following "System variables":
   - `ENVOS_SMGR_VALUE_01` - User password(For example, `your_pass`)
   - `ENVOS_SMGR_VALUE_02` - Host name (`localhost`)
   - `ENVOS_SMGR_VALUE_03` - Database name (For example, `EventTrackerDB`)
   - `ENVOS_SMGR_VALUE_04` - Port (For example, `5432`)
   - `ENVOS_SMGR_VALUE_06` - Username (For example, `postgres`)
3. Restart computer

downloads
pip install Flask psycopg2-binary python-dotenv
 pip install flask_socketio