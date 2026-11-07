-- Lab 5 Part F: write your queries for the assistant database here.
-- Q1 requests per intent
SELECT intent, COUNT(*) AS requests FROM interaction 
GROUP BY intent ORDER BY requests DESC;
-- Q2 average latency per intent
SELECT intent, ROUND(AVG(latency_ms),1) FROM interaction GROUP BY intent;
-- Q3 topics with the most thumbs-down (JOIN feedback with interaction)
SELECT i.topic, COUNT(*) FROM interaction as i JOIN feedback f ON f.request_id = i.request_id 
WHERE f.rating = -1 GROUP BY i.topic ORDER BY 2 DESC;