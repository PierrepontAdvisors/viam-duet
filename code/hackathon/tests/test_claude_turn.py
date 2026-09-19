from duet import claude_turn
from duet.session import ARTISTS


def test_every_artist_has_a_note_and_the_system_prompt_is_artist_free():
    assert set(claude_turn.ARTIST_NOTES) == set(ARTISTS)
    assert "Keith Haring" not in claude_turn.SYSTEM        # the note rides on the user text; SYSTEM stays cacheable
    assert "Keith Haring" in claude_turn.ARTIST_NOTES["haring"]
