from fastapi import APIRouter, Query, HTTPException
from models.mm_table_users import MmTableUsers
router = APIRouter()


router.get('poker_app/game/cards/{round}')
def get_cards(round: str, users: list[str] = Query(...)):
    if not MmTableUsers.get_db_connection().find_table_by_users(users):
        raise HTTPException(status_code=404, detail="not table has the given users as players")
    if round == 'preflop':
