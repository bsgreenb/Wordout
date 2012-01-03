biq query...

SELECT wordout_sharer.customer_sharer_id, wordout_sharer.code, wordout_sharer.redirect_link_id, wordout_sharer.enabled, wordout_click.id, actions_groupwise.action_id, actions_groupwise.action_name, action_total
FROM
wordout_sharer
LEFT JOIN
wordout_click
 ON wordout_sharer.id = wordout_click.sharer_id
LEFT JOIN
(
    SELECT wordout_action_type.action_id, wordout_action_type.action_name, wordout_action.click_id, COUNT(*) as action_total
    FROM
    wordout_action_type
    LEFT JOIN
    wordout_action
     ON wordout_action.action_id = wordout_action_type.id
    GROUP BY wordout_action_type.action_id
) AS actions_groupwise
 ON actions_groupwise.click_id = wordout_click.id
WHERE wordout_sharer.customer_id = 1
ORDER BY wordout_click.id DESC
LIMIT 15


#total clicks for all sharers..

#count of each action type for all sharers..

SELECT wordout_sharer.id, wordout_action_type.id, wordout_action_type.action_name, COUNT(wordout_action.id) as action_total
FROM
wordout_customer
INNER JOIN
wordout_sharer
 ON (wordout_customer.id = wordout_sharer.customer_id)
LEFT JOIN
wordout_click
 ON (wordout_click.sharer_id = wordout_sharer.id)
LEFT JOIN
wordout_action
 ON (wordout_action.click_id = wordout_click.id)
LEFT JOIN
wordout_action_type
 ON (wordout_action_type.id = wordout_action.action_id)
WHERE wordout_customer.id = 1
GROUP BY wordout_sharer.id, wordout_action_type.id
ORDER BY wordout_sharer.created DESC