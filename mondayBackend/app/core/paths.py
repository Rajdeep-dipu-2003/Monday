from pathlib import Path
import os

def get_db_path():
    home = Path.home()

    if os.name == "posix":
        if "darwin" in os.uname().sysname.lower():
            base = home / "Library" / "Application Support"
        else:
            base = home / ".local" / "share"
    else:
        base = Path(os.getenv("LOCALAPPDATA"))
        
    app_dir = base / "mondayApp"
    app_dir.mkdir(parents=True, exist_ok=True)

    return app_dir / "data.db"

DB_PATH = get_db_path()
DATABASE_URL = f"sqlite:///{DB_PATH}"