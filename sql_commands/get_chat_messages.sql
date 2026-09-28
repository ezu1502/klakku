SELECT sender_id, content, sent_at FROM messages
WHERE conversation_id = ?
ORDER BY sent_at ASC, id ASC;