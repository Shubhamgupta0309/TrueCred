Profile in Dashboard — Manual Test Steps

1. Start backend and frontend locally (see repo README for dev commands).
2. Log in as a student user and open the Student Dashboard (`/student-dashboard`).
   - Verify the top-right shows your TrueCred ID and a link to Edit (clickable avatar/name).
3. In the Student Dashboard right column, use the search input to search for another student (3+ chars) or enter a TrueCred ID (e.g., TC123456).
   - When a result is clicked, the right column should show that student's compact profile in the new Profile card.
   - If the selected student is your own profile, the card should show an "Edit profile" button linking to `/profile`.
   - If not your own, the card shows a "Request edit" button (currently logs to console).
4. Repeat the same flow in the College Dashboard (`/college-dashboard`) from the Issue Credentials tab or Requests tab where StudentSearch is available.
5. To test the full profile page, click a student in a search result without a parent callback — you should navigate to `/students/:truecredId` and see the full StudentProfile page.

Notes:

- No commits were pushed for these UI-only changes; run locally to verify before committing.
- If you want inline editing in the ProfileCard for owners, I can implement that next.

Additional tests for Profile tabs:

Student Dashboard:

- Open `/student-dashboard`. You should see a small tab bar with "Overview" and "Profile" above the main content.
- Click "Profile": the profile form (same behavior as College Profile) should render and allow editing your student profile.

Company Dashboard:

- Open `/company-dashboard`. There will be a tab bar including "Pending Requests", "History", and "Company Profile".
- Click "Company Profile": a Company profile form (minimal) should appear allowing edit/save.
