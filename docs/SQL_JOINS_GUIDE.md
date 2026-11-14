# SQL Joins Guide — Left Join & Self Join

> **Project:** College Club Management System (ClubHub DBMS)  
> **Database:** `trial_club`  
> **Target Tables:** `Students`, `Memberships`, `Clubs`  
> **Runnable SQL Script:** [`docs/hem-joins.sql`](file:///d:/VIT%20PUNE/GDG/cloud/docs/hem-joins.sql)

---

## 1. LEFT JOIN QUERY

### SQL Query:
```sql
SELECT 
    s.student_id,
    s.name AS student_name,
    s.dept_name,
    m.club_id,
    m.role AS club_role
FROM Students s
LEFT JOIN Memberships m 
    ON s.student_id = m.student_id
ORDER BY s.student_id;
```

### Explanation:
1. This query retrieves all students from the `Students` table along with their club affiliations if they are enrolled in any club.
2. Students who have not joined any club still appear in the results with `NULL` values, ensuring no student is excluded from the list.

---

## 2. SELF JOIN QUERY

### SQL Query:
```sql
SELECT 
    m1.club_id,
    m1.student_id AS leader_1_id,
    m1.role AS leader_1_role,
    m2.student_id AS leader_2_id,
    m2.role AS leader_2_role
FROM Memberships m1
JOIN Memberships m2 
    ON m1.club_id = m2.club_id 
   AND m1.membership_id != m2.membership_id
WHERE m1.role = 'President' 
  AND m2.role = 'Secretary'
  AND m1.status = 'Active' 
  AND m2.status = 'Active';
```

### Explanation:
1. This query joins the `Memberships` table with itself to find and pair the active President and Secretary within the same club.
2. It matches rows sharing the identical `club_id` while filtering for distinct leadership roles, linking complementary club executives together.

