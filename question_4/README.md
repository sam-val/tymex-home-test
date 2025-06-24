# Question 4:
You're working on a financial transaction system with the following schema:

```sql
CREATE TABLE transactions (
transaction_id UUID PRIMARY KEY,
account_number VARCHAR(50),
transaction_amount DECIMAL(19, 4),
transaction_type VARCHAR(20),
booking_date DATE,
entry_date TIMESTAMP
);
CREATE INDEX idx_account_number ON transactions(account_number);
```

The system has grown significantly over time and now contains:

- Over 10 million account numbers
- Some accounts have more than 1 million transactions
- The total table size exceeds several billion rows

Currently, the application uses this query to retrieve paginated transactions for a specific account:

```sql
SELECT * FROM transactions
WHERE account_number = ?
ORDER BY entry_date DESC
LIMIT 20 OFFSET ?;
```

This query has become increasingly slow as the system has grown, particularly for accounts with large numbers of transactions.

Provide suggestion to optimize this query

## Problems with this query

### 1. `ORDER BY entry DESC`
This can be very expensive, although we already have an index on `account_number` but when we have millions of row, sorting is costly.

### To fix it
One approach is to make a `composite index` between account_number and entry_date. We can make index for `entry ASC` too if there is a use-case.

```sql
CREATE INDEX idx_account_entry_date_desc
ON transactions(account_number, entry_date DESC);

-- can also add this index, depends on use case
CREATE INDEX idx_account_entry_date_asc
ON transactions(account_number, entry_date ASC);
```

### 2. `OFFSET ?`
When there are millions of records, offset can affect performance

```sql
SELECT * FROM transactions
WHERE account_number = ?
ORDER BY entry_date DESC
LIMIT 20 OFFSET 100000000000;
```

The database only need 20 but it skips through `100000000000` rows which is expensive.

### To fix

Use `where id > N` to paginate instead

```sql
SELECT * FROM transactions
WHERE account_number = '123' 
AND entry_date < '2024-08-10 13:45:00'
ORDER BY entry_date DESC
LIMIT 20;
```

Downside is for each page, we need to save previous oldest `entry_date` between every request.
