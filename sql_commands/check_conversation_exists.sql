

SELECT members1.conversation_id FROM conversation_members as members1

JOIN conversation_members as members2
    ON members1.conversation_id = members2.conversation_id

WHERE members1.user_id = ?
AND members2.user_id = ?

AND (
    SELECT COUNT(*)
    FROM conversation_members
    WHERE conversation_id = members1.conversation_id
) = 2;


