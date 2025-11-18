from typing import List,Optional

def make_table(headers : List,
               rows : List, 
               padding : Optional[int] = 1):
    """
    Render an ASCII table. Each cell in `rows` may be:
      - a simple value (int/float/str), or
      - a multiline string (e.g. an inner table produced by this function).
    Returns the full table as a single string.

    headers: list of header strings (one per column)
    rows: list of rows, each row is a list of cells (same length as headers)
    padding: spaces left/right inside each cell
    Thanks to GPT
    """
    # Normalize rows: each cell -> list of lines
    norm_rows = []
    for r in rows:
        if len(r) != len(headers):
            raise ValueError("Row length must match headers length")
        cell_lines = []
        for c in r:
            s = "" if c is None else str(c)
            lines = s.splitlines() or [""]
            cell_lines.append(lines)
        norm_rows.append(cell_lines)

    cols = len(headers)

    # compute column widths: max length among header and all cell lines in that column
    col_widths = []
    for j in range(cols):
        maxw = len(str(headers[j]))
        for r_cells in norm_rows:
            for line in r_cells[j]:
                maxw = max(maxw, len(line))
        col_widths.append(maxw)

    # helpers to build borders and rows
    def make_border():
        return "+" + "+".join("-" * (w + 2 * padding) for w in col_widths) + "+"

    def make_header_line():
        parts = []
        for h, w in zip(headers, col_widths):
            parts.append(" " * padding + str(h).ljust(w) + " " * padding)
        return "|" + "|".join(parts) + "|"

    # build the full output
    out_lines = []
    border = make_border()
    out_lines.append(border)
    out_lines.append(make_header_line())
    out_lines.append(border)

    for row_cells in norm_rows:
        # how many physical lines this row needs (max of cell line counts)
        height = max(len(lines) for lines in row_cells)
        for i in range(height):
            parts = []
            for j, lines in enumerate(row_cells):
                text = lines[i] if i < len(lines) else ""
                parts.append(" " * padding + text.ljust(col_widths[j]) + " " * padding)
            out_lines.append("|" + "|".join(parts) + "|")
        out_lines.append(border)

    return "\n".join(out_lines)
