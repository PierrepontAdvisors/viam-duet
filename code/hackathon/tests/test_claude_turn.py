from duet import claude_turn
from duet.session import ARTISTS


def test_every_artist_has_a_note_and_the_system_prompt_is_artist_free():
    assert set(claude_turn.ARTIST_NOTES) == set(ARTISTS)
    assert "Keith Haring" not in claude_turn.SYSTEM        # the note rides on the user text; SYSTEM stays cacheable
    assert "Keith Haring" in claude_turn.ARTIST_NOTES["haring"]


def test_every_artist_has_asks_for_each_length_and_the_prompt_artists_have_their_own():
    for a in ARTISTS:
        for length in ("short", "medium", "long"):
            assert claude_turn.asks_for(a, length)
    assert "colonnade" in claude_turn.asks_for("architect", "long") and "housing" in claude_turn.asks_for("designer", "medium")
    assert claude_turn.asks_for("mimic", "long") == claude_turn.asks_for("haring", "long")
    assert "Architect" in claude_turn.ARTIST_NOTES["architect"] and "Product Designer" in claude_turn.ARTIST_NOTES["designer"]
