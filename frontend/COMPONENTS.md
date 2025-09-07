# TrueCred Frontend Components

This document lists the key reusable components that will be used across the TrueCred frontend application.

## Layout Components

1. **AppLayout**
   - Main layout wrapper for authenticated pages
   - Includes header, sidebar, and main content area

2. **PublicLayout**
   - Layout for public pages
   - Includes public header and footer

3. **AuthLayout**
   - Layout for authentication pages
   - Simplified header and centered content

4. **AdminLayout**
   - Layout for admin pages
   - Admin header and sidebar with privileged navigation

5. **Sidebar**
   - Navigation sidebar for authenticated users
   - Different menus based on user role

6. **Header**
   - Application header with navigation and user menu
   - Search bar
   - Notification bell

7. **Footer**
   - Application footer with links and copyright

## Authentication Components

8. **LoginForm**
   - Email/username and password inputs
   - Remember me option
   - Submit button

9. **RegisterForm**
   - User information inputs
   - Password and confirmation
   - Terms agreement checkbox

10. **PasswordResetForm**
    - Email input or new password inputs depending on step

## Data Display Components

11. **CredentialCard**
    - Compact display of credential information
    - Verification status indicator
    - Action buttons

12. **ExperienceCard**
    - Compact display of experience information
    - Verification status indicator
    - Action buttons

13. **CredentialDetail**
    - Detailed view of credential information
    - Document previews
    - Verification information

14. **ExperienceDetail**
    - Detailed view of experience information
    - Associated credentials
    - Verification information

15. **VerificationStatusBadge**
    - Visual indicator of verification status
    - Different colors and icons for different statuses

16. **BlockchainVerificationInfo**
    - Display of blockchain verification details
    - Transaction hash
    - Timestamp
    - Verification status

17. **UserProfile**
    - User profile information display
    - Profile picture
    - Basic information
    - Contact details if visible

## Form Components

18. **CredentialForm**
    - Form for adding/editing credentials
    - Document upload
    - Field validation

19. **ExperienceForm**
    - Form for adding/editing experiences
    - Credential linking
    - Field validation

20. **VerificationRequestForm**
    - Form for requesting verification
    - Additional information
    - Verifier selection

21. **VerificationActionForm**
    - Form for verifiers to approve/reject
    - Comments/feedback field
    - Action buttons

22. **ProfileForm**
    - Form for editing user profile
    - Profile picture upload
    - Personal information fields

## Navigation Components

23. **Breadcrumbs**
    - Hierarchical navigation path
    - Links to parent pages

24. **Pagination**
    - Page navigation for lists
    - Items per page selector

25. **SearchBar**
    - Search input with filters
    - Auto-suggestions

26. **TabNavigation**
    - Tab-based navigation for sections
    - Active tab indicator

## Utility Components

27. **NotificationList**
    - List of user notifications
    - Read/unread status
    - Action buttons

28. **LoadingSpinner**
    - Loading indicator for async operations

29. **ErrorMessage**
    - Display for error messages
    - Different styles based on severity

30. **SuccessMessage**
    - Display for success messages

31. **ConfirmDialog**
    - Confirmation dialog for destructive actions
    - Customizable message and buttons

32. **FileUpload**
    - File upload component with preview
    - Drag and drop support
    - File type validation

33. **DatePicker**
    - Date selection component
    - Range selection option

## Dashboard Components

34. **DashboardSummary**
    - Summary cards for key metrics
    - Quick action buttons

35. **ActivityFeed**
    - Timeline of recent activities
    - Filterable by type

36. **VerificationRequestList**
    - List of pending verification requests
    - Filter and sort options

37. **StatisticsCard**
    - Display of key statistics
    - Visual chart or graph

## Admin Components

38. **UserManagementTable**
    - Table of users with management actions
    - Role assignment
    - Status indicators

39. **SystemSettingsForm**
    - Form for system-wide settings
    - Grouped by category

## Implementation Notes

- Use a design system like Material-UI, Chakra UI, or Tailwind CSS for consistent styling
- Implement responsive design for all components
- Ensure accessibility compliance (WCAG 2.1)
- Use TypeScript for type safety
- Document props and usage for each component
- Include unit tests for all components
