import pytest
import tempfile
import os
from trench_builder.core.code_vinculum import CodeVinculum

def test_code_vinculum_clean_file():
    """Verify that a standard formatted codebase file passes the audit."""
    validator = CodeVinculum()
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp:
        temp.write('print("Hello World")\n')
        temp.write('with open("out.txt", "w", encoding="utf-8") as f:\n')
        temp.write('    f.write("test")\n')
        temp_path = temp.name
        
    try:
        metrics = validator.audit_file(temp_path)
        assert metrics["git_conflicts"] == 0.0
        assert metrics["unsafe_file_writes"] == 0.0
        assert metrics["drive_casing_drift"] == 0.0
        
        passed, failures = validator.validate_all(metrics)
        assert passed
        assert len(failures) == 0
    finally:
        os.remove(temp_path)


def test_code_vinculum_conflict_markers():
    """Verify that git merge conflicts are detected."""
    validator = CodeVinculum()
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp:
        temp.write('<<<<<<< HEAD\n')
        temp.write('print("A")\n')
        temp.write('=======\n')
        temp.write('print("B")\n')
        temp.write('>>>>>>> remote-branch\n')
        temp_path = temp.name
        
    try:
        metrics = validator.audit_file(temp_path)
        assert metrics["git_conflicts"] == 1.0
        passed, failures = validator.validate_all(metrics)
        assert not passed
        assert "git_conflicts" in failures[0]
    finally:
        os.remove(temp_path)


def test_code_vinculum_unsafe_writes():
    """Verify that open() writes without explicit encoding are caught."""
    validator = CodeVinculum()
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp:
        # Unsafe write open
        temp.write('with open("output.json", "w") as f:\n')
        temp.write('    f.write("{}")\n')
        temp_path = temp.name
        
    try:
        metrics = validator.audit_file(temp_path)
        assert metrics["unsafe_file_writes"] == 1.0
        passed, failures = validator.validate_all(metrics)
        assert not passed
        assert "unsafe_file_writes" in failures[0]
    finally:
        os.remove(temp_path)


def test_code_vinculum_casing_drift():
    """Verify that lowercase c:\\ drive indicators are flagged."""
    validator = CodeVinculum()
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp:
        temp.write('path_var = "c:\\\\Users\\\\dasha\\\\Projects"\n')
        temp_path = temp.name
        
    try:
        metrics = validator.audit_file(temp_path)
        assert metrics["drive_casing_drift"] == 1.0
        passed, failures = validator.validate_all(metrics)
        assert not passed
        assert "drive_casing_drift" in failures[0]
    finally:
        os.remove(temp_path)
