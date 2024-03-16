from pathlib import Path


def find_project_root(current_path: Path) -> Path:
    for parent in current_path.parents:
        if (parent / '.project_root').exists():
            return parent
    raise FileNotFoundError('Project root not found')


def root_path():
    current_path = Path(__file__).resolve()
    root_path = find_project_root(current_path)
    return root_path
