# 0002. Note identity is content-derived; text fixes arrive as new Notes

**Status**: accepted (2026-11-04)

`anki/build_apkg.py` builds Notes with genanki's default GUID, a hash of the field text, so Anki recognises a Note on re-import only while its text is unchanged. We keep that rule instead of pinning explicit IDs: the TSV stays three columns, and a 10-day sprint expects only a handful of text fixes. Editing a Note's text therefore creates a new Note and leaves the old one in the collection as an Orphan to delete by hand; tag-only edits keep the identity and are safe.

**Considered options**: (a) a 4th TSV column holding a stable GUID pinned to today's content hashes — rejected: builder and validator changes plus a one-off pinning pass for little benefit at this size; (b) content-derived identity — chosen.

**Consequences**: before the first import of a batch, text edits are free. After import, every text fix costs one manual Orphan deletion in Anki's Browse. Orphans are found by comparing Note GUIDs of the revision last imported against the current TSVs.
