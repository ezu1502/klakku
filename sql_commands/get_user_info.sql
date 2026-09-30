SELECT users.id, users.username, COUNT(messages.id) AS message_count FROM users
LEFT JOIN messages ON messages.sender_id = users.id
WHERE users.username = ?

GROUP BY users.id, users.username;