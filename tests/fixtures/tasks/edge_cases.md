# Edge Cases Test File

This file contains edge cases and malformed tasks.

## Valid Edge Cases

- [ ] Task with variant selector emoji 📅︎ 2025-11-12
- [ ] Task with alternative scheduled emoji ⌛ 2025-11-13
- [ ] Task with alternative due emoji 📆 2025-11-14
- [ ] Task with another due emoji 🗓 2025-11-15
- [ ] Empty description 📅 2025-11-12

## Tasks Without Dates

- [ ] No date information at all
- [ ] Just a priority 🔺
- [x] Completed with no dates

## Unusual But Valid

- [ ] Multiple spaces in description    with    gaps
- [ ] Description with emoji 😀 in the middle 📅 2025-11-12
- [ ] Task with number 123 in it 📅 2025-11-12

## Not Tasks (Should Be Ignored)

This is a regular paragraph, not a task.

* This is a list item but not a checkbox task
- This is also a list item without checkbox

Some random text here.

## Indented Tasks

  - [ ] Indented task level 1
    - [ ] Indented task level 2
      - [ ] Indented task level 3

## Tasks in Blockquotes

> - [ ] Task inside blockquote
> - [x] Completed task in blockquote

## Numbered List Tasks

1. [ ] First numbered task
2. [ ] Second numbered task
3. [x] Third numbered task completed
