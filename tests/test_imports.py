import sys
from pathlib import Path

def test_imports():
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

    # These imports should succeed
    from src.ui.roi_setter import ROISetter
    from src.ui.roi_selector import ROISelector
    from src.core.intensity_analyzer import IntensityAnalyzer

    # Basic assertions that classes are present
    assert hasattr(ROISetter, '__init__')
    assert hasattr(ROISelector, '__init__')
    assert hasattr(IntensityAnalyzer, '__init__')
