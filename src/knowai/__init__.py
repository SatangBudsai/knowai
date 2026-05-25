__version__ = "0.2.0"


def _load_config() -> None:
    """Load Postgres connection info from a knowai config file or .env.

    Search order (highest priority wins, lower-priority sources never
    overwrite an already-set value):

        1. Process env vars already set (CI / Docker / shell exports win)
        2. ./knowai.toml — walks up from cwd to find a project-local config
        3. ~/.config/knowai/config.toml — user-global fallback (XDG-style)
        4. ./.env — last-resort, also used by docker-compose

    Failures are silent so importing knowai never breaks.
    """
    import os
    import tomllib
    from pathlib import Path

    _DB_MAPPING = {
        "host":     "POSTGRES_HOST",
        "port":     "POSTGRES_PORT",
        "user":     "POSTGRES_USER",
        "password": "POSTGRES_PASSWORD",
        "db":       "POSTGRES_DB",
        "schema":   "POSTGRES_SCHEMA",
    }

    def _apply_toml(path: Path) -> bool:
        try:
            with open(path, "rb") as fh:
                data = tomllib.load(fh)
            for key, env_name in _DB_MAPPING.items():
                val = data.get("database", {}).get(key)
                if val is not None and env_name not in os.environ:
                    os.environ[env_name] = str(val)
            return True
        except Exception:
            return False

    # 1. Walk up from cwd looking for project-local knowai.toml
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        cfg = parent / "knowai.toml"
        if cfg.is_file():
            _apply_toml(cfg)
            break

    # 2. User-global fallback (XDG-style). Honored when no env var was set
    #    by the project config above — _apply_toml only writes missing keys.
    xdg = os.getenv("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    global_cfg = Path(xdg) / "knowai" / "config.toml"
    if global_cfg.is_file():
        _apply_toml(global_cfg)

    # 3. .env fallback (docker-compose compatibility)
    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        pass


_load_config()
