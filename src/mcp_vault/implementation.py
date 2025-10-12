from pathlib import Path
import re


def load_api_token(config_path):
    """Load API token from a JSON file."""

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        token = data.get("apiKey")
        if not token:
            err = f"Error: 'apiKey' key not found in {config_path}"
            print(err)
            raise ValueError(err)
        return token
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        raise
    except json.JSONDecodeError:
        print(f"Error: Config file {config_path} is not valid JSON.")
        raise


def parse_headings(md_text):
    """Return a list of (level, title) pairs from Markdown text."""

    pattern = re.compile(r'^(#+)\s+(.*)', re.MULTILINE)
    return [(len(m.group(1)) * '#', m.group(2).strip()) for m in pattern.finditer(md_text)]


def find_parent_chain(headings, target):
    """Given a list of (level, title) and a target title, return its parent chain.
    
    Returns empty list if heading exists but has no parents, None if not found.
    """

    stack = []
    for level, title in headings:
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
        if title == target:
            # return all parent titles except the target itself
            return [t for _, t in stack[:-1]]
    return None


def list_headings(path: Path):
    """Return a list of all headings within the file."""

    md_text = path.read_text(encoding="utf-8")
    return parse_headings(md_text)


def nail_heading(path: Path, heading: str):
    """Return a structured heading chain."""

    md_text = path.read_text(encoding="utf-8")
    headings = parse_headings(md_text)

    chain = find_parent_chain(headings, heading)
    if chain is None:
        return "Heading not found!"

    chain.append(heading)
    return "::".join(chain)


if __name__ == "__main__":
    # quick and dirty testing implement
    # TODO add proper tests, yeah?
    import sys
    md_path = Path(sys.argv[1])
    md_text = md_path.read_text(encoding="utf-8")

    headings = parse_headings(md_text)
    print(headings)
    for lvl, title in headings:
        print(f"{lvl} {title}")

    md_heading = sys.argv[2] if len(sys.argv) > 2 else 'Test'

    print(nail_heading(md_path, md_heading))

