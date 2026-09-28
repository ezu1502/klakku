
SELECT members1.conversation_id, users.username
FROM conversation_members AS members1

JOIN conversation_members AS members2
    ON members1.conversation_id = members2.conversation_id

JOIN users
    ON users.id = members2.user_id


WHERE members1.user_id = ?
AND members2.user_id != ?