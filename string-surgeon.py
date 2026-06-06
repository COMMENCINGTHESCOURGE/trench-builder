#!/usr/bin/env python3
"""
STRING SURGEON — AST-based code translator.

Fixes the PANGEA_RECONSTITUTOR pattern (string.replace("cuda", "directml") as "architecture")
by operating on Python AST instead of raw text. Maps CUDA → DirectML, PyTorch CPU → GPU, etc.

Usage:
    python string-surgeon.py file.py                          # translate in-place
    python string-surgeon.py file.py --output file_fixed.py   # write to new file
    python string-surgeon.py file.py --dry-run                # show what would change
    python string-surgeon.py --list-transforms                # show all registered transforms
"""

import sys
import ast
import astor  # pip install astor
from pathlib import Path
from typing import Dict, List, Tuple


# ── Transformation Registry ──

TRANSFORMS: List[Tuple[str, Dict[str, str], str]] = [
    (
        "cuda_to_directml",
        {
            "cuda": "directml",
            "torch.cuda": "torch_directml",
            ".to('cuda')": ".to(torch_directml.device())",
            ".cuda()": ".to(torch_directml.device())",
        },
        "CUDA → DirectML (AMD GPU)",
    ),
    (
        "directml_to_cuda",
        {
            "torch_directml": "torch.cuda",
            "torch_directml.device()": "'cuda'",
        },
        "DirectML → CUDA (NVIDIA GPU)",
    ),
    (
        "cpu_to_gpu",
        {
            ".to('cpu')": ".to('cuda')",
            "device='cpu'": "device='cuda'",
        },
        "CPU → GPU",
    ),
    (
        "tensorflow_to_pytorch",
        {
            "tf.": "torch.",
            "tensorflow": "torch",
            "tf.keras": "torch.nn",
            "tf.Tensor": "torch.Tensor",
        },
        "TensorFlow → PyTorch",
    ),
]


class CodeSurgeon:
    """AST-safe code translator."""

    def __init__(self):
        self.transforms = {}
        for name, mapping, desc in TRANSFORMS:
            self.transforms[name] = {
                "mapping": mapping,
                "description": desc,
            }

    def list_transforms(self):
        """Print all registered transforms."""
        for name, info in self.transforms.items():
            print(f"  {name}: {info['description']}")
            for src, dst in info["mapping"].items():
                print(f"    {src!r}  ->  {dst!r}")

    def apply(self, code: str, transform_name: str) -> Tuple[str, List[str]]:
        """
        Apply a named transform to code.
        Returns (new_code, [list_of_changes]).
        """
        if transform_name not in self.transforms:
            print(f"[ERR] Unknown transform: {transform_name}")
            print(f"  Available: {list(self.transforms.keys())}")
            return code, []

        mapping = self.transforms[transform_name]["mapping"]
        changes = []

        # Try AST-level transforms first
        try:
            tree = ast.parse(code)
            modified = self._transform_ast(tree, mapping, changes)
            if modified:
                new_code = astor.to_source(tree)
                return new_code, changes
        except SyntaxError:
            pass

        # Fallback: string-level transform (for non-Python or malformed code)
        new_code = code
        for src, dst in mapping.items():
            if src in new_code:
                count = new_code.count(src)
                new_code = new_code.replace(src, dst)
                changes.append(f"  replaced {count}x: {src!r} -> {dst!r}")

        return new_code, changes

    def _transform_ast(self, tree: ast.AST, mapping: Dict[str, str], changes: List[str]) -> bool:
        """
        Walk the AST and transform attribute/name references.
        Returns True if any change was made.
        """
        modified = False

        class _TransformVisitor(ast.NodeTransformer):
            def __init__(self, mapping, changes):
                self.mapping = mapping
                self.changes = changes
                self.modified = False

            def visit_Attribute(self, node):
                # Full path like torch.cuda
                full_path = self._node_path(node)
                if full_path in self.mapping:
                    target = self.mapping[full_path]
                    self.changes.append(f"  ast: {full_path} -> {target}")
                    self.modified = True
                    # Build replacement AST
                    return self._build_attr_from_path(target)
                return self.generic_visit(node)

            def visit_Name(self, node):
                if node.id in self.mapping:
                    target = self.mapping[node.id]
                    self.changes.append(f"  ast: {node.id} -> {target}")
                    self.modified = True
                    return ast.Name(id=target, ctx=node.ctx)
                return node

            def visit_Call(self, node):
                # Handle .to('cuda') pattern
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ("cuda",):
                        self.changes.append(f"  ast: .cuda() -> .to(torch_directml.device())")
                        self.modified = True
                        return ast.Call(
                            func=ast.Attribute(
                                value=node.func.value,
                                attr="to",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="torch_directml", ctx=ast.Load()),
                                    attr="device",
                                    ctx=ast.Load(),
                                ),
                                args=[],
                                keywords=[],
                            )],
                            keywords=[],
                        )
                return self.generic_visit(node)

            @staticmethod
            def _node_path(node) -> str:
                """Build dotted path from nested Attribute nodes."""
                parts = []
                current = node
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                return ".".join(reversed(parts))

            @staticmethod
            def _build_attr_from_path(path: str) -> ast.AST:
                """Build nested Attribute nodes from dotted path."""
                parts = path.split(".")
                result = ast.Name(id=parts[0], ctx=ast.Load())
                for part in parts[1:]:
                    result = ast.Attribute(value=result, attr=part, ctx=ast.Load())
                return result

        transformer = _TransformVisitor(mapping, changes)
        transformer.visit(tree)
        return transformer.modified


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AST-based code translator")
    parser.add_argument("file", help="Python file to translate")
    parser.add_argument("--transform", "-t", default="cuda_to_directml", help="Transform name")
    parser.add_argument("--output", "-o", help="Output file (default: overwrite input)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show changes without writing")
    parser.add_argument("--list-transforms", action="store_true", help="List registered transforms")
    args = parser.parse_args()

    surgeon = CodeSurgeon()

    if args.list_transforms:
        print("Registered transforms:")
        surgeon.list_transforms()
        return

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"[ERR] File not found: {file_path}")
        sys.exit(1)

    code = file_path.read_text()
    new_code, changes = surgeon.apply(code, args.transform)

    if args.dry_run or not changes:
        print(f"Changes for {file_path}:")
        if changes:
            for c in changes:
                print(c)
        else:
            print("  No changes needed.")
        return

    output_path = Path(args.output) if args.output else file_path
    output_path.write_text(new_code)

    print(f"Applied {args.transform} to {file_path}")
    for c in changes:
        print(c)
    print(f"Written to {output_path}")


if __name__ == "__main__":
    main()
