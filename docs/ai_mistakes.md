# AI mistake: orphan model handling

**Situation:** Raw inventory contains 12 records referencing `model_id` 9002,
but that ID does not exist in the raw models table. An initial attempted fix
created a synthetic model row named `Model ID 9002 (unresolved)`. That did not
repair the source relationship; it moved the data-quality error into the Gross
margin by model chart and made an orphan look like a legitimate model category.

**How discovered:** A left join from raw inventory to raw models showed that the
models table contains IDs 1–54 and that 9002 is the only missing distinct ID.
It occurs on inventory IDs **621, 3577, 3885, 6801, 13646, 14656, 19474, 19698,
20217, 24234, 24619, and 24933**. The chart then visibly displayed the synthetic
`Model ID 9002 (unresolved)` category.

**How corrected:** No model dimension member is now created for 9002. During
foreign-key validation, each affected inventory row preserves `9002` in
`model_id_raw`, sets cleaned `model_id` to NULL, sets `model_id_orphan_flag` to
true, and receives `_row_quality_status = ERROR`. Sales analytics exclude records
whose linked inventory row is an error. As an additional display safeguard,
Gross margin by model explicitly removes rows where `model_id_orphan_flag` is
true or the model label contains `Model ID` or `Unmapped`.

**System-wide prevention:** A later audit found that other analytics paths still
used `Unmapped` as a display fallback and did not consistently validate joined
branch/model dimensions. The shared enrichment logic now excludes ERROR inventory
relationships before aggregation and requires canonical model/branch labels. It
does not discard a named model merely because an unrelated attribute such as
manufacturer is missing. Warranty drill-down applies the same rule. No management
metric or drill-down creates an `Unmapped` category; unresolved records remain
available only through data-quality flags and raw fields.
The same audit identified eight legitimate branch names that had never been added
to the reviewed exact mapping table. Rather than excluding their otherwise valid
sales, the precise raw spellings were explicitly mapped to Cape Coast, Koforidua,
Ho, Sunyani, Techiman, Wa, Bolgatanga, and Kasoa. No fuzzy matching was introduced.
