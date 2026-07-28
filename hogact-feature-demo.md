# HOG/EOG Actual Mismatch → Reason Prompt

## Scenario: IC/OG Train with HOG/EOG Discrepancy

Both [ic.php](../chg/ic.php) and [og.php](../chg/og.php) now enforce a reason when the operator selects a different **HOG/EOG(A)** (actual) than the **HOG/EOG(W)** (booked from timetable).

### Markup Changes

- `<select>` for HOG/EOG(A) got class `hogact` and two data attributes:
  - `data-w` = the booked value (readonly, from the timetable, acts as the baseline)
  - `data-prev` = the previous actual value (tracks reverts)
  
### JavaScript Behavior

**The prompt triggers when:**
1. User changes the HOG/EOG(A) dropdown to a different value than booked
2. Both booked and actual are non-empty (blank values skip silently)

**Example:**
```
Train 12345: booked HOG/EOG is HOG, but you recorded EOG.

Why was it worked on EOG? This will be saved in Remarks:
[user types: "Loco failed, substitution with EOG"]
```

**On save:**
- Reason is appended to Remarks as: `HOG/EOG HOG → EOG: Loco failed, substitution with EOG`
- If remarks already had text, the reason is prepended with ` | ` as a separator

**On cancel (empty reason):**
- Alert: "A reason is required to record EOG against booked HOG. Reverting to [prev]."
- The dropdown reverts to whatever was selected before (or "--" if new)
- `data-prev` resets to track the reverted value

### Allowed Changes (No Prompt)

These pass silently:
- Booked and actual are **the same** (e.g., both "HOG") — no change needed
- Actual is cleared **back to blank** (`--`) — treated as "not yet answered"
- Booked is blank (shouldn't happen in practice; table is readonly from timetable)

### Examples

| Booked | Actual (old) | Actual (new) | Prompt? | Note |
|--------|--------------|--------------|---------|------|
| HOG | -- | HOG | No | Match, nothing to explain |
| HOG | HOG | EOG | **Yes** | Mismatch, reason required |
| HOG | EOG | HOG | **Yes** | Switching back, still a mismatch vs booked |
| HOG | EOG | -- | No | Cleared; user can fill it later |
| EOG | -- | -- | No | Still blank, no change |

### Implementation

- **ic.php lines ~420-427:** select `class="hogact"` + data attributes + remarks-input class
- **ic.php lines ~583-617:** change event listener for `.hogact` selects, prompt logic
- **og.php lines ~390-397:** identical markup
- **og.php lines ~507-543:** identical JS

Both files share the exact pattern, so switching between IC and OG feels consistent.
