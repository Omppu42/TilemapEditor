

def insert_into_string(string: str, char: str, pos: int) -> str:
    return string[:pos] + char + string[pos:]

def remove_pos_from_str(string: str, pos: int) -> str:
    start = pos - 1 if pos > 0 else 0
    return string[:start] + string[pos:]

def remove_range_from_str(string: str, remove_start: int, remove_end: int) -> str:
    return string[:remove_start] + string[remove_end:]

def get_next_break_index_left(string: str, cursor_pos: int, breaks: "list[str]") -> int:
    closest_index = 0

    # Don't allow -1 for search end
    search_end = cursor_pos - 1 if cursor_pos > 0 else 0

    # Find a position closest to the cursor on the left that stops the control remove
    for _s in breaks:
        _pos = string.rfind(_s, 0, search_end) + 1
        if cursor_pos - _pos < cursor_pos - closest_index:
            closest_index = _pos
    
    # No stoppers found
    if closest_index == -1: return 0

    # If next to the stopper are more stoppers, extend the closest index to delete all adjacent stoppers
    for i in range(0, 10):
        # Continue looking further if not reached end and still finding stops
        if closest_index - i >= 0 and string[closest_index - i] in breaks:
            continue
        if i > 0: closest_index -= (i - 1)
        break

    return closest_index

def get_next_break_index_right(string: str, cursor_pos: int, breaks: "list[str]") -> int:
    closest_index = len(string)

    # Find a position closest to the cursor on the left that stops the control remove
    for _s in breaks:
        _pos = string.find(_s, cursor_pos + 1, len(string))
        if _pos == -1: _pos = len(string)

        if _pos - cursor_pos < closest_index - cursor_pos:
            closest_index = _pos

    # No stoppers found
    if closest_index == -1: return len(string)

    # If next to the stopper are more stoppers, extend the closest index to delete all adjacent stoppers
    for i in range(0, 10):
        # Continue looking further if not reached end and still finding stops
        if closest_index + i < len(string) and string[closest_index + i - 1] in breaks:
            continue
        if i > 0: closest_index += (i - 1)
        break
    
    return closest_index