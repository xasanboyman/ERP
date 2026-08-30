# Context and Environment

## Directories
- FastAPI Backend: `/home/xasanboy/ERP/Back`
- Vue/Vite Frontend: `/home/xasanboy/ERP/Front`
- Reference Laravel Backend: `/home/xasanboy/Knittix-new`

## Key Requirements
- Backend functional parity for Cutting Orders, Processes, Stages, Salary, Workers, Products.
- API endpoints `/cutting/order/list` and `/cutting/order/save` must support `responsible_user_ids`.
- Frontend `Cutting.vue` must have "Mas'ullar" dropdown fetching from `/api/user/list`.
- Frontend table must show circular user avatars that overlap (second overlays first by >50%), hover showing username tooltip.
