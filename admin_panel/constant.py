from admin_panel.forms import BookForm, BoardGameForm, StationeryForm

CATEGORY_MAP = {
    'books': BookForm,
    'board-games': BoardGameForm,
    'stationery': StationeryForm,
}

RELATED_MAP = {
    'books': 'book',
    'board-games': 'board_game',
    'stationery': 'stationery',
}