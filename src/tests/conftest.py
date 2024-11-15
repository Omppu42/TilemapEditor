
import sys
from pathlib import Path
from util.util_logger import logger

logger.log("LAUNCHING TESTS")

# Dynamically add the project root to PYTHONPATH
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


# Specify order of execution
def pytest_collection_modifyitems(session, config, items):
    first_test = "test_initialize.py"
    last_test = "test_end.py"

    include_files = "test_brushes.py"

    # Sort the test items
    first_items = [item for item in items if first_test in item.nodeid]
    last_items = [item for item in items if last_test in item.nodeid]
    middle_items = [item for item in items if item not in first_items + last_items]   # ALL FILES
    # middle_items = [item for item in items if include_files in item.nodeid]             # ONLY INCLUDE_FILES

    # Reorder items: first -> middle -> last
    items[:] = first_items + middle_items + last_items