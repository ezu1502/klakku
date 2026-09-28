SELECT conversation_id FROM conversation_members
WHERE user_id in (?, ?)
GROUP BY conversation_id
HAVING COUNT(DISTINCT user_id) = 2;