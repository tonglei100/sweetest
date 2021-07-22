from pathlib import Path


path = Path(__file__).resolve().parents[0]

__all__ = []
for p in path.iterdir():
    __all__.append(p.stem)