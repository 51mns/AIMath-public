# Locks

Active ownership is represented only by canonical lock files under this directory.

For each collision key `a/b/c`, the lock path is:

`coordination/locks/a/b/c.yml`

A task with multiple collision keys must add all corresponding lock files in one lock-only PR. Each file contains the same `lock_id`, task, actor and lease data. CI deduplicates by `lock_id`.

Do not pre-create placeholder locks.
